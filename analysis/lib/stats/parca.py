from pathlib import Path

import geopandas as gp
import pandas as pd
import shapely
import rasterio

from analysis.constants import M2_ACRES, PARCAS
from analysis.lib.raster import summarize_raster_by_units_grid

from analysis.lib.stats.summary_units import read_unit_from_feather


src_dir = Path("data/inputs/boundaries")
filename = src_dir / "parcas.tif"
mask_filename = src_dir / "parcas_mask.tif"
boundary_filename = src_dir / "parcas.feather"

BINS = range(0, len(PARCAS))
LABELS = {e["value"]: e["label"] for e in PARCAS}


def extract_parcas(df):
    """Extract intersection with PARCAs

        Parameters
        ----------
    df : GeoDataFrame
        area of interest

        Returns
        -------
        GeoDataFrame
            indexed on index of df (multiple records per index value); includes
            geometry field with the geometric intersection and acres calculated from
            that field

    """

    parcas = gp.read_feather(boundary_filename)

    # find all protected areas polygons that intersect any part of the AOI
    tmp = df.explode(ignore_index=False, index_parts=False)
    left, right = shapely.STRtree(parcas.geometry.values).query(
        tmp.geometry.values, predicate="intersects"
    )

    # no intersections
    if len(left) == 0:
        return None

    index_name = df.index.name or "index"
    results = (
        pd.DataFrame(
            {
                index_name: tmp.index.values.take(left),
                "parca_id": parcas.parca_id.values.take(right),
                "name": parcas.name.values.take(right),
                "description": parcas.description.values.take(right),
            }
        )
        # PARCA dataset has multiple polygons per PARCA boundary, group them back together
        .groupby([index_name, "parca_id"])
        .first()
        .reset_index()
        .sort_values(by=[index_name, "name"])
    )

    return results


def summarize_parcas_in_aoi(rasterized_geometry, df):
    """Calculate area in parcas

    Parameters
    ----------
    rasterized_geometry : RasterizedGeometry
    df : GeoDataFrame
        area of interest

    Returns
    -------
    dict or None
        {
            "entries": [{"value": <>, "label": <>, "acres": <>, "percent": <>}, ...],
            "total_parca_acres": <total_acres>,
            "outside_parca_acres": <nodata acres>,
            "outside_parca_percent": <nodata percent>,
            parcas": [{"name": <>, "description": <>}],
        }
    """

    # prescreen to make sure data are present
    with rasterio.open(mask_filename) as src:
        if not rasterized_geometry.detect_data(src):
            return None

    with rasterio.open(filename) as src:
        parca_acres = rasterized_geometry.get_acres_by_bin(src, bins=BINS)

    total_acres = parca_acres.sum()
    nodata_acres = (
        rasterized_geometry.acres - rasterized_geometry.outside_se_acres - total_acres
    )

    if nodata_acres < 1e-6:
        nodata_acres = 0

    entries = [
        {
            "value": i,
            "label": LABELS[i],
            "acres": acres.item(),
            "percent": (100 * acres / rasterized_geometry.acres).item(),
        }
        for i, acres in enumerate(parca_acres)
    ][::-1]

    parcas = extract_parcas(df)
    if parcas is not None:
        parcas = parcas.to_dict(orient="records")

    return {
        "entries": entries,
        "total_parca_acres": total_acres,
        "outside_parca_acres": nodata_acres,
        "outside_parca_percent": 100 * nodata_acres / rasterized_geometry.acres,
        "parcas": parcas,
    }


def summarize_parcas_by_units(df, units_grid, out_dir):
    """Calculate overlap with PARCAs

    Parameters
    ----------
    df : GeoDataFrame
        contains unit boundaries, indexed by id
    units_grid : SummaryUnitGrid instance
    out_dir : str
    """
    print("Calculating overlap with PARCAs")

    if (
        not len(df.columns.intersection({"value", "rasterized_acres", "outside_se"}))
        == 3
    ):
        raise ValueError(
            "GeoDataFrame for summary must include value, rasterized_acres, outside_se columns"
        )

    with rasterio.open(filename) as value_dataset:
        cellsize = value_dataset.res[0] * value_dataset.res[0] * M2_ACRES

        parca_acres = (
            summarize_raster_by_units_grid(
                df,
                units_grid,
                value_dataset,
                bins=BINS,
                progress_label="Summarizing PARCAs",
            )
            * cellsize
        )

    total_acres = parca_acres.sum(axis=1)
    nodata_acres = df.rasterized_acres - df.outside_se - total_acres
    nodata_acres[nodata_acres < 1e-6] = 0

    parcas = pd.DataFrame(
        parca_acres,
        columns=[f"parca_{v}" for v in BINS],
        index=df.index,
    )
    parcas["total_parca_acres"] = total_acres
    parcas["outside_parca_acres"] = nodata_acres

    parcas.reset_index().to_feather(out_dir / "parcas.feather")

    # intersect with polygons
    tmp = df.loc[df.index.isin(parcas.loc[parcas.parca_1 > 0].index.values)].copy()

    parca_list = extract_parcas(tmp)
    parca_list.to_feather(out_dir / "parcas_list.feather")


def get_parca_unit_results(results_dir, unit):
    """Fetch protected areas results for the unit_id

    Parameters
    ----------
    results_dir : Path
        path containing results
    unit : pandas.Series
        row for this unit from the units dataset, indexed by unit ID (unit.name)

    Returns
    -------
    dict or None
        {
            "entries": [{"value": <>, "label": <>, "acres": <>, "percent": <>}, ...],
            "total_parca_acres": <total_acres>,
            "outside_parca_acres": <nodata acres>,
            "outside_parca_percent": <nodata percent>,
            "parcas": [{"name": <>, "owner": <>, "acres": <>}]
        }
    """

    unit_results = read_unit_from_feather(results_dir / "parcas.feather", unit.name)

    if len(unit_results) == 0:
        return None

    unit_results = unit_results.iloc[0]

    cols = [c for c in unit_results.index if c.startswith("parca_")]
    parca_acres = unit_results[cols].values

    parca_results = [
        {
            "value": entry["value"],
            "label": entry["label"],
            "acres": parca_acres[entry["value"]].item(),
            "percent": (
                100 * parca_acres[entry["value"]] / unit.rasterized_acres
            ).item(),
        }
        for entry in PARCAS
    ][::-1]

    parcas = read_unit_from_feather(results_dir / "parcas_list.feather", unit.name)

    return {
        "entries": parca_results,
        "total_parca_acres": unit_results.total_parca_acres,
        "outside_parca_acres": (unit_results.outside_parca_acres).item(),
        "outside_parca_percent": (
            100 * unit_results.outside_parca_acres / unit.rasterized_acres
        ).item(),
        "parcas": parcas,
    }
