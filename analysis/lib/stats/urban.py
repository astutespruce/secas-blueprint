from pathlib import Path

import numpy as np
import pandas as pd
import rasterio

from analysis.constants import M2_ACRES, URBAN_YEARS
from analysis.lib.raster import (
    detect_data_by_mask,
    extract_count_in_geometry,
    summarize_raster_by_units_grid,
)
from analysis.lib.stats.summary_units import read_unit_from_feather

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
            "nonzero_urban_2060_percent": <percent of area urbanized at any probability not already urbanized in 2019>
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
            already_urban_acres = urban_acres[51]
            urban_results.append(
                {
                    "label": "Urban in 2019",
                    "acres": already_urban_acres,
                    "percent": 100 * already_urban_acres / rasterized_acres,
                }
            )
        elif year == 2060:
            # amount of additional urbanization by 2060 for any probability
            # is the sum of area in all pixels >0  and not already urban
            nonzero_urban_2060_acres = urban_acres[1:51].sum()

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

    noturban_2100_acres = urban_acres[0]  # set to 2100 by last loop

    # if nothing is urban or projected to urbanize by 2100, return None
    if urban_acres[1:].max() == 0:
        return None

    results = {
        "entries": urban_results,
        "total_urban_acres": total_urban_acres,
        "outside_urban_acres": outside_urban_acres,
        "outside_urban_percent": 100 * outside_urban_acres / rasterized_acres,
        "nonzero_urban_2060_percent": 100 * nonzero_urban_2060_acres / rasterized_acres,
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

            if year == 2060:
                # amount of additional urbanization by 2060 for any probability
                # is the sum of area in all pixels >0  and not already urban
                nonzero_urban_2060_acres = urban_acres[:, 1:51].sum(axis=1)

            # total urbanization is sum of acres by probability bin * probability
            urban[f"urban_proj_{year}"] = (urban_acres * PROBABILITIES).sum(axis=1)

    urban["nonzero_urban_2060"] = nonzero_urban_2060_acres
    urban["noturban_2100"] = urban_acres[:, 0]  # set to 2100 by last loop
    urban["outside_urban"] = outside_urban_acres

    # if nothing is urban / projected to urbanize by 2100, return None
    if urban_acres[:, 1:].max() == 0:
        return None

    urban.reset_index().to_feather(out_dir / "urban.feather")


def get_urban_unit_results(results_dir, unit_id, rasterized_acres):
    """Get current and projected urbanization for the unit_id

    Parameters
    ----------
    results_dir : Path
    unit_id : str
    rasterized_acres : float

    Returns
    -------
    dict (empty if no results available for unit_id)
        {
            "entries": [{
                "label": <label>,
                "acres": <acres>,
                "percent": <percent>
            }, ... <for current urban, projected urban, and area not urbanized by 2100 (if any)>],
            "outside_urban_acres": <acres outside this dataset but within SE>,
            "outside_urban_percent": <percent outside this dataset but within SE>,
            "noturban_2100_acres": <acres not urbanized by 2100>,
            "noturban_2100_percent": <percent not urbanized by 2100>,
            "nonzero_urban_2060_percent": <percent of area urbanized at any probability not already urbanized in 2019>
        }
    """
    urban_results = read_unit_from_feather(results_dir / "urban.feather", unit_id)
    if len(urban_results) == 0:
        return {}

    unit = urban_results.iloc[0]

    entries = [
        {
            "label": "Urban in 2019",
            "acres": unit.urban_2019,
            "percent": 100 * unit.urban_2019 / rasterized_acres,
        }
    ] + [
        {
            "label": f"{year} projected extent",
            "acres": unit[f"urban_proj_{year}"],
            "percent": 100 * unit[f"urban_proj_{year}"] / rasterized_acres,
        }
        for year in URBAN_YEARS
    ]

    return {
        "entries": entries,
        "outside_urban_acres": unit.outside_urban,
        "outside_urban_percent": 100 * unit.outside_urban / rasterized_acres,
        "noturban_2100_acres": unit.noturban_2100,
        "noturban_2100_percent": 100 * unit.noturban_2100 / rasterized_acres,
        "nonzero_urban_2060_percent": 100 * unit.nonzero_urban_2060 / rasterized_acres,
    }
