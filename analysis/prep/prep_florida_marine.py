from pathlib import Path
import os
import math

import numpy as np
import geopandas as gp
import pygeos as pg
from pyogrio import read_dataframe, write_dataframe
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT


from analysis.constants import DATA_CRS, MASK_FACTOR
from analysis.lib.io import write_raster
from analysis.lib.input_areas import get_input_area_mask
from analysis.lib.pygeos_util import to_dict_all
from analysis.lib.raster import add_overviews, create_lowres_mask
from analysis.lib.speedups import remap

src_dir = Path("source_data/florida")
marine_dir = src_dir / "Marine"
bnd_dir = Path("data/boundaries")
data_dir = Path("data/inputs")
out_dir = data_dir / "indicators/florida_marine"
outfilename = out_dir / "flm_blueprint.tif"

if not out_dir.exists():
    os.makedirs(out_dir)


### Marine
print("Extracting Florida marine input area mask...")
mask, transform, window = get_input_area_mask("flm")

print("Reading and warping Florida Blueprint...")
with rasterio.open(marine_dir / "FLBlueprintVer1.tif") as src:
    nodata = 255
    vrt = WarpedVRT(
        src,
        width=window.width,
        height=window.height,
        nodata=nodata,
        crs=DATA_CRS,
        transform=transform,
        resampling=Resampling.nearest,
    )

    data = vrt.read()[0].astype("uint8")


# remap data
remap_table = np.array([[1, 1], [2, 2], [3, 3]], dtype="uint8")
data = remap(data, remap_table, nodata=255)


# apply mask
data = np.where(mask == 1, data, nodata).astype("uint8")

write_raster(outfilename, data, transform=transform, crs=DATA_CRS, nodata=nodata)


add_overviews(outfilename)

create_lowres_mask(
    outfilename,
    str(outfilename).replace(".tif", "_mask.tif"),
    factor=MASK_FACTOR,
    ignore_zero=False,
)

