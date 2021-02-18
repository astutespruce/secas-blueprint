from pathlib import Path
from collections import OrderedDict
from sys import prefix

from progress.bar import Bar
import numpy as np
import pandas as pd
import pygeos as pg
import rasterio
from rasterio.mask import raster_geometry_mask
from rasterio.windows import Window

from analysis.constants import (
    ACRES_PRECISION,
    M2_ACRES,
    INPUTS,
    INDICATORS as ALL_INDICATORS,
    SOUTHATLANTIC_BOUNDS,
)
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    extract_zonal_mean,
    detect_data,
    summarize_raster_by_geometry,
)

src_dir = Path("data/inputs/indicators/southatlantic")
continuous_indicator_dir = Path("data/continuous_indicators/southatlantic")
indicators_mask_dir = src_dir / "masks"
sa_filename = src_dir / "sa_blueprint.tif"
sa_mask_filename = src_dir / "sa_blueprint_mask.tif"


INDICATORS = ALL_INDICATORS["southatlantic"]
INDICATOR_INDEX = OrderedDict({indicator["id"]: indicator for indicator in INDICATORS})


def detect_indicators(geometries, indicators):
    """Check area of interest against coarse resolution indicator mask for
    each indicator to see if indicator is present in this area.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    indicators : list-like of indicator IDs

    Returns
    -------
    list of indicator IDs present in area
    """

    if not indicators:
        return []

    with rasterio.open(indicators_mask_dir / indicators[0]["filename"]) as src:
        geometry_mask, transform, window = raster_geometry_mask(
            src, geometries, crop=True, all_touched=True
        )

    indicators_with_data = []
    for indicator in indicators:
        with rasterio.open(indicators_mask_dir / indicator["filename"]) as src:
            data = src.read(1, window=window)
            nodata = src.nodatavals[0]

            mask = (data == nodata) | geometry_mask

        # if there are unmasked areas, keep this indicator
        if mask.min() == False:
            indicators_with_data.append(indicator)

    return indicators_with_data


def extract_by_geometry(
    geometries, bounds, prescreen=False, marine=False, zonal_means=False
):
    """Calculate the area of overlap between geometries and South Atlantic
    Conservation Blueprint dataset.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]
    prescreen : bool (default False)
        if True, prescreen using lower resolution mask to determine if there
        is overlap with this dataset
    marine : bool (default False)
        True for marine lease blocks, False otherwise.
    zonal_means : bool (default False)
        if True, will calculate zonal means for continuous indicators

    Returns
    -------
    dict or None (if does not overlap)
    """

    if prescreen:
        # prescreen to make sure data are present
        with rasterio.open(sa_mask_filename) as src:
            if not detect_data(src, geometries, bounds):
                return None

    results = {}

    # create mask and window
    with rasterio.open(sa_filename) as src:
        try:
            shape_mask, transform, window = boundless_raster_geometry_mask(
                src, geometries, bounds, all_touched=True
            )

        except ValueError:
            return None

        # square meters to acres
        cellsize = src.res[0] * src.res[1] * M2_ACRES

    results["shape_mask"] = (
        ((~shape_mask).sum() * cellsize)
        .round(ACRES_PRECISION)
        .astype("float32")
        .round(ACRES_PRECISION)
        .astype("float32")
    )

    # Nothing in shape mask, return None
    if results["shape_mask"] == 0:
        return None

    max_value = INPUTS["sa"]["values"][-1]["value"]

    counts = extract_count_in_geometry(
        sa_filename, shape_mask, window, np.arange(max_value + 1), boundless=True
    )

    # there is no overlap
    if counts.max() == 0:
        return None

    results["sa"] = (counts * cellsize).round(ACRES_PRECISION).astype("float32")

    if marine:
        # marine areas only have marine indicators
        indicators = [i for i in INDICATORS if i["id"].startswith("marine_")]
        indicators = detect_indicators(geometries, indicators)

    else:
        # include all indicators that are present in area
        indicators = detect_indicators(geometries, INDICATORS)

    for indicator in indicators:
        id = indicator["id"]
        filename = src_dir / indicator["filename"]

        values = [e["value"] for e in indicator["values"]]
        bins = np.arange(0, max(values) + 1)
        counts = extract_count_in_geometry(
            filename, shape_mask, window, bins, boundless=True
        )

        # Some indicators exclude 0 values, their counts need to be zeroed out here
        min_value = min(values)
        if min_value > 0:
            counts[range(0, min_value)] = 0

        results[f"sa:{id}"] = (
            (counts * cellsize).round(ACRES_PRECISION).astype("float32")
        )

        if zonal_means and indicator.get("continuous"):
            continuous_filename = continuous_indicator_dir / indicator[
                "filename"
            ].replace("_Binned", "")
            mean = extract_zonal_mean(
                continuous_filename, shape_mask, window, boundless=True
            )
            if mean is not None:
                results[f"sa:{id}_avg"] = mean

    return results


