import math
from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
import rasterio
import shapely
from affine import Affine
from progress.bar import Bar
from rasterio.windows import Window
from rasterio.windows import transform as transform_for_window

from analysis.constants import DATA_CRS
from analysis.lib.raster import add_overviews, clip_window, get_data_window, shift_window, write_raster

WINDOW_SIZE = 4096
NODATA = np.uint8(0)


src_dir = Path("source_data/blueprint/subindicators")
amphibians_dir = src_dir / "2023GAP_amphibianModels"
reptiles_dir = src_dir / "2023GAP_reptileModels"


out_dir = Path("data/inputs")
subindicators_out_dir = out_dir / "subindicators"
subindicators_out_dir.mkdir(exist_ok=True)
working_dir = src_dir / "derived"
working_dir.mkdir(exist_ok=True)


################################################################################
### Create combined extent, terrestrial, and non-urban mask
################################################################################
# use NLCD as the extraction extent; it is already masked to extent and it covers
# a smaller extent closer to the species data
mask_filename = working_dir / "amphibian_reptile_mask.tif"
if not mask_filename.exists():
    with (
        rasterio.open(src_dir / "ElevationBasedTerrestrialMarineMask.tif") as terrestrial_mask,
        rasterio.open(out_dir / "nlcd/landcover_2021.tif") as nlcd,
    ):
        # nlcd already aligned to extent and has extent mask applied
        nlcd_data = nlcd.read(1)
        # mask out all nodata and existing urban (nlcd 2-5)
        mask_data = np.where(
            (nlcd_data == np.uint8(nlcd.nodata)) | ((nlcd_data >= np.uint8(2)) & (nlcd_data <= np.uint8(5))),
            NODATA,
            np.uint8(1),
        )
        del nlcd_data

        ### terrestrial extent is pixel-aligned but doesn't have same origin
        row_off = int((terrestrial_mask.transform.f - nlcd.transform.f) // nlcd.transform.a)
        col_off = int((terrestrial_mask.transform.c - nlcd.transform.c) // nlcd.transform.e)
        read_window = Window(row_off=row_off, col_off=col_off, width=nlcd.width, height=nlcd.height)
        t_mask_data = terrestrial_mask.read(1, window=read_window)
        mask_data *= t_mask_data
        del t_mask_data

        write_raster(mask_filename, mask_data, transform=nlcd.transform, crs=nlcd.crs, nodata=NODATA)
        add_overviews(mask_filename)
        del mask_data


mask = rasterio.open(mask_filename)
mask_data = mask.read(1)


################################################################################
### Extract Blueprint-aligned rasters at their data extent
################################################################################
tifs = {filename.name.split("_")[0]: filename for filename in amphibians_dir.glob("*.tif")}
tifs.update({filename.name.split("_")[0]: filename for filename in reptiles_dir.glob("*.tif")})

spp = (
    pd.read_excel(src_dir / "RSGCN_list_3may21_status.xlsx", engine="calamine")[
        ["Scientific Name", "Common Name", "strUC GAP2016"]
    ]
    .rename(columns={"Scientific Name": "SNAME", "Common Name": "CNAME", "strUC GAP2016": "id"})
    .dropna(subset="id")
)

# NOTE: there are 3 species listed for aDWSAx, 2 listed for aNPSAx; TODO: ask
# NOTE: Lampropeltis occipitolineata is not included in the SECAS list but also not in tifs; TODO: ask
# NOTE: several species in spreadsheet are not present in data folder; TODO: ask
ids = sorted(spp.loc[spp.id.str.startswith(("a", "r"))].id.unique())


### extract read window based on overlapping extent with Southeast Blueprint extent
with rasterio.open(tifs[ids[0]]) as src:
    # calculate reference transform that shifts species data to exactly match Blueprint extent
    # NOTE: we can do this because they are the same CRS and cell size, just slighthly shifted (~1m)
    y_off = ((src.transform.f - mask.transform.f) // mask.transform.a) * mask.transform.a
    x_off = ((src.transform.c - mask.transform.c) // mask.transform.e) * mask.transform.e
    f = y_off + mask.transform.f
    c = x_off + mask.transform.c
    ref_transform = Affine(a=mask.transform.a, b=mask.transform.b, c=c, d=mask.transform.d, e=mask.transform.e, f=f)

    # calculate read window within species data now assuming it is pixel aligned
    row_off = int(y_off / mask.transform.a)
    col_off = int(x_off / mask.transform.e)
    read_window = Window(row_off=row_off, col_off=col_off, width=mask.width, height=mask.height)


### create windows to detect data within bounds of the data that were read from raster
# this is an optimized approach to finding the actual data extent in a much smaller
# area
windows = []
for row_off in np.arange(read_window.height, step=WINDOW_SIZE):
    windows.append(
        np.array(
            [
                Window(row_off=row_off, col_off=col_off, width=WINDOW_SIZE, height=WINDOW_SIZE)
                for col_off in np.arange(read_window.width, step=WINDOW_SIZE)
            ]
        )
    )
windows = np.array(windows)


### Extract individual grids
for id in ids:
    outfilename = working_dir / f"{id}.tif"
    if outfilename.exists():
        continue

    if id not in tifs:
        print(f"ERROR: missing expected species: {id}")
        continue

    print(f"Extracting {id}")
    with rasterio.open(tifs[id]) as src:
        data = src.read(1, window=read_window)

        # optimization: calculate the windows that have data
        window_grid = np.zeros(windows.shape, dtype="bool")
        for i in range(windows.shape[0]):
            for j in range(windows.shape[1]):
                window = windows[i, j]
                window_grid[i, j] = data[window.toslices()].any()

        # extract data only within a window around the windows that had data; this greatly shrinks the extent
        w = Window(*get_data_window(window_grid.astype("uint8"), nodata=NODATA))
        ul = windows[w.row_off, w.col_off]
        out_window = Window(
            row_off=ul.row_off, col_off=ul.col_off, height=w.height * WINDOW_SIZE, width=w.width * WINDOW_SIZE
        )
        out_data = data[out_window.toslices()]

        # get the actual pixel-level data window within the above window
        data_window = Window(*get_data_window(out_data, nodata=NODATA))
        out_data = out_data[data_window.toslices()]
        out_window = Window(
            row_off=read_window.row_off + ul.row_off + data_window.row_off,
            col_off=read_window.col_off + ul.col_off + data_window.col_off,
            height=data_window.height,
            width=data_window.width,
        )
        out_transform = transform_for_window(out_window, ref_transform)

        # apply the combined extent / urban / terrestrial mask
        mask_window = shift_window(data_window, out_transform, mask.transform)
        out_data *= mask_data[mask_window.toslices()]

        write_raster(outfilename, out_data, transform=out_transform, crs=src.crs, nodata=NODATA)

del mask_data
mask.close()

################################################################################
### Stack and encode data
################################################################################

# TODO: transform species into one record per ID.  Need guidance from Rua.
spp = spp.groupby("id").first()


### Extract bounding boxes
boxes = []
for id in ids:
    filename = working_dir / f"{id}.tif"
    if not filename.exists():
        continue

    with rasterio.open(filename) as src:
        boxes.append({"id": id, "geometry": shapely.box(*src.bounds)})

df = gp.GeoDataFrame(boxes, geometry="geometry", crs=DATA_CRS).join(spp, on="id")
# extract upper left point of each and use this for clustering (instead of centroid by default)
bounds = shapely.bounds(df.geometry.values)
df["point"] = gp.GeoSeries(shapely.points(bounds[:, 0], bounds[:, 3]), crs=DATA_CRS)
df = df.sort_values(by="point").drop(columns=["point"]).reset_index(drop=True)

# group into 64 bit chunks
df["group"] = df.index // 64
groups = sorted(df.group.unique())

df["bit"] = np.uint64(0)
for group in groups:
    ix = df.group == group
    df.loc[ix, "bit"] = np.arange(ix.sum()).astype("uint64")

df[["group", "bit", "id", "SNAME", "CNAME"]].reset_index(drop=True).to_feather(
    subindicators_out_dir / "imperiled_amphibians_reptiles_index.feather"
)

for group in groups:
    outfilename = subindicators_out_dir / f"imperiled_amphibians_reptiles_{group}.tif"
    if outfilename.exists():
        continue

    rows = df.loc[df.group == group].copy()
    rows["src"] = rows.id.apply(lambda id: rasterio.open(working_dir / f"{id}.tif"))
    bounds = rows.total_bounds
    transform = Affine(30, 0, bounds[0], 0, -30, bounds[3])
    height = math.ceil((bounds[3] - bounds[1]) / 30)
    width = math.ceil((bounds[2] - bounds[0]) / 30)

    windows = []
    for row_off in np.arange(height, step=WINDOW_SIZE):
        for col_off in np.arange(width, step=WINDOW_SIZE):
            windows.append(Window(row_off=row_off, col_off=col_off, width=WINDOW_SIZE, height=WINDOW_SIZE))

    out = np.zeros(shape=(height, width), dtype="uint64")
    for _, row in rows.iterrows():
        for window in Bar(f"Processing {row.id}", max=len(windows)).iter(windows):
            window_transform = transform_for_window(window, transform)
            raw_window = shift_window(window, window_transform, row.src.transform)
            read_window = clip_window(
                shift_window(window, window_transform, row.src.transform), row.src.width, row.src.height
            )
            # if window doesn't overlap then skip it
            if read_window.width == 0 or read_window.height == 0:
                continue

            data = row.src.read(1, window=read_window)
            if data.max() == 0:
                continue

            out_window = shift_window(read_window, transform_for_window(read_window, row.src.transform), transform)
            out_ix = out_window.toslices()
            out[out_ix] = np.bitwise_or(np.left_shift(data.astype("uint64"), row.bit), out[out_ix])
            del data

    print(f"Saving output file")
    write_raster(outfilename, out, transform=transform, crs=DATA_CRS, nodata=0)
    add_overviews(outfilename)

    rows.src.apply(lambda x: x.close())


##### TODO:
# to check values
# reduce all to single value
# t = np.bitwise_or.reduce(data.flat)
# # number of species present is:
# np.bitwise_count(t)
# # extract specific bits that are set:
# NOTE: this is only for 8 bits at a time
# np.argwhere(np.unpackbits(t, bitorder="l") == 1).flatten()
# have to reverse bit order
# np.binary_repr(6922031441857478656)[::-1]
# ix = [bool(int(x)) for x in np.binary_repr(int(4.615195676723118e+18),width=64)[::-1]]
# np.arange(64)[ix]
