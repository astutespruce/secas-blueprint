import math
from pathlib import Path

from progress.bar import Bar
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
from analysis.lib.pygeos_util import to_dict


src_dir = Path("data/inputs/threats/urban")
results_filename = "data/results/huc12/urban.feather"


def extract_by_geometry(geometries, bounds):
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
                src, geometries, bounds, all_touched=False
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


def summarize_by_huc12(geometries):
    """Calculate current and projected urbanization for each decade from 2020 to
    2100.

    Parameters
    ----------
    geometries : Series of pygeos geometries, indexed by HUC12 id
    """

    index = []
    results = []
    for huc12, geometry in Bar(
        "Calculating Urbanization counts for HUC12", max=len(geometries)
    ).iter(geometries.iteritems()):
        zone_results = extract_by_geometry(
            [to_dict(geometry)], bounds=pg.total_bounds(geometry)
        )
        if zone_results is None:
            continue

        index.append(huc12)
        results.append(zone_results)

    cols = ["shape_mask", "urban"] + URBAN_YEARS
    df = pd.DataFrame(results, index=index)[cols]
    df = df.reset_index().rename(columns={"index": "id"}).round()
    df.columns = [str(c) for c in df.columns]

    df.to_feather(results_filename)
