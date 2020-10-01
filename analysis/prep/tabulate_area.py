"""
Calculate statistics for each HUC12 and marine lease block using
the Blueprint, indicators, SLR, Urbanization, and ownership datasets.
"""

import csv
import os
from pathlib import Path
from time import time
import warnings

import pandas as pd
import geopandas as gp
import numpy as np
from progress.bar import Bar
import pygeos as pg

from analysis.pygeos_util import to_crs, to_pygeos, sjoin, to_dict, intersection
from analysis.constants import (
    DEBUG,
    BLUEPRINT,
    URBAN_YEARS,
    DATA_CRS,
    GEO_CRS,
    M2_ACRES,
)
from analysis.lib.stats import (
    extract_blueprint_area,
    extract_urbanization_area,
    extract_slr_area,
)


data_dir = Path("data")
huc12_filename = data_dir / "inputs/summary_units/huc12.feather"
marine_filename = data_dir / "inputs/summary_units/marine_blocks.feather"
ownership_filename = data_dir / "inputs/boundaries/ownership.feather"
county_filename = data_dir / "inputs/boundaries/counties.feather"
parca_filename = data_dir / "inputs/boundaries/parca.feather"
slr_bounds_filename = data_dir / "inputs/threats/slr/slr_bounds.feather"

if DEBUG:
    debug_dir = Path("/tmp")
    huc12_debug_dir = debug_dir / "huc12"
    if not huc12_debug_dir.exists():
        os.makedirs(huc12_debug_dir)

    marine_debug_dir = debug_dir / "marine_blocks"
    if not marine_debug_dir.exists():
        os.makedirs(marine_debug_dir)

start = time()


### Inland
out_dir = data_dir / "results/huc12"
if not out_dir.exists():
    os.makedirs(out_dir)


# print("Reading HUC12 boundaries")
units = gp.read_feather(huc12_filename, columns=["id", "geometry"]).set_index("id")

# # transform to pandas Series instead of GeoSeries to get pygeos geometries for iterators below
geometries = pd.Series(units.geometry.values.data, index=units.index)

### Calculate counts of each category in blueprint and indicators and put into a DataFrame
counts = []
index = []

for huc12, geometry in Bar(
    "Calculating Blueprint and hubs / connectors counts for HUC12", max=len(geometries)
).iter(geometries.iteritems()):
    zone_results = extract_blueprint_area(
        [to_dict(geometry)], bounds=pg.total_bounds(geometry)
    )
    if zone_results is None:
        continue

    index.append(huc12)
    counts.append(zone_results)

count_df = pd.DataFrame(counts, index=index)

results = count_df[["shape_mask"]].copy()
results.index.name = "id"

### Export the Blueprint and hubs / connectors
# each column is an array of counts for each
for col in count_df.columns.difference(["shape_mask"]):
    s = count_df[col].apply(pd.Series).fillna(0)
    s.columns = [f"{col}_{c}" for c in s.columns]
    results = results.join(s)

results.reset_index().to_feather(out_dir / "blueprint.feather")

if DEBUG:
    results.to_csv(huc12_debug_dir / "blueprint.csv", index_label="id")


### Calculate counts for urbanization
index = []
results = []
for huc12, geometry in Bar(
    "Calculating Urbanization counts for HUC12", max=len(geometries)
).iter(geometries.iteritems()):
    zone_results = extract_urbanization_area(
        [to_dict(geometry)], bounds=pg.total_bounds(geometry)
    )
    if zone_results is None:
        continue

    index.append(huc12)
    results.append(zone_results)

cols = ["shape_mask", "urban"] + URBAN_YEARS
df = pd.DataFrame(results, index=index)[cols]
df = df.reset_index().rename(columns={"index": "id"}).round()
df.columns = [str(c) for c in df.columns]

df.to_feather(out_dir / "urban.feather")

if DEBUG:
    df.to_csv(huc12_debug_dir / "urban.csv", index=False)


### Calculate counts for SLR
# find the indexes of the geometries that overlap with SLR bounds; these are the only
# ones that need to be analyzed for SLR impacts
slr_bounds = gp.read_feather(slr_bounds_filename).geometry
tree = pg.STRtree(slr_bounds.geometry.values.data)
left, right = tree.query_bulk(geometries)
idx = np.unique(left)
slr_geometries = geometries.iloc[idx]

