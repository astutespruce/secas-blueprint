from pathlib import Path

import geopandas as gp
import pandas as pd
from pyogrio import read_dataframe
import rasterio
import shapely

from analysis.constants import M2_ACRES, OWNERSHIP
from analysis.lib.raster import summarize_raster_by_units_grid
from analysis.lib.stats.summary_units import read_unit_from_feather


src_dir = Path("data/inputs/boundaries")
filename = src_dir / "ownership.tif"
mask_filename = src_dir / "ownership_mask.tif"
boundary_filename = src_dir / "ownership.fgb"
columns = ["name", "owner"]

BINS = range(0, len(OWNERSHIP))
LABELS = {e["value"]: e["label"] for e in OWNERSHIP}


def extract_ownership(df, use_bbox=False):
    """Extract intersection with ownership data

        Parameters
        ----------
    df : GeoDataFrame
        area of interest
    use_bbox : bool, optional (default: False)
        if True, will filter ownership by bounds of df when reading features

        Returns
        -------
        GeoDataFrame
            indexed on index of df (multiple records per index value); includes
            geometry field with the geometric intersection and acres calculated from
            that field

    """

    index_name = df.index.name or "index"

    # Note: no need to explode(), geometries are already single-part
    ownership = read_dataframe(
        boundary_filename,
        columns=columns + ["geometry"],
        bbox=tuple(df.total_bounds) if use_bbox else None,
        # TODO: enable use_arrow once fixed in pyogrio
        use_arrow=not use_bbox,
    )

    if len(ownership) == 0:
        return None

    # find all ownership polygons that intersect any part of the AOI
    tmp = df.explode(ignore_index=False, index_parts=False)
    left, right = shapely.STRtree(ownership.geometry.values).query(
        tmp.geometry.values, predicate="intersects"
    )

    # no intersections
    if len(left) == 0:
        return None

    pairs = gp.GeoDataFrame(
        {
            "geometry": tmp.geometry.values.take(left),
            "index_right": ownership.index.values.take(right),
            "geometry_right": ownership.geometry.values.take(right),
        },
        index=pd.Index(tmp.index.values.take(left), name=index_name),
        geometry="geometry",
        crs=df.crs,
    )
    shapely.prepare(pairs.geometry.values)
    shapely.prepare(pairs.geometry_right.values)

    # if left completely contains right, the right geometry is the intersection
    left_contains = shapely.contains_properly(
        pairs.geometry.values, pairs.geometry_right.values
    )
    pairs.loc[left_contains, "geometry"] = pairs.loc[
        left_contains
    ].geometry_right.values

    # if right completely contains the left, the left (geometry) are the intersection
    right_contains = ~left_contains & shapely.contains_properly(
        pairs.geometry.values, pairs.geometry_right.values
    )

    # any that aren't contained in either direction must be intersected
    ix = ~(left_contains | right_contains)
    pairs.loc[ix, "geometry"] = shapely.intersection(
        pairs.loc[ix].geometry.values, pairs.loc[ix].geometry_right.values
    )

    # explode and only keep polygons
    pairs = pairs.drop(columns=["geometry_right"]).explode(
        ignore_index=False, index_parts=False
    )
    pairs = pairs.loc[shapely.get_type_id(pairs.geometry.values) == 3]

    if len(pairs) == 0:
        return None

    # aggregate to multipolygons based on ownership columns
    ownership = gp.GeoDataFrame(
        pairs.join(ownership[columns], on="index_right")
        .groupby([index_name] + columns)
        .agg({"geometry": shapely.multipolygons})
        .reset_index()
        .set_index(index_name),
        geometry="geometry",
        crs=df.crs,
    )

    ownership["acres"] = shapely.area(ownership.geometry.values) * M2_ACRES

    return ownership


