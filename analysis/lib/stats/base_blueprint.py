from pathlib import Path
from copy import deepcopy

import numpy as np
import pandas as pd
import rasterio

from analysis.constants import (
    INPUTS,
    ECOSYSTEMS,
    INDICATORS as ALL_INDICATORS,
    CORRIDORS,
    M2_ACRES,
)
from analysis.lib.util import pluck
from analysis.lib.raster import (
    extract_count_in_geometry,
    detect_data_by_mask,
    summarize_raster_by_geometry,
)
from analysis.lib.stats.core import huc12_raster_filename, marine_raster_filename

ID = "base"

INDICATORS = ALL_INDICATORS[ID]
INDICATOR_INDEX = {indicator["id"]: indicator for indicator in INDICATORS}

src_dir = Path("data/inputs/indicators/base")
base_blueprint_filename = src_dir / "base_blueprint.tif"
mask_filename = src_dir / "base_blueprint_mask.tif"
corridors_filename = src_dir / "corridors.tif"
corridors_mask_filename = src_dir / "corridors_mask.tif"


def detect_indicators_by_mask(mask, window, indicators):
    """Check area of interest against coarse resolution indicator mask for
    each indicator to see if indicator is present in this area.

    Parameters
    ----------
    dataset : open rasterio.Dataset
    mask : 2d array
        True outside shapes
    indicators : list-like of indicator IDs

    Returns
    -------
    list of indicator IDs present in area
    """

    indicators_with_data = []
    for indicator in indicators:
        with rasterio.open(
            src_dir / indicator["filename"].replace(".tif", "_mask.tif")
        ) as src:
            if detect_data_by_mask(src, mask, window):
                indicators_with_data.append(indicator)

    return indicators_with_data


