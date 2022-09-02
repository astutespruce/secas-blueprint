from itertools import product
import json
import math
from pathlib import Path
import re
import subprocess
from time import time

import rasterio
from rasterio.features import geometry_mask, dataset_features
import pandas as pd
import numpy as np
import pygeos as pg
import geopandas as gp
from pyarrow.csv import read_csv, ReadOptions
from pyogrio import (
    read_dataframe,
    write_dataframe,
    set_gdal_config_options,
    list_layers,
    read_bounds,
    read_info,
)


from analysis.constants import (
    DATA_CRS,
    MASK_FACTOR,
    SLR_YEARS,
    SLR_PROJ_COLUMNS,
    SLR_LEGEND,
)
from analysis.lib.colors import hex_to_uint8
from analysis.lib.io import write_raster
from analysis.lib.pygeos_util import (
    to_dict_all,
)
from analysis.lib.raster import add_overviews, create_lowres_mask


set_gdal_config_options({"OGR_ORGANIZE_POLYGONS": "ONLY_CCW"})

BLUEPRINT_RES = 30
SLR_RES = 15
MIN_AREA = SLR_RES * SLR_RES
LEVELS = list(range(0, 11))  # 0-10 feet inundation
NODATA = 255


def drop_all_holes(geometries):
    """Return geometries, dropping any holes.

    Parameters
    ----------
    geometries : ndarray of pygeos geometries

    Returns
    -------
    ndarray of pygeos geometries
    """
    parts, index = pg.get_parts(geometries, return_index=True)
    parts = pg.polygons(pg.get_exterior_ring(parts))

    return (
        pd.DataFrame({"geometry": parts}, index=index)
        .groupby(level=0)
        .geometry.apply(np.array)
        .apply(lambda g: pg.multipolygons(g) if len(g) > 1 else g[0])
        .values
    )


def get_holes(geometries):
    """Extract the holes from geometries and return as new polygons

    Parameters
    ----------
    geometries : ndarray of pygeos geometries

    Returns
    -------
    tuple of ndarray of geomtries, original index
    """
    parts, index = pg.get_parts(geometries, return_index=True)
    num_rings = pg.get_num_interior_rings(parts)

    ix = num_rings > 0
    index = np.arange(len(parts))[ix]
    out_index = np.repeat(index, num_rings[ix])

    holes = []

    for i in index:
        holes.extend(
            pg.get_interior_ring(parts[i], range(pg.get_num_interior_rings(parts[i])))
        )

    return pg.polygons(holes), out_index


def rasterize_depth_polygons(gdb, layer, width, height, transform):
    """Rasterize polygons to pixels according to the dimensions and transform
    provided.

    Parameters
    ----------
    gdb : str or Path
        Geodatabase path
    layer : str
        layer name
    width : int
    height : int
    transform : affine.Affine

    Returns
    -------
    ndarray of shape(height, width) with bool values
        values are True inside polygons
    """

    print(f"Reading and reprojecting {layer}")
    df = (
        read_dataframe(gdb, layer=layer, columns=[], force_2d=True)
        .explode(index_parts=False)
        .to_crs(DATA_CRS)
    )

    area = pg.area(df.geometry.values.data)
    total_area = area.sum()

    # Drop any polygons that are too small
    ix = area >= MIN_AREA
    df = df.loc[ix].copy()
    print(
        f"Dropped {(~ix).sum():,} polygons that are < {MIN_AREA} m2; now have {len(df):,} polygons and {100 * area[ix].sum() / total_area:.2f}% of original area"
    )

    print("Rasterizing.... (this might take a while)")

    # Write outer rings of polygons and then holes separately because this is
    # faster, though less precise (some holes may rasterize over the edge of the
    # original rings, yielding bays)
    polygons = drop_all_holes(df.geometry.values.data)
    fill_mask = geometry_mask(
        to_dict_all(polygons),
        out_shape=(height, width),
        transform=transform,
        invert=True,
    )

    holes = get_holes(df.geometry.values.data)[0]
    ix = pg.area(holes) >= MIN_AREA
    holes_mask = geometry_mask(
        to_dict_all(holes[ix]), out_shape=(height, width), transform=transform
    )

    fill_mask[holes_mask == 0] = 0

    return fill_mask


bnd_dir = Path("data/boundaries")
src_dir = Path("source_data/slr")
tmp_dir = src_dir / "rasterized"
tmp_dir.mkdir(parents=True, exist_ok=True)

out_dir = Path("data/inputs/threats/slr")
out_dir.mkdir(parents=True, exist_ok=True)

start = time()


colormap = {int(e["label"]): hex_to_uint8(e["color"]) + (255,) for e in SLR_LEGEND}


