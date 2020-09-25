import os
from pathlib import Path
import geopandas as gp
import pandas as pd
from pyogrio import read_dataframe, write_dataframe
import pygeos as pg
import numpy as np

# suppress warnings abuot writing to feather
import warnings

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES


src_dir = Path("source_data")
data_dir = Path("data")
analysis_dir = data_dir / "inputs/summary_units"
bnd_dir = data_dir / "boundaries"  # GPKGs output for reference
tile_dir = data_dir / "for_tiles"

if not analysis_dir.exists():
    os.makedirs(analysis_dir)

bnd_df = gp.read_feather(data_dir / "inputs/boundaries/se_boundary.feather")
bnd = bnd_df.geometry.values.data[0]

### Extract HUC12 within boundary
print("Reading source HUC12s...")
merged = None
for huc2 in [2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 21]:
    df = read_dataframe(
        src_dir
        / f"summary_units/huc12/WBD_{huc2:02}_HU2_GDB/WBD_{huc2:02}_HU2_GDB.gdb",
        layer="WBDHU12",
    )[["huc12", "name", "geometry"]].rename(columns={"huc12": "id"})

    if merged is None:
        merged = df

    else:
        merged = merged.append(df, ignore_index=True)

print("Projecting to match SE region data...")
huc12 = merged.to_crs(DATA_CRS)


# select out those within the SE boundary
print("Selecting HUC12s in region...")
tree = pg.STRtree(huc12.geometry.values.data)
ix = tree.query(bnd, predicate="intersects")
huc12 = huc12.iloc[ix].copy().reset_index(drop=True)

# make sure data are valid
huc12["geometry"] = pg.make_valid(huc12.geometry.values.data)

# calculate area
huc12["acres"] = (pg.area(huc12.geometry.values.data) * M2_ACRES).round().astype("uint")

# NOTE: we don't limit to those that are mostly in the region because it takes too long.

# Save in EPSG:5070 for analysis
huc12.to_feather(analysis_dir / "huc12.feather")
write_dataframe(huc12, bnd_dir / "huc12.gpkg", driver="GPKG")


# project to WGS84 for report maps
huc12_wgs84 = huc12.to_crs(GEO_CRS)
huc12_wgs84.to_feather(analysis_dir / "huc12_wgs84.feather")


### Marine units
print("Reading marine blocks...")

atl = read_dataframe(
    src_dir / "summary_units/marine_blocks/Atlantic/ATL_BLKCLP.shp",
    columns=["PROT_NUMBE", "BLOCK_NUMB"],
)
gulf = read_dataframe(
    src_dir / "summary_units/marine_blocks/Gulf_of_Mexico/blk_clip.shp",
    columns=["PROT_NUMBE", "BLOCK_NUMB"],
)

marine = atl.append(gulf, ignore_index=True)
marine["id"] = marine.PROT_NUMBE.str.strip() + "-" + marine.BLOCK_NUMB.str.strip()
marine["name"] = (
    marine.PROT_NUMBE.str.strip() + ": Block " + marine.BLOCK_NUMB.str.strip()
)

# there are a couple blocks without proper names and 0 area; drop them
marine = marine[["id", "name", "geometry"]].dropna().to_crs(DATA_CRS)

# select out those within the SE boundary
print("Selecting Marine blocks in region...")
tree = pg.STRtree(marine.geometry.values.data)
ix = tree.query(bnd, predicate="intersects")
marine = marine.iloc[ix].copy().reset_index(drop=True)

marine["geometry"] = pg.make_valid(marine.geometry.values.data)

marine["acres"] = (
    (pg.area(marine.geometry.values.data) * M2_ACRES).round().astype("uint")
)

# Save in EPSG:5070 for analysis
marine.to_feather(analysis_dir / "marine_blocks.feather")
write_dataframe(marine, bnd_dir / "marine_blocks.gpkg", driver="GPKG")

# project to WGS84 for report maps
marine_wgs84 = marine.to_crs(GEO_CRS)
marine_wgs84.to_feather(analysis_dir / "marine_blocks_wgs84.feather")


# ### Merge HUC12 and marine into single units file and export for creating tiles
df = huc12_wgs84.append(marine_wgs84, ignore_index=True, sort=False)
write_dataframe(df, tile_dir / "units.geojson", driver="GeoJSONSeq")
