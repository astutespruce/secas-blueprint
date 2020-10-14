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


src_dir = Path("data/inputs/threats/slr")


def extract_slr_area(geometries, bounds):
    """Calculate the area of overlap between geometries and each level of SLR
    between 0 (currently inundated) and 6 meters.

    Values are cumulative; the total area inundated is added to each higher
    level of SLR

    This is only applicable to inland (non-marine) areas that are near the coast.

    NOTE: SLR is in a VRT with a cell size derived from the underlying rasters.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
        Should be limited to features that intersect with bounds of SLR datasets
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    dict
        keys are mask, <decade>, ...
        values are the area of incremental (not total!) sea level rise by foot
    """
    vrt = slr_dir / "slr.vrt"

    results = {}

    # create mask and window
    with rasterio.open(vrt) as src:
        try:
            shape_mask, transform, window = boundless_raster_geometry_mask(
                src, geometries, bounds, all_touched=True
            )

        except ValueError:
            return None

        # square meters to acres
        cellsize = src.res[0] * src.res[1] * M2_ACRES

        data = src.read(1, window=window, boundless=True)
        nodata = src.nodatavals[0]
        mask = (data == nodata) | shape_mask
        data = np.where(mask, nodata, data)

    results["shape_mask"] = (
        ((~shape_mask).sum() * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    if results["shape_mask"] == 0:
        return None

    bins = np.arange(7)
    counts = extract_count_in_geometry(
        vrt, shape_mask, window, bins=bins, boundless=True
    )

    # accumulate values
    for bin in bins[1:]:
        counts[bin] = counts[bin] + counts[bin - 1]

    acres = (counts * cellsize).round(ACRES_PRECISION).astype("float32")
    results.update({i: a for i, a in enumerate(acres)})

    return results
