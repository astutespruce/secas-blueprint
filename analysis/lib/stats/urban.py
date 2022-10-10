from pathlib import Path

from progress.bar import Bar
import numpy as np
import pandas as pd
import pygeos as pg
import rasterio

from analysis.constants import URBAN_YEARS, M2_ACRES
from analysis.lib.raster import (
    extract_count_in_geometry,
    detect_data_by_mask,
    summarize_raster_by_units_grid,
)


# values are number of runs out of 50 that are predicted to urbanize
# 51 = urban as of 2019 (NLCD)
# NOTE: index 0 = not predicted to urbanize
PROBABILITIES = np.append(np.arange(0, 51) / 50.0, np.array([1.0]))


src_dir = Path("data/inputs/threats/urban")
urban_filename = str(src_dir / "urban_{year}.tif")
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

    bins = np.arange(0, len(PROBABILITIES))

    urban_results = []
    for year in URBAN_YEARS:
        filename = urban_filename.format(year=year)
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
        projected_acres = (urban_acres * PROBABILITIES).sum()
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


def summarize_urban_by_units_grid(df, units_grid, out_dir):
    """Summarize urban by HUC12

    Parameters
    ----------
    df : GeoDataFrame
        must have a "value" column with same values as used for corresponding units
        raster, and must have result of df.bounds joined in
    units_grid : SummaryUnitGrid instance
    out_dir : str
    """

    if (
        not len(df.columns.intersection({"value", "rasterized_acres", "outside_se"}))
        == 3
    ):
        raise ValueError(
            "GeoDataFrame for summary must include value, rasterized_acres, outside_se columns"
        )

    bins = np.arange(0, len(PROBABILITIES))

    year = URBAN_YEARS[0]
    with rasterio.open(urban_filename.format(year=year)) as value_dataset:
        cellsize = value_dataset.res[0] * value_dataset.res[0] * M2_ACRES

        urban_acres = (
            summarize_raster_by_units_grid(
                df,
                units_grid,
                value_dataset,
                bins=bins,
                progress_label=f"Summarizing Urban {year}",
            )
            * cellsize
        )

        # total urbanization is sum of acres by probability bin * probability
        projected_acres = (urban_acres * PROBABILITIES).sum(axis=1)

    already_urban_acres = urban_acres[:, 51]
    total_urban_acres = urban_acres.sum(axis=1)
    outside_urban_acres = df.rasterized_acres - df.outside_se - total_urban_acres
    outside_urban_acres[outside_urban_acres < 1e-6] = 0

    urban = pd.DataFrame(
        {"urban_2019": already_urban_acres, f"urban_proj_{year}": projected_acres},
        index=df.index,
    )

    for year in URBAN_YEARS[1:]:
        with rasterio.open(urban_filename.format(year=year)) as value_dataset:
            cellsize = value_dataset.res[0] * value_dataset.res[0] * M2_ACRES

            urban_acres = (
                summarize_raster_by_units_grid(
                    df,
                    units_grid,
                    value_dataset,
                    bins=bins,
                    progress_label=f"Summarizing Urban {year}",
                )
                * cellsize
            )

            # total urbanization is sum of acres by probability bin * probability
            urban[f"urban_proj_{year}"] = (urban_acres * PROBABILITIES).sum(axis=1)

    urban["outside_urban"] = outside_urban_acres

    urban.reset_index().to_feather(out_dir / "urban.feather")
