import math
from pathlib import Path

import numpy as np
import pandas as pd
import pygeos as pg
import rasterio
from rasterio.mask import raster_geometry_mask
from rasterio.windows import Window

from analysis.constants import URBAN_YEARS, ACRES_PRECISION, M2_ACRES
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    detect_data,
)


src_dir = Path("data/inputs/threats/urban")


def extract_urbanization_area(geometries, bounds):
    """Calculate the area of overlap between geometries and urbanization
    for each decade from 2020 to 2100.

    This is only applicable to inland (non-marine) areas.

    NOTE: urbanization is on a 60m grid

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    dict
        keys are mask, <decade>, ...
        values are the total acres of urbanization for each decade
    """
    results = {}

    # prescreen to make sure data are present
    with rasterio.open(src_dir / "urban_mask.tif") as src:
        if not detect_data(src, geometries, bounds):
            return None

    # create mask and window
    with rasterio.open(src_dir / "urban_2020.tif") as src:
        try:
            shape_mask, transform, window = boundless_raster_geometry_mask(
                src, geometries, bounds, all_touched=True
            )

        except ValueError:
            return None

        # square meters to acres
        cellsize = src.res[0] * src.res[1] * M2_ACRES

    results["shape_mask"] = (
        ((~shape_mask).sum() * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    if results["shape_mask"] == 0:
        return None

    # values are probability of urbanization per timestep * 1000 (uint16)
    # NOTE: index 0 = not predicted to urbanize
    # index 1 = already urban, so given a probability of 1
    # actual probabilities start at 0.025
    probabilities = (
        np.array(
            [
                0,
                1000,
                25,
                50,
                100,
                200,
                300,
                400,
                500,
                600,
                700,
                800,
                900,
                950,
                975,
                1000,
            ]
        )
        / 1000
    )
    bins = np.arange(0, len(probabilities))

    for year in URBAN_YEARS:
        filename = src_dir / f"urban_{year}.tif"
        counts = extract_count_in_geometry(
            filename, shape_mask, window, bins, boundless=True
        )

        if year == 2020:
            # extract area already urban (in index 1)
            results["urban"] = (
                (counts[1] * cellsize).round(ACRES_PRECISION).astype("float32")
            )

        # total urbanization is sum of pixel counts * probability
        results[year] = (
            ((counts * probabilities).sum() * cellsize)
            .round(ACRES_PRECISION)
            .astype("float32")
        )

    return results
