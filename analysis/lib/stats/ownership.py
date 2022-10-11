from pathlib import Path

import geopandas as gp
import pygeos as pg

from analysis.constants import M2_ACRES, OWNERSHIP, PROTECTION
from analysis.lib.geometry import intersection
from analysis.lib.stats.summary_units import read_unit_from_feather


src_dir = Path("data/inputs/boundaries")
ownership_filename = src_dir / "ownership.feather"


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

    df["acres"] = pg.area(df.geometry_right.values) * M2_ACRES

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


def get_ownership_unit_results(results_dir, unit_id, acres):
    """Fetch ownership and protection results for the unit_id

    Parameters
    ----------
    results_dir : Path
        path containing results
    unit_id : _type_
        _description_
    acres : float
        acres of polygon summary unit boundary

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
        results_dir / "ownership.feather", unit_id
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
                / acres,
            }
            for key, value in OWNERSHIP.items()
            if key in ownerships_present
        ]

    protection_results = read_unit_from_feather(
        results_dir / "protection.feather", unit_id
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
                / acres,
            }
            for key, value in PROTECTION.items()
            if key in protection_present
        ]

    return results
