"""
Prepare HUC12 and Marine Lease Block input areas.

NOTE: this must be run after prepare_input_areas.py
"""
import os
from pathlib import Path

import geopandas as gp
import pandas as pd
from pyogrio import read_dataframe, write_dataframe
import pygeos as pg
from progress.bar import Bar

# suppress warnings abuot writing to feather
import warnings

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES
from analysis.lib.pygeos_util import to_dict
from analysis.lib.raster import calculate_percent_overlap


src_dir = Path("source_data")
data_dir = Path("data")
analysis_dir = data_dir / "inputs/summary_units"
bnd_dir = data_dir / "boundaries"  # GIS files output for reference
tile_dir = data_dir / "for_tiles"
input_area_mask = data_dir / "inputs/input_areas_mask.tif"

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


# select out those within the SE states
print("Selecting HUC12s in region...")
tree = pg.STRtree(huc12.geometry.values.data)
ix = tree.query(bnd, predicate="intersects")
huc12 = huc12.iloc[ix].copy().reset_index(drop=True)

# make sure data are valid
huc12["geometry"] = pg.make_valid(huc12.geometry.values.data)

# calculate area
huc12["acres"] = (pg.area(huc12.geometry.values.data) * M2_ACRES).round().astype("uint")

# for those that touch the edge of the region, drop any that are not >= 50% in
# raster input area.  We are not able to use polygon intersection because it
# takes too long.
tree = pg.STRtree(huc12.geometry.values.data)
ix = tree.query(bnd, predicate="contains")

edge_df = huc12.loc[~huc12.id.isin(huc12.iloc[ix].id)].copy()
geometries = pd.Series(edge_df.geometry.values.data, index=edge_df.id)
drop_ids = []
for id, geometry in Bar(
    "Calculating HUC12 overlap with input area", max=len(geometries)
).iter(geometries.iteritems()):
    percent_overlap = calculate_percent_overlap(
        input_area_mask, [to_dict(geometry)], bounds=pg.total_bounds(geometry)
    )
    if percent_overlap < 50:
        drop_ids.append(id)

print(f"Dropping {len(drop_ids)} HUC12s that do not sufficiently overlap input areas")
huc12 = huc12.loc[~huc12.id.isin(drop_ids)].copy()

# extract geographic bounds
huc12_wgs84 = huc12.to_crs(GEO_CRS)
huc12 = huc12.join(huc12_wgs84.bounds)

# Save in EPSG:5070 for analysis
huc12.to_feather(analysis_dir / "huc12.feather")
write_dataframe(huc12, bnd_dir / "huc12.gpkg")


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

# some blocks have multiple parts, merge them
grouped = marine.groupby("id")

# save as DataFrame instead of GeoDataFrame for easier processing
marine = pd.DataFrame(
    grouped.geometry.apply(lambda g: g.values.data).apply(
        lambda g: pg.union_all(g) if len(g) > 1 else g[0]
    )
).join(grouped.name.first())

# coerce all to MultiPolygons
ix = pg.get_type_id(marine.geometry.values) == 3
marine.loc[ix, "geometry"] = marine.loc[ix].geometry.apply(
    lambda g: pg.multipolygons([g])
)

marine = (
    gp.GeoDataFrame(marine, geometry="geometry", crs=DATA_CRS)
    .reset_index()
    .rename(columns={"index": "id"})
)


# select out those within the SE boundary
print("Selecting Marine blocks in region...")
tree = pg.STRtree(marine.geometry.values.data)
ix = tree.query(bnd, predicate="intersects")
marine = marine.iloc[ix].copy().reset_index(drop=True)

marine["geometry"] = pg.make_valid(marine.geometry.values.data)

marine["acres"] = (
    (pg.area(marine.geometry.values.data) * M2_ACRES).round().astype("uint")
)

marine = marine.loc[marine.acres > 0].dropna()

marine_wgs84 = marine.to_crs(GEO_CRS)
marine = marine.join(marine_wgs84.bounds)

# Save in EPSG:5070 for analysis
marine.to_feather(analysis_dir / "marine_blocks.feather")
write_dataframe(marine, bnd_dir / "marine_blocks.gpkg")

# ### Merge HUC12 and marine into single units file and export for creating tiles
df = huc12_wgs84.append(marine_wgs84, ignore_index=True, sort=False)
write_dataframe(df, tile_dir / "units.geojson", driver="GeoJSONSeq")
