from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
from pyogrio import read_dataframe
import shapely

from analysis.constants import (
    M2_ACRES,
    OWNERSHIP,
    PROTECTION,
    GEO_CRS,
    DATA_CRS,
    M_MILES,
    LTA_SEARCH_RADIUS_BINS,
)
from analysis.lib.geometry import to_crs
from analysis.lib.stats.summary_units import read_unit_from_feather


src_dir = Path("data/inputs/boundaries")
ownership_filename = src_dir / "ownership.fgb"
ownership_columns = ["GAP_Sts", "Own_Type", "Loc_Own", "Loc_Nm"]


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
        ownership_filename,
        columns=ownership_columns + ["geometry"],
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
        pairs.join(ownership[ownership_columns], on="index_right")
        .groupby([index_name] + ownership_columns)
        .agg({"geometry": shapely.multipolygons})
        .reset_index()
        .set_index(index_name),
        geometry="geometry",
        crs=df.crs,
    )

    ownership["acres"] = shapely.area(ownership.geometry.values) * M2_ACRES

    return ownership


def summarize_ownership_in_aoi(df, total_acres):
    """Get ownership and protection levels and other statistics for the DataFrame

    Parameters
    ----------
    df : GeoDataFrame
    total_acres : float

    Returns
    -------
    dict
        {
            "ownership": [
                {
                    "label": <ownership type label>,
                    "acres": <acres of overlap>,
                    "percent" <percent of overlap>
                }
            ],
            "protection": [
                {
                    "label": <protection type label>,
                    "acres": <acres of overlap>,
                    "percent" <percent of overlap>
                }
            ],
            "protected_areas" [<top 25 protected area names and areas>],
            "num_protected_areas": <total number protected areas>
        }
    """

    ownership = extract_ownership(df, use_bbox=True)

    if ownership is None or len(ownership) == 0:
        return None

    results = dict()

    by_owner = (
        ownership[["Own_Type", "acres"]]
        .groupby(by="Own_Type")
        .acres.sum()
        .astype("float32")
        .to_dict()
    )
    # use the native order of OWNERSHIP to drive order of results
    results["ownership"] = [
        {
            "label": value["label"],
            "acres": by_owner[key],
            "percent": 100 * by_owner[key] / total_acres,
        }
        for key, value in OWNERSHIP.items()
        if key in by_owner
    ]

    by_protection = (
        ownership[["GAP_Sts", "acres"]]
        .groupby(by="GAP_Sts")
        .acres.sum()
        .astype("float32")
        .to_dict()
    )
    # use the native order of PROTECTION to drive order of results
    results["protection"] = [
        {
            "label": value["label"],
            "acres": by_protection[key],
            "percent": 100 * by_protection[key] / total_acres,
        }
        for key, value in PROTECTION.items()
        if key in by_protection
    ]

    # only list areas >= 1 acre
    by_area = (
        ownership.loc[ownership.acres >= 1][["Loc_Nm", "Loc_Own", "acres"]]
        .groupby(by=["Loc_Nm", "Loc_Own"])
        .acres.sum()
        .astype("float32")
        .round()
        .reset_index()
        .rename(columns={"Loc_Nm": "name", "Loc_Own": "owner"})
        .sort_values(by="acres", ascending=False)
    ).head(25)
    by_area.loc[by_area.name == "", "name"] = "Unknown name"
    by_area.loc[by_area.owner == "", "owner"] = "Unknown owner"

    results["protected_areas"] = by_area.to_dict(orient="records")
    results["num_protected_areas"] = len(by_area)

    return results


def summarize_ownership_by_units(df, out_dir):
    """Calculate overlap with ownership and protection

    Parameters
    ----------
    df : GeoDataFrame
        contains unit boundaries, indexed by id
    out_dir : str
    """
    print("Calculating overlap with land ownership and protection")

    index_name = df.index.name
    ownership = extract_ownership(df, use_bbox=False)

    if df is None:
        return

    by_owner = (
        ownership[["Own_Type", "acres"]]
        .groupby([index_name, "Own_Type"])
        .acres.sum()
        .astype("float32")
        .round()
        .reset_index()
    )

    by_protection = (
        ownership[["GAP_Sts", "acres"]]
        .groupby([index_name, "GAP_Sts"])
        .acres.sum()
        .astype("float32")
        .round()
        .reset_index()
    )

    by_owner.to_feather(out_dir / "ownership.feather")
    by_protection.to_feather(out_dir / "protection.feather")


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
    dict
        {
            "ownership": [{"label": <label>, "acres": <acres>, "percent": <percent>, ...}],
            "protection": [{"label": <label>, "acres": <acres>, "percent": <percent>, ...}],
        }

        ownership or protection keys will be absent if there is not data of that type
    """

    results = {}

    # read ownership / protection (may be empty)
    ownership_results = read_unit_from_feather(
        results_dir / "ownership.feather", unit.name
    )

    if len(ownership_results) > 0:
        ownerships_present = ownership_results.Own_Type.unique()
        # use the native order of OWNERSHIP to drive order of results
        results["ownership"] = [
            {
                "value": value["value"],
                "label": value["label"],
                "acres": ownership_results.loc[ownership_results.Own_Type == key]
                .iloc[0]
                .acres,
                "percent": 100
                * ownership_results.loc[ownership_results.Own_Type == key].iloc[0].acres
                / unit.acres,
            }
            for key, value in OWNERSHIP.items()
            if key in ownerships_present
        ]

    protection_results = read_unit_from_feather(
        results_dir / "protection.feather", unit.name
    )
    if len(protection_results) > 0:
        protection_present = protection_results.GAP_Sts.unique()
        # use the native order of PROTECTION to drive order of results
        results["protection"] = [
            {
                "value": value["value"],
                "label": value["label"],
                "acres": protection_results.loc[protection_results.GAP_Sts == key]
                .iloc[0]
                .acres,
                "percent": 100
                * protection_results.loc[protection_results.GAP_Sts == key]
                .iloc[0]
                .acres
                / unit.acres,
            }
            for key, value in PROTECTION.items()
            if key in protection_present
        ]

    # lists of protected areas omitted for summary units; these are often too long
    # and not useful

    return results


def get_lta_search_info(bounds):
    """Calculate geographic center and search radius in miles (binned to match
    website) to search against Land Trust Alliance website.

    Parameters
    ----------
    bounds : ndarray of shape (n, 4), in GEO_CRS

    Returns
    -------
    ndarray of shape (n, 2), ndarray of shape (n,)
        centers in long, lat and search distance in miles
    """
    boxes = to_crs(shapely.box(*bounds.T), GEO_CRS, DATA_CRS)
    centers = np.dstack(
        [(bounds[:, 0] + bounds[:, 2]) / 2, (bounds[:, 1] + bounds[:, 3]) / 2]
    )[0]

    extent_radius = (
        shapely.distance(
            shapely.get_point(shapely.get_exterior_ring(boxes), 0),
            shapely.centroid(boxes),
        )
        * M_MILES
    )

    indexes = np.clip(
        np.digitize(extent_radius, LTA_SEARCH_RADIUS_BINS),
        0,
        len(LTA_SEARCH_RADIUS_BINS) - 1,
    )

    return (
        centers,
        pd.Series(indexes)
        .map({i: v for i, v in enumerate(LTA_SEARCH_RADIUS_BINS)})
        .values,
    )
