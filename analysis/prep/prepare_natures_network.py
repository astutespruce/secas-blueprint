from pathlib import Path
import os
import math

import numpy as np
import rasterio
from rasterio.windows import Window, get_data_window
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
from pyogrio import read_dataframe

from analysis.constants import DATA_CRS, INPUT_AREA_VALUES, DEBUG
from analysis.lib.io import write_raster

values = [e["value"] for e in INPUT_AREA_VALUES if "nn" in e["id"]]


src_dir = Path("source_data/natures_network")
data_dir = Path("data/inputs")
out_dir = data_dir / "indicators/natures_network"


if not out_dir.exists():
    os.makedirs(out_dir)


# note: already in correct projection but assign to DATA_CRS as standard
src = rasterio.open(src_dir / "NaturesNetwork_conservdesign_180625.tif")
inputs = rasterio.open(data_dir / "input_areas.tif")

# extract overlapping window
window = inputs.window(*src.bounds)
window_floored = window.round_offsets(op="floor", pixel_precision=3)
w = math.ceil(window.width + window.col_off - window_floored.col_off)
h = math.ceil(window.height + window.row_off - window_floored.row_off)
window = Window(window_floored.col_off, window_floored.row_off, w, h)
window = window.intersection(Window(0, 0, inputs.width, inputs.height))

data = inputs.read(1, window=window)
mask = np.zeros(shape=data.shape, dtype="uint8")
for value in values:
    mask[data == value] = 1

data_window = get_data_window(mask, nodata=0)
mask = mask[data_window.toslices()]

# update window to account for data_window
window = Window(
    window.col_off + data_window.col_off,
    window.row_off + data_window.row_off,
    data_window.width,
    data_window.height,
)
transform = inputs.window_transform(window)

if DEBUG:
    write_raster("/tmp/nn_mask.tif", mask, transform, DATA_CRS, nodata=0)


# data must be warped to align with input grid
vrt = WarpedVRT(
    src,
    width=window.width,
    height=window.height,
    nodata=src.nodata,
    transform=transform,
    resampling=Resampling.nearest,
)
print("Reading and warping Nature's Network...")

data = vrt.read()[0]
nodata = 255

# clip by input area (treat 0 as nodata)
data[mask == 0] = nodata

# Remap the raw values to priorities
table = read_dataframe(
    src_dir / "NaturesNetwork_conservdesign_180625.tif.vat.dbf",
    columns=["Value", "Priority"],
)
table = table.loc[table.Value > 0].copy()
table["NewValue"] = table.Priority.astype("uint8")

for row in table.itertuples():
    data[data == row.Value] = row.NewValue


write_raster(out_dir / "natures_network.tif", data, transform, DATA_CRS, nodata=nodata)


src.close()
inputs.close()
