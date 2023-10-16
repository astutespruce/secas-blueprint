from pathlib import Path

import numpy as np
import pandas as pd
import rasterio

from analysis.constants import M2_ACRES, URBAN_YEARS
from analysis.lib.raster import (
    clip_window,
    detect_data_by_mask,
    extract_count_in_geometry,
    summarize_raster_by_units_grid,
)
from analysis.lib.stats.summary_units import read_unit_from_feather

# values are number of runs out of 50 that are predicted to urbanize
# 51 = urban as of 2021 (NLCD)
# NOTE: index 0 = not predicted to urbanize
PROBABILITIES = np.append(np.arange(0, 51) / 50.0, np.array([1.0]))


src_dir = Path("data/inputs/threats/urban")
urban_filename = str(src_dir / "urban_{year}.tif")
mask_filename = src_dir / "urban_mask.tif"


def extract_urban_by_mask(
    mask_config,
):
    """Calculate area of current urban and projected urbanization by decade
    based on shape_mask

    Parameters
    ----------
    mask_config : AOIMaskConfig

    Returns
    -------
    dict
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
    rasterized_acres = mask_config.mask_acres
    outside_se_acres = mask_config.outside_se_acres
    cellsize = mask_config.cellsize

    # prescreen to make sure data are present
    with rasterio.open(mask_filename) as src:
        prescreen_window = mask_config.get_prescreen_window(src.transform)
        # use window clipped to extent of dataset to see if there is even
        # any overlap
        clipped_window = clip_window(prescreen_window, src.width, src.height)
        if not (
            clipped_window.width > 0
            and clipped_window.height > 0
            and detect_data_by_mask(src, mask_config.prescreen_mask, prescreen_window)
        ):
            return None

    bins = range(len(PROBABILITIES))

    urban_results = []
    for year in URBAN_YEARS:
        filename = urban_filename.format(year=year)
        urban_acres = (
            extract_count_in_geometry(filename, mask_config, bins, boundless=True)
            * cellsize
        )
        total_urban_acres = urban_acres.sum()
        outside_urban_acres = rasterized_acres - outside_se_acres - total_urban_acres
        if outside_urban_acres < 1e-6:
            outside_urban_acres = 0

        if year == 2030:
            # extract area already urban (in index 51)
            already_urban_acres = urban_acres[51]
            urban_results.append(
                {
                    "label": "Urban in 2021",
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
        {"urban_2021": already_urban_acres, f"urban_proj_{year}": projected_acres},
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


def get_urban_unit_results(results_dir, unit):
    """Get current and projected urbanization for the unit_id

    Parameters
    ----------
    results_dir : Path
    unit : pandas.Series
        row for this unit from the units dataset, indexed by unit ID (unit.name)

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
    urban_results = read_unit_from_feather(results_dir / "urban.feather", unit.name)
    if len(urban_results) == 0:
        return {}

    urban_results = urban_results.iloc[0]

    entries = [
        {
            "label": "Urban in 2021",
            "acres": urban_results.urban_2021,
            "percent": 100 * urban_results.urban_2021 / unit.rasterized_acres,
        }
    ] + [
        {
            "year": year,
            "label": f"{year} projected extent",
            "acres": urban_results[f"urban_proj_{year}"],
            "percent": 100
            * urban_results[f"urban_proj_{year}"]
            / unit.rasterized_acres,
        }
        for year in URBAN_YEARS
    ]

    return {
        "entries": entries,
        "outside_urban_acres": urban_results.outside_urban,
        "outside_urban_percent": 100
        * urban_results.outside_urban
        / unit.rasterized_acres,
        "nonzero_urban_2060_percent": 100
        * urban_results.nonzero_urban_2060
        / unit.rasterized_acres,
        "noturban_2100_acres": urban_results.noturban_2100,
        "noturban_2100_percent": 100
        * urban_results.noturban_2100
        / unit.rasterized_acres,
    }
