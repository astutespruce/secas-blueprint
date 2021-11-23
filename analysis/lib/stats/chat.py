from pathlib import Path
from copy import deepcopy

import numpy as np
import pandas as pd
import geopandas as gp
import pygeos as pg

from analysis.constants import ACRES_PRECISION, M2_ACRES, INPUTS, INPUT_AREA_VALUES
from analysis.lib.pygeos_util import intersection, sjoin_geometry, explode


chat_dir = Path("data/inputs/indicators/chat")
out_dir = Path("data/results/huc12")

input_filename = "data/inputs/boundaries/input_areas.feather"


def get_chat_input_values(state):
    return [
        e["value"]
        for e in INPUT_AREA_VALUES
        if f"{state}chat" in set(e["id"].split(","))
    ]


def get_analysis_notes():
    return """Note: areas are based on the polygon boundary of this area
    compared to watershed boundaries rather than pixel-level analyses used
    elsewhere in this report."""


def summarize_by_areas(df, state, rank_only=False):
    """Calculate acres by value and area-weighted value for each CHAT field in fields.

    Parameters
    ----------
    df : GeoDataFrame
        area(s) of interest
    state : str, one of ['ok', 'tx']
    rank_only : bool (default False)
        if True, will only calculate areas for CHAT Rank
    Returns
    -------
    DataFrame
        columns for total_acres, analysis_acrs, chat_acres, and avg (bare) and
        _x suffixed fields for each field
    """
    if not df.index.name:
        df.index.name = "index"

    index_name = df.index.name
    df = df.reset_index()

    chat_df = gp.read_feather(chat_dir / f"{state}chat.feather")
    fields = ["chatrank"]

    if not rank_only:
        fields += [e["id"] for e in INPUTS[f"{state}chat"]["indicators"]]

    print("Intersecting with CHAT...")
    chat_df = intersection(df, chat_df)
    chat_df["acres"] = pg.area(chat_df.geometry_right.values.data) * M2_ACRES
    chat_df = chat_df.loc[chat_df.acres > 0].copy()

    if not len(chat_df):
        return None

    # total_acres = chat_df.groupby(index_name).geometry.first()
    total_acres = df.loc[df[index_name].isin(chat_df[index_name])].set_index(index_name)
    total_acres["total_acres"] = pg.area(total_acres.geometry.values.data) * M2_ACRES

    results = pd.DataFrame(
        chat_df.groupby(index_name).acres.sum().rename("chat_acres")
    ).join(total_acres[["total_acres"]], how="left")

    # intersect edge units with SE input areas to determine areas outside
    edge_df = explode(
        df.loc[
            df[index_name].isin(
                results.loc[(results.chat_acres < results.total_acres - 1)].index
            )
        ].copy()[[index_name, "geometry"]]
    )

    print("Intersecting with input areas, this may take a while...")
    input_df = gp.read_feather(input_filename).reset_index(drop=True)
    # this is inverted because input_df performs better if prepared (left side)
    # note: we don't do intersection() here because of topology errors

    left = pd.Series(input_df.geometry.values.data, index=input_df.index)
    right = pd.Series(edge_df.geometry.values.data, index=edge_df.index)
    intersects = sjoin_geometry(left, right, predicate="intersects")

    tmp = input_df.loc[intersects.index.unique()]

    # have to make valid first or fails with topology errors
    tmp.geometry = pg.make_valid(tmp.geometry.values.data)

    # clip to general area, otherwise intersection takes a way long time
    clip_box = pg.box(*pg.total_bounds(edge_df.geometry.values.data))
    tmp.geometry = pg.intersection(tmp.geometry.values.data, clip_box)

    tmp = tmp.join(intersects, how="inner").join(
        edge_df, on="index_right", rsuffix="_right"
    )

    tmp.geometry_right = pg.intersection(
        tmp.geometry.values.data, tmp.geometry_right.values.data
    )

    tmp["acres"] = pg.area(tmp.geometry_right.values.data) * M2_ACRES
    analysis_acres = (
        tmp.groupby(index_name)
        .acres.sum()
        .round(ACRES_PRECISION)
        .rename("analysis_acres")
    )

    # join analysis acres back to results
    results = results.join(analysis_acres)
    results.loc[results.analysis_acres.isnull(), "analysis_acres"] = results.total_acres

    area_results = dict()
    avg_results = dict()
    for field in fields:
        # Note: values are categorical, so this will add 0 area values for each category
        grouped = (
            chat_df.groupby([index_name, field])
            .acres.sum()
            .fillna(0)
            .round(ACRES_PRECISION)
            .reset_index()
        )
        # create an array of [<acres for value 0>, <acres for value 1>,... ]
        area_results[field] = grouped.groupby(index_name).acres.apply(np.array)

        # exclude nodata to calculate area-weighted average
        values = grouped.loc[grouped[field] > 0].set_index(index_name)
        total_acres = values.groupby(level=0).acres.sum().rename("total")
        values = values.join(total_acres)
        values["wtd_value"] = (values.acres / values.total) * values[field].astype(
            "uint8"
        )
        avg_results[field] = values.groupby(level=0).wtd_value.sum().round(1)

    area_results = pd.DataFrame(area_results)
    avg_results = pd.DataFrame(avg_results)

    results = results.join(avg_results).fillna(0)

    for field in fields:
        # convert areas array to columns
        s = area_results[field].apply(pd.Series)
        s.columns = [f"{field}_{c}" for c in s.columns]

        # drop any that are all 0; these are not present
        s = s.drop(columns=s.columns[s.max() == 0].tolist())
        results = results.join(s)

    return results


