from pathlib import Path
import warnings

import pandas as pd
import geopandas as gp
from pyogrio import read_dataframe, write_dataframe
import shapely

from analysis.constants import SECAS_STATES
from analysis.lib.geometry import make_valid

warnings.filterwarnings("ignore", message=".*polygon with more than 100 parts.*")


src_dir = Path("source_data/ownership")
data_dir = Path("data")
out_dir = data_dir / "inputs/boundaries"  # used as inputs for other steps


bnd_df = gp.read_feather(out_dir / "se_boundary.feather", columns=["geometry"])

### Read WMAs in Oklahoma from v3.0; most of these are missing from v4.0
# NOTE: this should be fixed in v5.0
# there are several duplicates; we drop them
ok_wma = (
    read_dataframe(
        src_dir / "pad_us3.0.gpkg",
        layer="PADUS3_0Combined_Proclamation_Marine_Fee_Designation_Easement",
        columns=[
            "Category",
            "State_Nm",
            "Own_Type",
            "GAP_Sts",
            "Loc_Nm",
            "Loc_Own",
            "Loc_Ds",
            "Agg_Src",
            "Des_Tp",
        ],
        where="State_Nm = 'OK' AND Loc_Ds = 'State Wildlife Management Area'",
        use_arrow=True,
    )
    .drop_duplicates()
    .drop(columns=["Loc_Ds"])
)


### Protected areas (PAD-US)
print("Processing PAD-US lands...")

# read specific states; data are already in EPSG:5070
states = ",".join(f"'{s}'" for s in SECAS_STATES + ["UNKF"])
df = read_dataframe(
    src_dir / "pad_us4.0.gpkg",
    layer="PADUS4_0Combined_Proclamation_Marine_Fee_Designation_Easement",
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
    use_arrow=True,
)

df = pd.concat([df, ok_wma], ignore_index=True).drop_duplicates()

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


# Use FGB (instead of Feather) for more optimal reading by area of interest
print("Writing files")
write_dataframe(df, out_dir / "ownership.fgb")
