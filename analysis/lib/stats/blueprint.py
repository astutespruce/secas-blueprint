from copy import deepcopy
from pathlib import Path

import pandas as pd
import rasterio

from analysis.constants import (
    BLUEPRINT,
    ECOSYSTEMS,
    INDICATORS,
    INDICATORS_INDEX,
    CORRIDORS,
    M2_ACRES,
)
from analysis.lib.util import pluck
from analysis.lib.raster import (
    clip_window,
    detect_data_by_mask,
    extract_count_in_geometry,
    summarize_raster_by_units_grid,
)
from analysis.lib.stats.summary_units import (
    read_unit_from_feather,
)

data_dir = Path("data")
src_dir = data_dir / "inputs"
indicators_dir = src_dir / "indicators"
blueprint_filename = src_dir / "blueprint.tif"
corridors_filename = src_dir / "corridors.tif"

BLUEPRINT_BINS = range(0, len(BLUEPRINT))
CORRIDOR_BINS = range(0, len(CORRIDORS))


def detect_indicators_by_mask(mask_config, indicators):
    """Check area of interest against coarse resolution indicator mask for
    each indicator to see if indicator is present in this area.

    Parameters
    ----------
    mask_config : AOIMaskConfig
    indicators : list-like of indicator IDs

    Returns
    -------
    list of indicator IDs present in area
    """

    prescreen_mask = mask_config.prescreen_mask

    indicators_with_data = []
    for indicator in indicators:
        mask_filename = (
            src_dir / "indicators" / indicator["filename"].replace(".tif", "_mask.tif")
        )
        with rasterio.open(mask_filename) as src:
            prescreen_window = mask_config.get_prescreen_window(src.transform)
            # use window clipped to extent of dataset to see if there is even
            # any overlap
            clipped_window = clip_window(prescreen_window, src.width, src.height)
            if (
                clipped_window.width > 0
                and clipped_window.height > 0
                and detect_data_by_mask(src, prescreen_mask, prescreen_window)
            ):
                indicators_with_data.append(indicator)

    return indicators_with_data


def extract_blueprint_by_mask(mask_config, subregions):
    """Extract areas by each Blueprint category based on shape_mask

    It is assumed that shape_mask has already been prescreened to ensure
    overlap with Blueprint.

    Parameters
    ----------
    mask_config : AOIMaskConfig
    subregions : set
        set of subregion names that are present in AOI

    Returns
    -------
    list of dicts, in descending priority order
        [
            {"value": <value>, "label": <label>, "acres": <acres>, "percent": <percent>}, ...
        ]
    """
    rasterized_acres = mask_config.mask_acres
    cellsize = mask_config.cellsize

    blueprint_acres = (
        extract_count_in_geometry(
            blueprint_filename,
            mask_config,
            bins=range(len(BLUEPRINT)),
            boundless=True,
        )
        * cellsize
    )
    total_acres = blueprint_acres.sum()

    blueprint = [
        {
            **e,
            "acres": blueprint_acres[i],
            "percent": 100 * blueprint_acres[i] / mask_config.mask_acres,
        }
        for i, e in enumerate(pluck(BLUEPRINT, ["value", "label"]))
    ][::-1]

    corridor_acres = (
        extract_count_in_geometry(
            corridors_filename,
            mask_config,
            bins=range(len(CORRIDORS)),
            boundless=True,
        )
        * cellsize
    )

    # empty dict indicates no hubs / corridors present
    corridors = {}

    # 0 is not hub / corridor, so ignore that for determining presence
    if corridor_acres[1:].max() > 0:
        # only keep the ones that are present
        corridor_values = [
            {
                **e,
                "acres": corridor_acres[i],
                "percent": 100 * corridor_acres[i] / rasterized_acres,
            }
            for i, e in enumerate(pluck(CORRIDORS, ["label", "value", "color", "type"]))
            if corridor_acres[i]
        ]
        # sort so that value 0 goes to end
        corridor_values = sorted(corridor_values, key=lambda x: x["value"] or 99)
        corridor_types = set(v["type"] for v in corridor_values if v["value"] > 0)
        corridors = {"entries": corridor_values, "types": corridor_types}

    ### for each indicator present, merge indicator info with acres
    indicators_present = detect_indicators_by_mask(
        mask_config,
        INDICATORS,
    )
    indicators = {}
    for indicator in indicators_present:
        id = indicator["id"]
        filename = src_dir / "indicators" / indicator["filename"]
        bins = range(0, indicator["values"][-1]["value"] + 1)
        indicator_acres = (
            extract_count_in_geometry(filename, mask_config, bins, boundless=True)
            * cellsize
        )

        if indicator_acres.sum() == 0:
            continue

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

        good_threshold = indicator.get("goodThreshold", None)
        if good_threshold is not None:
            indicator_results["good_total"] = indicator_acres[good_threshold:].sum()

        indicators[id] = indicator_results

    ### aggregate indicators up to ecosystems
    # determine ecosystems present from indicators
    ecosystem_ids = {id.split("_")[0] for id in indicators}
    ecosystems_present = [deepcopy(e) for e in ECOSYSTEMS if e["id"] in ecosystem_ids]
    ecosystems = []
    for ecosystem in ecosystems_present:
        id = ecosystem["id"]

        # include either indicators that are present or those expected based on
        # subregions
        expected_indicators = [
            id
            for id in ecosystem["indicators"]
            if id in indicators
            or subregions.intersection(INDICATORS_INDEX[id]["subregions"])
        ]

        ecosystem["indicator_summary"] = [
            {
                "id": id,
                "label": INDICATORS_INDEX[id]["label"],
                "present": id in indicators,
            }
            for id in expected_indicators
        ]

        # update ecosystem with only indicators that are present
        ecosystem["indicators"] = [
            indicators[id] for id in ecosystem["indicators"] if id in indicators
        ]
        ecosystems.append(ecosystem)

    results = {
        "blueprint": blueprint,
        # don't include Not a priority in legend
        "legend": pluck(BLUEPRINT[1:], ["label", "color"])[::-1],
        "ecosystems": ecosystems,
        "total_acres": total_acres,
    }

    if corridors:
        results["corridors"] = corridors

    return results


