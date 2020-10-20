from pathlib import Path
import os
import math

import numpy as np
import geopandas as gp
import pygeos as pg
from pyogrio import read_dataframe, write_dataframe
import rasterio
from rasterio.enums import Resampling
from rasterio.features import rasterize
from rasterio.vrt import WarpedVRT


from analysis.constants import DATA_CRS, DEBUG, INPUT_AREA_VALUES, MASK_FACTOR
from analysis.lib.io import write_raster
from analysis.lib.input_areas import get_input_area_mask
from analysis.lib.pygeos_util import to_dict_all
from analysis.lib.raster import add_overviews, create_lowres_mask


src_dir = Path("source_data/naturescape")
bnd_dir = Path("data/boundaries")
data_dir = Path("data/inputs")
out_dir = data_dir / "indicators/naturescape"
cores_outfilename = out_dir / "ns_cores.tif"
connectors_outfilename = out_dir / "ns_connectors.tif"
tnc_outfilename = out_dir / "tnc_resilient_connected.tif"
ns_outfilename = out_dir / "ns_priority.tif"


if not out_dir.exists():
    os.makedirs(out_dir)

### Get input area mask
print("Extracting NatureScape input area mask...")
mask, transform, window = get_input_area_mask("app")

inputs_df = gp.read_feather(bnd_dir / "input_areas.feather")
values = [e["value"] for e in INPUT_AREA_VALUES if "app" in set(e["id"].split(","))]
bnd = pg.union_all(inputs_df.loc[inputs_df.value.isin(values)].geometry.values.data)


### Warp TNC resilient and connected landscapes to match Blueprint input area
print("Reading and warping TNC resilient and connected landscapes...")
with rasterio.open(src_dir / "Resilient_and_Connected20180308.tif") as rc:
    vrt = WarpedVRT(
        rc,
        width=window.width,
        height=window.height,
        nodata=int(rc.nodata),
        transform=transform,
        crs=DATA_CRS,
        resampling=Resampling.nearest,
    )

    data = vrt.read()[0]

# convert to uint8
data = np.where(data == int(rc.nodata), 255, data)

# clip to mask
data = np.where(mask == 1, data, 255).astype("uint8")

tnc_data = data.copy()

# Reclassify to incremental values based on lookup table
print("Reclassifying TNC data...")
table = read_dataframe(
    src_dir / "Resilient_and_Connected20180308.tif.vat.dbf",
    read_geometry=False,
    columns=["Value"],
)

for i, row in table.iterrows():
    if i == row.Value:
        continue

    data[data == row.Value] = i

write_raster(tnc_outfilename, data, transform=transform, crs=DATA_CRS, nodata=255)


# Reclassify to merge with below
print("Reclassifying TNC data for merge...")
# map TNC values to merged NatureScape / TNC values
tnc_values = {
    # 0:0, # noop
    2: 4,
    3: 0,
    # 4: 4, # noop
    11: 4,
    12: 2,
    13: 4,
    14: 4,
    33: 2,
    112: 4,
}

for value, out_value in tnc_values.items():
    tnc_data[tnc_data == value] = out_value


### AppLCC NatureScape

local_cores_df = read_dataframe(src_dir / "LocalCores.shp", columns=[]).to_crs(DATA_CRS)
regional_cores_df = read_dataframe(src_dir / "RegionalCores.shp", columns=[]).to_crs(
    DATA_CRS
)
important_areas_df = read_dataframe(
    src_dir / "OtherImportantAreas.shp", columns=[]
).to_crs(DATA_CRS)

local_connectors_df = read_dataframe(src_dir / "LocalConnector.shp", columns=[]).to_crs(
    DATA_CRS
)
regional_connectors_df = read_dataframe(
    src_dir / "RegionalConnector.shp", columns=[]
).to_crs(DATA_CRS)

### Select intersecting features and merge
# NOTE: due to input areas coming from 30m raster, they take FOREVER to run
# an interesection analysis.  We sidestep that by rasterizing then masking these.
#
# Classify with the following values
# 1. local cores, 2. regional cores, 3. important areas, 4. local connectors, 5. regional connectors
merged = None
for i, df in enumerate(
    [
        local_cores_df,
        regional_cores_df,
        important_areas_df,
        local_connectors_df,
        regional_connectors_df,
    ]
):
    tree = pg.STRtree(df.geometry.values.data)
    ix = tree.query(bnd, predicate="intersects")
    df = df.iloc[ix].copy()
    df["value"] = i + 1

    if i == 0:
        merged = df
    else:
        merged = merged.append(df, ignore_index=True, sort=False)

df = merged

if DEBUG:
    write_dataframe(df, "/tmp/naturescape.gpkg", driver="GPKG")


### Create cores raster
# cores and important areas don't overlap; just rasterize them

print("Rasterizing cores and other important areas...")
cores = np.ones(shape=data.shape, dtype="uint8") * 255
# set all areas inside the mask as 0
cores = np.where(mask == 1, 0, 255)

for value in [1, 2, 3]:
    print(f"Processing value {value}...")
    shapes = to_dict_all(df.loc[df.value == value].geometry.values.data)
    data = rasterize(
        shapes, data.shape, transform=transform, dtype="uint8", default_value=1, fill=0
    )
    cores = np.where(data == 1, value, cores)

# Apply the mask
cores = np.where(mask == 1, cores, 255).astype("uint8")

write_raster(cores_outfilename, cores, transform, DATA_CRS, nodata=255)

### Create connectors raster
# connectors overlap each other and areas above, code these as
# 1. local connectors, 2. regional connectors, 3. both

print("Rasterizing connectors...")

connectors = np.zeros(shape=data.shape, dtype="uint8")

for i, value in enumerate([4, 5]):
    print(f"Processing value {value}...")
    shapes = to_dict_all(df.loc[df.value == value].geometry.values.data)
    data = rasterize(
        shapes,
        data.shape,
        transform=transform,
        dtype="uint8",
        default_value=i + 1,
        fill=0,
    )
    connectors += data

# Apply the mask
connectors = np.where(mask == 1, connectors, 255).astype("uint8")

write_raster(connectors_outfilename, connectors, transform, DATA_CRS, nodata=255)


### reclassify to create final values per final value list in inputs.json
out = np.ones(shape=data.shape, dtype="uint8") * 255
# set all areas inside the mask as 0
out = np.where(mask == 1, 0, 255)

out = np.where(tnc_data == 4, 4, out)
out = np.where((connectors > 0) & (connectors < 255), 3, out)

# cores + TNC overwrite connectors where they overlap
out = np.where(tnc_data == 2, 2, out)
out = np.where((cores > 0) & (cores < 255), 1, out)

out = out.astype("uint8")
# Note: values 4 and 5 overlap with other values and each other,
# merge them so lower values are on top

write_raster(ns_outfilename, out, transform, DATA_CRS, nodata=255)


for outfilename in [
    cores_outfilename,
    connectors_outfilename,
    tnc_outfilename,
    ns_outfilename,
]:
    add_overviews(outfilename)

    create_lowres_mask(
        outfilename,
        str(outfilename).replace(".tif", "_mask.tif"),
        factor=MASK_FACTOR,
        ignore_zero=False,
    )
