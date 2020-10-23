from pathlib import Path
from copy import deepcopy

import numpy as np
import pandas as pd
import geopandas as gp
import pygeos as pg

from analysis.constants import ACRES_PRECISION, M2_ACRES, INPUTS
from analysis.lib.pygeos_util import intersection


chat_dir = Path("data/inputs/indicators/chat")

out_dir = Path("data/results/huc12")


def get_analysis_notes():
    return """Note: areas are based on the polygon boundary of this area
    compared to watershed boundaries rather than pixel-level analyses used
    elsewhere in this report."""


def summarize_by_areas(df, state, rank_only=False, means=False):
    """Calculate acres by value and area-weighted value for each CHAT field in fields.

    Parameters
    ----------
    df : GeoDataFrame
        area(s) of interest
    state : str, one of ['ok', 'tx']
    rank_only : bool (default False)
        if True, will only calculate areas for CHAT Rank
    means : bool
        if True, will calculate area-weighted mean ranks
    Returns
    -------
    dict of DataFrames, all indexed by incoming index
        {
            "total_acres": ...
            "acres": ...,
            "avg": ...
        }
    """
    if not df.index.name:
        df.index.name = "index"

    index_name = df.index.name
    df = df.reset_index()

    chat_df = gp.read_feather(chat_dir / f"{state}chat.feather")
    fields = ["chatrank"]

    if not rank_only:
        fields += [e["id"] for e in INPUTS[f"{state}chat"]["indicators"]]

    df = intersection(df, chat_df)
    df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES
    df = df.loc[df.acres > 0].copy()

    if not len(df):
        return None

    results = {"total_acres": df.groupby(index_name).acres.sum().round(ACRES_PRECISION)}

    area_results = dict()
    avg_results = dict()
    for field in fields:
        # Note: values are categorical, so this will add 0 area values for each category
        grouped = (
            df.groupby([index_name, field])
            .acres.sum()
            .fillna(0)
            .round(ACRES_PRECISION)
            .reset_index()
        )
        # create an array of [<acres for value 0>, <acres for value 1>,... ]
        area_results[field] = grouped.groupby(index_name).acres.apply(np.array)

        if means:
            # exclude nodata to calculate area-weighted average
            values = grouped.loc[grouped[field] > 0].set_index(index_name)
            total_acres = values.groupby(level=0).acres.sum().rename("total")
            values = values.join(total_acres)
            values["wtd_value"] = (values.acres / values.total) * values[field].astype(
                "uint8"
            )
            avg_results[field] = values.groupby(level=0).wtd_value.sum().round(1)

    results["acres"] = pd.DataFrame(area_results)

    if means:
        results["avg"] = pd.DataFrame(avg_results)

    return results


def summarize_by_aoi(df, state, analysis_acres, total_acres):
    """Get results for CHAT Rank for a given area of interest.

    Parameters
    ----------
    df : GeoDataFrame
        input area of interest
    state : str
        CHAT state
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
            "analysis_notes": <analysis_notes>,
            "remainder": <acres outside of input>
            "remainder_percent" <percent of total acres outside input>
        }
    """

    # 0 values not present for top-level rank
    values = pd.DataFrame(INPUTS[f"{state}chat"]["values"][1:])

    chat_df = gp.read_feather(
        chat_dir / f"{state}chat.feather", columns=["geometry", "chatrank"]
    )

    df = intersection(df, chat_df)
    df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES
    df = df.loc[df.acres > 0].copy()

    if not len(df):
        return None

    by_rank = df.groupby("chatrank").acres.sum().fillna(0)

    df = values.join(by_rank, how="left", on="value")
    df["percent"] = 100 * df.acres / total_acres

    priorities = df[["value", "blueprint", "label", "acres", "percent"]].to_dict(
        orient="records"
    )
    legend = df[["label", "color"]].to_dict(orient="records")

    remainder = max(analysis_acres - df.acres.sum(), 0)
    remainder = remainder if remainder >= 1 else 0

    return {
        "priorities": priorities,
        "legend": legend,
        "analysis_notes": get_analysis_notes(),
        "remainder": remainder,
        "remainder_percent": 100 * remainder / total_acres,
    }


def summarize_by_huc12(units_df, out_dir):
    for state in ["ok", "tx"]:
        print(f"Calculating overlap with {state} CHAT...")

        chat_results = summarize_by_areas(units_df, state, rank_only=False, means=True)

        if chat_results is None:
            continue

        area_results = chat_results["acres"]
        avg_results = chat_results["avg"]

        results = pd.DataFrame(chat_results["total_acres"].rename("total_acres"))

        # bare indicator IDs are averages
        results = results.join(avg_results).fillna(0)

        for field in area_results.keys():
            # convert array to columns
            s = area_results[field].apply(pd.Series)
            s.columns = [f"{field}_{c}" for c in s.columns]

            # drop any that are all 0; these are not present
            s = s.drop(columns=s.columns[s.max() == 0].tolist())
            results = results.join(s)

        results.reset_index().to_feather(out_dir / f"{state}chat.feather")


def get_huc12_results(id, state, analyisis_acres, total_acres):
    """Get results for CHAT Rank for a given HUC12.

    Parameters
    ----------
    id : str
        HUC12 ID
    state : str
        CHAT state
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
            "analysis_notes": <analysis_notes>,
            "remainder": <acres outside of input>,
            "remainder_percent" <percent of total acres outside input>
        }
    """

    # 0 values not present for top-level rank
    values = INPUTS[f"{state}chat"]["values"][1:]
    columns = ["id"] + [f'chatrank_{v["value"]}' for v in values]

    df = pd.read_feather(out_dir / f"{state}chat.feather", columns=columns).set_index(
        "id"
    )
    if not id in df.index:
        return dict()

    row = df.loc[id]

    remainder = max(analyisis_acres - row.sum(), 0)
    remainder = remainder if remainder >= 1 else 0

    priorities = []
    legend = []
    for value in values:
        acres = row[f'chatrank_{value["value"]}']
        priorities.append(
            {
                "value": value["value"],
                "label": value["label"],
                "blueprint": value["blueprint"],
                "acres": acres,
                "percent": 100 * acres / total_acres,
            }
        )

        legend.append({"label": value["label"], "color": value["color"]})

    return {
        "priorities": priorities,
        "legend": legend,
        "analysis_notes": get_analysis_notes(),
        "remainder": remainder,
        "remainder_percent": 100 * remainder / total_acres,
    }

