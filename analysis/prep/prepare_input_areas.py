from pathlib import Path

import geopandas as gp
import pandas as pd
import pygeos as pg
import rasterio
from rasterio.features import rasterize
from pyogrio import read_dataframe, write_dataframe

from analysis.pygeos_util import explode, to_dict


src_dir = Path("source_data/boundaries")
data_dir = Path("data")
out_dir = data_dir / "inputs"
bnd_dir = data_dir / "boundaries"
json_dir = Path("constants")

blueprint_filename = out_dir / "blueprint_4.tif"


df = read_dataframe(
    src_dir / "SE_Blueprint_v4_0_Vectors.gdb", layer="InputAreas_v4_0_SECAS_20191031"
)

# making valid takes a really long time, and probably not necessary
# df["geometry"] = pg.make_valid(df.geometry.values.data)
df["inputs"] = df.InputOverlapAreasSECAS_InputUsedIn_4_0.str.lower().apply(
    lambda x: x.replace("tx chat", "chat")
    .replace("ok chat", "chat")
    .replace(" ", "")
    .replace(";", ",")
)

# split parts for easier indexing
df = explode(df)

df = df[["inputs", "geometry"]].copy()

inputs = df.inputs.unique()
inputs.sort()
inputs = pd.DataFrame({"inputs": inputs})
inputs.to_feather(out_dir / "input_area_values.feather")

inputs.reset_index().rename(columns={"index": "value", "inputs": "id"}).to_json(
    json_dir / "input_area_values.json", orient="records"
)


df = df.join(
    inputs.reset_index().rename(columns={"index": "value"}).set_index("inputs"),
    on="inputs",
)

write_dataframe(df, bnd_dir / "input_areas.gpkg", driver="GPKG")


# Rasterize to match the blueprint

df = pd.DataFrame(df[["geometry", "value"]].copy())
df.geometry = df.geometry.values.data

# convert to pairs of GeoJSON , value
shapes = df.apply(lambda row: (to_dict(row.geometry), row.value), axis=1)

with rasterio.open(blueprint_filename) as src:
    data = rasterize(
        shapes.values, src.shape, transform=src.transform, dtype="uint8", fill=255
    )

    with rasterio.open(out_dir / "input_areas.tif", "w", **src.profile) as out:
        out.write(data, 1)

