import os
from pathlib import Path

import pandas as pd
import pygeos as pg
import geopandas as gp
import numpy as np
from pyogrio import read_dataframe, write_dataframe

from analysis.pygeos_util import intersection

from analysis.constants import DATA_CRS, INPUTS, CHAT_CATEGORIES


# OK has the most fields
field_map = {e["field"]: e["id"] for e in INPUTS["okchat"]["indicators"]}
chat_fields = ["chatrank"] + list(field_map.values())


data_dir = Path("data")
src_dir = Path("source_data/chat")
out_dir = data_dir / "inputs/indicators/chat"
gis_dir = data_dir / "indicators/chat"
tile_dir = data_dir / "for_tiles"

if not out_dir.exists():
    os.makedirs(out_dir)

if not gis_dir.exists():
    os.makedirs(gis_dir)

inputs_df = gp.read_feather(data_dir / "boundaries/input_areas.feather")

# Is in EPSG:5070 but not recognized as such
print("Reading CHAT data...")
df = (
    read_dataframe(src_dir / "WAFWA_CHAT_Lower48.shp")
    .set_crs(DATA_CRS)
    .drop(columns=['ls_cond'])
    .rename(columns=field_map)
    .rename(columns={'chat_rank': 'chatrank'})
)

for col in chat_fields:
    df[col] = df[col].astype("uint8")

df = df.drop(columns=["hexagon_id"])

### Find the CHAT units that intersect with OK / TX input areas
# Use centerpoints, since input area roughly follows edges of hexes
points = pg.centroid(df.geometry.values.data)
tree = pg.STRtree(points)

for state in ["ok", "tx"][1:]: # FIXME
    print(f"Processing {state} CHAT...")
    input_area = pg.union_all(
        inputs_df.loc[inputs_df.inputs == f"{state}chat"].geometry.values.data
    )
    ix = tree.query(input_area, predicate="intersects")
    state_df = df.iloc[ix].reset_index(drop=True)

    # lcon not present for TX
    if state=='tx':
        state_df = state_df.drop(columns=['lcon'])

    # for proofing
    write_dataframe(state_df, gis_dir / f"{state}chat.gpkg", driver="GPKG")

    # for tiles
    write_dataframe(state_df, tile_dir / f"{state}chat.geojson", driver="GeoJSONSeq")

    # convert attributes to categoricals for analysis
    for col in chat_fields:
        if not col in state_df.columns:
            continue


        state_df[col] = pd.Series(
            pd.Categorical.from_codes(
                state_df[col], categories=CHAT_CATEGORIES, ordered=True
            )
        )

    state_df.to_feather(out_dir / f"{state}chat.feather")
