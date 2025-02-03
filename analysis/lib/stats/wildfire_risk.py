from pathlib import Path

import pandas as pd
import rasterio

from analysis.constants import WILDFIRE_RISK, M2_ACRES
from analysis.lib.raster import summarize_raster_by_units_grid
from analysis.lib.stats.summary_units import (
    read_unit_from_feather,
)

data_dir = Path("data")
src_dir = data_dir / "inputs/threats/wildfire_risk"
filename = src_dir / "wildfire_risk.tif"
mask_filename = src_dir / "wildfire_risk_mask.tif"

WILDFIRE_RISK_BINS = range(0, len(WILDFIRE_RISK))
WILDFIRE_RISK_LABELS = {e["value"]: e["label"] for e in WILDFIRE_RISK}


def summarize_wildfire_risk_in_aoi(rasterized_geometry):
    """Calculate area in each probability bin based on rasterized_geometry

    Parameters
    ----------
    rasterized_geometry : RasterizedGeometry

    Returns
    -------
    dict
        {
            "entries": [
                {
                "label": <label>,
                "acres": <acres>,
                "percent": <percent>,
                }, ...
            ]
            "total_wildfire_risk_acres": <acres within this dataset>,
            "outside_wildfire_risk_acres": <acres outside this dataset but within SE>,
            "outside_wildfire_risk_percent": <percent outside this dataset but within SE>,
        }
        OR
        None if there is only NODATA
    """

    # prescreen to make sure data are present
    with rasterio.open(mask_filename) as src:
        if not rasterized_geometry.detect_data(src):
            return None

    with rasterio.open(filename) as src:
        wildfire_risk_acres = rasterized_geometry.get_acres_by_bin(
            src, bins=WILDFIRE_RISK_BINS
        )

    total_acres = wildfire_risk_acres.sum()
    nodata_acres = (
        rasterized_geometry.acres - rasterized_geometry.outside_se_acres - total_acres
    )

    if nodata_acres < 1e-6:
        nodata_acres = 0

    entries = [
        {
            "value": i,
            "label": WILDFIRE_RISK_LABELS[i],
            "acres": acres.item(),
            "percent": (100 * acres / rasterized_geometry.acres).item(),
        }
        for i, acres in enumerate(wildfire_risk_acres)
    ]

    return {
        "entries": entries,
        "total_wildfire_risk_acres": total_acres,
        "outside_wildfire_risk_acres": nodata_acres,
        "outside_wildfire_risk_percent": 100 * nodata_acres / rasterized_geometry.acres,
    }


def summarize_wildfire_risk_by_units_grid(df, units_grid, out_dir):
    """Summarize wildfire risk by HUC12

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

    with rasterio.open(filename) as value_dataset:
        cellsize = value_dataset.res[0] * value_dataset.res[0] * M2_ACRES

        wildfire_risk_acres = (
            summarize_raster_by_units_grid(
                df,
                units_grid,
                value_dataset,
                bins=WILDFIRE_RISK_BINS,
                progress_label="Summarizing wildfire risk",
            )
            * cellsize
        )

    total_acres = wildfire_risk_acres.sum(axis=1)
    nodata_acres = df.rasterized_acres - df.outside_se - total_acres
    nodata_acres[nodata_acres < 1e-6] = 0

    wildfire_risk = pd.DataFrame(
        wildfire_risk_acres,
        columns=[f"wildfire_risk_{v}" for v in WILDFIRE_RISK_BINS],
        index=df.index,
    )
    wildfire_risk["total_wildfire_risk_acres"] = total_acres
    wildfire_risk["outside_wildfire_risk_acres"] = nodata_acres

    wildfire_risk.reset_index().to_feather(out_dir / "wildfire_risk.feather")


def get_wildfire_risk_unit_results(results_dir, unit):
    """Get wildfire risk for the unit

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
            }, ... ],
            "outside_wildfire_risk_acres": <acres outside this dataset but within SE>,
            "outside_wildfire_risk_percent": <percent outside this dataset but within SE>,
        }
    """
    wildfire_risk_results = read_unit_from_feather(
        results_dir / "wildfire_risk.feather", unit.name
    )
    if len(wildfire_risk_results) == 0:
        return {}

    wildfire_risk_results = wildfire_risk_results.iloc[0]

    cols = [c for c in wildfire_risk_results.index if c.startswith("wildfire_risk_")]
    wildfire_risk_acres = wildfire_risk_results[cols].values

    wildfire_risk = [
        {
            "value": entry["value"],
            "label": entry["label"],
            "acres": wildfire_risk_acres[entry["value"]].item(),
            "percent": (
                100 * wildfire_risk_acres[entry["value"]] / unit.rasterized_acres
            ).item(),
        }
        for entry in WILDFIRE_RISK
    ]

    return {
        "entries": wildfire_risk,
        "total_wildfire_risk_acres": wildfire_risk_results.total_wildfire_risk_acres,
        "outside_wildfire_risk_acres": (
            wildfire_risk_results.outside_wildfire_risk_acres
        ).item(),
        "outside_wildfire_risk_percent": (
            100
            * wildfire_risk_results.outside_wildfire_risk_acres
            / unit.rasterized_acres
        ).item(),
    }
