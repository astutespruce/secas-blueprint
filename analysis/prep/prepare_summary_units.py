import os
from pathlib import Path

from progress.bar import Bar
import geopandas as gp
import pandas as pd
from pyogrio import read_dataframe, write_dataframe
import numpy as np
import rasterio
from rasterio.features import rasterize
import shapely

from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES, SECAS_HUC2
from analysis.lib.geometry import make_valid, to_dict
from analysis.lib.raster import write_raster, add_overviews, get_window


src_dir = Path("source_data")
data_dir = Path("data")
analysis_dir = data_dir / "inputs/summary_units"
bnd_dir = data_dir / "boundaries"  # GIS files output for reference
blueprint_extent_filename = data_dir / "inputs/boundaries/blueprint_extent.tif"

if not analysis_dir.exists():
    os.makedirs(analysis_dir)

bnd_df = gp.read_feather(data_dir / "inputs/boundaries/se_boundary.feather")
bnd = bnd_df.geometry.values[0]

subregion_df = gp.read_feather(data_dir / "inputs/boundaries/subregions.feather")

### Extract HUC12 within boundary
print("Reading source HUC12s...")

# data are in EPSG:4269 (NAD83 Geographic)
bnd_4326 = bnd_df.to_crs("EPSG:4326").geometry.values[0]

merged = None
for huc2 in SECAS_HUC2:
    df = (
        read_dataframe(
            src_dir
            / f"summary_units/huc12/WBD_{huc2:02}_HU2_GDB/WBD_{huc2:02}_HU2_GDB.gdb",
            layer="WBDHU12",
            use_arrow=True,
            mask=bnd_4326,
            columns=["huc12", "name"],
        )
        .rename(columns={"huc12": "id"})
        .to_crs(DATA_CRS)
    )

    if merged is None:
        merged = df

    else:
        merged = pd.concat([merged, df], ignore_index=True)

huc12 = merged.reset_index(drop=True)

# make sure data are valid
huc12["geometry"] = make_valid(huc12.geometry.values)

# calculate area
huc12["acres"] = shapely.area(huc12.geometry.values) * M2_ACRES

# for those that touch the edge of the region, drop any that are not >= 50% in
# raster input area.
tree = shapely.STRtree(huc12.geometry.values)
ix = tree.query(bnd, predicate="contains")

edge_df = huc12.loc[~huc12.id.isin(huc12.iloc[ix].id)].copy()
edge_df["overlap"] = (
    100
    * shapely.area(shapely.intersection(edge_df.geometry.values, bnd))
    / shapely.area(edge_df.geometry.values)
)

drop_ids = edge_df.loc[edge_df.overlap < 50].id

print(f"Dropping {len(drop_ids)} HUC12s that do not sufficiently overlap input areas")
huc12 = huc12.loc[~huc12.id.isin(drop_ids)].copy()

# extract geographic bounds
huc12_wgs84 = huc12.to_crs(GEO_CRS)
huc12 = huc12.join(huc12_wgs84.bounds)

huc12["value"] = np.arange(1, len(huc12) + 1).astype("uint16")

# get subregions list for each huc12
tree = shapely.STRtree(huc12.geometry.values)
left, right = tree.query(subregion_df.geometry.values, predicate="intersects")
pairs = (
    pd.Series(
        subregion_df.subregion.values.take(left),
        index=huc12.id.values.take(right),
        name="subregions",
    )
    .groupby(level=0)
    .apply(list)
)
huc12 = huc12.join(pairs, on="id")


### Marine units
print("Reading marine blocks...")

atl = read_dataframe(
    src_dir / "summary_units/marine_blocks/Atlantic.zip",
    columns=["PROT_NUMBE", "BLOCK_NUMB"],
).to_crs(DATA_CRS)
gulf = read_dataframe(
    src_dir / "summary_units/marine_blocks/Gulf_of_Mexico.zip",
    columns=["PROT_NUMBE", "BLOCK_NUMB"],
).to_crs(DATA_CRS)

marine = pd.concat([atl, gulf], ignore_index=True)
marine["id"] = marine.PROT_NUMBE.str.strip() + "-" + marine.BLOCK_NUMB.str.strip()
marine["name"] = (
    marine.PROT_NUMBE.str.strip() + ": Block " + marine.BLOCK_NUMB.str.strip()
)

# there are a couple blocks without proper names and 0 area; drop them
marine = marine[["id", "name", "geometry"]].dropna()

# some blocks have multiple parts, merge them
grouped = marine.groupby("id")

# save as DataFrame instead of GeoDataFrame for easier processing
marine = pd.DataFrame(
    grouped.geometry.apply(lambda g: g.values).apply(
        lambda g: shapely.union_all(g) if len(g) > 1 else g[0]
    )
).join(grouped.name.first())

# coerce all to MultiPolygons
ix = shapely.get_type_id(marine.geometry.values) == 3
marine.loc[ix, "geometry"] = marine.loc[ix].geometry.apply(
    lambda g: shapely.multipolygons([g])
)

marine = (
    gp.GeoDataFrame(marine, geometry="geometry", crs=DATA_CRS)
    .reset_index()
    .rename(columns={"index": "id"})
)


# select out those within the SE boundary
print("Selecting Marine blocks in region...")
tree = shapely.STRtree(marine.geometry.values)
ix = tree.query(bnd, predicate="intersects")
marine = marine.iloc[ix].copy().reset_index(drop=True)

