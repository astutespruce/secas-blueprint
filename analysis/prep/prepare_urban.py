from pathlib import Path
import math
from time import time

from progress.bar import Bar
import numpy as np
import rasterio
import pygeos as pg
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
from rasterio.windows import Window

from analysis.constants import MASK_RESOLUTION, URBAN_YEARS, DATA_CRS, URBAN_COLORS
from analysis.lib.colors import interpolate_colormap, hex_to_uint8
from analysis.lib.raster import add_overviews, create_lowres_mask, write_raster

CHUNK_SIZE = 500  # number of rows to read at a time
NODATA = 255

# NOTE: bins are in counts of runs projected to urbanize
# bins are 0: 0, 1: >0 to 0.25, 2: > 0.25 to 0.5, 3: >0.5, 4: already urban
BINS = [0, 0.9999, 12.5, 25]


# Create color ramp for outputs

colormap = {
    0: (255, 255, 255, 0),
    **{
        i + 1: hex_to_uint8(color) + (255,)
        for i, color in enumerate(
            interpolate_colormap({1: URBAN_COLORS[1], 50: URBAN_COLORS[3]})
        )
    },
    51: hex_to_uint8(URBAN_COLORS[4]),
}


start = time()

bnd_dir = Path("data/inputs/boundaries")
src_dir = Path("source_data/urban")
nlcd_dir = Path("data/inputs/nlcd")
out_dir = Path("data/inputs/threats/urban")
tmp_dir = Path("/tmp")

out_dir.mkdir(parents=True, exist_ok=True)

bnd_raster = rasterio.open(bnd_dir / "nonmarine_mask.tif")
bnd = pg.box(*bnd_raster.bounds)


# Read NLCD 2019 prepared using analysis/prep/prepare_nlcd.py
# this aligns exactly to bnd_raster
print("Reading NLCD 2019")
with rasterio.open(nlcd_dir / "landcover_2019.tif") as src:
    already_urban = src.read(1)
    already_urban = np.where((already_urban >= 2) & (already_urban <= 5), True, False)


### Find the overlapping window for the SE Blueprint extent
# NOTE: the urban layers are basically in same projection but use NAD83 instead of WGS84
with rasterio.open(src_dir / "probability_SSP2_2020.tif") as src:
    window = src.window(*pg.total_bounds(bnd))
    window_floored = window.round_offsets(op="floor", pixel_precision=3)
    w = math.ceil(window.width + window.col_off - window_floored.col_off)
    h = math.ceil(window.height + window.row_off - window_floored.row_off)
    window = Window(window_floored.col_off, window_floored.row_off, w, h)
    # make sure that window is within extent of data
    window = window.intersection(Window(0, 0, src.width, src.height))
    transform = src.window_transform(window)

full_window = window

### Calculate windows for extracting data
# The full raster is too big to read into memory and digitize, so
# we process in chunks based on the window
# NOTE: data are provided using a blocksize that is full width and 1px high
offsets = list(range(0, full_window.height + 1, CHUNK_SIZE))
heights = ([CHUNK_SIZE] * (len(offsets) - 1)) + [full_window.height - offsets[-1]]
windows = [
    Window(
        full_window.col_off,
        full_window.row_off + offsets[i],
        full_window.width,
        heights[i],
    )
    for i in range(len(offsets))
]


### Extract data
# NOTE: the source data do not distinguish between NODATA outside analysis area
# and areas not projected to urbanize

for year in URBAN_YEARS:
    year_start = time()
    outfilename = out_dir / f"urban_{year}.tif"

    if outfilename.exists():
        print(f"Skipping {year} (already exists)")
        continue

    with rasterio.open(src_dir / f"probability_SSP2_{year}.tif") as src:
        out = np.zeros((full_window.height, full_window.width), dtype="uint8")

        for window in Bar(f"Processing {year}", max=len(windows)).iter(windows):
            out_offset = window.row_off - full_window.row_off
            data = src.read(1, window=window)
            # nan is areas not projected to urbanize and actual NODATA
            data[np.isnan(data)] = np.float32(0.0)

            # probability values are number of runs out of 50 that predicted
            # urbanization; convert back to the number of runs
            binned = (data * np.float32(50.0)).astype("uint8")

            out[out_offset : out_offset + window.height, :] = binned

        print("Writing temporary raster")
        tmp_filename = tmp_dir / f"urban_{year}_binned.tif"
        write_raster(tmp_filename, out, transform, crs=src.crs, nodata=NODATA)

    ### Warp and extract to SE Blueprint extent
    print("Warping to align with SE Blueprint")
    with rasterio.open(tmp_filename) as src:
        vrt = WarpedVRT(
            src,
            width=bnd_raster.width,
            height=bnd_raster.height,
            nodata=NODATA,
            transform=bnd_raster.transform,
            crs=DATA_CRS,
            resampling=Resampling.nearest,
        )

        data = vrt.read()[0]

    print("Setting already urban")
    # set a value of 51 where already urban
    data = np.where(already_urban, np.uint8(51), data)

    ### Set areas outside the SE Blueprint to NODATA
    print("Masking to inland areas in the SE")
    outside = bnd_raster.read(1) == 0
    data[outside] = NODATA

    print("Writing final dataset")
    write_raster(outfilename, data, bnd_raster.transform, bnd_raster.crs, nodata=NODATA)

    with rasterio.open(outfilename, "r+") as out:
        out.write_colormap(1, colormap)

    print("Adding overviews")
    add_overviews(outfilename)

    print(f"Done with {year} in {time()-year_start:.2f}s")

bnd_raster.close()

del already_urban


### Create mask of where urban pixels (including 0) are present through 2100
print("Creating urban mask")
outfilename = out_dir / "urban_mask.tif"
if not outfilename.exists():
    create_lowres_mask(
        out_dir / f"urban_2100.tif",
        outfilename,
        resolution=MASK_RESOLUTION,
        ignore_zero=False,
    )


### Reclassify 2060 into bins for report and tiles
print("Reclassifying 2060 for mapping")

colormap = {k: hex_to_uint8(color) + (255,) for k, color in URBAN_COLORS.items()}
colormap[0] = (255, 255, 255, 0)

with rasterio.open(out_dir / "urban_2060.tif") as src:
    data = src.read(1)

    binned = np.digitize(data, BINS, right=True).astype("uint8") - np.uint8(1)
    binned[data == 51] = len(BINS)
    binned[data == NODATA] = NODATA

    outfilename = out_dir / "urban_2060_binned.tif"
    write_raster(
        outfilename,
        binned,
        transform=src.transform,
        crs=src.crs,
        nodata=NODATA,
    )

    with rasterio.open(outfilename, "r+") as out:
        out.write_colormap(1, colormap)

    add_overviews(outfilename)


print(f"All done in {time()-start:.2f}s")
