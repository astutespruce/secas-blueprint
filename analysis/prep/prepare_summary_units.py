import os
from pathlib import Path
import warnings

import geopandas as gp
import pandas as pd
from pyogrio import read_dataframe, write_dataframe
import pygeos as pg
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window

from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES, SECAS_HUC2
from analysis.lib.geometry import make_valid, to_dict
from analysis.lib.raster import write_raster, add_overviews

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
bnd = bnd_df.geometry.values.data[0]

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
tree = pg.STRtree(huc12.geometry.values.data)
ix = tree.query(bnd, predicate="intersects")
huc12 = huc12.iloc[ix].copy().reset_index(drop=True)

# make sure data are valid
huc12["geometry"] = make_valid(huc12.geometry.values.data)

# calculate area
huc12["acres"] = (pg.area(huc12.geometry.values.data) * M2_ACRES).round().astype("uint")

# for those that touch the edge of the region, drop any that are not >= 50% in
# raster input area.
tree = pg.STRtree(huc12.geometry.values.data)
ix = tree.query(bnd, predicate="contains")

edge_df = huc12.loc[~huc12.id.isin(huc12.iloc[ix].id)].copy()
edge_df["overlap"] = (
    100
    * pg.area(pg.intersection(edge_df.geometry.values.data, bnd))
    / pg.area(edge_df.geometry.values.data)
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

# Save in EPSG:5070 for analysis
huc12.to_feather(analysis_dir / "huc12.feather")
write_dataframe(huc12, bnd_dir / "huc12.fgb")


# rasterize for summary unit analysis, use full extent
print("Rasterizing geometries")
tmp = pd.DataFrame(huc12)
tmp["geometry"] = tmp.geometry.values.data
tmp["value"] = tmp.index.values + 1

with rasterio.open(input_area_filename) as src:
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

    outfilename = bnd_dir / "huc12.tif"
    write_raster(outfilename, data, transform=src.transform, crs=src.crs, nodata=0)

    add_overviews(outfilename)


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

# only keep those that are >= 50% within region
tree = pg.STRtree(marine.geometry.values.data)
ix = tree.query(bnd, predicate="contains")

edge_df = marine.loc[~marine.id.isin(marine.iloc[ix].id)].copy()
edge_df["overlap"] = (
    100
    * pg.area(pg.intersection(edge_df.geometry.values.data, bnd))
    / pg.area(edge_df.geometry.values.data)
)

drop_ids = edge_df.loc[edge_df.overlap < 50].id

print(
    f"Dropping {len(drop_ids)} marine blocks that do not sufficiently overlap input areas"
)
marine = marine.loc[~marine.id.isin(drop_ids)].copy()

marine_wgs84 = marine.to_crs(GEO_CRS)
marine = marine.join(marine_wgs84.bounds)

# boundary between base blueprint and FL marine is at border of marine blocks
tree = pg.STRtree(marine.geometry.values.data)
left, right = tree.query_bulk(input_areas.geometry.values.data, predicate="intersects")

tmp = pd.DataFrame(
    {
        "input_id": input_areas.id.values.take(left),
        "input_area": input_areas.geometry.values.data.take(left),
        "block": marine.geometry.values.data.take(right),
        "block_id": marine.id.values.take(right),
    }
)

count = tmp.groupby("block_id").size()
ids = count[count > 1].index
ix = tmp.block_id.isin(ids)

# use centroids to determine which side
tmp.loc[ix, "center"] = pg.centroid(tmp.loc[ix].block.values)
pg.prepare(tmp.input_area.values)
tmp.loc[ix, "contains"] = pg.contains(tmp.loc[ix].input_area, tmp.loc[ix].center)
tmp.contains = tmp.contains.fillna(True)

tmp = tmp.loc[tmp.contains, ["input_id", "block_id"]].set_index("block_id")
marine = marine.join(tmp, on="id")

# Save in EPSG:5070 for analysis
marine.to_feather(analysis_dir / "marine_blocks.feather")
write_dataframe(marine, bnd_dir / "marine_blocks.fgb")


# rasterize for summary unit analysis, use full extent
print("Rasterizing geometries")
tmp = pd.DataFrame(marine)
tmp["geometry"] = tmp.geometry.values.data
tmp["value"] = tmp.index.values + 1

with rasterio.open(input_area_filename) as src:
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

    outfilename = bnd_dir / "marine_blocks.tif"
    write_raster(outfilename, data, transform=src.transform, crs=src.crs, nodata=0)

    add_overviews(outfilename)
