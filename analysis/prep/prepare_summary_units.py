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

warnings.filterwarnings("ignore", message=".*polygon with more than 100 parts.*")


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
left, right = shapely.STRtree(huc12.geometry.values).query(
    subregion_df.geometry.values, predicate="intersects"
)
subregions = (
    pd.DataFrame(
        {
            "subregions": subregion_df.subregion.values.take(left),
            "regions": subregion_df.region.values.take(left),
        },
        index=huc12.id.values.take(right),
    )
    .groupby(level=0)
    .agg({"subregions": "unique", "regions": "unique"})
)

huc12 = huc12.join(subregions, on="id")


### Marine units
print("Reading marine hexes...")

conus = read_dataframe(
    src_dir
    / "summary_units/hex/EPA_Hexagons_40km_Unioned_w_GoMMAPPS_Hegagons_40km.shp",
    columns=["HEXID", "HEXID_1"],
    use_arrow=True,
).to_crs(DATA_CRS)
conus["id"] = conus[["HEXID", "HEXID_1"]].max(axis=1)
conus = conus.drop(columns=["HEXID", "HEXID_1"])

caribbean = read_dataframe(
    src_dir / "summary_units/hex/VIPR_Hexagons_DoNOTexactlyMatchEPAHexes.shp",
    columns=[],
    use_arrow=True,
).to_crs(DATA_CRS)
caribbean["id"] = caribbean.index + conus.id.max() + 1

marine = pd.concat([conus, caribbean], ignore_index=True)
marine["id"] = marine.id.astype(str)
marine["name"] = "Hex ID: " + marine.id


# select out those within the marine subregions / Caribbean
hex_subregions = subregion_df.loc[subregion_df.region.isin(["marine", "caribbean"])]
tree = shapely.STRtree(marine.geometry.values)
ix = np.unique(tree.query(hex_subregions.geometry.values, predicate="intersects")[1])
marine = marine.iloc[ix].copy().reset_index(drop=True)

marine["geometry"] = shapely.make_valid(marine.geometry.values)

# Find and dissolve overlapping HUC12s
print("Dissolving HUC12s")
tree = shapely.STRtree(marine.geometry.values)
left, right = tree.query(huc12.geometry.values, predicate="intersects")
huc12_bnd = shapely.polygons(
    shapely.get_exterior_ring(
        shapely.get_parts(shapely.union_all(huc12.geometry.values.take(left)))
    )
)

# drop any that are completely contained
contained = tree.query(huc12_bnd, predicate="contains_properly")[1]
ix = np.setdiff1d(np.arange(len(marine)), contained)
marine = marine.take(ix)

marine["acres"] = shapely.area(marine.geometry.values) * M2_ACRES

# cut any that intersect HUC12s to fall outside HUC12s
huc12_bnd = shapely.multipolygons(huc12_bnd)
tree = shapely.STRtree(marine.geometry.values)
clip_ix = tree.query(huc12_bnd, predicate="intersects")
keep_ix = np.setdiff1d(np.arange(len(marine)), clip_ix)

print("Clipping marine hexes to fall outside HUC12s")
clipped = marine.take(clip_ix)
clipped["geometry"] = shapely.difference(clipped.geometry.values, huc12_bnd)
clipped["acres"] = shapely.area(clipped.geometry.values) * M2_ACRES

# only keep those still within Blueprint extent
tree = shapely.STRtree(clipped.geometry.values)
ix = tree.query(bnd, predicate="intersects")
clipped = clipped.take(ix)

tree = shapely.STRtree(clipped.geometry.values)
ix = clipped.index.values.take(tree.query(bnd, predicate="contains_properly"))
clipped["overlap_acres"] = 0.0
clipped.loc[ix, "overlap_acres"] = clipped.loc[ix].acres

ix = clipped.overlap_acres == 0
clipped.loc[ix, "overlap_acres"] = (
    shapely.area(shapely.intersection(clipped.loc[ix].geometry.values, bnd)) * M2_ACRES
)

# only keep those larger than a 30x30 m pixel
clipped = clipped.loc[clipped.overlap_acres >= 0.222].drop(columns=["overlap_acres"])

marine = pd.concat([marine.take(keep_ix), clipped], ignore_index=True).reset_index(
    drop=True
)

# coerce all to multi
ix = shapely.get_type_id(marine.geometry.values) == 3
marine.loc[ix, "geometry"] = marine.loc[ix].geometry.apply(
    lambda g: shapely.multipolygons([g])
)

marine_wgs84 = marine.to_crs(GEO_CRS)
marine = marine.join(marine_wgs84.bounds)

marine["value"] = np.arange(1, len(marine) + 1).astype("uint16")

# get subregions for marine hexes
# NOTE: these are pre-filtered to only include marine / Caribbean subregions and
# avoid edge effects
tree = shapely.STRtree(marine.geometry.values)
left, right = tree.query(hex_subregions.geometry.values, predicate="intersects")
pairs = (
    pd.Series(
        hex_subregions.subregion.values.take(left),
        index=marine.id.values.take(right),
        name="subregions",
    )
    .groupby(level=0)
    .apply(list)
)
marine = marine.join(pairs, on="id")


# rasterize for summary unit analysis, use full extent
tmp_huc12 = pd.DataFrame(huc12[["id", "value", "geometry"]].join(huc12.bounds))
tmp_huc12["geometry"] = tmp_huc12.geometry.values

tmp_marine = pd.DataFrame(marine[["id", "value", "geometry"]].join(marine.bounds))
tmp_marine["geometry"] = tmp_marine.geometry.values

with rasterio.open(blueprint_extent_filename) as src:
    extent_data = src.read(1)
    nodata = np.uint(src.nodata)

    print("Rasterizing HUC12s")
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

    print("Rasterizing marine hexes")
    data = rasterize(
        tmp_marine.apply(lambda row: (to_dict(row.geometry), row.value), axis=1),
        (src.height, src.width),
        transform=src.transform,
        fill=0,  # values are >= 1
        # can use uint16 since there are ~32k hexes
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

    outfilename = bnd_dir / "marine_hex.tif"
    write_raster(outfilename, data, transform=src.transform, crs=src.crs, nodata=0)
    add_overviews(outfilename)

# Save in EPSG:5070 for analysis
huc12.to_feather(analysis_dir / "huc12.feather")
write_dataframe(huc12, bnd_dir / "huc12.fgb")
marine.to_feather(analysis_dir / "marine_hex.feather")
write_dataframe(marine, bnd_dir / "marine_hex.fgb")
