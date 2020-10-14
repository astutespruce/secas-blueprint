from pathlib import Path

import numpy as np
import pandas as pd
import pygeos as pg

from analysis.constants import ACRES_PRECISION, M2_ACRES

from analysis.lib.pygeos_util import intersection


def summarize_chat(df, chat_df, fields):
    """Calculate acres by value and area-weighted value for each CHAT field in fields.

    Parameters
    ----------
    df : GeoDataFrame
        area(s) of interest
    chat_df : GeoDataFrame
    fields : list-like of CHAT field names

    Returns
    -------
    dict of DataFrames, all indexed by incoming index
        {
            "total_acres": ...
            "acres": ...,
            "avg": ...
        }
    """
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

        # exclude nodata to calculate area-weighted average
        values = grouped.loc[grouped[field] > 0].set_index(index_name)
        total_acres = values.groupby(level=0).acres.sum().rename("total")
        values = values.join(total_acres)
        values["wtd_value"] = (values.acres / values.total) * values[field].astype(
            "uint8"
        )
        avg_results[field] = values.groupby(level=0).wtd_value.sum().round(1)

    results["acres"] = pd.DataFrame(area_results)
    results["avg"] = pd.DataFrame(avg_results)

    return results

