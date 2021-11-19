import os
from pathlib import Path
import geopandas as gp
import pygeos as pg
from pyogrio.geopandas import read_dataframe, write_dataframe

# suppress warnings abuot writing to feather
import warnings

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

from analysis.constants import GEO_CRS, DATA_CRS
from analysis.lib.pygeos_util import explode


src_dir = Path("source_data")
data_dir = Path("data")
out_dir = data_dir / "inputs/boundaries"  # used as inputs for other steps
tile_dir = data_dir / "for_tiles"

if not out_dir.exists():
    os.makedirs(out_dir)

if not tile_dir.exists():
    os.makedirs(tile_dir)


### Extract the boundary
bnd_df = read_dataframe(
    src_dir / "blueprint/SE_Blueprint_2021_Vectors.gdb",
    layer="SECAS_Boundary_2021_20211117",
)[["geometry"]]
# boundary has multiple geometries, union together and cleanup
bnd_df = gp.GeoDataFrame(
    geometry=[pg.union_all(pg.make_valid(bnd_df.geometry.values.data))],
    index=[0],
    crs=bnd_df.crs,
)
bnd_df.to_feather(out_dir / "se_boundary.feather")
write_dataframe(bnd_df, data_dir / "boundaries/se_boundary.fgb")

# create GeoJSON for tiling
bnd_geo = bnd_df.to_crs(GEO_CRS)
write_dataframe(bnd_geo, tile_dir / "se_boundary.geojson", driver="GeoJSONSeq")

### Create mask by cutting SA bounds out of world bounds
print("Creating mask...")
world = pg.box(-180, -85, 180, 85)
mask = pg.normalize(pg.difference(world, bnd_geo.geometry.values.data))

write_dataframe(
    gp.GeoDataFrame({"geometry": mask}, index=[0], crs=GEO_CRS),
    tile_dir / "se_mask.geojson",
    driver="GeoJSONSeq",
)

### Extract counties within SA bounds
print("Extracting states and counties...")
states = (
    read_dataframe(
        src_dir / "boundaries/tl_2019_us_state.shp",
        read_geometry=False,
        columns=["STATEFP", "NAME"],
    )
    .rename(columns={"NAME": "state"})
    .set_index("STATEFP")
)

counties = (
    read_dataframe(
        src_dir / "boundaries/tl_2019_us_county.shp",
        columns=["STATEFP", "GEOID", "NAME", "geometry"],
    )
    .rename(columns={"GEOID": "FIPS", "NAME": "county"})
    .to_crs(DATA_CRS)
)

# select counties within the SA boundary
tree = pg.STRtree(counties.geometry.values.data)
ix = tree.query(bnd_df.geometry.values.data[0], predicate="intersects")
counties = counties.iloc[ix].join(states, on="STATEFP").drop(columns=["STATEFP"])


# write_dataframe(counties, out_dir / "counties.gpkg")
counties.to_feather(out_dir / "counties.feather")
