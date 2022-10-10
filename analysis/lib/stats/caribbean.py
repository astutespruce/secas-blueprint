from pathlib import Path

import numpy as np
import pandas as pd
import rasterio

from analysis.constants import INPUTS, M2_ACRES
from analysis.lib.raster import (
    extract_count_in_geometry,
    summarize_raster_by_units_grid,
    offset_window,
)
from analysis.lib.util import pluck

ID = "car"

src_dir = Path("data/inputs/indicators/caribbean")
caribbean_filename = src_dir / "caribbean_lcd.tif"
mask_filename = src_dir / "caribbean_lcd_mask.tif"
results_filename = "data/results/huc12/caribbean.feather"

LEGEND = [
    {"label": "Rank 1-3: highest priority", "color": "#4D004B"},
    {"label": "Rank 4-8: high priority", "color": "#843F98"},
    {"label": "Rank 9-12: medium priority", "color": "#8C96C6"},
    {"label": "Rank 13-24: not a priority", "color": "#FFFFFF"},
]


def extract_caribbean_by_mask(
    shape_mask,
    window,
    origin,
    cellsize,
    rasterized_acres,
    outside_se_acres,
    **kwargs,
):
    """Calculate the area of each Caribbean LCD watershed rank based on shape_mask

    It is assumed shape_mask has already been prescreened to ensure overlap with
    Caribbean LCD.

    Parameters
    ----------
    shape_mask : 2d array
        True outside shapes
    window : rasterio.windows.Window
        read window for Southeast standard origin
    origin : list
        [xmin, ymin] of origin of grid from which window is based
    cellsize : float
        pixel area in acres
    rasterized_acres : float
        rasterized area of shape mask
    outside_se_acres : float
        acres outside SE Blueprint

    Returns
    -------
    dict
        {
            "priorities": <acres by priority category>,
            "legend": <entries for legend>,
            "total_acres": <total acres within input>,
            "outside_input_acres": <acres outside this input but within SE>,
            "outside_input_percent": <percent outside this input but within SE>,
        }
    """

    # adjust window to align with Caribbean
    with rasterio.open(caribbean_filename) as src:
        car_origin = [src.transform.c, src.transform.f]
        read_window = offset_window(origin, car_origin, src.res[0], window)

    max_value = INPUTS[ID]["values"][-1]["value"]

    priority_acres = (
        extract_count_in_geometry(
            caribbean_filename,
            shape_mask,
            read_window,
            np.arange(max_value + 1),
            boundless=True,
        )
        * cellsize
    )

    total_acres = priority_acres.sum()
    outside_input_acres = rasterized_acres - outside_se_acres - total_acres
    if outside_input_acres < 1e-6:
        outside_input_acres = 0

    # only include priority ranks that are present
    priorities = [
        {
            **e,
            "acres": priority_acres[i],
            "percent": 100 * priority_acres[i] / rasterized_acres,
        }
        for i, e in enumerate(
            pluck(INPUTS[ID]["values"], ["blueprint", "value", "label"])
        )
        if priority_acres[i]
    ]

    return {
        "priorities": priorities,
        "legend": LEGEND,
        "total_acres": total_acres,
        "outside_input_acres": outside_input_acres,
        "outside_input_percent": 100 * outside_input_acres / rasterized_acres,
    }


