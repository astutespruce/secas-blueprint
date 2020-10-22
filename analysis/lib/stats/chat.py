from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gp
import pygeos as pg

from analysis.constants import ACRES_PRECISION, M2_ACRES, INPUTS
from analysis.lib.pygeos_util import intersection


chat_dir = Path("data/inputs/indicators/chat")


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
    chat_df = gp.read_feather(chat_dir / f"{state}chat.feather")
    fields = ["chatrank"]

    if not rank_only:
        fields += [e["id"] for e in INPUTS[f"{state}chat"]["indicators"]]

    df = intersection(df, chat_df)
    df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES
    df = df.loc[df.acres > 0].copy()

    if not len(df):
        return None

    index_name = df.index.name or "index"
    df = df.reset_index()

    results = {"total_acres": df.groupby(index_name).acres.sum().round(ACRES_PRECISION)}

    area_results = dict()
    avg_results = dict()
    for field in fields:
        grouped = (
            df.groupby([index_name, field])
            .acres.sum()
            .fillna(0)
            .round(ACRES_PRECISION)
            .reset_index()
        )
        # create an array of [<acres for value 0>, <acres for value 1>,... ]
        area_results[field] = grouped.groupby("id").acres.apply(np.array)

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
