import math
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.features import bounds
from rasterio.mask import raster_geometry_mask, geometry_mask
from rasterio.windows import Window

from analysis.constants import (
    BLUEPRINT,
    INPUT_AREA_VALUES,
    HUBS_CONNECTORS,
    URBAN_YEARS,
    ACRES_PRECISION,
    M2_ACRES,
)
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    detect_data,
)


src_dir = Path("data/inputs")
indicators_dir = src_dir / "indicators"
continuous_indicator_dir = Path("data/continuous_indicators")
blueprint_filename = src_dir / "se_blueprint2020.tif"
bp_inputs_filename = src_dir / "input_areas.tif"
hubs_connectors_filename = src_dir / "hubs_connectors.tif"
urban_dir = src_dir / "threats/urban"
slr_dir = src_dir / "threats/slr"


def extract_blueprint_area(geometries, bounds):
    """Calculate the area of overlap between geometries and Blueprint and hubs /
    connectors.

    NOTE: Blueprint and hubs / connectors are on the same grid

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    dict or None (if does not overlap Blueprint data)
        {"shape_mask": <shape_mask_area>, "blueprint": [...], "hubs_connectors": [...]}
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
    # NOTE: this does not detect that area is completely outside SA area
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

    # prescreen area to make sure data are present
    with rasterio.open(
        str(hubs_connectors_filename).replace(".tif", "_mask.tif")
    ) as src:
        if not detect_data(src, geometries, bounds):
            results["hubs_connectors"] = np.array([0, 0], dtype="uint")
            return results

    hubs_connectors_counts = extract_count_in_geometry(
        hubs_connectors_filename,
        shape_mask,
        window,
        np.arange(len(HUBS_CONNECTORS)),
        boundless=True,
    )
    results["hubs_connectors"] = (
        (hubs_connectors_counts * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    return results


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
    with rasterio.open(urban_dir / "urban_mask.tif") as src:
        if not detect_data(src, geometries, bounds):
            return None

    # create mask and window
    with rasterio.open(urban_dir / "urban_2020.tif") as src:
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
        filename = urban_dir / f"urban_{year}.tif"
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
