from pathlib import Path
import subprocess

import geopandas as gp
from pyogrio import read_dataframe, write_dataframe
import shapely

from analysis.constants import GEO_CRS


data_dir = Path("data")
tmp_dir = Path("/tmp")
out_dir = Path("tiles")
out_dir.mkdir(exist_ok=True)

tippecanoe = "tippecanoe"
tile_join = "tile-join"


def get_col_types(df, bool_cols=None):
    """Convert pandas types to tippecanoe data types.

    Parameters
    ----------
    df : DataFrame
    bool_cols : set, optional (default: None)
        If present, set of column names that will be set as bool type

    Returns
    -------
    list of ['-T', '<col>:<type'] entries for each column
    """
    out = []
    for col, dtype in df.dtypes.astype("str").to_dict().items():
        if dtype == "geometry":
            continue

        out.append("-T")
        out_type = dtype
        if dtype == "object":
            out_type = "string"
        elif "int" in dtype:
            out_type = "int"
        elif "float" in dtype:
            out_type = "float"

        # overrides
        if bool_cols and col in bool_cols:
            out_type = "bool"

        out.append(f"{col}:{out_type}")

    return out


def create_tileset(infilename, outfilename, minzoom, maxzoom, layer_id, col_types=None):
    col_types = col_types or []
    ret = subprocess.run(
        [tippecanoe, "-f", "-pg", "--hilbert", "-ai", "--drop-smallest-as-needed"]
        + ["-l", layer_id]
        + ["-Z", str(minzoom), "-z", str(maxzoom)]
        + col_types
        + ["-o", f"{str(outfilename)}", str(infilename)]
    )
    ret.check_returncode()


# ### Create state tileset (all states)
# print(
#     "\n\n------------------------------------------------\nCreating state tiles\n------------------------------------------------\n"
# )
# df = read_dataframe(
#     "zip://source_data/boundaries/tl_2021_us_state.zip/tl_2021_us_state.shp",
#     columns=["STATEFP"],
# ).to_crs(GEO_CRS)

# infilename = tmp_dir / "states.fgb"
# write_dataframe(df, infilename)

# create_tileset(
#     infilename,
#     out_dir / "states.mbtiles",
#     minzoom=0,
#     maxzoom=5,
#     layer_id="states",
#     col_types=get_col_types(df),
# )

### Create ownership and subregion tiles
print(
    "\n\n------------------------------------------------\nCreating protected areas and subregion tiles\n------------------------------------------------\n"
)

tilesets = []

print("creating ownership tiles")
df = gp.read_feather(
    data_dir / "inputs/boundaries/ownership.feather",
    columns=["geometry", "Own_Type", "GAP_Sts", "Loc_Nm", "Loc_Own"],
).to_crs(GEO_CRS)

infilename = tmp_dir / "ownership.fgb"
write_dataframe(df, infilename)

outfilename = tmp_dir / "se_ownership.mbtiles"
tilesets.append(outfilename)
create_tileset(
    infilename,
    outfilename,
    minzoom=4,
    maxzoom=14,
    layer_id="ownership",
    col_types=get_col_types(df),
)


print("creating subregion tiles")
df = gp.read_feather(
    data_dir / "boundaries/base_subregions.feather",
).to_crs(GEO_CRS)

infilename = tmp_dir / "subregions.fgb"
write_dataframe(df, infilename)

outfilename = tmp_dir / "se_subregions.mbtiles"
tilesets.append(outfilename)
create_tileset(
    infilename,
    outfilename,
    minzoom=2,
    maxzoom=14,
    layer_id="subregions",
    col_types=get_col_types(df),
)


# create SLR NODATA tiles
print("creating SLR tiles")
df = (
    gp.read_feather(
        data_dir / "for_tiles/slr_not_modeled.feather", columns=["geometry"]
    )
    .to_crs(GEO_CRS)
    .explode(ignore_index=True)
)
# reset the index to a new attribute, because tippecanoe segfaults when no attributes
# present besides geometry
df = df.reset_index()
infilename = tmp_dir / "slr_not_modeled.fgb"
write_dataframe(df, infilename)

outfilename = tmp_dir / "slr_not_modeled.mbtiles"
tilesets.append(outfilename)
create_tileset(
    infilename,
    outfilename,
    minzoom=2,
    maxzoom=14,
    layer_id="slr_not_modeled",
)

outfilename = out_dir / "se_other_features.mbtiles"
ret = subprocess.run(
    [
        tile_join,
        "-f",
        "-pg",
        "--no-tile-size-limit",
    ]
    + ["-o", f"{str(outfilename)}"]
    + tilesets
)
ret.check_returncode()


######### Create combined tileset for summary units, boundary, mask for frontend
tilesets = []

### Prepare boundary and inverse mask
print(
    "\n\n------------------------------------------------\nCreating boundary and mask tiles\n------------------------------------------------\n"
)
bnd_df = gp.read_feather(data_dir / "inputs/boundaries/se_boundary.feather").to_crs(
    GEO_CRS
)
infilename = tmp_dir / "se_boundary.fgb"
write_dataframe(bnd_df, infilename)

outfilename = tmp_dir / "se_boundary.mbtiles"
create_tileset(infilename, outfilename, minzoom=2, maxzoom=14, layer_id="boundary")
tilesets.append(outfilename)


# Create mask by cutting SA bounds out of world bounds
# NOTE: mask is only used in report
world = shapely.box(-180, -85, 180, 85)
mask = shapely.normalize(shapely.difference(world, bnd_df.geometry.values[0]))

infilename = tmp_dir / "se_mask.fgb"
write_dataframe(gp.GeoDataFrame({"geometry": mask}, index=[0], crs=GEO_CRS), infilename)

outfilename = tmp_dir / "se_mask.mbtiles"
create_tileset(infilename, outfilename, minzoom=0, maxzoom=8, layer_id="mask")
tilesets.append(outfilename)


### Export HUC12 / marine blocks to tiles
print(
    "\n\n------------------------------------------------\nCreating summary unit tiles\n------------------------------------------------\n"
)
df = gp.read_feather(data_dir / "for_tiles/summary_units.feather")
infilename = tmp_dir / "summary_units.fgb"
write_dataframe(df, infilename)

outfilename = tmp_dir / "units.mbtiles"
create_tileset(
    infilename,
    outfilename,
    minzoom=8,
    maxzoom=14,
    layer_id="units",
    col_types=get_col_types(df),
)
tilesets.append(outfilename)


### Merge tiles
print(
    "\n\n------------------------------------------------\nMerging summary units, boundary, mask\n------------------------------------------------\n"
)


outfilename = out_dir / "se_map_units.mbtiles"
ret = subprocess.run(
    [tile_join, "-f", "-pg"] + ["-o", f"{str(outfilename)}"] + tilesets
)
ret.check_returncode()
