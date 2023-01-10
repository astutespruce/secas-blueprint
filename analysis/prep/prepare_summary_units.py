import os
from pathlib import Path
import warnings

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

# suppress warnings about writing to feather
warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


src_dir = Path("source_data")
data_dir = Path("data")
analysis_dir = data_dir / "inputs/summary_units"
bnd_dir = data_dir / "boundaries"  # GIS files output for reference
input_area_filename = data_dir / "inputs/boundaries/input_areas.tif"

if not analysis_dir.exists():
    os.makedirs(analysis_dir)

bnd_df = gp.read_feather(data_dir / "inputs/boundaries/se_boundary.feather")
bnd = bnd_df.geometry.values[0]

input_areas = gp.read_feather(data_dir / "inputs/boundaries/input_areas.feather")

### Extract HUC12 within boundary
print("Reading source HUC12s...")
merged = None
for huc2 in SECAS_HUC2:
    df = (
        read_dataframe(
            src_dir
            / f"summary_units/huc12/WBD_{huc2:02}_HU2_GDB/WBD_{huc2:02}_HU2_GDB.gdb",
            layer="WBDHU12",
        )[["huc12", "name", "geometry"]]
        .rename(columns={"huc12": "id"})
        .to_crs(DATA_CRS)
    )

    if merged is None:
        merged = df

    else:
        merged = pd.concat([merged, df], ignore_index=True)

huc12 = merged.reset_index(drop=True)


# select HUC12s within the SE states
print("Selecting HUC12s in region...")
tree = shapely.STRtree(huc12.geometry.values)
ix = tree.query(bnd, predicate="intersects")
huc12 = huc12.iloc[ix].copy().reset_index(drop=True)

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

# Areas where HUC2 == 21 are in Puerto Rico, everwhere else has Base Blueprint
huc12.loc[huc12.id.str.startswith("21"), "input_id"] = "car"
huc12.input_id = huc12.input_id.fillna("base")

huc12["value"] = np.arange(1, len(huc12) + 1).astype("uint16")

# rasterize for summary unit analysis, use full extent
print("Rasterizing geometries")
tmp = pd.DataFrame(huc12[["id", "value", "geometry"]].join(huc12.bounds))
tmp["geometry"] = tmp.geometry.values

with rasterio.open(input_area_filename) as src:
    input_areas_data = src.read(1)
    nodata = np.uint(src.nodata)

    # create tuples of GeoJSON, value
    shapes = tmp.apply(lambda row: (to_dict(row.geometry), row.value), axis=1)

    data = rasterize(
        shapes,
        (src.height, src.width),
        transform=src.transform,
        fill=0,  # values are >= 1
        # can use uint16 since there are ~25k watersheds
        dtype="uint16",
    )

    # calculate pixel count of each unit
    counts = np.zeros((len(tmp),), dtype="uint")
    outside_se_counts = np.zeros((len(tmp),), dtype="uint")
    for i, (_, row) in Bar("Rasterizing units", max=len(tmp)).iter(
        enumerate(tmp.iterrows())
    ):
        unit_window = get_window(src, (row.minx, row.miny, row.maxx, row.maxy))
        in_unit = data[unit_window.toslices()] == row.value
        counts[i] = in_unit.sum().astype("uint")

        outside_se = input_areas_data[unit_window.toslices()][in_unit] == nodata
        outside_se_counts[i] = outside_se.sum().astype("uint")

    huc12["pixels"] = counts
    cellsize = src.res[0] * src.res[0] * M2_ACRES
    huc12["rasterized_acres"] = counts * cellsize
    huc12["outside_se"] = outside_se_counts * cellsize

    outfilename = bnd_dir / "huc12.tif"
    write_raster(outfilename, data, transform=src.transform, crs=src.crs, nodata=0)

    add_overviews(outfilename)


# Save in EPSG:5070 for analysis
huc12.to_feather(analysis_dir / "huc12.feather")
write_dataframe(huc12, bnd_dir / "huc12.fgb")

###############################################################################

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

marine = pd.concat([atl, gulf], ignore_index=True)
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

# boundary between base blueprint and FL marine is at border of marine blocks
tree = shapely.STRtree(marine.geometry.values)
left, right = tree.query(input_areas.geometry.values, predicate="intersects")

tmp = pd.DataFrame(
    {
        "input_id": input_areas.id.values.take(left),
        "input_area": input_areas.geometry.values.take(left),
        "block": marine.geometry.values.take(right),
        "block_id": marine.id.values.take(right),
    }
)

count = tmp.groupby("block_id").size()
ids = count[count > 1].index
ix = tmp.block_id.isin(ids)

# use centroids to determine which side
tmp.loc[ix, "center"] = shapely.centroid(tmp.loc[ix].block.values)
shapely.prepare(tmp.input_area.values)
tmp.loc[ix, "contains"] = shapely.contains(tmp.loc[ix].input_area, tmp.loc[ix].center)
tmp.contains = tmp.contains.fillna(True)

tmp = tmp.loc[tmp.contains, ["input_id", "block_id"]].set_index("block_id")
marine = marine.join(tmp, on="id")

marine["value"] = np.arange(1, len(marine) + 1).astype("uint16")

# rasterize for summary unit analysis, use full extent
print("Rasterizing geometries")
tmp = pd.DataFrame(marine[["id", "value", "geometry"]].join(marine.bounds))
tmp["geometry"] = tmp.geometry.values

with rasterio.open(input_area_filename) as src:
    input_areas_data = src.read(1)
    nodata = np.uint(src.nodata)

    # create tuples of GeoJSON, value
    shapes = tmp.apply(lambda row: (to_dict(row.geometry), row.value), axis=1)

    data = rasterize(
        shapes,
        (src.height, src.width),
        transform=src.transform,
        fill=0,  # values are >= 1
        # can use uint16 since there are ~35k blocks
        dtype="uint16",
    )

    # calculate pixel count of each unit
    counts = np.zeros((len(tmp),), dtype="uint")
    outside_se_counts = np.zeros((len(tmp),), dtype="uint")
    for i, (_, row) in enumerate(tmp.iterrows()):
        unit_window = get_window(src, (row.minx, row.miny, row.maxx, row.maxy))
        in_unit = data[unit_window.toslices()] == row.value
        counts[i] = in_unit.sum().astype("uint")

        outside_se = input_areas_data[unit_window.toslices()][in_unit] == nodata
        outside_se_counts[i] = outside_se.sum().astype("uint")

    marine["pixels"] = counts
    cellsize = src.res[0] * src.res[0] * M2_ACRES
    marine["rasterized_acres"] = counts * cellsize
    marine["outside_se"] = outside_se_counts * cellsize

    outfilename = bnd_dir / "marine_blocks.tif"
    write_raster(outfilename, data, transform=src.transform, crs=src.crs, nodata=0)

    add_overviews(outfilename)


# Save in EPSG:5070 for analysis
marine.to_feather(analysis_dir / "marine_blocks.feather")
write_dataframe(marine, bnd_dir / "marine_blocks.fgb")
