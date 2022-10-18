from pathlib import Path
import subprocess

import geopandas as gp
import pygeos as pg
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import GEO_CRS


data_dir = Path("data")
tmp_dir = Path("/tmp")
out_dir = Path("tiles")
out_dir.mkdir(exist_ok=True)

# use locally-compiled version from github.com/felt/tippecanoe
tippecanoe = "../lib/tippecanoe/tippecanoe"
tile_join = "../lib/tippecanoe/tile-join"


def create_tileset(infilename, outfilename, minzoom, maxzoom, layer_id):
    ret = subprocess.run(
        [
            tippecanoe,
            "-f",
            "-pg",
            "--hilbert",
            "-ai",
        ]
        + ["-l", layer_id]
        + ["-Z", str(minzoom), "-z", str(maxzoom)]
        + ["-o", f"{str(outfilename)}", str(infilename)]
    )
    ret.check_returncode()


tilesets = []


### Prepare boundary and inverse mask
print("Creating boundary and mask tiles")
bnd_df = gp.read_feather(data_dir / "inputs/boundaries/se_boundary.feather").to_crs(
    GEO_CRS
)
infilename = tmp_dir / "se_boundary.fgb"
write_dataframe(bnd_df, infilename)

outfilename = tmp_dir / "se_boundary.mbtiles"
create_tileset(infilename, outfilename, minzoom=0, maxzoom=8, layer_id="boundary")
tilesets.append(outfilename)


# Create mask by cutting SA bounds out of world bounds
world = pg.box(-180, -85, 180, 85)
mask = pg.normalize(pg.difference(world, bnd_df.geometry.values.data[0]))

infilename = tmp_dir / "se_mask.fgb"
write_dataframe(gp.GeoDataFrame({"geometry": mask}, index=[0], crs=GEO_CRS), infilename)

outfilename = tmp_dir / "se_mask.mbtiles"
create_tileset(infilename, outfilename, minzoom=0, maxzoom=8, layer_id="mask")
tilesets.append(outfilename)


### Export HUC12 / marine blocks to tiles
print("Creating summary unit tiles")
df = gp.read_feather(data_dir / "for_tiles/summary_units.feather")
infilename = tmp_dir / "summary_units.fgb"
write_dataframe(df, infilename)

outfilename = tmp_dir / "units.mbtiles"
create_tileset(infilename, outfilename, minzoom=8, maxzoom=14, layer_id="units")
tilesets.append(outfilename)


### Create state tileset (all states)
print("Creating state tiles")
df = read_dataframe(
    "source_data/boundaries/tl_2021_us_state/tl_2021_us_state.shp", columns=["STATEFP"]
).to_crs(GEO_CRS)

infilename = tmp_dir / "states.fgb"
write_dataframe(df, infilename)

outfilename = tmp_dir / "states.mbtiles"
create_tileset(infilename, outfilename, minzoom=0, maxzoom=5, layer_id="states")
tilesets.append(outfilename)

### Create ownership tiles
print("Creating protected areas tiles")
df = gp.read_feather(
    data_dir / "inputs/boundaries/ownership.feather", columns=["Own_Type", "GAP_Sts"]
).to_crs(GEO_CRS)

infilename = tmp_dir / "ownership.fgb"
write_dataframe(df, infilename)

outfilename = tmp_dir / "ownership.mbtiles"
create_tileset(infilename, outfilename, minzoom=0, maxzoom=15, layer_id="ownership")
tilesets.append(outfilename)


### Merge tiles
print("Merging tilesets")

outfilename = out_dir / "se_map_units.mbtiles"
ret = subprocess.run(
    [
        tile_join,
        "-f",
    ]
    + ["-o", f"{str(outfilename)}"]
    + tilesets
)
ret.check_returncode()
