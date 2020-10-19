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
from rasterio.windows import Window, get_data_window

from analysis.constants import DATA_CRS, INPUT_AREA_VALUES, DEBUG
from analysis.lib.io import write_raster
from analysis.lib.pygeos_util import to_dict_all

values = [e["value"] for e in INPUT_AREA_VALUES if "app" in e["id"]]

ns_src_dir = Path("source_data/naturescape")
bnd_dir = Path("data/boundaries")
data_dir = Path("data/inputs")
out_dir = data_dir / "indicators/naturescape"


if not out_dir.exists():
    os.makedirs(out_dir)

inputs_df = gp.read_feather(bnd_dir / "input_areas.feather")

bnd = pg.union_all(inputs_df.loc[inputs_df.value.isin(values)].geometry.values.data)
bnd_df = gp.GeoDataFrame(geometry=[bnd], crs=inputs_df.crs)

local_cores_df = read_dataframe(ns_src_dir / "LocalCores.shp", columns=[]).to_crs(
    DATA_CRS
)
regional_cores_df = read_dataframe(ns_src_dir / "RegionalCores.shp", columns=[]).to_crs(
    DATA_CRS
)
important_areas_df = read_dataframe(
    ns_src_dir / "OtherImportantAreas.shp", columns=[]
).to_crs(DATA_CRS)

local_connectors_df = read_dataframe(
    ns_src_dir / "LocalConnector.shp", columns=[]
).to_crs(DATA_CRS)
regional_connectors_df = read_dataframe(
    ns_src_dir / "RegionalConnector.shp", columns=[]
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


### Get window into raster for bounds of input area
# NOTE: not using bounds of df above since it extends beyond input area
with rasterio.open(data_dir / "input_areas.tif") as src:
    nodata = int(src.nodata)
    window = src.window(*pg.total_bounds(bnd))
    window_floored = window.round_offsets(op="floor", pixel_precision=3)
    w = math.ceil(window.width + window.col_off - window_floored.col_off)
    h = math.ceil(window.height + window.row_off - window_floored.row_off)
    window = Window(window_floored.col_off, window_floored.row_off, w, h)
    window = window.intersection(Window(0, 0, src.width, src.height))
    transform = src.window_transform(window)

    data = src.read(1, window=window)

mask = np.zeros(shape=data.shape, dtype="uint8")
for value in values:
    mask[data == value] = 1


### Create cores raster
# cores and important areas don't overlap; just rasterize them
cores = np.ones(shape=data.shape, dtype="uint8") * nodata
# set all areas inside the mask as 0
cores = np.where(mask == 1, 0, nodata)

for value in [1, 2, 3]:
    print(f"Processing value {value}...")
    shapes = to_dict_all(df.loc[df.value == value].geometry.values.data)
    data = rasterize(
        shapes, data.shape, transform=transform, dtype="uint8", default_value=1, fill=0
    )
    cores = np.where(data == 1, value, cores)

# Apply the mask
cores = np.where(mask == 1, cores, nodata).astype("uint8")

write_raster(
    out_dir / "naturescape_cores.tif", cores, transform, DATA_CRS, nodata=nodata
)

### Create connectors raster
# connectors overlap each other and areas above, code these as
# 1. local connectors, 2. regional connectors, 3. both

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
connectors = np.where(mask == 1, connectors, nodata).astype("uint8")

write_raster(
    out_dir / "naturescape_connectors.tif",
    connectors,
    transform,
    DATA_CRS,
    nodata=nodata,
)


### reclassify to create final values per final value list in inputs.json
out = np.ones(shape=data.shape, dtype="uint8") * nodata
# set all areas inside the mask as 0
out = np.where(mask == 1, 0, nodata)

out = np.where((connectors > 0) & (connectors < nodata), 3, out)
# cores overwrite connectors where they overlap
out = np.where((cores > 0) & (cores < nodata), 1, out)

out = out.astype("uint8")
# Note: values 4 and 5 overlap with other values and each other,
# merge them so lower values are on top

write_raster(out_dir / "naturescape.tif", out, transform, DATA_CRS, nodata=nodata)

