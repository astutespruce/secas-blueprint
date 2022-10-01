from pathlib import Path

from progress.bar import Bar
import numpy as np
import pandas as pd
import pygeos as pg
import geopandas as gp
import rasterio

from analysis.constants import (
    ACRES_PRECISION,
    M2_ACRES,
    SLR_PROJ_COLUMNS,
    SLR_YEARS,
    SLR_PROJ_SCENARIOS,
)
from analysis.lib.raster import (
    detect_data_by_mask,
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
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


def summarize_by_huc12(geometries):
    """Summarize by HUC12

    Parameters
    ----------
    geometries : Series of pygeos geometries, indexed by HUC12 id
    """

    # find the indexes of the geometries that overlap with SLR bounds; these are the only
    # ones that need to be analyzed for SLR impacts

    slr_mask = gp.read_feather(extent_filename)

    ix = np.unique(
        pg.STRtree(geometries).query_bulk(
            slr_mask.geometry.values.data, predicate="intersects"
        )[1]
    )
    geometries = geometries.take(ix)

    results = []
    index = []
    for huc12, geometry in Bar(
        "Calculating SLR counts for HUC12", max=len(geometries)
    ).iter(geometries.iteritems()):
        zone_results = extract_by_geometry(
            geometry, [to_dict(geometry)], bounds=pg.total_bounds(geometry)
        )
        if zone_results is None:
            continue

        index.append(huc12)
        results.append(zone_results)

    df = pd.DataFrame(results, index=index)

    df = (
        df[["shape_mask"] + list(df.columns.difference(["shape_mask"]))]
        .reset_index()
        .rename(columns={"index": "id"})
        .round()
    )
    df.to_feather(results_filename)
