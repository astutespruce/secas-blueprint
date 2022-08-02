import math
from pathlib import Path
import re
import subprocess
from time import time

import rasterio
from rasterio.features import geometry_mask
import pandas as pd
import numpy as np
import pygeos as pg
import geopandas as gp
from pyogrio import (
    read_dataframe,
    set_gdal_config_options,
    list_layers,
    read_bounds,
    read_info,
)


from analysis.constants import DATA_CRS
from analysis.lib.io import write_raster
from analysis.lib.pygeos_util import (
    to_dict_all,
)
from analysis.lib.raster import add_overviews


set_gdal_config_options({"OGR_ORGANIZE_POLYGONS": "ONLY_CCW"})

BLUEPRINT_RES = 30
SLR_RES = 15
MIN_AREA = SLR_RES * SLR_RES
LEVELS = list(range(0, 11))  # 0-10 feet inundation
NODATA = 255


def drop_all_holes(geometries):
    """Return geometries, dropping any holes.

    Parameters
    ----------
    geometries : ndarray of pygeos geometries

    Returns
    -------
    ndarray of pygeos geometries
    """
    parts, index = pg.get_parts(geometries, return_index=True)
    parts = pg.polygons(pg.get_exterior_ring(parts))

    return (
        pd.DataFrame({"geometry": parts}, index=index)
        .groupby(level=0)
        .geometry.apply(np.array)
        .apply(lambda g: pg.multipolygons(g) if len(g) > 1 else g[0])
        .values
    )


def get_holes(geometries):
    """Extract the holes from geometries and return as new polygons

    Parameters
    ----------
    geometries : ndarray of pygeos geometries

    Returns
    -------
    tuple of ndarray of geomtries, original index
    """
    parts, index = pg.get_parts(geometries, return_index=True)
    num_rings = pg.get_num_interior_rings(parts)

    ix = num_rings > 0
    index = np.arange(len(parts))[ix]
    out_index = np.repeat(index, num_rings[ix])

    holes = []

    for i in index:
        holes.extend(
            pg.get_interior_ring(parts[i], range(pg.get_num_interior_rings(parts[i])))
        )

    return pg.polygons(holes), out_index


def rasterize_depth_polygons(gdb, layer, width, height, transform):
    """Rasterize polygons to pixels according to the dimensions and transform
    provided.

    Parameters
    ----------
    gdb : str or Path
        Geodatabase path
    layer : str
        layer name
    width : int
    height : int
    transform : affine.Affine

    Returns
    -------
    ndarray of shape(height, width) with bool values
        values are True inside polygons
    """

    print(f"Reading and reprojecting {layer}")
    df = (
        read_dataframe(gdb, layer=layer, columns=[], force_2d=True)
        .explode(index_parts=False)
        .to_crs(DATA_CRS)
    )

    area = pg.area(df.geometry.values.data)
    total_area = area.sum()

    # Drop any polygons that are too small
    ix = area >= MIN_AREA
    df = df.loc[ix].copy()
    print(
        f"Dropped {(~ix).sum():,} polygons that are < {MIN_AREA} m2; now have {len(df):,} polygons and {100 * area[ix].sum() / total_area:.2f}% of original area"
    )

    print("Rasterizing.... (this might take a while)")

    # Write outer rings of polygons and then holes separately because this is
    # faster, though less precise (some holes may rasterize over the edge of the
    # original rings, yielding bays)
    polygons = drop_all_holes(df.geometry.values.data)
    fill_mask = geometry_mask(
        to_dict_all(polygons),
        out_shape=(height, width),
        transform=transform,
        invert=True,
    )

    holes = get_holes(df.geometry.values.data)[0]
    ix = pg.area(holes) >= MIN_AREA
    holes_mask = geometry_mask(
        to_dict_all(holes[ix]), out_shape=(height, width), transform=transform
    )

    fill_mask[holes_mask == 0] = 0

    return fill_mask


src_dir = Path("source_data/slr")
out_dir = Path("data/inputs/threats/slr")
out_dir.mkdir(parents=True, exist_ok=True)