def summarize_by_aoi(shapes, bounds, outside_se_acres):
    """Calculate ranks and areas of overlap within Caribbean Priority Watersheds.

    Parameters
    ----------
    shapes : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]
    outside_se_acres : float
        acres of the analysis area that are outside the SE Blueprint region

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

    counts = extract_by_geometry(shapes, bounds, prescreen=False)

    if counts is None:
        return None

    total_acres = counts["shape_mask"]
    analysis_acres = total_acres - outside_se_acres

    values = pd.DataFrame(INPUTS[ID]["values"])

    df = values.join(pd.Series(counts[ID], name="acres"))
    df["percent"] = 100 * np.divide(df.acres, total_acres)

    # sort into correct order
    df.sort_values(by=["blueprint", "value"], ascending=[False, True], inplace=True)

    # drop any values that are not present
    df = df.loc[df.acres > 0]

    priorities = df[["value", "blueprint", "label", "acres", "percent"]].to_dict(
        orient="records"
    )

    remainder = max(analysis_acres - df.acres.sum(), 0)
    remainder = remainder if remainder >= 1 else 0

    return {
        "priorities": priorities,
        "legend": LEGEND,
        "analysis_acres": analysis_acres,
        "total_acres": total_acres,
        "remainder": remainder,
        "remainder_percent": 100 * remainder / total_acres,
    }


def summarize_caribbean_by_units_grid(df, units_grid, out_dir):
    """Summarize by marine lease block

    Parameters
    ----------
    df : GeoDataFrame
        must have a "value" column with same values as used for corresponding units
        raster, and must have result of df.bounds joined in
    units_grid : SummaryUnitGrid instance
    out_dir : str
    """

    if (
        not len(df.columns.intersection({"value", "rasterized_acres", "outside_se"}))
        == 3
    ):
        raise ValueError(
            "GeoDataFrame for summary must include value, rasterized_acres, outside_se columns"
        )

    with rasterio.open(caribbean_filename) as value_dataset:
        cellsize = value_dataset.res[0] * value_dataset.res[0] * M2_ACRES
        bins = range(0, INPUTS[ID]["values"][-1]["value"] + 1)

        priority_acres = (
            summarize_raster_by_units_grid(
                df,
                units_grid,
                value_dataset,
                bins=bins,
                progress_label="Summarizing Base Blueprint",
            )
            * cellsize
        )

    priorities = pd.DataFrame(
        priority_acres,
        columns=[f"priority_{v}" for v in bins],
        index=df.index,
    )
    total_acres = priority_acres.sum(axis=1)
    outside_input_acres = (
        df.rasterized_acres.values - df.outside_se.values - total_acres
    )
    outside_input_acres[outside_input_acres < 1e-6] = 0
    priorities["outside_input"] = outside_input_acres

    priorities.reset_index().to_feather(out_dir / f"{ID}.feather")


# def get_huc12_results(id, analysis_acres, total_acres):
#     """Get results for Base Blueprint dataset for a given HUC12

#     Parameters
#     ----------
#     id : str
#         HUC12
#     analysis_acres : float
#         area of summary unit less any area outside SE Blueprint
#     total_acres : float
#         area of summary unit

#     Returns
#     -------
#     dict
#         {
#             "priorities": [...],
#             "legend": [...],
#             "analysis_notes": <analysis_notes>,
#             "remainder": <acres outside of input>,
#             "remainder_percent" <percent of total acres outside input>
#         }
#     """

#     df = pd.read_feather(results_filename).set_index("id")

#     if id not in df.index:
#         return None

#     values = pd.DataFrame(INPUTS[ID]["values"])

#     row = df.loc[id]
#     blueprint_cols = [c for c in row.index if c.startswith("base_")]

#     df = values.join(pd.Series(row[blueprint_cols].values, name="acres"))
#     df["percent"] = 100 * np.divide(df.acres, row.shape_mask)

#     # sort into correct order
#     df.sort_values(by=["blueprint", "value"], ascending=False, inplace=True)

#     # drop any values that are not present
#     df = df.loc[df.acres > 0]

#     priorities = df[["value", "blueprint", "label", "acres", "percent"]].to_dict(
#         orient="records"
#     )

#     remainder = max(analysis_acres - df.acres.sum(), 0)
#     remainder = remainder if remainder >= 1 else 0

#     return {
#         "priorities": priorities,
#         "legend": LEGEND,
#         "analysis_acres": analysis_acres,
#         "total_acres": total_acres,
#         "remainder": remainder,
#         "remainder_percent": 100 * remainder / total_acres,
#     }
