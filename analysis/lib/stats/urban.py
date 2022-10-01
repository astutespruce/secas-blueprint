from pathlib import Path

from progress.bar import Bar
import numpy as np
import pandas as pd
import pygeos as pg
import rasterio

from analysis.constants import URBAN_YEARS, ACRES_PRECISION, M2_ACRES
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    detect_data_by_mask,
)
from analysis.lib.geometry import to_dict


src_dir = Path("data/inputs/threats/urban")
mask_filename = src_dir / "urban_mask.tif"
results_filename = "data/results/huc12/urban.feather"


def extract_urban_by_mask(
    shape_mask,
    window,
    cellsize,
    prescreen_mask,
    prescreen_window,
    rasterized_acres,
    outside_se_acres,
    **kwargs,
):
    """Calculate area of current urban and projected urbanization by decade
    based on shape_mask

    Parameters
    ----------
    shape_mask : 2d array
        True outside shapes
    window : rasterio.windows.Window
        read window for Southeast standard origin
    cellsize : float
        pixel area in acres
    prescreen_mask : 2d array
        True outside shapes, at lower resolution
    prescreen_window : rasterio.windows.Window
        read window for Southeast standard origin at lower resolution
    rasterized_acres : float
        rasterized area of shape mask
    outside_se_acres : float
        acres outside SE Blueprint

    Returns
    -------
    dict
        {
            "entries": [{
                "label": <label>,
                "acres": <acres>,
                "percent": <percent>
            }, ... <for current urban, projected urban, and area not urbanized by 2100 (if any)>],
            "total_urban_acres": <acres within this dataset>,
            "outside_urban_acres": <acres outside this dataset but within SE>,
            "outside_urban_percent": <percent outside this dataset but within SE>,
            "noturban_2100_acres": <acres not urbanized by 2100>,
            "noturban_2100_percent": <percent not urbanized by 2100>,
            "percent_increase_by_2060": <percent of (2060-2019) / 2019>
        }
    """
    # prescreen to make sure data are present
    with rasterio.open(mask_filename) as src:
        if not detect_data_by_mask(src, prescreen_mask, prescreen_window):
            return None

    # values are number of runs out of 50 that are predicted to urbanize
    # 51 = urban as of 2019 (NLCD)
    # NOTE: index 0 = not predicted to urbanize
    probabilities = np.append(np.arange(0, 51) / 50.0, np.array([1.0]))
    bins = np.arange(0, len(probabilities))

    urban_results = []
    for year in URBAN_YEARS:
        filename = src_dir / f"urban_{year}.tif"
        urban_acres = (
            extract_count_in_geometry(
                filename, shape_mask, window, bins, boundless=True
            )
            * cellsize
        )
        total_urban_acres = urban_acres.sum()
        outside_urban_acres = rasterized_acres - outside_se_acres - total_urban_acres
        if outside_urban_acres < 1e-6:
            outside_urban_acres = 0

        if year == 2020:
            # extract area already urban (in index 51)
            urban_results.append(
                {
                    "label": "Urban in 2019",
                    "acres": urban_acres[51],
                    "percent": 100 * urban_acres[51] / rasterized_acres,
                }
            )

        # total urbanization is sum of acres by probability bin * probability
        projected_acres = (urban_acres * probabilities).sum()
        urban_results.append(
            {
                "year": year,
                "label": f"{year} projected extent",
                "acres": projected_acres,
                "percent": 100 * projected_acres / rasterized_acres,
            }
        )

    already_urban_acres = urban_results[0]["acres"]
    urban_2060_acres = urban_results[5]["acres"]
    noturban_2100_acres = urban_acres[0]  # set to 2100 by last loop

    results = {
        "entries": urban_results,
        "total_urban_acres": total_urban_acres,
        "outside_urban_acres": outside_urban_acres,
        "outside_urban_percent": 100 * outside_urban_acres / rasterized_acres,
        "percent_increase_by_2060": 100
        * (urban_2060_acres - already_urban_acres)
        / already_urban_acres
        if already_urban_acres
        else 0,
        "noturban_2100_acres": noturban_2100_acres,
        "noturban_2100_percent": 100 * noturban_2100_acres / rasterized_acres,
    }

    return results


def summarize_by_huc12(geometries):
    """Calculate current and projected urbanization for each decade from 2020 to
    2100

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
