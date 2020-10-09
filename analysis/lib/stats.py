import math
from pathlib import Path

import numpy as np
import pandas as pd
import pygeos as pg
import rasterio
from rasterio.features import bounds
from rasterio.mask import raster_geometry_mask, geometry_mask
from rasterio.windows import Window

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
    detect_data,
)
from analysis.pygeos_util import intersection


src_dir = Path("data/inputs")
blueprint_filename = src_dir / "se_blueprint2020.tif"
bp_inputs_filename = src_dir / "input_areas.tif"
urban_dir = src_dir / "threats/urban"
slr_dir = src_dir / "threats/slr"
chat_filename = src_dir / "indicators/chat/chat.feather"


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


def summarize_chat(df, chat_df, fields):
    """Calculate acres by value and area-weighted value for each CHAT field in fields.

    Parameters
    ----------
    df : GeoDataFrame
        area(s) of interest
    chat_df : GeoDataFrame
    fields : list-like of CHAT field names

    Returns
    -------
    dict of DataFrames, all indexed by incoming index
        {
            "total_acres": ...
            "acres": ...,
            "avg": ...
        }
    """
    df = intersection(df, chat_df)
    df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES
    df = df.loc[df.acres > 0].copy()

    if not len(df):
        return None

    index_name = df.index.name or "index"
    df = df.reset_index()

    results = {
        'total_acres': df.groupby(index_name).acres.sum().round(ACRES_PRECISION)
    }

    area_results = dict()
    avg_results = dict()
    for field in fields:
        grouped = df.groupby([index_name, field]).acres.sum().fillna(0).round(ACRES_PRECISION).reset_index()
        # create an array of [<acres for value 0>, <acres for value 1>,... ]
        area_results[field] = grouped.groupby("id").acres.apply(np.array)

        # exclude nodata to calculate area-weighted average
        values = grouped.loc[grouped[field]>0].set_index(index_name)
        total_acres = values.groupby(level=0).acres.sum().rename('total')
        values = values.join(total_acres)
        values['wtd_value'] = (values.acres / values.total) * values[field].astype('uint8')
        avg_results[field] = values.groupby(level=0).wtd_value.sum().round(1)

    results['acres'] = pd.DataFrame(area_results)
    results['avg'] = pd.DataFrame(avg_results)

    return results