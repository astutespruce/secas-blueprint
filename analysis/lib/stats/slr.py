from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
import rasterio
import shapely

from analysis.constants import (
    M2_ACRES,
    SLR_DEPTH_BINS,
    SLR_NODATA_VALUES,
    SLR_NODATA_COLS,
    SLR_PROJ_COLUMNS,
    SLR_YEARS,
    SLR_PROJ_SCENARIOS,
)
from analysis.lib.raster import (
    detect_data_by_mask,
    extract_count_in_geometry,
    summarize_raster_by_units_grid,
)
from analysis.lib.stats.summary_units import read_unit_from_feather


SLR_BINS = SLR_DEPTH_BINS + [v["value"] for v in SLR_NODATA_VALUES]


src_dir = Path("data/inputs/threats/slr")
depth_filename = src_dir / "slr.tif"
mask_filename = src_dir / "slr_mask.tif"
proj_filename = src_dir / "noaa_1deg_cells.feather"
results_filename = "data/results/huc12/slr.feather"


def extract_slr_by_mask_and_geometry(
    shape_mask,
    window,
    cellsize,
    prescreen_mask,
    prescreen_window,
    rasterized_acres,
    outside_se_acres,
    geometry,
    **kwargs,
):
    """Calculate area inundated at each depth level based on shape_mask and
    projections by NOAA scenario and decade based on geometry

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
    geometry : shapely geometry

    Returns
    -------
    dict
        {
            "depth": [{
                "label": <label>,
                "acres": <acres>,
                "percent": <percent>
            }, ... <for each inundation depth and NODATA type>],
            "total_slr_acres": <acres within this dataset>,
            "projections": {
                <scenario>: [<depth in 2020>, <depth in 2030>, ... <depth in 2100>]
            }
        }
        OR
        {
            "na": True <if only in inland areas>
        }
        OR
        None if there is only NODATA / areas not modeled
    """
    # prescreen to make sure data are present
    with rasterio.open(mask_filename) as src:
        if not detect_data_by_mask(src, prescreen_mask, prescreen_window):
            return None

    slr_acres = (
        extract_count_in_geometry(
            depth_filename, shape_mask, window, bins=SLR_BINS, boundless=True
        )
        * cellsize
    )
    total_slr_acres = slr_acres.sum()
    slr_nodata_acres = rasterized_acres - outside_se_acres - total_slr_acres

    if slr_nodata_acres < 1e-6:
        slr_nodata_acres = 0

    # combine areas not modeled with SLR nodata areas
    slr_acres[13] += slr_nodata_acres

    # if all areas in the polygon have no SLR data, return None
    if np.allclose(slr_acres[13], rasterized_acres):
        return None

    # if the only value present is for inland areas where not applicable, show that message
    if np.allclose(slr_acres[12], rasterized_acres):
        return {"na": True}

    # accumulate values for 0-10ft
    slr_acres[:11] = np.cumsum(slr_acres[:11])

    slr_results = [
        {
            "value": i,
            "label": f"{i} {'foot' if i==1 else 'feet'}",
            "acres": acres,
            "percent": 100 * acres / rasterized_acres,
        }
        for i, acres in enumerate(slr_acres[:11])
    ] + [
        {
            **v,
            "acres": slr_acres[v["value"]],
            "percent": 100 * slr_acres[v["value"]] / rasterized_acres,
        }
        for v in SLR_NODATA_VALUES
        if slr_acres[v["value"]] > 0
    ]

    # intersect with 1-degree pixels; there should always be data available if
    # there are SLR depth data
    df = gp.read_feather(proj_filename)
    tree = shapely.STRtree(df.geometry.values)
    df = df.iloc[tree.query(geometry, predicate="intersects")].copy()

    # calculate area-weighted means
    intersection_area = shapely.area(shapely.intersection(df.geometry.values, geometry))
    area_factor = intersection_area / intersection_area.sum()

    projections = df[SLR_PROJ_COLUMNS].multiply(area_factor, axis=0).sum().round(2)

    projections = {
        SLR_PROJ_SCENARIOS[scenario]: [
            projections[f"{year}_{scenario}"] for year in SLR_YEARS
        ]
        for scenario in SLR_PROJ_SCENARIOS
    }

    return {
        "depth": slr_results,
        "total_slr_acres": total_slr_acres,
        "projections": projections,
    }


