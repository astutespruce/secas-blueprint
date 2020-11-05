"""
Note: rasters are effectively in the same projection as EPSG:5070, but have slightly
different WKT.  These are set to match other rasters.

Note: rasters are pixel-aligned, no need to resample to match.
"""

import os
from pathlib import Path
import math

import numpy as np
import rasterio
from affine import Affine
from rasterio.enums import Resampling

from analysis.constants import URBAN_YEARS, DATA_CRS, OVERVIEW_FACTORS
from analysis.lib.speedups import remap
from analysis.lib.raster import create_lowres_mask


groups = ["app", "gcp", "gcpo", "serap"]
values = np.array(
    [0, 1, 25, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950, 975, 1000]
)

src_dir = Path("source_data/urban")
out_dir = Path("data/inputs/threats/urban")

if not out_dir.exists():
    os.makedirs(out_dir)


# Calculate outer bounds
rasters = [
    rasterio.open(str(src_dir / f"{group}_sleuth" / f"{group}_urb2020"))
    for group in groups
]
tmp = np.array([src.bounds for src in rasters]).T
xmin, ymin = tmp[:2].min(axis=1)
xmax, ymax = tmp[2:].max(axis=1)
bounds = [xmin, ymin, xmax, ymax]

cellsize = int(rasters[0].res[0])

width = int((xmax - xmin) / cellsize)
height = int((ymax - ymin) / cellsize)
transform = Affine(a=cellsize, b=0, c=xmin, d=0, e=-cellsize, f=ymax)

nodata = int(rasters[0].nodata)


for year in URBAN_YEARS:
    print(f"Processing {year}...")
    rasters = [
        rasterio.open(str(src_dir / f"{group}_sleuth" / f"{group}_urb{year}"))
        for group in groups
    ]

    # initialize to output nodata value
    out = np.ones(shape=(height, width), dtype="uint8") * 255

    for src in rasters:
        data = src.read(1)

        # fill nodata value and convert to uint16
        data[data == nodata] = 65535
        data = data.astype("uint16")

        # convert to indexed
        remap_table = np.array(
            [[value, index] for index, value in enumerate(values)] + [[65535, 255]],
            dtype="uint16",
        )
        data = remap(data, remap_table, nodata=255, fill=0)

        # figure out position in out
        # rows start at max y, offset is from top bound
        row_off = math.ceil((bounds[3] - src.bounds[3]) / cellsize)
        col_off = math.ceil((src.bounds[0] - bounds[0]) / cellsize)

        data_height, data_width = data.shape

        ix = (
            slice(row_off, row_off + data_height, None),
            slice(col_off, col_off + data_width, None),
        )

        out[ix] = np.where((data >= 0) & (data < 255), data.astype("uint8"), out[ix])

    meta = {
        "driver": "GTiff",
        "crs": DATA_CRS,
        "transform": transform,
        "width": width,
        "height": height,
        "count": 1,
        "nodata": 255,
        "dtype": "uint8",
        "compress": "lzw",
    }

    with rasterio.open(out_dir / f"urban_{year}.tif", "w", **meta) as outfile:
        outfile.write(out, 1)

        outfile.build_overviews(OVERVIEW_FACTORS, Resampling.nearest)

create_lowres_mask(
    out_dir / "urban_2100.tif", out_dir / "urban_mask.tif", factor=8, ignore_zero=True
)