def summarize_ownership_in_aoi(rasterized_geometry, df):
    """Calculate area in protected areas

    Parameters
    ----------
    rasterized_geometry : RasterizedGeometry
    df : GeoDataFrame
        area of interest

    Returns
    -------
    dict or None
        {
            "entries": [{"value": <>, "label": <>, "acres": <>, "percent": <>}, ...],
            "total_ownership_acres": <total_acres>,
            "outside_ownership_acres": <nodata acres>,
            "outside_ownership_percent": <nodata percent>,
            "protected_areas": [{"name": <>, "owner": <>, "acres": <>}],
            "num_protected_areas": <number of protected areas>
        }
    """

    # prescreen to make sure data are present
    with rasterio.open(mask_filename) as src:
        if not rasterized_geometry.detect_data(src):
            return None

    with rasterio.open(filename) as src:
        ownership_acres = rasterized_geometry.get_acres_by_bin(src, bins=BINS)

    total_acres = ownership_acres.sum()
    nodata_acres = (
        rasterized_geometry.acres - rasterized_geometry.outside_se_acres - total_acres
    )

    if nodata_acres < 1e-6:
        nodata_acres = 0

    entries = [
        {
            "value": i,
            "label": LABELS[i],
            "acres": acres.item(),
            "percent": (100 * acres / rasterized_geometry.acres).item(),
        }
        for i, acres in enumerate(ownership_acres)
    ]

    protected_areas = []
    num_protected_areas = 0

    ownership_records = extract_ownership(df, use_bbox=True)
    if ownership_records is not None:
        # only list areas >= 1 acre
        by_area = (
            ownership_records.loc[ownership_records.acres >= 1][
                ["name", "owner", "acres"]
            ]
            .groupby(by=["name", "owner"])
            .acres.sum()
            .astype("float32")
            .round()
            .reset_index()
            .sort_values(by="acres", ascending=False)
        ).head(25)
        by_area.loc[by_area.name == "", "name"] = "Unknown name"

        protected_areas = by_area.to_dict(orient="records")
        num_protected_areas = len(by_area)

    return {
        "entries": entries,
        "total_ownership_acres": total_acres,
        "outside_ownership_acres": nodata_acres,
        "outside_ownership_percent": 100 * nodata_acres / rasterized_geometry.acres,
        "protected_areas": protected_areas,
        "num_protected_areas": num_protected_areas,
    }


def summarize_ownership_by_units(df, units_grid, out_dir):
    """Calculate overlap with ownership and protection

    Parameters
    ----------
    df : GeoDataFrame
        contains unit boundaries, indexed by id
    units_grid : SummaryUnitGrid instance
    out_dir : str
    """
    print("Calculating overlap with land ownership and protection")

    if (
        not len(df.columns.intersection({"value", "rasterized_acres", "outside_se"}))
        == 3
    ):
        raise ValueError(
            "GeoDataFrame for summary must include value, rasterized_acres, outside_se columns"
        )

    with rasterio.open(filename) as value_dataset:
        cellsize = value_dataset.res[0] * value_dataset.res[0] * M2_ACRES

        ownership_acres = (
            summarize_raster_by_units_grid(
                df,
                units_grid,
                value_dataset,
                bins=BINS,
                progress_label="Summarizing ownership",
            )
            * cellsize
        )

    total_acres = ownership_acres.sum(axis=1)
    nodata_acres = df.rasterized_acres - df.outside_se - total_acres
    nodata_acres[nodata_acres < 1e-6] = 0

    ownership = pd.DataFrame(
        ownership_acres,
        columns=[f"ownership_{v}" for v in BINS],
        index=df.index,
    )
    ownership["total_ownership_acres"] = total_acres
    ownership["outside_ownership_acres"] = nodata_acres

    ownership.reset_index().to_feather(out_dir / "ownership.feather")


def get_ownership_unit_results(results_dir, unit):
    """Fetch ownership and protection results for the unit_id

    Parameters
    ----------
    results_dir : Path
        path containing results
    unit : pandas.Series
        row for this unit from the units dataset, indexed by unit ID (unit.name)

    Returns
    -------
    dict or None
        {
            "entries": [{"value": <>, "label": <>, "acres": <>, "percent": <>}, ...],
            "total_ownership_acres": <total_acres>,
            "outside_ownership_acres": <nodata acres>,
            "outside_ownership_percent": <nodata percent>,
            "protected_areas": [{"name": <>, "owner": <>, "acres": <>}],
            "num_protected_areas": <number of protected areas>
        }
    """

    # read ownership / protection (may be empty for unit)
    ownership_results = read_unit_from_feather(
        results_dir / "ownership.feather", unit.name
    )

    if len(ownership_results) == 0:
        return None

    ownership_results = ownership_results.iloc[0]

    cols = [c for c in ownership_results.index if c.startswith("ownership_")]
    ownership_acres = ownership_results[cols].values

    ownership = [
        {
            "value": entry["value"],
            "label": entry["label"],
            "acres": ownership_acres[entry["value"]].item(),
            "percent": (
                100 * ownership_acres[entry["value"]] / unit.rasterized_acres
            ).item(),
        }
        for entry in OWNERSHIP
    ]

    return {
        "entries": ownership,
        "total_ownership_acres": ownership_results.total_ownership_acres,
        "outside_ownership_acres": (ownership_results.outside_ownership_acres).item(),
        "outside_ownership_percent": (
            100 * ownership_results.outside_ownership_acres / unit.rasterized_acres
        ).item(),
    }