def summarize_slr_by_units_grid(df, units_grid, out_dir):
    """Summarize by SLR inundation depth and projections by HUC12

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

    with rasterio.open(depth_filename) as value_dataset:
        cellsize = value_dataset.res[0] * value_dataset.res[0] * M2_ACRES

        slr_acres = (
            summarize_raster_by_units_grid(
                df,
                units_grid,
                value_dataset,
                bins=SLR_BINS,
                progress_label="Summarizing SLR inundation depth",
            )
            * cellsize
        )

        total_slr_acres = slr_acres.sum(axis=1)

        slr_nodata_acres = df.rasterized_acres - df.outside_se - total_slr_acres

        slr_nodata_acres[slr_nodata_acres < 1e-6] = 0

        # combine areas not modeled with SLR nodata areas
        slr_acres[:, 13] += slr_nodata_acres

        # accumulate values for bins 0-10
        slr_acres[:, :11] = np.cumsum(slr_acres[:, :11], axis=1)

    depth_cols = [f"depth_{v}" for v in SLR_DEPTH_BINS]
    cols = depth_cols + SLR_NODATA_COLS

    slr = pd.DataFrame(
        slr_acres,
        columns=cols,
        index=df.index,
    )

    # only calculate projections where there is data [:12]
    # (exclude not modeled / inland counties)
    ix = slr.loc[slr[depth_cols + ["not_inundated"]].sum(axis=1) > 0].index.values
    subset = df.loc[ix]

    proj = gp.read_feather(proj_filename)
    tree = shapely.STRtree(subset.geometry.values)
    left, right = tree.query(proj.geometry.values, predicate="intersects")

    # for each unit, calculate the area-weighted mean
    tmp = pd.DataFrame(
        {
            "geometry": subset.geometry.values.take(right),
            "proj": proj.index.values.take(left),
            "proj_geometry": proj.geometry.values.take(left),
        },
        index=subset.index.values.take(right),
    ).join(proj[SLR_PROJ_COLUMNS], on="proj")

    tmp["intersection_area"] = shapely.area(
        shapely.intersection(tmp.geometry.values, tmp.proj_geometry.values)
    )
    tmp = tmp.join(
        tmp.groupby(level=0).intersection_area.sum().rename("total_intersection_area")
    )
    tmp["area_factor"] = tmp.intersection_area / tmp.total_intersection_area

    for col in SLR_PROJ_COLUMNS:
        tmp[col] = tmp[col] * tmp.area_factor

    tmp = tmp[SLR_PROJ_COLUMNS].groupby(level=0).sum()

    slr = slr.join(tmp)

    slr.reset_index().to_feather(out_dir / "slr.feather")


def get_slr_unit_results(results_dir, unit_id, rasterized_acres):
    """Get SLR depth and projection results for unit_id

    Parameters
    ----------
    results_dir : Path
    unit_id : str
    rasterized_acres : float

    Returns
    -------
    dict (empty if no SLR data available for unit_id)
        {
            "depth": [{
                "label": <label>,
                "acres": <acres>,
                "percent": <percent>
            }, ... <for each inundation depth>],
            "notinundated_acres" : <acres not inundated by 10ft >,
            "notinundated_percent" : <percent not inundated by 10ft >,
            "projections": {
                <scenario>: [<depth in 2020>, <depth in 2030>, ... <depth in 2100>]
            }
        }
    """
    slr_results = read_unit_from_feather(results_dir / "slr.feather", unit_id)
    if len(slr_results) == 0:
        return {}

    unit = slr_results.iloc[0]

    # if all areas in the polygon have no SLR data, return None
    if np.allclose(unit.nodata, rasterized_acres):
        return {}

    # if the only value present is for inland areas where not applicable, show that message
    if np.allclose(unit.not_applicable, rasterized_acres):
        return {"na": True}

    depth = [
        {
            "value": i,
            "label": f"{i} {'foot' if i==1 else 'feet'}",
            "acres": unit[f"depth_{i}"],
            "percent": 100 * unit[f"depth_{i}"] / rasterized_acres,
        }
        for i in SLR_DEPTH_BINS
    ] + [
        {
            **v,
            "acres": unit[col],
            "percent": 100 * unit[col] / rasterized_acres,
        }
        for col, v in zip(SLR_NODATA_COLS, SLR_NODATA_VALUES)
        if unit[col] > 0
    ]

    projections = {
        SLR_PROJ_SCENARIOS[scenario]: [unit[f"{year}_{scenario}"] for year in SLR_YEARS]
        for scenario in SLR_PROJ_SCENARIOS
    }

    return {
        "depth": depth,
        "notinundated_acres": unit.not_inundated,
        "notinundated_percent": 100 * unit.not_inundated / rasterized_acres,
        "projections": projections,
    }
