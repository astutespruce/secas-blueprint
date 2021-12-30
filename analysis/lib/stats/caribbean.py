from pathlib import Path

import geopandas as gp
import pandas as pd
import pygeos as pg

from analysis.constants import M2_ACRES

from analysis.lib.pygeos_util import intersection


src_dir = Path("data/inputs/indicators/caribbean")
caribbean_filename = src_dir / "caribbean.feather"

out_dir = Path("data/results/huc12")
results_filename = out_dir / "caribbean.feather"


COLORS = {0: "#EEE", 1: "#807dba", 2: "#005a32"}

LABELS = {0: "Not a priority", 1: "Medium priority", 2: "High priority"}

LEGEND = [
    {"label": "Rank 1-8: high priority", "color": "#005a32"},
    {"label": "Rank 9-12: medium priority", "color": "#807dba"},
]


def get_analysis_notes():
    return """Note: areas are based on the polygon boundary of this area
    compared to watershed boundaries rather than pixel-level analyses used
    elsewhere in this report."""


def get_rank_value(rank):
    """Construct value entry (value, label, color, blueprint) for a Caribbean
    priority watershed rank.

    Parameters
    ----------
    rank : int [0...24]

    Returns
    -------
    dict
        {"value": <value>, "label": <label>, "color": <color>, "blueprint": <>}
    """
    blueprint = 0
    if rank <= 8:
        blueprint = 2
    elif rank <= 12:
        blueprint = 1

    return {
        "value": rank,
        "label": f"{rank}: {LABELS[blueprint]}",
        "color": COLORS[blueprint],
        "blueprint": blueprint,
    }


def generate_values():
    """Programmatically generate list of values, colors, labels for Caribbean
    due to large number of values
    """

    return [get_rank_value(i) for i in range(0, 25)]


def summarize_by_aoi(df, analysis_acres, total_acres):
    """Calculate ranks and areas of overlap within Caribbean Priority Watersheds.

    Parameters
    ----------
    df : GeoDataframe
        area of interest
    analysis_acres : float
        area in acres of area of interest less any area outside SE Blueprint
    total_acres : float
        area in acres of area of interest

        dict
        {
            "priorities": [...],
            "legend": [...],
            "analysis_notes": <analysis_notes>
        }
    """

    car_df = gp.read_feather(caribbean_filename, columns=["geometry", "carrank"])
    df = intersection(df, car_df)
    df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES

    # aggregate totals by rank
    by_rank = (
        df[["carrank", "acres"]]
        .groupby(by="carrank")
        .acres.sum()
        .astype("float32")
        .reset_index()
        .sort_values(by="carrank")
    )

    priorities = []
    for ix, row in by_rank.iterrows():
        value = get_rank_value(row.carrank)
        value["acres"] = row.acres
        value["percent"] = 100 * row.acres / analysis_acres

        priorities.append(value)

    # Note: input area remainder deliberately omitted, since all
    # areas outside but close to this input are outside SE Blueprint
    return {
        "priorities": priorities,
        "legend": LEGEND,
        "analysis_notes": get_analysis_notes(),
        "analysis_acres": analysis_acres,
        "total_acres": total_acres,
    }


def summarize_by_huc12(df):
    """Calculate overlap of HUC12 summary units with HUC10 priority watersheds.

    This uses the HUC10 component of the HUC12 index to do a basic join, and
    returns those watersheds that are present in the Caribbean dataset.

    Parameters
    ----------
    df : GeoDataFrame
        summary units
    """

    print("Calculating overlap with Caribbean priority watersheds...")

    df = df.copy()
    car_df = pd.read_feather(
        caribbean_filename, columns=["HUC10", "carrank"]
    ).set_index("HUC10")

    # extract HUC10 codes from HUC12 index
    df["HUC10"] = df.index.str[:10]

    df = df.join(car_df, on="HUC10", how="inner")[["carrank"]].reset_index()

    df.to_feather(results_filename)


def get_huc12_results(id, analysis_acres, total_acres):
    """Get results for Priority Watershed Rank for a given HUC12.

    Parameters
    ----------
    id : str
        HUC12 ID
    analysis_acres : float
        area of HUC12 summary unit less any area outside SE Blueprint
    total_acres : float
        area of HUC12 summary unit

    Returns
    -------
    dict
        {
            "priorities": [...],
            "legend": [...],
            "analysis_notes": <analysis_notes>
        }
    """
    df = pd.read_feather(results_filename).set_index("id")

    rank = df.loc[id].carrank if id in df.index else 0
    value = get_rank_value(rank)
    value["acres"] = analysis_acres
    value["percent"] = 100 * analysis_acres / total_acres

    # Note: input area remainder deliberately omitted, since all
    # areas outside but close to this input are outside SE Blueprint
    return {
        "priorities": [value],
        "legend": LEGEND,
        "analysis_notes": get_analysis_notes(),
        "analysis_acres": analysis_acres,
        "total_acres": total_acres,
    }