marine["geometry"] = shapely.make_valid(marine.geometry.values)

marine["acres"] = shapely.area(marine.geometry.values) * M2_ACRES

# only keep those that are larger than 100 acres (arbitrary); others are slivers
marine = marine.loc[marine.acres > 100].dropna()

# only keep those that are >= 50% within region
tree = shapely.STRtree(marine.geometry.values)
ix = tree.query(bnd, predicate="contains")

edge_df = marine.loc[~marine.id.isin(marine.iloc[ix].id)].copy()
edge_df["overlap"] = (
    100
    * shapely.area(shapely.intersection(edge_df.geometry.values, bnd))
    / shapely.area(edge_df.geometry.values)
)

drop_ids = edge_df.loc[edge_df.overlap < 50].id

print(
    f"Dropping {len(drop_ids)} marine blocks that do not sufficiently overlap input areas"
)
marine = marine.loc[~marine.id.isin(drop_ids)].copy()

marine_wgs84 = marine.to_crs(GEO_CRS)
marine = marine.join(marine_wgs84.bounds)

marine["value"] = np.arange(1, len(marine) + 1).astype("uint16")

# get subregions for marine blocks
# NOTE: these are pre-filtered to only include marine subregions and avoid edge
# effects
marine_subregions = subregion_df.loc[subregion_df.marine]
tree = shapely.STRtree(marine.geometry.values)
left, right = tree.query(marine_subregions.geometry.values, predicate="intersects")
pairs = (
    pd.Series(
        marine_subregions.subregion.values.take(left),
        index=marine.id.values.take(right),
        name="subregions",
    )
    .groupby(level=0)
    .apply(list)
)
marine = marine.join(pairs, on="id")


# rasterize for summary unit analysis, use full extent
print("Rasterizing geometries")
tmp_huc12 = pd.DataFrame(huc12[["id", "value", "geometry"]].join(huc12.bounds))
tmp_huc12["geometry"] = tmp_huc12.geometry.values

tmp_marine = pd.DataFrame(marine[["id", "value", "geometry"]].join(marine.bounds))
tmp_marine["geometry"] = tmp_marine.geometry.values

with rasterio.open(blueprint_extent_filename) as src:
    extent_data = src.read(1)
    nodata = np.uint(src.nodata)

    data = rasterize(
        # create tuples of GeoJSON, value
        tmp_huc12.apply(lambda row: (to_dict(row.geometry), row.value), axis=1),
        (src.height, src.width),
        transform=src.transform,
        fill=0,  # values are >= 1
        # can use uint16 since there are ~25k watersheds
        dtype="uint16",
    )

    # calculate pixel count of each unit
    counts = np.zeros((len(tmp_huc12),), dtype="uint")
    outside_se_counts = np.zeros((len(tmp_huc12),), dtype="uint")
    for i, (_, row) in Bar("Rasterizing units", max=len(tmp_huc12)).iter(
        enumerate(tmp_huc12.iterrows())
    ):
        unit_window = get_window(src, (row.minx, row.miny, row.maxx, row.maxy))
        in_unit = data[unit_window.toslices()] == row.value
        counts[i] = in_unit.sum().astype("uint")

        outside_se = extent_data[unit_window.toslices()][in_unit] == nodata
        outside_se_counts[i] = outside_se.sum().astype("uint")

    huc12["pixels"] = counts
    cellsize = src.res[0] * src.res[0] * M2_ACRES
    huc12["rasterized_acres"] = counts * cellsize
    huc12["outside_se"] = outside_se_counts * cellsize

    outfilename = bnd_dir / "huc12.tif"
    write_raster(outfilename, data, transform=src.transform, crs=src.crs, nodata=0)
    add_overviews(outfilename)

    data = rasterize(
        tmp_marine.apply(lambda row: (to_dict(row.geometry), row.value), axis=1),
        (src.height, src.width),
        transform=src.transform,
        fill=0,  # values are >= 1
        # can use uint16 since there are ~35k blocks
        dtype="uint16",
    )

    # calculate pixel count of each unit
    counts = np.zeros((len(tmp_marine),), dtype="uint")
    outside_se_counts = np.zeros((len(tmp_marine),), dtype="uint")
    for i, (_, row) in Bar("Rasterizing units", max=len(tmp_marine)).iter(
        enumerate(tmp_marine.iterrows())
    ):
        unit_window = get_window(src, (row.minx, row.miny, row.maxx, row.maxy))
        in_unit = data[unit_window.toslices()] == row.value
        counts[i] = in_unit.sum().astype("uint")

        outside_se = extent_data[unit_window.toslices()][in_unit] == nodata
        outside_se_counts[i] = outside_se.sum().astype("uint")

    marine["pixels"] = counts
    cellsize = src.res[0] * src.res[0] * M2_ACRES
    marine["rasterized_acres"] = counts * cellsize
    marine["outside_se"] = outside_se_counts * cellsize

    outfilename = bnd_dir / "marine_blocks.tif"
    write_raster(outfilename, data, transform=src.transform, crs=src.crs, nodata=0)
    add_overviews(outfilename)

# Save in EPSG:5070 for analysis
huc12.to_feather(analysis_dir / "huc12.feather")
write_dataframe(huc12, bnd_dir / "huc12.fgb")
marine.to_feather(analysis_dir / "marine_blocks.feather")
write_dataframe(marine, bnd_dir / "marine_blocks.fgb")
