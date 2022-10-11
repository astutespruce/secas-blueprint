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
    summarize_raster_by_units_grid,
)
from analysis.lib.stats.summary_units import read_unit_from_feather

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
    if len(corridors):
        results["corridors"] = corridors

    return results


def summarize_base_blueprint_by_units_grid(df, units_grid, out_dir, marine=False):
    """Summarize by HUC12 or marine lease block

    Parameters
    ----------
    df : GeoDataFrame
        must have a "value" column with same values as used for corresponding units
        raster, and must have result of df.bounds joined in
    units_grid : SummaryUnitGrid instance
    out_dir : str
    marine : bool
        if True, will summarize marine lease blocks, otherwise HUC12s
    """

    if (
        not len(df.columns.intersection({"value", "rasterized_acres", "outside_se"}))
        == 3
    ):
        raise ValueError(
            "GeoDataFrame for summary must include value, rasterized_acres, outside_se columns"
        )

    with rasterio.open(base_blueprint_filename) as value_dataset:
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

    with rasterio.open(corridors_filename) as value_dataset:
        bins = range(0, CORRIDORS[-1]["value"] + 1)

        corridor_acres = (
            summarize_raster_by_units_grid(
                df,
                units_grid,
                value_dataset,
                bins=bins,
                progress_label="Summarizing Base Blueprint Corridors",
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

    corridors = pd.DataFrame(
        corridor_acres,
        columns=[f"corridors_{v}" for v in bins],
        index=df.index,
    )

    out = priorities.join(corridors)

    # only use marine indicators in marine blocks; otherwise check them all
    if marine:
        check_indicators = [i for i in INDICATORS if i["id"].startswith("base:marine_")]
    else:
        check_indicators = INDICATORS

    for indicator in check_indicators:
        id = indicator["id"]
        filename = src_dir / indicator["filename"]
        values = [v["value"] for v in indicator["values"]]
        with rasterio.open(filename) as value_dataset:
            indicator_acres = (
                summarize_raster_by_units_grid(
                    df,
                    units_grid,
                    value_dataset,
                    bins=range(0, values[-1] + 1),
                    progress_label=f"Summarizing {indicator['label']}",
                )
                * cellsize
            )

            # skip any where no data are present in any units
            if not indicator_acres.any():
                print(f"{indicator['label']} is not present in any summary units")
                continue

        # Some indicators exclude 0 values, their columns need to be dropped
        if values[0] > 0:
            indicator_acres = indicator_acres[:, values[0] :]

        total_indicator_acres = indicator_acres.sum(axis=1)
        outside_indicator_acres = total_acres - total_indicator_acres
        outside_indicator_acres[outside_indicator_acres < 1e-6] = 0
        indicator_df = pd.DataFrame(
            indicator_acres, columns=[f"{id}_value_{v}" for v in values], index=df.index
        )
        indicator_df[f"{id}_outside"] = outside_indicator_acres

        out = out.join(indicator_df)

    out.reset_index().to_feather(out_dir / f"{ID}.feather")


def get_base_blueprint_unit_results(results_dir, unit_id, rasterized_acres):
    """Get Base Blueprint HUC12 / marine block results for unit_id

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
            "corridors" <acres by corridors category; key only present if corridors are present>,
            "ecosystems": <dict: ecosystem and indicator info>,
            "legend": <entries for legend>,
            "total_acres": <total acres within input>,
            "outside_input_acres": <acres outside this input but within SE>,
            "outside_input_percent": <percent outside this input but within SE>,
        }
    """

    base_results = read_unit_from_feather(results_dir / f"{ID}.feather", unit_id)
    if len(base_results) == 0:
        return {}

    unit = base_results.iloc[0]

    priority_cols = [c for c in base_results if c.startswith("priority_")]
    priority_acres = unit[priority_cols].values
    total_acres = priority_acres.sum()

    # get priority results in descending order
    priorities = [
        {
            **entry,
            "acres": priority_acres[entry["value"]],
            "percent": 100 * priority_acres[entry["value"]] / rasterized_acres,
        }
        for entry in pluck(INPUTS[ID]["values"], ["blueprint", "value", "label"])
    ][::-1]

    corridor_cols = [c for c in base_results if c.startswith("corridors_")]
    corridor_acres = unit[corridor_cols].values
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

    # only check areas of indicators actually present in summaries for unit type
    check_indicators = [
        e for e in INDICATORS if f"{e['id']}_outside" in base_results.columns
    ]

    indicators = {}
    for indicator in check_indicators:
        id = indicator["id"]
        values = indicator["values"]
        indicator_cols = [f"{id}_value_{v['value']}" for v in values]
        indicator_acres = unit[indicator_cols].values
        total_acres = indicator_acres.sum()

        if total_acres == 0:
            continue

        outside_acres = unit[f"{id}_outside"]

        indicator_results = {
            **indicator,
            # merge acres and sort highest value to lowest
            "values": [
                {
                    **v,
                    "acres": indicator_acres[i],
                    "percent": 100 * indicator_acres[i] / rasterized_acres,
                }
                for i, v in enumerate(values)
            ][::-1],
            "total_acres": total_acres,
            "outside_indicator_acres": outside_acres,
            "outside_indicator_percent": 100 * outside_acres / rasterized_acres,
        }

        if "goodThreshold" in indicator:
            indicator_results["good_total"] = indicator_acres[
                # adjust index because values are only from min_value to max_value
                indicator["goodThreshold"]
                - indicator["values"][0]["value"] :
            ].sum()

        indicators[id] = indicator_results

    # aggregate indicators up to ecosystems
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
        "priorities": priorities,
        "legend": pluck(INPUTS[ID]["values"], ["label", "color"])[:0:-1],
        "ecosystems": ecosystems,
        "total_acres": total_acres,
        "outside_input_acres": unit.outside_input,
        "outside_input_percent": 100 * unit.outside_input / rasterized_acres,
    }

    if len(corridors):
        results["corridors"] = corridors

    return results
