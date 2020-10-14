"""
Calculate statistics for each HUC12 and marine lease block using
the Blueprint, SLR, Urbanization, and ownership datasets.
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

from analysis.lib.pygeos_util import sjoin, to_dict, intersection
from analysis.constants import (
    DEBUG,
    BLUEPRINT,
    URBAN_YEARS,
    DATA_CRS,
    GEO_CRS,
    M2_ACRES,
    ACRES_PRECISION,
    INPUTS,
    GULF_HYPOXIA_BOUNDS,
)
from analysis.lib.stats import (
    extract_blueprint_area,
    extract_urbanization_area,
    extract_slr_area,
    summarize_ownership,
    summarize_chat,
    extract_gulf_hypoxia_area,
)


data_dir = Path("data")
huc12_filename = data_dir / "inputs/summary_units/huc12.feather"
marine_filename = data_dir / "inputs/summary_units/marine_blocks.feather"
county_filename = data_dir / "inputs/boundaries/counties.feather"
parca_filename = data_dir / "inputs/boundaries/parca.feather"
slr_bounds_filename = data_dir / "inputs/threats/slr/slr_bounds.feather"
chat_dir = data_dir / "inputs/indicators/chat"


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

### Calculate area of each category in blueprint and inputs and put into a DataFrame
counts = []
index = []

for huc12, geometry in Bar(
    "Calculating Blueprint and input counts for HUC12", max=len(geometries)
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

### Export the Blueprint results
# each column is an array of counts for each
for col in count_df.columns.difference(["shape_mask"]):
    s = count_df[col].apply(pd.Series).fillna(0)
    s.columns = [f"{col}_{c}" for c in s.columns]
    results = results.join(s)

results.reset_index().to_feather(out_dir / "blueprint.feather")

if DEBUG:
    results.to_csv(huc12_debug_dir / "blueprint.csv", index_label="id")


### Calculate area for urbanization
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


### Calculate area for SLR
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
by_owner, by_protection = summarize_ownership(units)
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

### Process OK / TX
for state in ["ok", "tx"]:
    print(f"Calculating overlap with {state} CHAT...")
    chat = gp.read_feather(chat_dir / f"{state}chat.feather")
    fields = ["chatrank"] + [e["id"] for e in INPUTS[f"{state}chat"]["indicators"]]

    chat_results = summarize_chat(units, chat, fields=fields)
    area_results = chat_results["acres"]
    avg_results = chat_results["avg"]

    results = pd.DataFrame(chat_results["total_acres"].rename("total_acres"))

    # bare indicator IDs are averages
    results = results.join(avg_results).fillna(0)

    for field in fields:
        # convert array to columns
        s = area_results[field].apply(pd.Series)
        s.columns = [f"{field}_{c}" for c in s.columns]

        # drop any that are all 0; these are not present
        s = s.drop(columns=s.columns[s.max() == 0].tolist())
        results = results.join(s)

    results.reset_index().to_feather(out_dir / f"{state}chat.feather")

    if DEBUG:
        results.to_csv(huc12_debug_dir / f"{state}chat.csv", index_label="id")


### Calculate area for Gulf Hypoxia
# only for those HUC12s that intersect with bounds of Gulf Hypoxia dataset
tree = pg.STRtree(geometries)
ix = tree.query(pg.box(*GULF_HYPOXIA_BOUNDS))
gh_geometries = geometries.iloc[ix]

index = []
results = []
for huc12, geometry in Bar(
    "Calculating Gulf Hypoxia area for HUC12", max=len(gh_geometries)
).iter(gh_geometries.iteritems()):
    zone_results = extract_gulf_hypoxia_area(
        [to_dict(geometry)], bounds=pg.total_bounds(geometry)
    )
    if zone_results is None:
        continue

    index.append(huc12)
    results.append(zone_results)

count_df = pd.DataFrame(results, index=index)

results = count_df[["shape_mask"]].copy()
results.index.name = "id"

# each column is an array of counts for each
for col in count_df.columns.difference(["shape_mask"]):
    s = count_df[col].apply(pd.Series).fillna(0)
    s.columns = [f"{col}_{c}" for c in s.columns]
    results = results.join(s)

results = results.reset_index()
results.to_feather(out_dir / "gulf_hypoxia.feather")

if DEBUG:
    results.to_csv(huc12_debug_dir / "gulf_hypoxia.csv", index=False)


# #########################################################################


### Marine blocks
out_dir = data_dir / "results/marine_blocks"
if not out_dir.exists():
    os.makedirs(out_dir)

print("Reading marine blocks boundaries")
units = gp.read_feather(marine_filename, columns=["id", "geometry"]).set_index("id")

geometries = pd.Series(units.geometry.values.data, index=units.index)


### Calculate area of each category in blueprint and inputs and put into a DataFrame
counts = []
index = []
for id, geometry in Bar(
    "Calculating Blueprint counts for marine blocks", max=len(geometries)
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

### Export the Blueprint results
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


### Calculate overlap with ownership and protection
print("Calculating overlap with land ownership and protection")
by_owner, by_protection = summarize_ownership(units)
by_owner.to_feather(out_dir / "ownership.feather")
by_protection.to_feather(out_dir / "protection.feather")

if DEBUG:
    by_owner.to_csv(marine_debug_dir / "ownership.csv", index=False)
    by_protection.to_csv(marine_debug_dir / "protection.csv", index=False)
