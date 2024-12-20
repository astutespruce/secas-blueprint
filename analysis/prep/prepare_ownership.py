from pathlib import Path
import warnings

import pandas as pd
import geopandas as gp
import numpy as np
from pyogrio import read_dataframe, write_dataframe
import rasterio
from rasterio.features import rasterize
import shapely

from analysis.constants import SECAS_STATES, OWNERSHIP, PROTECTION
from analysis.lib.colors import hex_to_uint8
from analysis.lib.geometry import make_valid, to_dict
from analysis.lib.raster import write_raster, add_overviews

warnings.filterwarnings("ignore", message=".*polygon with more than 100 parts.*")

NODATA = 255

src_dir = Path("source_data/ownership")
data_dir = Path("data")
out_dir = data_dir / "inputs/boundaries"  # used as inputs for other steps
constants_dir = Path("constants")


bnd_df = gp.read_feather(out_dir / "se_boundary.feather", columns=["geometry"])

################################################################################
### Compile protected areas
################################################################################


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
            # used for sorting
            "IUCN_Cat",
            "Pub_Access",
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
        # used for sorting
        "IUCN_Cat",
        "Pub_Access",
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
write_dataframe(
    df.drop(
        columns=[
            "IUCN_Cat",
            "Pub_Access",
        ]
    ),
    out_dir / "ownership.fgb",
)


################################################################################
### Sort (in ascending priority) and rasterize
################################################################################

# save the original order
df["orig_order"] = df.index.values

# use sort of IUCN categories from script here: https://www.sciencebase.gov/catalog/item/652d4ebbd34e44db0e2ee458
iucn_sort = {
    "Ia": 0,
    "Ib": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "Other Conservation Area": 7,
    "Unassigned": 8,
}
df["iucn_sort"] = df.IUCN_Cat.map(iucn_sort)

pub_access_sort = {"XA": 0, "RA": 1, "OA": 2, "UK": 3}
df["pub_access_sort"] = df.Pub_Access.map(pub_access_sort)

# sort marine areas lower, these are not included in the flattened stats datasets from PAD-US
df["marine_sort"] = 0
df.loc[df.Category == "Marine", "marine_sort"] = 1

# sort in ascending order first
df = df.sort_values(
    by=["marine_sort", "iucn_sort", "pub_access_sort", "orig_order"]
).reset_index(drop=True)

# find any lower order polygons completely contained within higher order ones
tree = shapely.STRtree(df.geometry.values)
left, right = tree.query(df.geometry.values, predicate="contains_properly")
pairs = pd.DataFrame({"outer": df.index.take(left), "inner": df.index.take(right)})
drop_ix = pairs.loc[pairs.outer < pairs.inner].inner.unique()
df = df.loc[~df.index.isin(drop_ix)].reset_index(drop=True)

ownership = pd.DataFrame(OWNERSHIP.values()).rename(columns={"code": "ownership_code"})
ownership_colormap = (
    ownership.set_index("ownership_code")
    .color.apply(lambda x: hex_to_uint8(x) + (255,) if x else (255, 255, 255, 0))
    .to_dict()
)

protection = pd.DataFrame(PROTECTION.values()).rename(
    columns={"code": "protection_code"}
)
protection_colormap = (
    protection.set_index("protection_code")
    .color.apply(lambda x: hex_to_uint8(x) + (255,) if x else (255, 255, 255, 0))
    .to_dict()
)

df = (
    df.join(ownership.ownership_code, on="Own_Type")
    .join(protection.protection_code, on="GAP_Sts")
    .reset_index()
)

# reverse sort so that highest-priority features get rasterized last, on top
df = df.sort_values(by="index", ascending=False)

# use the SE Blueprint extent grid to derive the master offset coordinates
# so that everything is correctly aligned
extent = rasterio.open(data_dir / "inputs/boundaries/blueprint_extent.tif")
extent_data = extent.read(1)

align_ul = np.take(extent.transform, [2, 5]).tolist()


print("Rasterizing ownership")
data = rasterize(
    df.apply(lambda row: (to_dict(row.geometry), row.ownership_code), axis=1),
    transform=extent.transform,
    out_shape=extent.shape,
    fill=0,
    dtype="uint8",
)


data = np.where(extent_data == 1, data, 0)

outfilename = data_dir / "boundaries/ownership.tif"
write_raster(
    outfilename,
    data,
    extent.transform,
    crs=extent.crs,
    nodata=0,
)

del data

with rasterio.open(outfilename, "r+") as out:
    out.write_colormap(1, ownership_colormap)

add_overviews(outfilename)


print("Rasterizing protection")
data = rasterize(
    df.apply(lambda row: (to_dict(row.geometry), row.protection_code), axis=1),
    transform=extent.transform,
    out_shape=extent.shape,
    fill=0,
    dtype="uint8",
)

data = np.where(extent_data == 1, data, 0)

outfilename = data_dir / "boundaries/protection.tif"
write_raster(
    outfilename,
    data,
    extent.transform,
    crs=extent.crs,
    nodata=0,
)

del data

with rasterio.open(outfilename, "r+") as out:
    out.write_colormap(1, protection_colormap)

add_overviews(outfilename)