results = []
index = []
for huc12, geometry in Bar(
    "Calculating SLR counts for HUC12", max=len(slr_geometries)
).iter(slr_geometries.iteritems()):
    zone_results = extract_slr_area(
        [to_dict(geometry)], bounds=pg.total_bounds(geometry)
    )
    if zone_results is None:
        continue

    index.append(huc12)
    results.append(zone_results)

df = pd.DataFrame(results, index=index)

# reorder columns
df = df[["shape_mask"] + list(df.columns.difference(["shape_mask"]))]
# extract only areas that actually had SLR pixels
df = df[df[df.columns[1:]].sum(axis=1) > 0]
df.columns = [str(c) for c in df.columns]
df = df.reset_index().rename(columns={"index": "id"}).round()
df.to_feather(out_dir / "slr.feather")

if DEBUG:
    df.to_csv(huc12_debug_dir / "slr.csv", index=False)


### Calculate overlap with ownership and protection
print("Calculating overlap with land ownership and protection")
ownership = gp.read_feather(
    ownership_filename, columns=["geometry", "Own_Type", "GAP_Sts"]
)

df = intersection(units, ownership)
df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES

# drop areas that touch but have no overlap
df = df.loc[df.acres > 0].copy()

by_owner = (
    df[["Own_Type", "acres"]]
    .groupby(by=[df.index.get_level_values(0), "Own_Type"])
    .acres.sum()
    .astype("float32")
    .round()
    .reset_index()
    .rename(columns={"level_0": "id"})
)

by_protection = (
    df[["GAP_Sts", "acres"]]
    .groupby(by=[df.index.get_level_values(0), "GAP_Sts"])
    .acres.sum()
    .astype("float32")
    .round()
    .reset_index()
    .rename(columns={"level_0": "id"})
)

by_owner.to_feather(out_dir / "ownership.feather")
by_protection.to_feather(out_dir / "protection.feather")

if DEBUG:
    by_owner.to_csv(huc12_debug_dir / "ownership.csv", index=False)
    by_protection.to_csv(huc12_debug_dir / "protection.csv", index=False)


### Calculate spatial join with counties
print("Calculating spatial join with counties")
counties = gp.read_feather(county_filename)
df = (
    sjoin(units, counties, how="inner")[["FIPS", "state", "county"]]
    .reset_index()
    .round()
)
df.to_feather(out_dir / "counties.feather")

if DEBUG:
    df.to_csv(huc12_debug_dir / "counties.csv", index=False)


#########################################################################


### Marine blocks
out_dir = data_dir / "results/marine_blocks"
if not out_dir.exists():
    os.makedirs(out_dir)

print("Reading marine blocks boundaries")
units = gp.read_feather(marine_filename, columns=["id", "geometry"]).set_index("id")

geometries = pd.Series(units.geometry.values.data, index=units.index)


### Calculate counts of each category in blueprint and indicators and put into a DataFrame
counts = []
index = []
for id, geometry in Bar(
    "Calculating Blueprint and Indicator counts for marine blocks", max=len(geometries)
).iter(geometries.iteritems()):
    zone_results = extract_blueprint_area(
        [to_dict(geometry)], bounds=pg.total_bounds(geometry)
    )
    if zone_results is None:
        continue

    index.append(id)
    counts.append(zone_results)

count_df = pd.DataFrame(counts, index=index).fillna(0)

results = count_df[["shape_mask"]].copy()
results.index.name = "id"

### Export the Blueprint hubs / connectors
# each column is an array of counts for each
for col in count_df.columns.difference(["shape_mask"]):
    s = count_df[col].apply(pd.Series).fillna(0)
    s.columns = [f"{col}_{c}" for c in s.columns]
    results = results.join(s)

results.reset_index().rename(columns={"index": "id"}).to_feather(
    out_dir / "blueprint.feather"
)

if DEBUG:
    results.to_csv(marine_debug_dir / "blueprint.csv", index_label="id")


print(
    "Processed {:,} zones in {:.2f}m".format(len(geometries), (time() - start) / 60.0)
)
