import math
from pathlib import Path

import numpy as np
import pandas as pd
import pygeos as pg
import rasterio

from analysis.constants import (
    BLUEPRINT,
    INPUT_AREA_VALUES,
    URBAN_YEARS,
    ACRES_PRECISION,
    M2_ACRES,
)
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
)
from analysis.lib.pygeos_util import intersection


src_dir = Path("data/inputs")
blueprint_filename = src_dir / "se_blueprint2020.tif"
bp_inputs_filename = src_dir / "input_areas.tif"


def extract_blueprint_area(geometries, bounds):
    """Calculate the area of overlap between geometries and Blueprint grids.

    NOTE: Blueprint and inputs are on the same grid

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    dict or None (if does not overlap Blueprint data)
        {"shape_mask": <shape_mask_area>, "blueprint": [...], ...}
    """

    results = {}

    # create mask and window
    with rasterio.open(blueprint_filename) as src:
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

    blueprint_counts = extract_count_in_geometry(
        blueprint_filename,
        shape_mask,
        window,
        np.arange(len(BLUEPRINT)),
        boundless=True,
    )
    results["blueprint"] = (
        (blueprint_counts * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    bp_input_counts = extract_count_in_geometry(
        bp_inputs_filename,
        shape_mask,
        window,
        bins=range(0, len(INPUT_AREA_VALUES)),
        boundless=True,
    )
    results["inputs"] = (
        (bp_input_counts * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    return results