# use the Base Blueprint extent grid to derive the master offset coordinates
# so that everything is correctly aligned
# NOTE: SLR data extends beyond the base blueprint extent, don't use it for masking
with rasterio.open(bnd_dir / "base_blueprint_extent.tif") as src:
    align_ul = np.take(src.transform, [2, 5]).tolist()

for gdb in sorted(src_dir.glob("*slr_data_dist/*.gdb")):
    chunk_start = time()

    outfilename = (
        tmp_dir
        / f"{gdb.stem.replace('_slr_final_dist', '')}_{LEVELS[0]}_{LEVELS[-1]}ft.tif"
    )

    if outfilename.exists():
        print(f"Skipping {gdb} (outputs already exist)")
        continue

    print(f"\n\n--------- Processing {gdb} ------------")

    # ignore the low-lying areas, gather the SLR depth layers in order of descending
    # depth so that we stack from highest to lowest
    slr_layers = sorted(
        [l[0] for l in list_layers(gdb) if "_slr_" in l[0]],
        key=lambda l: int(re.findall("\d+(?=ft)", l)[0]),
        reverse=True,
    )

    # calculate the outer bounds and dimensions
    print("Calculating outer bounds")
    xmin = math.inf
    ymin = math.inf
    xmax = -math.inf
    ymax = -math.inf
    for layer in slr_layers:
        # WARNING: CRS is not consistent across the suite
        crs = read_info(gdb, layer)["crs"]
        bounds = (
            gp.GeoDataFrame(geometry=pg.box(*read_bounds(gdb, layer)[1]), crs=crs)
            .to_crs(DATA_CRS)
            .total_bounds
        )
        xmin = min(xmin, bounds[0])
        ymin = min(ymin, bounds[1])
        xmax = max(xmax, bounds[2])
        ymax = max(ymax, bounds[3])

    # snap the origin of this grid to align_ul
    xmin = (math.floor((xmin - align_ul[0]) / SLR_RES) * SLR_RES) + align_ul[0]
    ymax = align_ul[1] - (math.ceil((align_ul[1] - ymax) / SLR_RES) * SLR_RES)
    transform = (SLR_RES, 0, xmin, 0, -SLR_RES, ymax)

    width = math.ceil((xmax - xmin) / SLR_RES)
    height = math.ceil((ymax - ymin) / SLR_RES)

    out = np.ones((height, width), dtype="uint8") * np.uint8(NODATA)

    for layer in slr_layers:
        depth = np.uint8(re.findall("\d+(?=ft)", layer)[0])
        mask = rasterize_depth_polygons(gdb, layer, width, height, transform)
        depth = mask.astype("uint8") * depth

        out = np.where(mask, depth, out)

        # DEBUG:
        # write_raster(
        #     f"/tmp/{layer}.tif",
        #     mask.astype("uint8"),
        #     transform=transform,
        #     crs=DATA_CRS,
        #     nodata=0,
        # )

    print("Writing combined depth raster")
    # Output values are 0 - 10 and NODATA = 255
    write_raster(
        outfilename,
        out,
        transform=transform,
        crs=DATA_CRS,
        nodata=NODATA,
    )

    print("Adding overviews")
    add_overviews(outfilename)

    print(f"Completed in {time() - chunk_start:.2f}s")


files = list(tmp_dir.glob("*.tif"))

### Build VRT using GDAL CLI
print("Building VRT")
vrt_filename = tmp_dir / "slr.vrt"
ret = subprocess.run(
    [
        "gdalbuildvrt",
        "-overwrite",
        "-resolution",
        "user",
        "-tr",
        str(SLR_RES),
        str(SLR_RES),
        str(vrt_filename),
    ]
    + files
)
ret.check_returncode()


## Combine into a single raster
print("Combining into single raster")
outfilename = out_dir / "slr.tif"
with rasterio.open(vrt_filename) as src:
    data = src.read(1)
    write_raster(outfilename, data, transform=src.transform, crs=src.crs, nodata=NODATA)

    with rasterio.open(outfilename, "r+") as out:
        out.write_colormap(1, colormap)

    add_overviews(outfilename)

print("Creating SLR mask")
create_lowres_mask(
    outfilename,
    out_dir / "slr_mask.tif",
    factor=MASK_FACTOR * 2,  # convert to 480m to match others, since resolution is 15m
    ignore_zero=False,
)

### Extract a boundary polygon of everywhere that we extracted SLR data according
# to the low resolution mask
with rasterio.open(out_dir / "slr_mask.tif") as src:
    f = dataset_features(src, 1, geographic=False)
    polys = drop_all_holes(pg.from_geojson([json.dumps(p["geometry"]) for p in f]))