def summarize_blueprint_by_units_grid(df, units_grid, out_dir, marine=False):
    """Summarize by HUC12 or marine lease block

    Parameters
    ----------
    df : GeoDataFrame
        must have a "value" column with same values as used for corresponding units
        raster, and must have result of df.bounds joined in
    units_grid : SummaryUnitGrid instance
    out_dir : str
    marine : bool, optional (default: False)
        if True, analysis is limited to marine indicators
    """

    if "value" not in df.columns:
        raise ValueError("GeoDataFrame for summary must include value column")

    with rasterio.open(blueprint_filename) as value_dataset:
        cellsize = value_dataset.res[0] * value_dataset.res[0] * M2_ACRES

        blueprint_acres = (
            summarize_raster_by_units_grid(
                df,
                units_grid,
                value_dataset,
                bins=BLUEPRINT_BINS,
                progress_label="Summarizing Southeast Blueprint",
            )
            * cellsize
        )
        total_acres = blueprint_acres.sum(axis=1)

    with rasterio.open(corridors_filename) as value_dataset:
        corridor_acres = (
            summarize_raster_by_units_grid(
                df,
                units_grid,
                value_dataset,
                bins=CORRIDOR_BINS,
                progress_label="Summarizing hubs & corridors",
            )
            * cellsize
        )

    out = pd.DataFrame(
        blueprint_acres,
        columns=[f"blueprint_{v}" for v in BLUEPRINT_BINS],
        index=df.index,
    ).join(
        pd.DataFrame(
            corridor_acres,
            columns=[f"corridors_{v}" for v in CORRIDOR_BINS],
            index=df.index,
        )
    )

    # only use marine indicators in marine blocks; otherwise check them all
    # because some marine indicators are coastal
    if marine:
        check_indicators = [i for i in INDICATORS if i["id"].startswith("m_")]
    else:
        check_indicators = INDICATORS

    for indicator in check_indicators:
        id = indicator["id"]
        filename = indicators_dir / indicator["filename"]
        # WARNING: some indicators have missing values in the range and are non-contiguous
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
        # so that index 0 is aligned with first value of indicator
        if values[0] > 0:
            indicator_acres = indicator_acres[:, values[0] :]

        total_indicator_acres = indicator_acres.sum(axis=1)
        outside_indicator_acres = total_acres - total_indicator_acres
        outside_indicator_acres[outside_indicator_acres < 1e-6] = 0
        # store a column of 0s for indicators with discontinuous value ranges
        indicator_df = pd.DataFrame(
            indicator_acres,
            columns=[f"{id}_value_{v}" for v in range(values[0], values[-1] + 1)],
            index=df.index,
        )
        indicator_df[f"{id}_outside"] = outside_indicator_acres

        out = out.join(indicator_df)

    out.reset_index().to_feather(out_dir / "blueprint.feather")


