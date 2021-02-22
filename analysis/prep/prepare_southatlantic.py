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


from analysis.constants import DATA_CRS, MASK_FACTOR, INDICATORS as ALL_INDICATORS
from analysis.lib.io import write_raster
from analysis.lib.input_areas import get_input_area_mask
from analysis.lib.pygeos_util import to_dict_all
from analysis.lib.raster import add_overviews, create_lowres_mask


INDICATORS = ALL_INDICATORS["sa"]


src_dir = Path("source_data/southatlantic")
bnd_dir = Path("data/boundaries")
data_dir = Path("data/inputs")
out_dir = data_dir / "indicators/southatlantic"
continuous_indicators_out_dir = Path("data/continuous_indicators/southatlantic")

if not out_dir.exists():
    os.makedirs(out_dir)

### Get input area mask
print("Extracting SA input area mask...")
mask, transform, window = get_input_area_mask("sa")

print("Reading and warping SA Blueprint...")
outfilename = out_dir / "sa_blueprint.tif"
with rasterio.open(src_dir / "Blueprint2020.tif") as src:
    nodata = int(src.nodata)
    vrt = WarpedVRT(
        src,
        width=window.width,
        height=window.height,
        nodata=nodata,
        transform=transform,
        crs=DATA_CRS,
        resampling=Resampling.nearest,
    )

    data = vrt.read()[0]

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


### Process indicators

# because indicators are large, these are extracted directly from sa-blueprint-sv
indicators_src_dir = Path("../sa-blueprint-sv/data/inputs/indicators")
continuous_indicators_src_dir = Path("../sa-blueprint-sv/data/continuous_indicators")

for indicator in INDICATORS:
    id = indicator["id"]
    filename = indicator["filename"]
    outfilename = out_dir / filename

    print(f"Reading and warping {id}...")

    with rasterio.open(indicators_src_dir / filename) as src:
        nodata = int(src.nodata)
        vrt = WarpedVRT(
            src,
            width=window.width,
            height=window.height,
            nodata=nodata,
            transform=transform,
            crs=DATA_CRS,
            resampling=Resampling.nearest,
        )

        data = vrt.read()[0]

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

    if indicator.get("continuous", False):
        print(f"Reading and warping {id} - continuous...")
        filename = filename.replace("_Binned", "")
        outfilename = continuous_indicators_out_dir / filename

        with rasterio.open(continuous_indicators_src_dir / filename) as src:
            dtype = src.dtypes[0]
            nodata = src.nodata
            vrt = WarpedVRT(
                src,
                width=window.width,
                height=window.height,
                nodata=nodata,
                transform=transform,
                crs=DATA_CRS,
                resampling=Resampling.nearest,
            )

            data = vrt.read()[0]

        # apply mask
        data = np.where(mask == 1, data, nodata).astype(dtype)

        write_raster(
            outfilename, data, transform=transform, crs=DATA_CRS, nodata=nodata
        )
