from pathlib import Path
import os

import numpy as np
import pygeos as pg
import rasterio
from rasterio.features import rasterize
from pyogrio import read_dataframe

from analysis.constants import DATA_CRS, MASK_FACTOR
from analysis.lib.io import write_raster
from analysis.lib.input_areas import get_input_area_mask, get_input_area_boundary
from analysis.lib.raster import add_overviews, create_lowres_mask, extract_window
from analysis.lib.speedups import remap
from analysis.lib.pygeos_util import to_dict_all, dissolve, explode


src_dir = Path("source_data/natures_network")
data_dir = Path("data/inputs")
out_dir = data_dir / "indicators/natures_network"
outfilename = out_dir / "nn_priority.tif"

if not out_dir.exists():
    os.makedirs(out_dir)

### Get input area mask
print("Extracting Nature's Network input area mask...")
mask, transform, window = get_input_area_mask("nn")
nodata = 255

print("Reading and warping Nature's Network...")
with rasterio.open(src_dir / "NaturesNetwork_conservdesign_180625.tif") as src:
    # note: raster does not have nodata set; 0 indicates NODATA (outside extent)
    # and 0 values
    data = extract_window(src, window, transform, nodata=nodata)

# apply input area mask
data = np.where(mask == 1, data, nodata).astype("uint8")

print("Reclassifying data...")
# Remap the raw values to priorities and categories
table = read_dataframe(
    src_dir / "NaturesNetwork_conservdesign_180625.tif.vat.dbf",
    columns=["Value", "Priority", "Descrpt"],
    read_geometry=False,
)
table = table.loc[table.Value > 0].copy()
table.Priority = table.Priority.astype("uint8")
table["category"] = table.Descrpt.str[0].astype("uint8")

remap_table = table[["Value", "Priority"]].values.astype("uint8")
priority_data = remap(data, remap_table, nodata=nodata)

write_raster(outfilename, priority_data, transform, DATA_CRS, nodata=nodata)

print("Adding overviews and masks...")
add_overviews(outfilename)

create_lowres_mask(
    outfilename,
    str(outfilename).replace(".tif", "_mask.tif"),
    factor=MASK_FACTOR,
    ignore_zero=False,
)


### Process indicators

# Extract cores from the categories
table["aquatic_cores"] = table.Descrpt.str.contains("Aquatic")
table["terrestrial_cores"] = table.Descrpt.str.contains("Terrestrial")
table["imperiled_cores"] = table.Descrpt.str.contains("Imperiled")

for core_type in ["aquatic_cores", "terrestrial_cores", "imperiled_cores"]:
    print(f"Processing {core_type}")
    cores_data = remap(
        data, table[["Value", core_type]].values.astype("uint8"), nodata=nodata
    )

    outfilename = out_dir / f"{core_type}.tif"
    write_raster(outfilename, cores_data, transform, DATA_CRS, nodata=nodata)
    add_overviews(outfilename)
    create_lowres_mask(
        outfilename,
        str(outfilename).replace(".tif", "_mask.tif"),
        factor=MASK_FACTOR,
        ignore_zero=True,
    )

### Process habitat condition
print("Extracting habitat condition...")
with rasterio.open(src_dir / "indicators/HABITAT_CONDITION_web.tif") as src:
    data = extract_window(src, window, transform, nodata=nodata)

# apply input area mask
data = np.where(mask == 1, data, nodata).astype("uint8")

# Classes used for symbology are 0-47 (lowest), 48-88, 89-200 (highest)
# see the *.sd file for this dataset
data[data <= 47] = 0
data[(data > 47) & (data <= 88)] = 1
data[(data > 88) & (data <= 200)] = 2

outfilename = out_dir / "habitat_condition.tif"
write_raster(outfilename, data, transform, DATA_CRS, nodata=nodata)
add_overviews(outfilename)
create_lowres_mask(
    outfilename,
    str(outfilename).replace(".tif", "_mask.tif"),
    factor=MASK_FACTOR,
    ignore_zero=False,
)

### Process Habitat Importance
print("Extracting habitat condition...")
with rasterio.open(src_dir / "indicators/habitat_importance.tif") as src:
    dtype = src.dtypes[0]
    data = extract_window(src, window, transform, nodata=src.nodata)

    # apply input area mask
    data = np.where(mask == 1, data, src.nodata).astype(dtype)


table = read_dataframe(
    src_dir / "indicators/habitat_importance.tif.vat.dbf", read_geometry=False
)

# Classes on Impt_sum used for symbology are 0-22 (highest), 23-77, 78-200 (lowest)
# see the *.sd file for this dataset

table["new_value"] = 0
table.loc[table.Impt_sum <= 77, "new_value"] = 1
table.loc[table.Impt_sum <= 22, "new_value"] = 2

data = remap(
    data, table[["Value", "new_value"]].values.astype(dtype), nodata=nodata
).astype("uint8")

