from pathlib import Path
import os
import math

import numpy as np
import rasterio
from rasterio.windows import Window, get_data_window
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
from pyogrio import read_dataframe

from analysis.constants import DATA_CRS, MASK_FACTOR
from analysis.lib.io import write_raster
from analysis.lib.input_areas import get_input_area_mask
from analysis.lib.raster import add_overviews, create_lowres_mask


src_dir = Path("source_data/natures_network")
data_dir = Path("data/inputs")
out_dir = data_dir / "indicators/natures_network"
priority_outfilename = out_dir / "nn_priority.tif"
category_outfilename = out_dir / "nn_category.tif"

if not out_dir.exists():
    os.makedirs(out_dir)

# Remap the raw values to priorities and categories
table = read_dataframe(
    src_dir / "NaturesNetwork_conservdesign_180625.tif.vat.dbf",
    columns=["Value", "Priority", "Descrpt"],
    read_geometry=False,
)
table = table.loc[table.Value > 0].copy()
table.Priority = table.Priority.astype("uint8")
table["category"] = table.Descrpt.str[0].astype("uint8")


### Get input area mask
print("Extracting Nature's Network input area mask...")
mask, transform, window = get_input_area_mask("nn")

nodata = 255


with rasterio.open(src_dir / "NaturesNetwork_conservdesign_180625.tif") as src:
    # note: raster does not have nodata set; 0 indicates NODATA (outside extent)
    # and 0 values

    # data must be warped to align with input grid
    vrt = WarpedVRT(
        src,
        width=window.width,
        height=window.height,
        nodata=nodata,
        transform=transform,
        crs=DATA_CRS,
        resampling=Resampling.nearest,
    )
    print("Reading and warping Nature's Network...")

    data = vrt.read()[0]

# apply mask
data = np.where(mask == 1, data, nodata).astype("uint8")

priority_data = data.copy()
category_data = data.copy()

print("Reclassifying data...")
for i, row in table.iterrows():
    priority_data[priority_data == row.Value] = row.Priority
    category_data[category_data == row.Value] = row.category

write_raster(priority_outfilename, priority_data, transform, DATA_CRS, nodata=nodata)
write_raster(category_outfilename, category_data, transform, DATA_CRS, nodata=nodata)

print("Adding overviews and masks...")
for outfilename in [priority_outfilename, category_outfilename]:
    add_overviews(outfilename)

    create_lowres_mask(
        outfilename,
        str(outfilename).replace(".tif", "_mask.tif"),
        factor=MASK_FACTOR,
        ignore_zero=False,
    )
