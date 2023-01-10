from pathlib import Path
import warnings

import geopandas as gp
from pyogrio import read_dataframe, write_dataframe
import shapely

from analysis.constants import SECAS_STATES
from analysis.lib.geometry import make_valid

# suppress warnings about writing to feather
warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

src_dir = Path("source_data/ownership")
data_dir = Path("data")
out_dir = data_dir / "inputs/boundaries"  # used as inputs for other steps

filename = src_dir / "pad_us3.0.gpkg"
layer = "PADUS3_0Combined_Proclamation_Marine_Fee_Designation_Easement"


bnd_df = gp.read_feather(out_dir / "se_boundary.feather", columns=["geometry"])

### Protected areas (PAD-US)
print("Processing PAD-US lands...")

# read specific states; data are already in EPSG:5070
states = ",".join(f"'{s}'" for s in SECAS_STATES + ["UNKF"])
df = read_dataframe(
    filename,
    layer=layer,
    columns=[
        "Category",
        "State_Nm",
        "Own_Type",
        "GAP_Sts",
        "Loc_Nm",
        "Loc_Own",
        "Agg_Src",
        "Des_Tp",
    ],
    where=f"State_Nm in ({states})",
)

# drop BOEM lease block groups
df = df.loc[df.Agg_Src != "USGS_PADUS2_0Marine_BOEM_Block_Dissolve"].drop(
    columns=["Agg_Src"]
)

# drop proclamation boundaries but retain military lands that only show up as proclamation
df = df.loc[(df.Category != "Proclamation") | (df.Des_Tp == "MIL")].reset_index(
    drop=True
)


tree = shapely.STRtree(df.geometry.values)
ix = tree.query(bnd_df.geometry.values[0], predicate="intersects")
df = df.iloc[ix].copy()

print("making valid and exploding parts...")
df["geometry"] = make_valid(df.geometry.values)
df = df.explode(ignore_index=True)

# there may be some geometry errors after cleaning up above, keep only polys
df = df.loc[shapely.get_type_id(df.geometry.values) == 3].reset_index(drop=True)


print("Writing files")
df.to_feather(out_dir / "ownership.feather")
write_dataframe(df, data_dir / "boundaries/ownership.fgb")
