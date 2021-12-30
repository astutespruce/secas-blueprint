from pathlib import Path

import numpy as np
import pandas as pd
import rasterio

from analysis.constants import (
    ACRES_PRECISION,
    M2_ACRES,
    INPUTS,
    GULF_HYPOXIA_BOUNDS,
)
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    summarize_raster_by_geometry,
    detect_data,
)

src_dir = Path("data/inputs/indicators/gulf_hypoxia")
gh_filename = src_dir / "gulf_hypoxia.tif"
gh_mask_filename = src_dir / "gulf_hypoxia_mask.tif"

out_dir = Path("data/results/huc12")
results_filename = out_dir / "gulf_hypoxia.feather"


def extract_by_geometry(geometries, bounds, prescreen=False):
    """Calculate the area of overlap between geometries and Gulf Hypoxia dataset.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]
    prescreen : bool (default False)
        if True, prescreen using lower resolution mask to determine if there
        is overlap with this dataset

    Returns
    -------
    dict or None (if does not overlap Gulf Hypoxia dataset)
    """

    if prescreen:
        # prescreen to make sure data are present
        with rasterio.open(gh_mask_filename) as src:
            if not detect_data(src, geometries, bounds):
                return None

    results = {}

    # create mask and window
    with rasterio.open(gh_filename) as src:
        try:
            shape_mask, transform, window = boundless_raster_geometry_mask(
                src, geometries, bounds, all_touched=False
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

    max_value = INPUTS["gh"]["values"][-1]["value"]

    counts = extract_count_in_geometry(
        gh_filename, shape_mask, window, np.arange(max_value + 1), boundless=True
    )

    # there is no overlap
    if counts.max() == 0:
        return None

    results["gh"] = (counts * cellsize).round(ACRES_PRECISION).astype("float32")

    return results


def summarize_by_aoi(shapes, bounds, outside_se_acres):
    """Get results for Gulf Hypoxia dataset for a given area of interest.

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

    values = pd.DataFrame(INPUTS["gh"]["values"])

    df = values.join(pd.Series(results["gh"], name="acres"))
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
        "analysis_acres": analysis_acres,
        "total_acres": total_acres,
        "remainder": remainder,
        "remainder_percent": 100 * remainder / total_acres,
    }


def summarize_by_huc12(geometries):
    """Summarize by HUC12

    Parameters
    ----------
    geometries : Series of pygeos geometries, indexed by HUC12 id
    """

    summarize_raster_by_geometry(
        geometries,
        extract_by_geometry,
        outfilename=out_dir / "gulf_hypoxia.feather",
        progress_label="Calculating Gulf Hypoxia area by HUC12",
        bounds=GULF_HYPOXIA_BOUNDS,
    )


def get_huc12_results(id, analysis_acres, total_acres):
    """Get results for Gulf Hypoxia dataset for a given HUC12.

    Parameters
    ----------
    id : str
        HUC12 ID
    analysis_acres : float
        area of HUC12 summary unit less any area outside SE Blueprint
    total_acres : float
        area of HUC12 summary unit

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

    values = pd.DataFrame(INPUTS["gh"]["values"])

    row = df.loc[id]
    cols = [c for c in row.index if c.startswith("gh_")]

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
        "analysis_acres": analysis_acres,
        "total_acres": total_acres,
        "remainder": remainder,
        "remainder_percent": 100 * remainder / total_acres,
    }
