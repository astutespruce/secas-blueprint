from pathlib import Path
import os

import numpy as np
import rasterio
from rasterio.windows import get_data_window
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from analysis.constants import INPUT_AREA_VALUES, DEBUG
from analysis.lib.io import write_raster

# Steps
# extract input area data area
# reproject / align to blueprint / inputs grid
# clip to input area


values = [e["value"] for e in INPUT_AREA_VALUES if "gh" in e["id"]]


data_dir = Path("data/inputs")
src_dir = Path("source_data/gulf_hypoxia")
out_dir = data_dir / "indicators/gulf_hypoxia"

if not out_dir.exists():
    os.makedirs(out_dir)


with rasterio.open(data_dir / "input_areas.tif") as src:
    data = src.read(1)

    out = np.zeros(shape=data.shape, dtype="uint8")
    for value in values:
        out[data == value] = 1

    window = get_data_window(out, nodata=0)

    transform = src.window_transform(window)

    mask = out[window.toslices()] == 1

    if DEBUG:
        write_raster(
            "/tmp/gh_mask.tif", mask.astype("uint8"), transform, crs=src.crs, nodata=0
        )

# NOTE: data cover all of MS, can just use extent of data; mask above is ignored

with rasterio.open(src_dir / "Missouri_cfa_huc_sum2.tif") as gh:
    # data must be warped to align with input grid
    vrt = WarpedVRT(
        gh,
        width=window.width,
        height=window.height,
        nodata=gh.nodata,
        transform=transform,
        resampling=Resampling.nearest,
    )
    print("Reading and warping gulf hypoxia...")

    gh_data = vrt.read()[0]

    write_raster(
        out_dir / "gulf_hypoxia.tif",
        gh_data,
        transform,
        crs=src.crs,
        nodata=int(gh.nodata),
    )