def summarize_by_aoi(df, state, total_acres):
    """Get results for CHAT Rank for a given area of interest.

    Parameters
    ----------
    df : GeoDataFrame
        input area of interest
    state : str
        CHAT state
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

    # FIXME:
    return None

    # 0 values not present for top-level rank
    values = pd.DataFrame(INPUTS[f"{state}chat"]["values"][1:])

    chat_df = gp.read_feather(
        chat_dir / f"{state}chat.feather", columns=["geometry", "chatrank"]
    )

    chat_df = intersection(df, chat_df)
    chat_df["acres"] = pg.area(chat_df.geometry_right.values.data) * M2_ACRES
    chat_df = chat_df.loc[chat_df.acres > 0].copy()

    if not len(chat_df):
        return None

    by_rank = chat_df.groupby("chatrank").acres.sum().fillna(0)

    chat_df = values.join(by_rank, how="left", on="value")
    chat_df["percent"] = 100 * chat_df.acres / total_acres

    priorities = chat_df[["value", "blueprint", "label", "acres", "percent"]].to_dict(
        orient="records"
    )
    legend = chat_df[["label", "color"]].to_dict(orient="records")

    remainder = 0
    se_remainder = 0
    analysis_acres = total_acres

    chat_acres = chat_df.acres.sum()
    if chat_acres < total_acres:
        # only needed if this area is at edge of input or region
        # intersect with input areas to determine what part is outside CHAT
        # vs outside SE
        input_df = gp.read_feather(input_filename, columns=["value", "geometry"])
        tmp = intersection(df, input_df)
        tmp["acres"] = pg.area(tmp.geometry_right.values.data) * M2_ACRES

        # this excludes area outside SE region
        analysis_acres = tmp.acres.sum()

        se_remainder = max(total_acres - analysis_acres, 0)
        se_remainder = se_remainder if se_remainder >= 1 else 0

        # this calculates area within SE region but outside CHAT
        remainder = (
            analysis_acres
            - tmp.loc[tmp.value.isin(get_chat_input_values(state))].acres.sum()
        )

        remainder = max(remainder, 0)
        remainder = remainder if remainder >= 1 else 0

    return {
        "priorities": priorities,
        "legend": legend,
        "analysis_notes": get_analysis_notes(),
        "analysis_acres": analysis_acres,
        "total_acres": total_acres,
        "remainder": remainder,
        "remainder_percent": 100 * remainder / total_acres,
        "se_remainder": se_remainder,
        "se_remainder_percent": 100 * se_remainder / total_acres,
    }


def summarize_by_huc12(units_df):
    for state in ["ok", "tx"]:
        print(f"Calculating overlap with {state} CHAT...")

        results = summarize_by_areas(units_df, state, rank_only=False)

        if results is None:
            continue

        results.reset_index().to_feather(out_dir / f"{state}chat.feather")


def get_huc12_results(id, state):
    """Get results for CHAT Rank for a given HUC12.

    Parameters
    ----------
    id : str
        HUC12 ID
    state : str
        CHAT state

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
    columns = ["id", "total_acres", "analysis_acres", "chat_acres"] + [
        f'chatrank_{v["value"]}' for v in values
    ]

    df = pd.read_feather(out_dir / f"{state}chat.feather", columns=columns).set_index(
        "id"
    )
    if not id in df.index:
        return dict()

    row = df.loc[id]

    se_remainder = max(row.total_acres - row.analysis_acres, 0)
    se_remainder = se_remainder if se_remainder >= 1 else 0

    remainder = max(row.analysis_acres - row.chat_acres, 0)
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
                "percent": 100 * acres / row.total_acres,
            }
        )

        legend.append({"label": value["label"], "color": value["color"]})

    return {
        "priorities": priorities,
        "legend": legend,
        "analysis_notes": get_analysis_notes(),
        "analysis_acres": row.analysis_acres,
        "total_acres": row.total_acres,
        "remainder": remainder,
        "remainder_percent": 100 * remainder / row.total_acres,
        "se_remainder": se_remainder,
        "se_remainder_percent": 100 * se_remainder / row.total_acres,
    }