def get_blueprint_unit_results(results_dir, unit):
    """Get results for a single summary unit (HUC12 / marine lease block).

    Parameters
    ----------
    results_dir : Path
    unit : pandas.Series
        row for this unit from the units dataset, indexed by unit ID (unit.name)

    Returns
    -------
    dict or None
    """

    # read SE Blueprint
    blueprint_results = read_unit_from_feather(
        results_dir / "blueprint.feather", unit.name
    )
    if len(blueprint_results) == 0:
        return None

    blueprint_results = blueprint_results.iloc[0]

    cols = [c for c in blueprint_results.index if c.startswith("blueprint_")]
    blueprint_acres = blueprint_results[cols].values
    total_acres = blueprint_acres.sum()

    # transform and reorder into descending priority
    blueprint = [
        {
            "value": entry["value"],
            "label": entry["label"],
            "acres": blueprint_acres[entry["value"]],
            "percent": 100 * blueprint_acres[entry["value"]] / unit.rasterized_acres,
        }
        for entry in BLUEPRINT
    ][::-1]

    cols = [c for c in blueprint_results.index if c.startswith("corridors_")]
    corridor_acres = blueprint_results[cols].values
    corridors = {}

    # ignore 0 (not a hub / corridor)
    if corridor_acres[1:].max() > 0:
        # only keep the ones that are present
        corridor_values = [
            {
                **e,
                "acres": corridor_acres[i],
                "percent": 100 * corridor_acres[i] / unit.rasterized_acres,
            }
            for i, e in enumerate(pluck(CORRIDORS, ["label", "value", "color", "type"]))
            if corridor_acres[i]
        ]
        # sort so that value 0 goes to end
        corridor_values = sorted(corridor_values, key=lambda x: x["value"] or 99)
        corridor_types = set(v["type"] for v in corridor_values if v["value"] > 0)
        corridors = {"entries": corridor_values, "types": corridor_types}

    # only check areas of indicators actually present in summaries for unit type
    check_indicators = [
        e for e in INDICATORS if f"{e['id']}_outside" in blueprint_results.index
    ]

    indicators = {}
    for indicator in check_indicators:
        id = indicator["id"]
        values = indicator["values"]
        cols = [f"{id}_value_{v['value']}" for v in values]
        indicator_acres = blueprint_results[cols].values
        total_acres = indicator_acres.sum()

        # if only 0 values are present, ignore this indicator
        if total_acres == 0 or (
            values[0]["value"] == 0 and indicator_acres[1:].max() == 0
        ):
            continue

        outside_acres = blueprint_results[f"{id}_outside"]

        indicator_results = {
            **indicator,
            # merge acres and sort highest value to lowest
            "values": [
                {
                    **v,
                    "acres": indicator_acres[i],
                    "percent": 100 * indicator_acres[i] / unit.rasterized_acres,
                }
                for i, v in enumerate(values)
            ][::-1],
            "total_acres": total_acres,
            "outside_indicator_acres": outside_acres,
            "outside_indicator_percent": 100 * outside_acres / unit.rasterized_acres,
        }

        good_threshold = indicator.get("goodThreshold", None)
        if good_threshold is not None:
            indicator_results["good_total"] = indicator_acres[
                # adjust index because values are only from min_value to max_value
                good_threshold
                - indicator["values"][0]["value"] :
            ].sum()

        indicators[id] = indicator_results

    # aggregate indicators up to ecosystems
    ecosystem_ids = {id.split("_")[0] for id in indicators}
    ecosystems_present = [deepcopy(e) for e in ECOSYSTEMS if e["id"] in ecosystem_ids]
    ecosystems = []
    for ecosystem in ecosystems_present:
        id = ecosystem["id"]

        # include either indicators that are present or those expected based on
        # subregions
        expected_indicators = [
            id
            for id in ecosystem["indicators"]
            if id in indicators
            or unit.subregions.intersection(INDICATORS_INDEX[id]["subregions"])
        ]

        ecosystem["indicator_summary"] = [
            {
                "id": id,
                "label": INDICATORS_INDEX[id]["label"],
                "present": id in indicators,
            }
            for id in expected_indicators
        ]

        # update ecosystem with only indicators that are present
        ecosystem["indicators"] = [
            indicators[id] for id in ecosystem["indicators"] if id in indicators
        ]
        ecosystems.append(ecosystem)

    results = {
        "blueprint": blueprint,
        # don't include Not a priority in legend
        "legend": pluck(BLUEPRINT[1:], ["label", "color"])[::-1],
        "total_acres": total_acres,
        "ecosystems": ecosystems,
    }

    if corridors:
        results["corridors"] = corridors

    return results
