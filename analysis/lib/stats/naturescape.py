import math
from pathlib import Path

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
    NATURESCAPE_BOUNDS,
)
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    summarize_raster_by_geometry,
    detect_data,
)

src_dir = Path("data/inputs/indicators/naturescape")
ns_filename = src_dir / "ns_priority.tif"
ns_mask_filename = src_dir / "ns_priority_mask.tif"


def extract_by_geometry(geometries, bounds):
    """Calculate the area of overlap between geometries and NatureScape dataset.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    dict or None (if does not overlap Nature's Network dataset)
    """

    # prescreen to make sure data are present
    with rasterio.open(ns_mask_filename) as src:
        if not detect_data(src, geometries, bounds):
            return None

    results = {}

    # create mask and window
    with rasterio.open(ns_filename) as src:
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

    max_value = INPUTS["app"]["values"][-1]["value"]

    counts = extract_count_in_geometry(
        ns_filename, shape_mask, window, np.arange(max_value + 1), boundless=True
    )

    # there is no overlap
    if counts.max() == 0:
        return None

    results["app"] = (counts * cellsize).round(ACRES_PRECISION).astype("float32")

    return results


def summarize_by_huc12(geometries, out_dir):
    """Summarize by HUC12

    Parameters
    ----------
    geometries : Series of pygeos geometries, indexed by HUC12 id
    out_dir : str
    """

    summarize_raster_by_geometry(
        geometries,
        extract_by_geometry,
        outfilename=out_dir / "naturescape.feather",
        progress_label="Calculating NatureScape area by HUC12",
        bounds=NATURESCAPE_BOUNDS,
    )
