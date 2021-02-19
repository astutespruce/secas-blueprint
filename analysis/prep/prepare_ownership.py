import os
from pathlib import Path
import warnings

import pandas as pd
import geopandas as gp
from geopandas.array import from_wkb
import pygeos as pg
from pyogrio import read_dataframe, write_dataframe, read_info
from pyogrio.raw import read

# suppress warnings about writing to feather
warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

from analysis.constants import GEO_CRS, DATA_CRS, SE_STATES
from analysis.lib.pygeos_util import explode


src_dir = Path("source_data/ownership")
data_dir = Path("data")
out_dir = data_dir / "inputs/boundaries"  # used as inputs for other steps
tile_dir = data_dir / "for_tiles"

gdb = src_dir / "PAD_US2_1.gdb"
layer = "PADUS2_1Combined_Marine_Fee_Designation_Easement"

bnd_df = gp.read_feather(out_dir / "se_boundary.feather", columns=["geometry"])


### Protected areas (PAD-US)
print("Processing PAD-US lands...")

# this is a very large dataset with some invalid geometries so we have to read it in chunks
count = read_info(gdb, layer=layer)["features"]
chunk_size = 10000

merged = None
for chunk in range(0, count, chunk_size):
    print(f"Reading chunk {chunk} - {chunk+chunk_size -1}..")
    # have to read it raw because of geometry errors
    meta, geometry, field_data = read(
        gdb,
        layer=layer,
        columns=[
            "Category",
            "State_Nm",
            "Own_Type",
            "GAP_Sts",
            "Loc_Nm",
            "Loc_Own",
            "Agg_Src",
        ],
        force_2d=True,
        skip_features=chunk,
        max_features=chunk_size - 1,
    )

    columns = meta["fields"].tolist()
    data = {columns[i]: field_data[i] for i in range(len(columns))}
    df = pd.DataFrame(data, columns=columns)
    df["geometry"] = geometry

    df = df.loc[df.State_Nm.isin(SE_STATES + ["UNKF"])].copy()
    # drop BOEM lease block groups
    df = df.loc[df.Agg_Src != "USGS_PADUS2_0Marine_BOEM_Block_Dissolve"].drop(
        columns=["Agg_Src"]
    )

    if not len(df):
        continue

    if merged is None:
        merged = df

    else:
        merged = merged.append(df, ignore_index=True)

df = merged
df["geometry"] = from_wkb(df.geometry)
# set the CRS, it is same as 5070 but not recognized properly
df = gp.GeoDataFrame(df, geometry="geometry", crs=DATA_CRS)

tree = pg.STRtree(df.geometry.values.data)
ix = tree.query(bnd_df.geometry.values.data[0], predicate="intersects")
df = df.iloc[ix].copy()


print("making valid...")
df["geometry"] = pg.make_valid(df.geometry.values.data)

df = explode(df).reset_index()
# there are some geometry errors after cleaning up above, keep only polys
df = df.loc[pg.get_type_id(df.geometry.values.data) == 3].copy()


df.to_feather(out_dir / "ownership.feather")
write_dataframe(df, data_dir / "boundaries/ownership.gpkg", driver="GPKG")

# Write for tiles
write_dataframe(
    df[["geometry", "Own_Type", "GAP_Sts"]].to_crs(GEO_CRS),
    tile_dir / "ownership.geojson",
    driver="GeoJSONSeq",
)

