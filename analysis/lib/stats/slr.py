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
from analysis.lib.raster import summarize_raster_by_units_grid
from analysis.lib.stats.summary_units import read_unit_from_feather


SLR_BINS = SLR_DEPTH_BINS + [v["value"] for v in SLR_NODATA_VALUES]


src_dir = Path("data/inputs/threats/slr")
depth_filename = src_dir / "slr.tif"
mask_filename = src_dir / "slr_mask.tif"
proj_filename = src_dir / "noaa_1deg_cells.feather"


def summarize_slr_in_aoi(rasterized_geometry, geometry):
    """Calculate area inundated at each depth level based on shape_mask and
    projections by NOAA scenario and decade based on geometry

    Parameters
    ----------
    rasterized_geometry : RasterizedGeometry
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
        None if there is only NODATA
    """

    # prescreen to make sure data are present
    with rasterio.open(mask_filename) as src:
        if not rasterized_geometry.detect_data(src):
            return None

    with rasterio.open(depth_filename) as src:
        slr_acres = rasterized_geometry.get_acres_by_bin(src, bins=SLR_BINS)

    total_slr_acres = slr_acres.sum()
    slr_nodata_acres = (
        rasterized_geometry.acres
        - rasterized_geometry.outside_se_acres
        - total_slr_acres
    )

    if slr_nodata_acres < 1e-6:
        slr_nodata_acres = 0

    # set NODATA into value 13
    slr_acres[13] += slr_nodata_acres

    # if all areas in the polygon have no SLR data, return None
    if np.allclose(slr_acres[13], rasterized_geometry.acres):
        return None

    # if the only value present is for inland areas where not applicable, show that message
    # also, if it is a mix of inland areas and nodata, just default to NA as well
    if np.allclose(slr_acres[12], rasterized_geometry.acres) or (
        (slr_acres[12] > 0) and slr_acres[:11].sum() == 0
    ):
        return {"na": True}

    # accumulate values for 0-10ft
    slr_acres[:11] = np.cumsum(slr_acres[:11])

    slr_results = [
        {
            "value": i,
            "label": f"{i} {'foot' if i==1 else 'feet'}",
            "acres": acres,
            "percent": 100 * acres / rasterized_geometry.acres,
        }
        for i, acres in enumerate(slr_acres[:11])
    ] + [
        {
            **v,
            "acres": slr_acres[v["value"]],
            "percent": 100 * slr_acres[v["value"]] / rasterized_geometry.acres,
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

    # set NODATA into value 13
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
    slr["total_slr_acres"] = total_slr_acres

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


def get_slr_unit_results(results_dir, unit):
    """Get SLR depth and projection results for unit_id

    Parameters
    ----------
    results_dir : Path
    unit : pandas.Series
        row for this unit from the units dataset, indexed by unit ID (unit.name)

    Returns
    -------
    dict (empty if no SLR data available for unit_id)
        {
            "depth": [{
                "label": <label>,
                "acres": <acres>,
                "percent": <percent>
            }, ... <for each inundation depth>],
            "projections": {
                <scenario>: [<depth in 2020>, <depth in 2030>, ... <depth in 2100>]
            }
        }
    """
    slr_results = read_unit_from_feather(results_dir / "slr.feather", unit.name)
    if len(slr_results) == 0:
        return None

    slr_results = slr_results.iloc[0]

    # if all areas in the polygon have no SLR data, return None
    if np.allclose(slr_results.nodata, unit.rasterized_acres):
        return None

    # if the only value present is for inland areas where not applicable, show that message
    # also, if it is a mix of inland areas and nodata, just default to NA as well
    if np.allclose(slr_results.not_applicable, unit.rasterized_acres) or (
        slr_results.not_applicable > 0
        and sum(slr_results[f"depth_{i}"] for i in SLR_DEPTH_BINS) == 0
    ):
        return {"na": True}

    depth = [
        {
            "value": i,
            "label": f"{i} {'foot' if i==1 else 'feet'}",
            "acres": slr_results[f"depth_{i}"],
            "percent": 100 * slr_results[f"depth_{i}"] / unit.rasterized_acres,
        }
        for i in SLR_DEPTH_BINS
    ] + [
        {
            **v,
            "acres": slr_results[col],
            "percent": 100 * slr_results[col] / unit.rasterized_acres,
        }
        for col, v in zip(SLR_NODATA_COLS, SLR_NODATA_VALUES)
        if slr_results[col] > 0
    ]

    projections = None

    if pd.notnull(slr_results[f"{SLR_YEARS[0]}_{list(SLR_PROJ_SCENARIOS.keys())[0]}"]):
        projections = {
            SLR_PROJ_SCENARIOS[scenario]: [
                slr_results[f"{year}_{scenario}"].round(2) for year in SLR_YEARS
            ]
            for scenario in SLR_PROJ_SCENARIOS
        }

    return {
        "depth": depth,
        "total_slr_acres": slr_results.total_slr_acres,
        "projections": projections,
    }
