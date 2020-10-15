import math
from pathlib import Path

import numpy as np
import pandas as pd
import pygeos as pg
import rasterio
from rasterio.mask import raster_geometry_mask
from rasterio.windows import Window

from analysis.constants import URBAN_YEARS, ACRES_PRECISION, M2_ACRES, INPUTS
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    detect_data,
)

src_dir = Path("data/inputs/indicators/gulf_hypoxia")
gulf_hypoxia_filename = src_dir / "gulf_hypoxia.tif"


def extract_gulf_hypoxia_area(geometries, bounds):
    """Calculate the area of overlap between geometries and Gulf Hypoxia dataset.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    dict or None (if does not overlap Gulf Hypoxia dataset)
    """

    results = {}

    # create mask and window
    with rasterio.open(gulf_hypoxia_filename) as src:
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

    max_value = INPUTS["gh"]["values"][-1]["value"]

    counts = extract_count_in_geometry(
        gulf_hypoxia_filename,
        shape_mask,
        window,
        np.arange(max_value + 1),
        boundless=True,
    )

    # there is no overlap
    if counts.max() == 0:
        return None

    results["gh"] = (counts * cellsize).round(ACRES_PRECISION).astype("float32")

    return results