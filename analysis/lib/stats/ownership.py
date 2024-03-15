from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
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
from analysis.lib.geometry import intersection, to_crs
from analysis.lib.stats.summary_units import read_unit_from_feather


src_dir = Path("data/inputs/boundaries")
ownership_filename = src_dir / "ownership.feather"


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
    ownership = gp.read_feather(ownership_filename)
    df = intersection(df, ownership)

    if df is None:
        return None

    df["acres"] = shapely.area(df.geometry_right.values.data) * M2_ACRES
    df = df.loc[df.acres > 0].copy()

    if not len(df):
        return None

    results = dict()

    by_owner = (
        df[["Own_Type", "acres"]]
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
        df[["GAP_Sts", "acres"]]
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

    by_area = (
        df[["Loc_Nm", "Loc_Own", "acres"]]
        .groupby(by=[df.index.get_level_values(0), "Loc_Nm", "Loc_Own"])
        .acres.sum()
        .astype("float32")
        .round()
        .reset_index()
        .rename(columns={"level_0": "id", "Loc_Nm": "name", "Loc_Own": "owner"})
        .sort_values(by="acres", ascending=False)
    )
    # drop very small areas, these are not helpful
    by_area = by_area.loc[by_area.acres >= 1].copy()

    results["protected_areas"] = by_area.head(25).to_dict(orient="records")
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

    ownership = gp.read_feather(
        ownership_filename, columns=["geometry", "Own_Type", "GAP_Sts"]
    )

    index_name = df.index.name

    df = intersection(df, ownership)

    if df is None:
        return

    df["acres"] = shapely.area(df.geometry_right.values) * M2_ACRES

    # drop areas that touch but have no overlap
    df = df.loc[df.acres > 0].copy()

    by_owner = (
        df[["Own_Type", "acres"]]
        .groupby([index_name, "Own_Type"])
        .acres.sum()
        .astype("float32")
        .round()
        .reset_index()
    )

    by_protection = (
        df[["GAP_Sts", "acres"]]
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
