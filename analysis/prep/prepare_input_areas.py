from pathlib import Path

import geopandas as gp
import pandas as pd
import pygeos as pg
import rasterio
from rasterio.features import rasterize
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import MASK_FACTOR
from analysis.lib.pygeos_util import explode, to_dict
from analysis.lib.raster import add_overviews, create_lowres_mask


src_dir = Path("source_data/blueprint")
data_dir = Path("data")
out_dir = data_dir / "inputs"
bnd_dir = data_dir / "boundaries"
json_dir = Path("constants")

blueprint_filename = out_dir / "se_blueprint2020.tif"


df = read_dataframe(
    src_dir / "SE_Blueprint_v2020_Vectors.gdb", layer="InputAreas_SECAS_v2020_20201005"
)

# some areas are null inputs, drop them
df = df.loc[df.InputOverlapAreasSECAS_InputUsedIn2020.notnull()].copy()


# making valid takes a really long time, and probably not necessary
# df["geometry"] = pg.make_valid(df.geometry.values.data)
df["inputs"] = df.InputOverlapAreasSECAS_InputUsedIn2020.str.lower().apply(
    lambda x: x.replace("tx chat", "txchat")
    .replace("ok chat", "okchat")
    .replace(" ", "")
    .replace(";", ",")
)

# split parts for easier indexing
df = explode(df).reset_index()

df = df[["inputs", "geometry"]].copy()

inputs = df.inputs.unique()
inputs.sort()
inputs = pd.DataFrame({"inputs": inputs})

inputs.reset_index().rename(columns={"index": "value", "inputs": "id"}).to_json(
    json_dir / "input_area_values.json", orient="records"
)


df = df.join(
    inputs.reset_index().rename(columns={"index": "value"}).set_index("inputs"),
    on="inputs",
)

write_dataframe(df, bnd_dir / "input_areas.gpkg", driver="GPKG")
df.to_feather(out_dir / "boundaries/input_areas.feather")

# Rasterize to match the blueprint

df = pd.DataFrame(df[["geometry", "value"]].copy())
df.geometry = df.geometry.values.data

# convert to pairs of GeoJSON , value
shapes = df.apply(lambda row: (to_dict(row.geometry), row.value), axis=1)

print("Rasterizing inputs...")
with rasterio.open(blueprint_filename) as src:
    data = rasterize(
        shapes.values, src.shape, transform=src.transform, dtype="uint8", fill=255
    )
    profile = src.profile


outfilename = out_dir / "input_areas.tif"

with rasterio.open(outfilename, "w", **profile) as out:
    out.write(data, 1)

add_overviews(outfilename)

create_lowres_mask(
    outfilename,
    str(outfilename).replace(".tif", "_mask.tif"),
    factor=MASK_FACTOR,
    ignore_zero=False,
)
