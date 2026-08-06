from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
import shapely
import rasterio

from analysis.constants import M2_ACRES, PARCAS, PARCAS_POLY
from analysis.lib.io import read_unit_from_feather
from analysis.lib.raster import summarize_raster_by_units_grid


src_dir = Path("data/inputs")
filename = src_dir / PARCAS["filename"]
mask_filename = src_dir / PARCAS["filename"].replace(".tif", "_mask.tif")
boundary_filename = src_dir / PARCAS_POLY["filename"]

BINS = range(0, len(PARCAS["values"]))
LABELS = {e["value"]: e["label"] for e in PARCAS["values"]}


def extract_parcas_in_aoi(df):
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
    left, right = shapely.STRtree(parcas.geometry.values).query(tmp.geometry.values, predicate="intersects")

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
    if total_acres == 0:
        return None

    nodata_acres = rasterized_geometry.acres - rasterized_geometry.outside_se_acres - total_acres
    if nodata_acres < 1e-6:
        nodata_acres = 0

    # if only 0 values (not a PARCA) are present, ignore PARCAs
    if parca_acres[1:].max() == 0:
        return None

    entries = [
        {
            "value": i,
            "label": LABELS[i],
            "acres": acres.item(),
            "percent": (100 * acres / rasterized_geometry.acres).item(),
        }
        for i, acres in enumerate(parca_acres)
    ][::-1]

    parcas = extract_parcas_in_aoi(df)
    if parcas is not None:
        parcas = parcas.to_dict(orient="records")

    return {
        "entries": entries,
        "total_parca_acres": total_acres,
        "outside_parca_acres": nodata_acres,
        "outside_parca_percent": 100 * nodata_acres / rasterized_geometry.acres,
        "parcas": parcas,
    }


def extract_parcas_in_analysis_units(df):
    """Extract PARCAs and their area overlap with each analysis unit

    Parameters
    ----------
    df : GeoDataFrame
        uses index to aggregate results

    Returns
    -------
    DataFrame
        indexed on same index as df, returns list of dicts of name and acres per row in df
    """

    index_name = df.index.name or "index"
    columns = ["parca_id", "name", "description"]
    tmp = df.explode(ignore_index=False, index_parts=False)
    out_name = PARCAS_POLY["id"]

    # NOTE: we are ignoring description for this usage
    parcas = gp.read_feather(boundary_filename, columns=["geometry"] + columns)

    # find all PARCA polygons that intersect any part of the AOI
    left, right = shapely.STRtree(parcas.geometry.values).query(tmp.geometry.values, predicate="intersects")

    # no intersections
    if len(left) == 0:
        return None

    pairs = gp.GeoDataFrame(
        {
            "geometry": tmp.geometry.values.take(left),
            "index_right": parcas.index.values.take(right),
            "geometry_right": parcas.geometry.values.take(right),
        },
        index=pd.Index(tmp.index.values.take(left), name=index_name),
        geometry="geometry",
        crs=df.crs,
    )
    shapely.prepare(pairs.geometry.values)
    shapely.prepare(pairs.geometry_right.values)

    # if left completely contains right, the right geometry is the intersection
    left_contains = shapely.contains_properly(pairs.geometry.values, pairs.geometry_right.values)
    pairs.loc[left_contains, "geometry"] = pairs.loc[left_contains].geometry_right.values

    # if right completely contains the left, the left (geometry) are the intersection
    right_contains = ~left_contains & shapely.contains_properly(pairs.geometry.values, pairs.geometry_right.values)

    # any that aren't contained in either direction must be intersected
    ix = ~(left_contains | right_contains)
    pairs.loc[ix, "geometry"] = shapely.intersection(pairs.loc[ix].geometry.values, pairs.loc[ix].geometry_right.values)

    # explode and only keep polygons
    pairs = pairs.drop(columns=["geometry_right"]).explode(ignore_index=False, index_parts=False)
    pairs = pairs.loc[shapely.get_type_id(pairs.geometry.values) == 3]

    if len(pairs) == 0:
        return None

    # aggregate to multipolygons based on PARCA columns
    parcas = gp.GeoDataFrame(
        pairs.join(parcas[columns], on="index_right")
        .groupby([index_name] + columns)
        .agg({"geometry": shapely.multipolygons})
        .reset_index()
        .set_index(index_name),
        geometry="geometry",
        crs=df.crs,
    )

    parcas["acres"] = shapely.area(parcas.geometry.values) * M2_ACRES

    # transform to dict per original row
    parcas[out_name] = parcas[["name", "description", "acres"]].to_dict(orient="records")
    parcas = parcas[out_name].groupby(index_name).apply(np.array)

    out = df[[]].join(parcas)
    # fill with empty arrays
    out.loc[out[out_name].isnull(), out_name] = out[out_name].apply(lambda x: np.array([]))

    return out[out_name]


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

    if not len(df.columns.intersection({"value", "rasterized_acres", "outside_se"})) == 3:
        raise ValueError("GeoDataFrame for summary must include value, rasterized_acres, outside_se columns")

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

    parca_list = extract_parcas_in_aoi(tmp)
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
            "parcas": [{"name": <>, "description": <>}]
        }
    """

    unit_results = read_unit_from_feather(results_dir / "parcas.feather", unit.name)

    if len(unit_results) == 0:
        return None

    unit_results = unit_results.iloc[0]

    cols = [c for c in unit_results.index if c.startswith("parca_")]
    parca_acres = unit_results[cols].values

    # if only 0 values (not a PARCA) are present, ignore PARCAs
    if parca_acres[1:].max() == 0:
        return None

    parca_results = [
        {
            "value": entry["value"],
            "label": entry["label"],
            "acres": parca_acres[entry["value"]].item(),
            "percent": (100 * parca_acres[entry["value"]] / unit.rasterized_acres).item(),
        }
        for entry in PARCAS["values"]
    ][::-1]

    parcas = read_unit_from_feather(
        results_dir / "parcas_list.feather",
        unit.name,
        columns=["id", "name", "description"],
    ).to_dict(orient="records")

    return {
        "entries": parca_results,
        "total_parca_acres": unit_results.total_parca_acres,
        "outside_parca_acres": (unit_results.outside_parca_acres).item(),
        "outside_parca_percent": (100 * unit_results.outside_parca_acres / unit.rasterized_acres).item(),
        "parcas": parcas,
    }
