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
from analysis.lib.stats.summary_units import read_unit_from_feather

ID = "car"

src_dir = Path("data/inputs/indicators/caribbean")
caribbean_filename = src_dir / "caribbean_lcd.tif"
mask_filename = src_dir / "caribbean_lcd_mask.tif"

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


def get_caribbean_unit_results(results_dir, unit_id, rasterized_acres):
    """Get HUC12 results for unit_id

    Parameters
    ----------
    results_dir : Path
    unit_id : str
    rasterized_acres : float

    Returns
    -------
     Returns
    -------
    dict (empty if no results for unit_id)
        {
            "priorities": <acres by priority category>,
            "legend": <entries for legend>,
            "total_acres": <total acres within input>,
            "outside_input_acres": <acres outside this input but within SE>,
            "outside_input_percent": <percent outside this input but within SE>,
        }
    """

    car_results = read_unit_from_feather(results_dir / f"{ID}.feather", unit_id)
    if len(car_results) == 0:
        return {}

    unit = car_results.iloc[0]

    cols = [c for c in car_results if c.startswith("priority_")]
    priority_acres = unit[cols].values
    total_acres = priority_acres.sum()

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
        "outside_input_acres": unit.outside_input,
        "outside_input_percent": 100 * unit.outside_input / rasterized_acres,
    }