outfilename = out_dir / "habitat_importance.tif"
write_raster(outfilename, data, transform, DATA_CRS, nodata=nodata)
add_overviews(outfilename)
create_lowres_mask(
    outfilename,
    str(outfilename).replace(".tif", "_mask.tif"),
    factor=MASK_FACTOR,
    ignore_zero=False,
)


### Process Aquatic Ecological Integrity
print("Processing aquatic integrity")
with rasterio.open(
    src_dir / "indicators/AquaticIEI_v3_2/DSL_aquaiei-r_2010_v3.2.tif"
) as src:
    dtype = src.dtypes[0]
    data = extract_window(src, window, transform, nodata=src.nodata)

    # apply input area mask
    data = np.where(mask == 1, data, src.nodata).astype(dtype)

# this is on a continuous scale from 0 to 1; bin into 10 classes
data[data == src.nodata] = 255
data[(data >= 0) & (data <= 0.1)] = 0
data[(data > 0.1) & (data <= 0.2)] = 1
data[(data > 0.2) & (data <= 0.3)] = 2
data[(data > 0.3) & (data <= 0.4)] = 3
data[(data > 0.4) & (data <= 0.5)] = 4
data[(data > 0.5) & (data <= 0.6)] = 5
data[(data > 0.6) & (data <= 0.7)] = 6
data[(data > 0.7) & (data <= 0.8)] = 6
data[(data > 0.8) & (data <= 0.9)] = 8
data[(data > 0.9) & (data <= 1)] = 9

data = data.astype("uint8")

outfilename = out_dir / "aquatic_integrity.tif"
write_raster(outfilename, data, transform, DATA_CRS, nodata=nodata)
add_overviews(outfilename)
create_lowres_mask(
    outfilename,
    str(outfilename).replace(".tif", "_mask.tif"),
    factor=MASK_FACTOR,
    ignore_zero=True,
)

### Process terrestrial integrity
print("Processing terrestrial integrity")
with rasterio.open(src_dir / "indicators/IEI_2010_r_v3_2/iei-r_2010_v3.2.tif") as src:
    dtype = src.dtypes[0]
    data = extract_window(src, window, transform, nodata=src.nodata)

    # apply input area mask
    data = np.where(mask == 1, data, src.nodata).astype(dtype)

# this is on a continuous scale from 0 to 1; bin into 10 classes
data[data == src.nodata] = 255
data[(data >= 0) & (data <= 0.1)] = 0
data[(data > 0.1) & (data <= 0.2)] = 1
data[(data > 0.2) & (data <= 0.3)] = 2
data[(data > 0.3) & (data <= 0.4)] = 3
data[(data > 0.4) & (data <= 0.5)] = 4
data[(data > 0.5) & (data <= 0.6)] = 5
data[(data > 0.6) & (data <= 0.7)] = 6
data[(data > 0.7) & (data <= 0.8)] = 6
data[(data > 0.8) & (data <= 0.9)] = 8
data[(data > 0.9) & (data <= 1)] = 9

data = data.astype("uint8")

outfilename = out_dir / "integrity.tif"
write_raster(outfilename, data, transform, DATA_CRS, nodata=nodata)
add_overviews(outfilename)
create_lowres_mask(
    outfilename,
    str(outfilename).replace(".tif", "_mask.tif"),
    factor=MASK_FACTOR,
    ignore_zero=False,
)

### Process freshwater resilience by watershed

print("Processing freshwater resilience")

bnd = get_input_area_boundary("nn")
df = read_dataframe(
    src_dir
    / "indicators/Freshwater_Resilience/FW_resilience_highesthigh_watersheds.shp",
    columns=["RES_CLASS"],
).to_crs(DATA_CRS)

tree = pg.STRtree(df.geometry.values.data)
ix = tree.query(bnd, predicate="intersects")
df = df.iloc[ix].copy()

# remap values so that they are 1-4; 0 is fill value, 255 nodata
df["value"] = df.RES_CLASS.map(
    {
        "Complex: Highest Relative Resilience": 4,
        "Complex: High Relative Resilience": 3,
        "Non-Complex: Highest Relative Score": 2,
        "Non-Complex: High Relative Score": 2,
    }
)

# dissolve by value
df = dissolve(explode(df), by=["value"])

# rasterize
df["g"] = to_dict_all(df.geometry.values.data)
shapes = df[["g", "value"]].values.tolist()

data = rasterize(shapes, mask.shape, transform=transform, dtype="uint8", fill=0)

# apply input area mask
nodata = 255
data = np.where(mask == 1, data, nodata).astype("uint8")


outfilename = out_dir / "freshwater_resilience.tif"
write_raster(outfilename, data, transform, DATA_CRS, nodata=nodata)
add_overviews(outfilename)
create_lowres_mask(
    outfilename,
    str(outfilename).replace(".tif", "_mask.tif"),
    factor=MASK_FACTOR,
    ignore_zero=False,
)