# use the Base Blueprint extent grid to derive the master offset coordinates
# so that everything is correctly aligned
with rasterio.open(
    "source_data/blueprint/1_ExtentLayers/BaseBlueprintExtent2022.tif"
) as src:
    align_ul = np.take(src.transform, [2, 5]).tolist()


start = time()

for gdb in sorted(src_dir.glob("*slr_data_dist/*.gdb")):
    chunk_start = time()

    outfilename = (
        out_dir
        / f"{gdb.stem.replace('_slr_final_dist', '')}_{LEVELS[0]}_{LEVELS[-1]}ft.tif"
    )

    if outfilename.exists():
        print(f"Skipping {gdb} (outputs already exist)")
        continue

    print(f"\n\n--------- Processing {gdb} ------------")

    # ignore the low-lying areas, gather the SLR depth layers in order of descending
    # depth so that we stack from highest to lowest
    slr_layers = sorted(
        [l[0] for l in list_layers(gdb) if "_slr_" in l[0]],
        key=lambda l: int(re.findall("\d+(?=ft)", l)[0]),
        reverse=True,
    )

    # calculate the outer bounds and dimensions
    print("Calculating outer bounds")
    xmin = math.inf
    ymin = math.inf
    xmax = -math.inf
    ymax = -math.inf
    for layer in slr_layers:
        # WARNING: CRS is not consistent across the suite
        crs = read_info(gdb, layer)["crs"]
        bounds = (
            gp.GeoDataFrame(geometry=pg.box(*read_bounds(gdb, layer)[1]), crs=crs)
            .to_crs(DATA_CRS)
            .total_bounds
        )
        xmin = min(xmin, bounds[0])
        ymin = min(ymin, bounds[1])
        xmax = max(xmax, bounds[2])
        ymax = max(ymax, bounds[3])

    # snap the origin of this grid to align_ul
    xmin = (math.floor((xmin - align_ul[0]) / SLR_RES) * SLR_RES) + align_ul[0]
    ymax = align_ul[1] - (math.ceil((align_ul[1] - ymax) / SLR_RES) * SLR_RES)
    transform = (SLR_RES, 0, xmin, 0, -SLR_RES, ymax)

    width = math.ceil((xmax - xmin) / SLR_RES)
    height = math.ceil((ymax - ymin) / SLR_RES)

    out = np.ones((height, width), dtype="uint8") * np.uint8(NODATA)

    for layer in slr_layers:
        depth = np.uint8(re.findall("\d+(?=ft)", layer)[0])
        mask = rasterize_depth_polygons(gdb, layer, width, height, transform)
        depth = mask.astype("uint8") * depth

        out = np.where(mask, depth, out)

        # DEBUG:
        # write_raster(
        #     f"/tmp/{layer}.tif",
        #     mask.astype("uint8"),
        #     transform=transform,
        #     crs=DATA_CRS,
        #     nodata=0,
        # )

    print("Writing combined depth raster")
    # Output values are 0 - 10 and NODATA = 255
    write_raster(
        outfilename,
        out,
        transform=transform,
        crs=DATA_CRS,
        nodata=NODATA,
    )

    print("Adding overviews")
    add_overviews(outfilename)

    print(f"Completed in {time() - chunk_start:.2f}s")


files = list(out_dir.glob("*.tif"))

### Build VRT using GDAL CLI
print("Building VRT")
ret = subprocess.run(
    [
        "gdalbuildvrt",
        "-overwrite",
        "-resolution",
        "user",
        "-tr",
        str(SLR_RES),
        str(SLR_RES),
        str(out_dir / "slr.vrt"),
    ]
    + files
)
ret.check_returncode()


### Write a dataset of the bounds of each chunk of raster data
print("Extracting raster bounds to new dataset")
boxes = []
for filename in files:
    with rasterio.open(filename) as src:
        boxes.append(pg.box(*src.bounds))

# union them together into a single polygon
bnd = pg.union_all(boxes)

df = gp.GeoDataFrame({"geometry": [bnd], "index": [0]}, crs=DATA_CRS)
df.to_feather(out_dir / "slr_bounds.feather")

print(f"All done in {time() - start:.2f}s")
