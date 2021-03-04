from pathlib import Path
import os

import numpy as np
from pyogrio import read_dataframe
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from analysis.constants import DATA_CRS, MASK_FACTOR
from analysis.lib.io import write_raster
from analysis.lib.input_areas import get_input_area_mask
from analysis.lib.raster import add_overviews, create_lowres_mask
from analysis.lib.speedups import remap


src_dir = Path("source_data/midse")
bnd_dir = Path("data/boundaries")
data_dir = Path("data/inputs")
out_dir = data_dir / "indicators/midse"
outfilename = out_dir / "midse_blueprint.tif"

if not out_dir.exists():
    os.makedirs(out_dir)


### Get input area mask
print("Extracting MidSE input area mask...")
mask, transform, window = get_input_area_mask("ms")

print("Reading and warping MidSE Blueprint...")
nodata = 65535  # force new nodata value outside known input range of values
with rasterio.open(src_dir / "MS_SEB2020_Submit.img") as src:
    vrt = WarpedVRT(
        src,
        width=window.width,
        height=window.height,
        nodata=nodata,
        transform=transform,
        crs=DATA_CRS,
        resampling=Resampling.nearest,
    )

    raw_data = vrt.read()[0]

raw_data = raw_data.astype("uint16")

write_raster(
    src_dir / "midse_raw.tif",
    raw_data,
    transform=transform,
    crs=DATA_CRS,
    nodata=nodata,
)


print("Reclassifying data...")
table = read_dataframe(src_dir / "MS_SEB2020_Submit.img.vat.dbf")
table["priority"] = table.M_SEBcode.astype("uint8")
remap_table = table[["Value", "priority"]].values.astype("uint16")

data = remap(raw_data, remap_table, nodata=nodata)

print("Done reclassifying values")

# coerce down to uint8, set nodata to smaller value
data[data == nodata] = 255
nodata = 255

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
