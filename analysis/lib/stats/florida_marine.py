from pathlib import Path
from collections import OrderedDict

import numpy as np
import pandas as pd
import rasterio

from analysis.constants import INPUTS, INDICATORS as ALL_INDICATORS, M2_ACRES
from analysis.lib.raster import (
    extract_count_in_geometry,
    summarize_raster_by_units_grid,
    offset_window,
)
from analysis.lib.util import pluck

ID = "flm"

# TODO: indicators once available
INDICATORS = ALL_INDICATORS.get(ID, [])
INDICATOR_INDEX = OrderedDict({indicator["id"]: indicator for indicator in INDICATORS})


src_dir = Path("data/inputs/indicators/florida_marine")
flm_filename = src_dir / "flm_blueprint.tif"
mask_filename = src_dir / "flm_blueprint_mask.tif"
results_filename = "data/results/marine_blocks/florida.feather"


def extract_florida_marine_by_mask(
    shape_mask,
    window,
    origin,
    cellsize,
    rasterized_acres,
    outside_se_acres,
    **kwargs,
):
    """Calculate the area of each Florida Marine Blueprint priority category
    based on shape_mask.

    It is assumed shape_mask has already been prescreened to ensure overlap with
    Florida Marine.

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

    # adjust window to align with Florida Marine
    with rasterio.open(flm_filename) as src:
        flm_origin = [src.transform.c, src.transform.f]
        read_window = offset_window(origin, flm_origin, src.res[0], window)

    max_value = INPUTS[ID]["values"][-1]["value"]

    priority_acres = (
        extract_count_in_geometry(
            flm_filename,
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

    priorities = [
        {
            **e,
            "acres": priority_acres[i],
            "percent": 100 * priority_acres[i] / rasterized_acres,
        }
        for i, e in enumerate(
            pluck(INPUTS[ID]["values"], ["blueprint", "value", "label"])
        )
    ]

    return {
        "priorities": priorities,
        # don't include Not a priority in legend
        "legend": pluck(INPUTS[ID]["values"], ["label", "color"])[:-1],
        "total_acres": total_acres,
        "outside_input_acres": outside_input_acres,
        "outside_input_percent": 100 * outside_input_acres / rasterized_acres,
    }


def summarize_florida_marine_by_units_grid(df, units_grid, out_dir):
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

    with rasterio.open(flm_filename) as value_dataset:
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


# def summarize_by_marine_block(geometries):
#     """Summarize by marine_block

#     Parameters
#     ----------
#     geometries : Series of pygeos geometries, indexed by marine block ID
#     """

#     summarize_raster_by_geometry(
#         geometries,
#         extract_by_geometry,
#         outfilename=results_filename,
#         progress_label="Calculating Florida Marine Blueprint area by Marine Block",
#         bounds=INPUTS[ID]["bounds"],
#     )


# def get_marine_block_results(id, analysis_acres, total_acres):
#     """Get results for Florida Conservation Blueprint dataset for a given
#     marine block.

#     Parameters
#     ----------
#     id : str
#         marine block ID
#     analysis_acres : float
#         area of marine block summary unit less any area outside SE Blueprint
#     total_acres : float
#         area of marine block summary unit

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
#     cols = [c for c in row.index if c.startswith("flm_")]

#     df = values.join(pd.Series(row[cols].values, name="acres"))
#     df["percent"] = 100 * np.divide(df.acres, row.shape_mask)

#     # sort into correct order
#     df.sort_values(by=["blueprint", "value"], ascending=[False, True], inplace=True)

#     priorities = df[["value", "blueprint", "label", "acres", "percent"]].to_dict(
#         orient="records"
#     )

#     # don't include Not a priority in legend
#     legend = df[["label", "color"]].iloc[:-1].to_dict(orient="records")

#     remainder = max(analysis_acres - df.acres.sum(), 0)
#     remainder = remainder if remainder >= 1 else 0

#     # Bring in indicators
#     prefix = ID
#     indicator_cols = [c for c in row.index if c.startswith(f"{prefix}:")]
#     indicators_present = {c.rsplit("_", 1)[0] for c in indicator_cols}

#     counts = {
#         id: np.array(
#             [
#                 getattr(row, c)
#                 for c in indicator_cols
#                 if c.startswith(id) and not c.endswith("avg")
#             ]
#         )
#         for id in indicators_present
#     }

#     return {
#         "priorities": priorities,
#         "ecosystems": extract_indicators(counts),
#         "legend": legend,
#         "analysis_acres": analysis_acres,
#         "total_acres": total_acres,
#         "remainder": remainder,
#         "remainder_percent": 100 * remainder / total_acres,
#     }