slr_mask = gp.GeoDataFrame(geometry=polys, crs=DATA_CRS)
slr_mask.to_feather(out_dir / "extracted_slr_bounds.feather")
write_dataframe(slr_mask, tmp_dir / "extracted_slr_bounds.fgb")

### Create 1-degree grid cell dataset from NOAA CSV
print("Extracting NOAA SLR projections at 1-degree cell level")
df = (
    read_csv(
        src_dir / "Sea_Level_Rise_Datasets_2022/SLR_TF U.S. Sea Level Projections.csv",
        read_options=ReadOptions(skip_rows=17),
    )
    .select(
        [
            "PSMSL Site",
            "Lat",
            "Long",
            "Regional Classification",
            "Scenario",
            "Offset 2000 to 2005 (cm)",
            "RSL2020 (cm)",
            "RSL2030 (cm)",
            "RSL2040 (cm)",
            "RSL2050 (cm)",
            "RSL2060 (cm)",
            "RSL2070 (cm)",
            "RSL2080 (cm)",
            "RSL2090 (cm)",
            "RSL2100 (cm)",
        ]
    )
    .to_pandas()
    .dropna()
    .rename(
        columns={
            "Regional Classification": "Region",
            "Offset 2000 to 2005 (cm)": "offset",
            "RSL2020 (cm)": "2020",
            "RSL2030 (cm)": "2030",
            "RSL2040 (cm)": "2040",
            "RSL2050 (cm)": "2050",
            "RSL2060 (cm)": "2060",
            "RSL2070 (cm)": "2070",
            "RSL2080 (cm)": "2080",
            "RSL2090 (cm)": "2090",
            "RSL2100 (cm)": "2100",
        }
    )
)


# Only keep those that are 1 degree cells (others are tide guages) that overlap
# with the SECAS region
# Only keep the 50th percentile of each scenario
df = df.loc[
    df["PSMSL Site"].str.startswith("grid")
    & df["Region"].isin(
        ["Northeast", "Southeast", "Western Gulf", "Eastern Gulf", "Caribbean"]
    )
    & df.Scenario.str.contains("MED")
].set_index("PSMSL Site")

# Apply the 2000-2005 offset to the project values
decade_cols = [str(y) for y in SLR_YEARS]
for col in decade_cols:
    df[col] += df.offset

# Convert cm to feet
df[decade_cols] = df[decade_cols] * 0.0328084

# Transform scenarios to match NOAA docs (values are GMSL rise in meters)
scenarios = {
    "0.3": "l",  # "Low",
    "0.5": "il",  # "Intermediate-Low",
    "1.0": "i",  # "Intermediate",
    "1.5": "ih",  # "Intermediate-High",
    "2.0": "h",  # "High",
}

df["Scenario"] = df.Scenario.apply(lambda x: x.split(" - ")[0]).map(scenarios)

# Transform scenarios to columns per decade
df = (
    df.loc[df.Scenario == "l", ["Region", "Lat", "Long"] + decade_cols]
    .rename(columns={c: f"{c}_l" for c in decade_cols})
    .join(
        df.loc[df.Scenario == "il", decade_cols].rename(
            columns={c: f"{c}_il" for c in decade_cols}
        )
    )
    .join(
        df.loc[df.Scenario == "i", decade_cols].rename(
            columns={c: f"{c}_i" for c in decade_cols}
        )
    )
    .join(
        df.loc[df.Scenario == "ih", decade_cols].rename(
            columns={c: f"{c}_ih" for c in decade_cols}
        )
    )
    .join(
        df.loc[df.Scenario == "h", decade_cols].rename(
            columns={c: f"{c}_h" for c in decade_cols}
        )
    )
    .reset_index(drop=True)
)


cells = pg.box(*np.array([df.Long - 0.5, df.Lat - 0.5, df.Long + 0.5, df.Lat + 0.5]))

df = gp.GeoDataFrame(
    df.drop(columns=["Lat", "Long"]), geometry=cells, crs="EPSG:4326"
).to_crs(DATA_CRS)

# only keep those that intersect the areas of extracted SLR (some cells are inland / offshore)
tree = pg.STRtree(df.geometry.values.data)
ix = np.unique(
    tree.query_bulk(slr_mask.geometry.values.data, predicate="intersects")[1]
)
df = df.take(ix).reset_index(drop=True)


# reorder columns in ascending decade and scenario

df = df[["geometry", "Region"] + SLR_PROJ_COLUMNS]

df.to_feather(out_dir / "noaa_1deg_cells.feather")

# DEBUG
write_dataframe(df, tmp_dir / "noaa_1deg_cells.fgb")


print(f"All done in {time() - start:.2f}s")