def summarize_by_aoi(shapes, bounds, outside_se_acres):
    """Get results for South Atlantic Conservation Blueprint dataset
    for a given area of interest.

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

    values = pd.DataFrame(INPUTS["sa"]["values"])

    df = values.join(pd.Series(counts["sa"], name="acres"))
    df["percent"] = 100 * np.divide(df.acres, total_acres)

    # sort into correct order
    df.sort_values(by=["blueprint", "value"], ascending=False, inplace=True)

    priorities = df[["value", "blueprint", "label", "acres", "percent"]].to_dict(
        orient="records"
    )

    # don't include Not a priority in legend
    legend = df[["label", "color"]].iloc[:-1].to_dict(orient="records")

    remainder = max(analysis_acres - df.acres.sum(), 0)
    remainder = remainder if remainder >= 1 else 0

    results = {
        "priorities": priorities,
        "legend": legend,
        "analysis_acres": analysis_acres,
        "total_acres": total_acres,
        "remainder": remainder,
        "remainder_percent": 100 * remainder / total_acres,
    }

    # Bring in indicators
    prefix = "sa"
    indicators = []
    indicator_ids = [f'{prefix}:{i["id"]}' for i in INDICATORS]
    indicator_ids = [i for i in indicator_ids if i in counts]

    for indicator_id in indicator_ids:
        indicator = INDICATOR_INDEX[indicator_id.split(":")[1]]
        values = counts[indicator_id]

        # drop indicators that are not present in this area
        # if only 0 values are present, ignore this indicator
        if values[1:].max() > 0:
            indicators.append(indicator_id)
            results[indicator_id] = values.tolist()
            min_value = indicator["values"][0]["value"]
            results[f"{indicator_id}_total"] = values[min_value:].sum()

            if "goodThreshold" in indicator:
                results[f"{indicator_id}_good_total"] = values[
                    indicator["goodThreshold"] :
                ].sum()

    results["indicators"] = indicators

    return results


def summarize_by_unit(geometries, out_dir, marine=False):
    """Summarize by HUC12 / marine lease block

    Parameters
    ----------
    geometries : Series of pygeos geometries, indexed by HUC12 / marine lease block id
    out_dir : str or Path object
    marine : bool
        True for marine lease blocks, False otherwise
    """

    summarize_raster_by_geometry(
        geometries,
        extract_by_geometry,
        outfilename=out_dir / "southatlantic.feather",
        progress_label="Summarizing South Atlantic",
        bounds=SOUTHATLANTIC_BOUNDS,
        marine=marine,
        zonal_means=True,
    )


def get_unit_results(unit_type, id, analysis_acres, total_acres):
    """Get results for South Atlantic Conservation Blueprint dataset for a
    given HUC12 or marine lease block.

    Parameters
    ----------
    unit_type : str, one of ['huc12', 'marine_blocks']

    id : str
        HUC1marine lease block ID
    analysis_acres : float
        area of marine lease block summary unit less any area outside SE Blueprint
    total_acres : float
        area of marine lease block summary unit

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
    if unit_type == "huc12":
        results_filename = "data/results/huc12/southatlantic.feather"
    else:
        results_filename = "data/results/marine_blocks/southatlantic.feather"

    df = pd.read_feather(results_filename).set_index("id")

    if not id in df.index:
        return None

    values = pd.DataFrame(INPUTS["sa"]["values"])

    row = df.loc[id]
    blueprint_cols = [c for c in row.index if c.startswith("sa_")]

    df = values.join(pd.Series(row[blueprint_cols].values, name="acres"))
    df["percent"] = 100 * np.divide(df.acres, row.shape_mask)

    # sort into correct order
    df.sort_values(by=["blueprint", "value"], ascending=False, inplace=True)

    priorities = df[["value", "blueprint", "label", "acres", "percent"]].to_dict(
        orient="records"
    )

    # don't include Not a priority in legend
    legend = df[["label", "color"]].iloc[:-1].to_dict(orient="records")

    remainder = max(analysis_acres - df.acres.sum(), 0)
    remainder = remainder if remainder >= 1 else 0

    results = {
        "priorities": priorities,
        "legend": legend,
        "analysis_acres": analysis_acres,
        "total_acres": total_acres,
        "remainder": remainder,
        "remainder_percent": 100 * remainder / total_acres,
    }

    # Bring in indicators
    prefix = "sa"
    indicators = []
    indicator_ids = [f'{prefix}:{i["id"]}' for i in INDICATORS]
    indicator_cols = [c for c in row.index if c.startswith(f"{prefix}:")]
    indicators_present = {c.rsplit("_", 1)[0] for c in indicator_cols}

    for indicator_id in indicator_ids:
        if not indicator_id in indicators_present:
            continue

        indicator = INDICATOR_INDEX[indicator_id.split(":")[1]]

        values = np.array(
            [
                getattr(row, c)
                for c in indicator_cols
                if c.startswith(indicator_id) and not c.endswith("avg")
            ]
        )
        # drop indicators that are not present in this area
        # if only 0 values are present, ignore this indicator
        if values[1:].max() > 0:
            indicators.append(indicator_id)
            results[indicator_id] = values.tolist()
            min_value = indicator["values"][0]["value"]
            results[f"{indicator_id}_total"] = values[min_value:].sum()

            if "goodThreshold" in indicator:
                results[f"{indicator_id}_good_total"] = values[
                    indicator["goodThreshold"] :
                ].sum()

    results["indicators"] = indicators

    return results
