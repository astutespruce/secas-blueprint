from pathlib import Path

import numpy as np
import pandas as pd
import pygeos as pg
import geopandas as gp
import rasterio

from analysis.constants import (
    M2_ACRES,
    SLR_PROJ_COLUMNS,
    SLR_YEARS,
    SLR_PROJ_SCENARIOS,
)
from analysis.lib.raster import (
    detect_data_by_mask,
    extract_count_in_geometry,
    summarize_raster_by_units_grid,
)
from analysis.lib.geometry import to_dict


SLR_BINS = np.arange(11)


src_dir = Path("data/inputs/threats/slr")
depth_filename = src_dir / "slr.tif"
mask_filename = src_dir / "slr_mask.tif"
extent_filename = src_dir / "extracted_slr_bounds.feather"
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
    geometry : pygeos geometry

    Returns
    -------
    dict
        {
            "depth": [{
                "label": <label>,
                "acres": <acres>,
                "percent": <percent>
            }, ... <for each inundation depth>],
            "total_slr_acres": <acres within this dataset>,
            "notinundated_acres" : <acres not inundated by 10ft >,
            "notinundated_percent" : <percent not inundated by 10ft >,
            "projections": {
                <scenario>: [<depth in 2020>, <depth in 2030>, ... <depth in 2100>]
            }
        }
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

    # accumulate values
    slr_acres = np.cumsum(slr_acres)

    slr_results = [
        {
            "label": f"{i} {'foot' if i==1 else 'feet'}",
            "acres": acres,
            "percent": 100 * acres / rasterized_acres,
        }
        for i, acres in enumerate(slr_acres)
    ]

    # since areas not inundated are NODATA, and SLR is theoretically available
    # everywhere, use area not accounted for in inundated depth bins for this value
    not_inundated_acres = rasterized_acres - outside_se_acres - total_slr_acres
    if not_inundated_acres < 1e-6:
        not_inundated_acres = 0

    # intersect with 1-degree pixels; there should always be data available if
    # there are SLR depth data
    df = gp.read_feather(proj_filename)
    tree = pg.STRtree(df.geometry.values.data)
    df = df.iloc[tree.query(geometry, predicate="intersects")].copy()

    # calculate area-weighted means
    intersection_area = pg.area(pg.intersection(df.geometry.values.data, geometry))
    area_factor = intersection_area / intersection_area.sum()

    projections = df[SLR_PROJ_COLUMNS].multiply(area_factor, axis=0).sum().round(2)

    projections = {
        SLR_PROJ_SCENARIOS[scenario]: [
            projections[f"{year}_{scenario}"] for year in SLR_YEARS
        ]
        for scenario in SLR_PROJ_SCENARIOS
    }

    results = {
        "depth": slr_results,
        "total_slr_acres": total_slr_acres,
        "notinundated_acres": not_inundated_acres,
        "notinundated_percent": 100 * not_inundated_acres / rasterized_acres,
        "projections": projections,
    }

    return results


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

    # prescreen to areas that overlap with SLR inundation depth extent
    slr_extent = gp.read_feather(extent_filename, columns=[])
    tree = pg.STRtree(df.geometry.values.data)
    ix = tree.query_bulk(slr_extent.geometry.values.data, predicate="intersects")[1]
    df = df.take(np.unique(ix))

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

        # accumulate values
        slr_acres = np.cumsum(slr_acres, axis=1)

    # since areas not inundated are NODATA, and SLR is theoretically available
    # everywhere, use area not accounted for in inundated depth bins for this value
    not_inundated_acres = df.rasterized_acres - df.outside_se - total_slr_acres
    not_inundated_acres[not_inundated_acres < 1e-6] = 0

    slr = pd.DataFrame(
        slr_acres,
        columns=[f"depth_{v}" for v in SLR_BINS],
        index=df.index,
    )
    slr["not_inundated"] = not_inundated_acres

    proj = gp.read_feather(proj_filename)
    tree = pg.STRtree(df.geometry.values.data)
    left, right = tree.query_bulk(proj.geometry.values.data, predicate="intersects")

    # for each unit, calculate the area-weighted mean
    tmp = pd.DataFrame(
        {
            "geometry": df.geometry.values.data.take(right),
            "proj": proj.index.values.take(left),
            "proj_geometry": proj.geometry.values.data.take(left),
        },
        index=df.index.values.take(right),
    ).join(proj[SLR_PROJ_COLUMNS], on="proj")

    tmp["intersection_area"] = pg.area(
        pg.intersection(tmp.geometry.values.data, tmp.proj_geometry.values)
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
