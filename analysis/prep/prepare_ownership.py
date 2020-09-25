import os
from pathlib import Path
import warnings
import pandas as pd
import geopandas as gp
import pygeos as pg
from pyogrio.geopandas import read_dataframe, write_dataframe

# suppress warnings about writing to feather
warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

from analysis.constants import GEO_CRS, DATA_CRS, SE_STATES
from analysis.pygeos_util import explode


src_dir = Path("source_data/ownership")
data_dir = Path("data")
out_dir = data_dir / "inputs/boundaries"  # used as inputs for other steps
tile_dir = data_dir / "for_tiles"


### Protected areas (PAD-US)
print("Processing PAD-US lands...")

merged = None
for state in SE_STATES:
    print(f"Reading {state}...")
    df = read_dataframe(
        src_dir / f"PADUS2_0{state}_Arc10GDB/PADUS2_0{state}.gdb",
        columns=["Own_Type", "GAP_Sts", "Loc_Nm", "Loc_Own"],
    ).to_crs(DATA_CRS)

    print("making valid...")
    df["geometry"] = pg.make_valid(df.geometry.values.data)

    df = explode(df)
    # there are some geometry errors after cleaning up above, keep only polys
    df = df.loc[pg.get_type_id(df.geometry.values.data) == 3].copy()

    if merged is None:
        merged = df

    else:
        merged = merged.append(df, ignore_index=True)

df = merged

df.to_feather(out_dir / "ownership.feather")
write_dataframe(df, data_dir / "boundaries/ownership.gpkg", driver="GPKG")

# Write for tiles
write_dataframe(
    df[["geometry", "Own_Type", "GAP_Sts"]].to_crs(GEO_CRS),
    tile_dir / "ownership.geojson",
    driver="GeoJSONSeq",
)

