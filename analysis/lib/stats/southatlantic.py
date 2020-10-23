import math
from pathlib import Path

from progress.bar import Bar
import numpy as np
import pandas as pd
import pygeos as pg
import rasterio
from rasterio.mask import raster_geometry_mask
from rasterio.windows import Window

from analysis.constants import (
    URBAN_YEARS,
    ACRES_PRECISION,
    M2_ACRES,
    INPUTS,
    SOUTHATLANTIC_BOUNDS,
)
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    detect_data,
    summarize_raster_by_geometry,
)

src_dir = Path("data/inputs/indicators/southatlantic")
sa_filename = src_dir / "sa_blueprint.tif"
sa_mask_filename = src_dir / "sa_blueprint_mask.tif"


def extract_by_geometry(geometries, bounds, prescreen=False):
    """Calculate the area of overlap between geometries and South Atlantic
    Conservation Blueprint dataset.

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

    results = extract_by_geometry(shapes, bounds, prescreen=False)

    if results is None:
        return None

    total_acres = results["shape_mask"]
    analysis_acres = total_acres - outside_se_acres

    values = pd.DataFrame(INPUTS["sa"]["values"])

    df = values.join(pd.Series(results["sa"], name="acres"))
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

    return {
        "priorities": priorities,
        "legend": legend,
        "remainder": remainder,
        "remainder_percent": 100 * remainder / total_acres,
    }


def summarize_by_unit(geometries, out_dir):
    """Summarize by HUC12 / marine lease block

    Parameters
    ----------
    geometries : Series of pygeos geometries, indexed by HUC12 / marine lease block id
    out_dir : str
    """

    summarize_raster_by_geometry(
        geometries,
        extract_by_geometry,
        outfilename=out_dir / "southatlantic.feather",
        progress_label="Summarizing South Atlantic",
        bounds=SOUTHATLANTIC_BOUNDS,
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
    cols = [c for c in row.index if c.startswith("sa_")]

    df = values.join(pd.Series(row[cols].values, name="acres"))
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

    return {
        "priorities": priorities,
        "legend": legend,
        "remainder": remainder,
        "remainder_percent": 100 * remainder / total_acres,
    }
