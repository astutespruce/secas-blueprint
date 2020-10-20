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
    FLORIDA_BOUNDS,
)
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    detect_data,
    summarize_raster_by_geometry,
)

src_dir = Path("data/inputs/indicators/florida")
sa_filename = src_dir / "fl_blueprint.tif"
sa_mask_filename = src_dir / "fl_blueprint_mask.tif"


def extract_by_geometry(geometries, bounds):
    """Calculate the area of overlap between geometries and Florida
    Conservation Blueprint dataset.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    dict or None (if does not overlap)
    """

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

    max_value = INPUTS["fl"]["values"][-1]["value"]

    counts = extract_count_in_geometry(
        sa_filename, shape_mask, window, np.arange(max_value + 1), boundless=True
    )

    # there is no overlap
    if counts.max() == 0:
        return None

    results["fl"] = (counts * cellsize).round(ACRES_PRECISION).astype("float32")

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
        outfilename=out_dir / "southatlantic.feather",
        progress_label="Calculating South Atlantic area by HUC12",
        bounds=FLORIDA_BOUNDS,
    )