def extract_base_blueprint_by_mask(
    shape_mask,
    window,
    cellsize,
    prescreen_mask,
    prescreen_window,
    rasterized_acres,
    outside_se_acres,
    **kwargs,
):
    """Extract summary statistics of Base Blueprint based on shape_mask

    Parameters
    ----------
    shape_mask : 2d array
        True outside shapes
    window : rasterio.windows.Window
        read window for Southeast standard origin
    cellsize : float
        pixel area in acres
    prescreen_mask : 2d array
        True outside shapes, at lower resolution
    prescreen_window : rasterio.windows.Window
        read window for Southeast standard origin at lower resolution
    rasterized_acres : float
        rasterized area of shape mask
    outside_se_acres : float
        acres outside SE Blueprint

    Returns
    -------
    dict
        {
            "priorities": <acres by priority category>,
            "corridors" <acres by corridors category; key only present if corridors are present>,
            "ecosystems": <dict: ecosystem and indicator info>,
            "legend": <entries for legend>,
            "total_acres": <total acres within input>,
            "outside_input_acres": <acres outside this input but within SE>,
            "outside_input_percent": <percent outside this input but within SE>,
        }
    """

    max_value = INPUTS[ID]["values"][-1]["value"]

    priority_acres = (
        extract_count_in_geometry(
            base_blueprint_filename,
            shape_mask,
            window,
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

    corridor_acres = (
        extract_count_in_geometry(
            corridors_filename,
            shape_mask,
            window,
            np.arange(CORRIDORS[-1]["value"] + 1),
            boundless=True,
        )
        * cellsize
    )

    # only keep the ones that are present
    corridors = [
        {
            **e,
            "acres": corridor_acres[i],
            "percent": 100 * corridor_acres[i] / rasterized_acres,
        }
        for i, e in enumerate(pluck(CORRIDORS, ["label"]))
        if corridor_acres[i]
    ]

    ### for each indicator present, merge indicator info with acres
    indicators_present = detect_indicators_by_mask(
        prescreen_mask,
        prescreen_window,
        INDICATORS,
    )
    indicators = {}
    for indicator in indicators_present:
        id = indicator["id"]
        filename = src_dir / indicator["filename"]

        bins = np.arange(0, indicator["values"][-1]["value"] + 1)
        indicator_acres = (
            extract_count_in_geometry(
                filename, shape_mask, window, bins, boundless=True
            )
            * cellsize
        )

        # Some indicators exclude 0 values, their counts need to be zeroed out here
        min_value = indicator["values"][0]["value"]
        if min_value > 0:
            indicator_acres[range(0, min_value)] = 0

        # if only 0 values are present, ignore this indicator
        if indicator_acres[1:].max() == 0:
            continue

        total_indicator_acres = indicator_acres[min_value:].sum()
        outside_indicator_acres = total_acres - total_indicator_acres
        if outside_indicator_acres < 1e-6:
            outside_indicator_acres = 0

        indicator_results = {
            **indicator,
            # merge acres and sort highest value to lowest
            "values": [
                {
                    **v,
                    "acres": indicator_acres[v["value"]],
                    "percent": 100 * indicator_acres[v["value"]] / rasterized_acres,
                }
                for v in indicator["values"]
            ][::-1],
            "total_acres": total_indicator_acres,
            "outside_indicator_acres": outside_indicator_acres,
            "outside_indicator_percent": 100
            * outside_indicator_acres
            / rasterized_acres,
        }

        if "goodThreshold" in indicator:
            indicator_results["good_total"] = indicator_acres[
                indicator["goodThreshold"] :
            ].sum()

        indicators[id] = indicator_results

    ### aggregate indicators up to ecosystems
    # determine ecosystems present from indicators
    ecosystem_ids = {id.split(":")[1].split("_")[0] for id in indicators}
    ecosystems_present = [deepcopy(e) for e in ECOSYSTEMS if e["id"] in ecosystem_ids]
    ecosystems = []
    for ecosystem in ecosystems_present:
        id = ecosystem["id"]

        ecosystem["indicator_summary"] = [
            {
                "id": id,
                "label": INDICATOR_INDEX[id]["label"],
                "present": id in indicators,
            }
            for id in ecosystem["indicators"]
            if id.startswith("base:")
        ]

        # update ecosystem with only indicators that are present
        ecosystem["indicators"] = [
            indicators[id] for id in ecosystem["indicators"] if id in indicators
        ]
        ecosystems.append(ecosystem)

    results = {
        "priorities": priorities[::-1],
        # don't include Not a priority in legend
        "legend": pluck(INPUTS[ID]["values"], ["label", "color"])[:0:-1],
        "ecosystems": ecosystems,
        "total_acres": total_acres,
        "outside_input_acres": outside_input_acres,
        "outside_input_percent": 100 * outside_input_acres / rasterized_acres,
    }
    if corridors is not None:
        results["corridors"] = corridors

    return results


# def summarize_by_unit(geometries, out_dir, marine=False):
#     """Summarize by HUC12 / marine lease block

#     Parameters
#     ----------
#     geometries : Series of pygeos geometries, indexed by HUC12 / marine lease block id
#     out_dir : str or Path object
#     marine : bool
#         True for marine lease blocks, False otherwise
#     """

#     summarize_raster_by_geometry(
#         geometries,
#         extract_by_geometry,
#         outfilename=out_dir / "base_blueprint.feather",
#         progress_label="Summarizing Base Blueprint",
#         bounds=INPUTS[ID]["bounds"],
#         marine=marine,
#     )


def summarize_blueprint_by_unit(df, out_dir, marine=False):
    """Summarize by HUC12 or marine lease block

    Parameters
    ----------
    df : GeoDataFrame
        must have a "value" column with same values as used for corresponding units
        raster, and must have result of df.bounds joined in
    out_dir : str
    marine : bool
        if True, will summarize marine lease blocks, otherwise HUC12s
    """

    if not len(df.columns.intersection({"value", "pixels"})) == 2:
        raise ValueError(
            "GeoDataFrame for summary must include value and pixels columns"
        )

    units_raster_filename = marine_raster_filename if marine else huc12_raster_filename
    with rasterio.open(units_raster_filename) as units_dataset, rasterio.open(
        base_blueprint_filename
    ) as value_dataset:
        cellsize = value_dataset.res[0] * value_dataset.res[0] * M2_ACRES
        bins = range(0, INPUTS[ID]["values"][-1]["value"] + 1)

        blueprint_counts = summarize_raster_by_geometry(
            df,
            units_dataset,
            value_dataset,
            bins=bins,
            progress_label="Summarizing Base Blueprint",
        )

    # NOTE: use count of pixels to calculate area outside SE; otherwise small
    # floating point errors
    total = blueprint_counts.sum(axis=1)
    outside_se = df.pixels - total

    # output values are acres
    out = pd.DataFrame(
        blueprint_counts * cellsize,
        columns=[f"value_{v}" for v in bins],
        index=df.index,
    )

    # TODO: drop columns not applicable

    out["total"] = total * cellsize
    out["outside_se"] = outside_se * cellsize
    # TODO: area outside input

    # TODO: add list of indicators present, store each in its own file?

    out.reset_index().to_feather(out_dir / "base_blueprint.feather")


# FIXME: rework
# def get_unit_results(unit_type, id, analysis_acres, total_acres):
#     """Get results for Base Blueprint dataset for a given HUC12 or marine lease
#     block.

#     Parameters
#     ----------
#     unit_type : str, one of ['huc12', 'marine_blocks']

#     id : str
#         HUC12 or marine lease block ID
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
#     if unit_type == "huc12":
#         results_filename = "data/results/huc12/southatlantic.feather"
#     else:
#         results_filename = "data/results/marine_blocks/southatlantic.feather"

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
#         # "priorities": priorities,
#         "ecosystems": extract_indicators(counts),
#         # "legend": legend,
#         "analysis_acres": analysis_acres,
#         "total_acres": total_acres,
#         # "remainder": remainder,
#         # "remainder_percent": 100 * remainder / total_acres,
#     }
