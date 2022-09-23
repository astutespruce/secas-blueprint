from pathlib import Path
from collections import OrderedDict
from copy import deepcopy

import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import raster_geometry_mask

from analysis.constants import (
    ACRES_PRECISION,
    M2_ACRES,
    INPUTS,
)
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    detect_data,
    summarize_raster_by_geometry,
)

ID = "car"

src_dir = Path("data/inputs/indicators/caribbean")
caribbean_filename = src_dir / "caribbean_lcd.tif"
mask_filename = src_dir / "caribbean_lcd_mask.tif"
results_filename = "data/results/huc12/caribbean.feather"


# COLORS = {0: "#EEE", 1: "#807dba", 2: "#005a32"}

# LABELS = {0: "Not a priority", 1: "Medium priority", 2: "High priority"}

LEGEND = [
    {"label": "Rank 1-3: highest priority", "color": "#4D004B"},
    {"label": "Rank 4-8: high priority", "color": "#843F98"},
    {"label": "Rank 9-12: medium priority", "color": "#8C96C6"},
    {"label": "Rank 13-24: not a priority", "color": "#FFFFFF"},
]


def extract_by_geometry(geometries, bounds, prescreen=False):
    """Calculate the area of overlap between geometries and Caribbean LCD dataset.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]
    prescreen : bool (default False)
        if True, prescreen using lower resolution mask to determine if there
        is overlap with this dataset

    Returns
    -------
    dict or None (if does not overlap)
    """

    if prescreen:
        # prescreen to make sure data are present
        with rasterio.open(mask_filename) as src:
            if not detect_data(src, geometries, bounds):
                return None

    results = {}

    # create mask and window
    with rasterio.open(caribbean_filename) as src:
        try:
            shape_mask, transform, window = boundless_raster_geometry_mask(
                src, geometries, bounds, all_touched=False
            )

        except ValueError:
            return None

        # square meters to acres
        cellsize = src.res[0] * src.res[1] * M2_ACRES

    results["shape_mask"] = (
        ((~shape_mask).sum() * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    # Nothing in shape mask, return None
    if results["shape_mask"] == 0:
        return None

    max_value = INPUTS[ID]["values"][-1]["value"]

    counts = extract_count_in_geometry(
        caribbean_filename, shape_mask, window, np.arange(max_value + 1), boundless=True
    )

    # there is no overlap
    if counts.max() == 0:
        return None

    results[ID] = (counts * cellsize).round(ACRES_PRECISION).astype("float32")

    return results


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


def summarize_by_huc12(geometries, out_dir):
    """Summarize by HUC12

    Parameters
    ----------
    geometries : Series of pygeos geometries, indexed by HUC12
    out_dir : str or Path object
    marine : bool
        True for marine lease blocks, False otherwise
    """

    summarize_raster_by_geometry(
        geometries,
        extract_by_geometry,
        outfilename=results_filename,
        progress_label="Summarizing Caribbean LCD",
        bounds=INPUTS[ID]["bounds"],
    )


def get_huc12_results(id, analysis_acres, total_acres):
    """Get results for Base Blueprint dataset for a given HUC12

    Parameters
    ----------
    id : str
        HUC12
    analysis_acres : float
        area of summary unit less any area outside SE Blueprint
    total_acres : float
        area of summary unit

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

    df = pd.read_feather(results_filename).set_index("id")

    if id not in df.index:
        return None

    values = pd.DataFrame(INPUTS[ID]["values"])

    row = df.loc[id]
    blueprint_cols = [c for c in row.index if c.startswith("base_")]

    df = values.join(pd.Series(row[blueprint_cols].values, name="acres"))
    df["percent"] = 100 * np.divide(df.acres, row.shape_mask)

    # sort into correct order
    df.sort_values(by=["blueprint", "value"], ascending=False, inplace=True)

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
