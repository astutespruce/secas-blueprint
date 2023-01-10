from pathlib import Path

import pandas as pd
import rasterio
import shapely

from analysis.constants import (
    BLUEPRINT,
    INPUTS,
    M2_ACRES,
)
from analysis.lib.geometry import to_crs
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    summarize_raster_by_units_grid,
)
from analysis.lib.stats.ownership import get_lta_search_info
from analysis.lib.stats.summary_units import (
    read_unit_from_feather,
    huc12_filename,
    marine_filename,
)
from analysis.lib.util import pluck

data_dir = Path("data")
src_dir = data_dir / "inputs"
blueprint_filename = src_dir / "se_blueprint_2022.tif"
bp_inputs_filename = src_dir / "boundaries/input_areas.tif"
bp_inputs_mask_filename = src_dir / "boundaries/input_areas_mask.tif"


def get_shape_mask(shapes, bounds):
    """Calculate the area of overlap between geometries and Blueprint grids.

    NOTE: Blueprint and inputs are on the same grid

    Parameters
    ----------
    shapes : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    dict or None (if no overlap with Blueprint input areas)
        {
            'prescreen_origin': <xmin, ymax of lowres mask>,
            'prescreen_mask': <2d array, True outside shapes, at lower resolution>,
            'prescreen_window': rasterio.windows.Window <window for reading data based on lower resolution grid>
            'cellsize': <pixel area in acres>,
            'origin': <xmin, ymax>,
            'shape_mask': <2d array, True outside shapes>,
            'rasterized_area': <acres within rasterized shapes>,
            'window': rasterio.windows.Window <window for reading data based Southeast standard grid>
        }
    """

    # create lowres shape mask and window (used to presecreen some datasets)
    with rasterio.open(bp_inputs_mask_filename) as src:
        prescreen_mask, _, prescreen_window = boundless_raster_geometry_mask(
            src, shapes, bounds, all_touched=True
        )

        results = {
            "prescreen_origin": [src.transform.c, src.transform.f],
            "prescreen_mask": prescreen_mask,
            "prescreen_window": prescreen_window,
        }

    # create mask and window
    with rasterio.open(bp_inputs_filename) as src:
        shape_mask, _, window = boundless_raster_geometry_mask(
            src, shapes, bounds, all_touched=False
        )

        cellsize = src.res[0] * src.res[1] * M2_ACRES

        results.update(
            {
                "cellsize": cellsize,
                "origin": [src.transform.c, src.transform.f],
                "shape_mask": shape_mask,
                "rasterized_acres": (~shape_mask).sum() * cellsize,
                "window": window,
            }
        )

    return results


def extract_input_areas_by_mask(shape_mask, window, cellsize):
    """Extract stats of Blueprint input areas based on shape_mask.

    It is assumed that shape_mask has already been prescreened to ensure
    overlap with input areas.

    Parameters
    ----------
    shape_mask : 2d array
        True outside shapes
    window : rasterio.windows.Window
        read window for Southeast standard origin
    cellsize : float
        pixel area in acres

    Returns
    -------
    dict
        {
            "inside_se_acres": <acres within Blueprint inputs>,
            "inputs": {<id>: <acres>, ...},
            "promote_base": <True if base is only input present>
        }
    """
    counts = extract_count_in_geometry(
        bp_inputs_filename,
        shape_mask,
        window,
        bins=range(0, max(e["value"] for e in INPUTS.values()) + 1),
        boundless=True,
    )

    total_count = counts.sum()

    return {
        "inside_se_acres": (total_count * cellsize),
        "inputs": {
            e["id"]: (counts[e["value"]] * cellsize)
            for e in INPUTS.values()
            if counts[e["value"]]
        },
        # promote base blueprint if it is the only input present
        "promote_base": counts[1] == total_count,
    }


def extract_blueprint_by_mask(shape_mask, window, cellsize, rasterized_acres, **kwargs):
    """Extract areas by each Blueprint category based on shape_mask

    It is assumed that shape_mask has already been prescreened to ensure
    overlap with Blueprint.

    Parameters
    ----------
    shape_mask : 2d array
        True outside shapes
    window : rasterio.windows.Window
        read window for Southeast standard origin
    cellsize : float
        pixel area in acres
    rasterized_acres : float
        area of rasterized shapes

    Returns
    -------
    list of dicts, in descending priority order
        [
            {"value": <value>, "label": <label>, "acres": <acres>, "percent": <percent>}, ...
        ]
    """
    blueprint_acres = (
        extract_count_in_geometry(
            blueprint_filename,
            shape_mask,
            window,
            bins=range(len(BLUEPRINT)),
            boundless=True,
        )
        * cellsize
    )

    blueprint = [
        {
            **e,
            "acres": blueprint_acres[i],
            "percent": 100 * blueprint_acres[i] / rasterized_acres,
        }
        for i, e in enumerate(pluck(BLUEPRINT, ["value", "label"]))
    ][::-1]

    return blueprint


def summarize_blueprint_by_units_grid(df, units_grid, out_dir):
    """Summarize by HUC12 or marine lease block

    Parameters
    ----------
    df : GeoDataFrame
        must have a "value" column with same values as used for corresponding units
        raster, and must have result of df.bounds joined in
    units_grid : SummaryUnitGrid instance
    out_dir : str
    """

    if not "value" in df.columns:
        raise ValueError("GeoDataFrame for summary must include value column")

    with rasterio.open(blueprint_filename) as value_dataset:
        cellsize = value_dataset.res[0] * value_dataset.res[0] * M2_ACRES
        bins = range(0, len(BLUEPRINT))

        blueprint_acres = (
            summarize_raster_by_units_grid(
                df,
                units_grid,
                value_dataset,
                bins=bins,
                progress_label="Summarizing Southeast Blueprint",
            )
            * cellsize
        )

    out = pd.DataFrame(
        blueprint_acres,
        columns=[f"value_{v}" for v in bins],
        index=df.index,
    )

    out.reset_index().to_feather(out_dir / "blueprint.feather")


def get_unit_core_results(unit_type, unit_id):
    """Get results for a single summary unit (HUC12 / marine lease block).

    Parameters
    ----------
    unit_type : str, one of {'huc12', 'marine_blocks'}
    unit_id : str

    Returns
    -------
    DataFrame, dict<results> (None, None if id not present)
    """

    units_filename = huc12_filename if unit_type == "huc12" else marine_filename
    results_dir = data_dir / "results" / unit_type

    # read units and select by ID
    df = read_unit_from_feather(
        units_filename,
        unit_id,
        columns=[
            "id",
            "name",
            "acres",
            "rasterized_acres",
            "outside_se",
            "input_id",
            "minx",
            "miny",
            "maxx",
            "maxy",
        ],
    )

    if len(df) == 0:
        return None, None

    unit = df.iloc[0]

    name_suffix = "subwatershed" if unit_type == "huc12" else "marine lease block"
    name = f"{unit['name']} {name_suffix}"

    bounds = df[["minx", "miny", "maxx", "maxy"]].apply(list, axis=1)[0]

    # read SE Blueprint
    blueprint_results = (
        read_unit_from_feather(results_dir / "blueprint.feather", unit_id)
        .iloc[0]
        .values
    )

    # transform and reorder into descending priority
    blueprint = [
        {
            "value": entry["value"],
            "label": entry["label"],
            "acres": blueprint_results[entry["value"]],
            "percent": 100 * blueprint_results[entry["value"]] / unit.rasterized_acres,
        }
        for entry in BLUEPRINT
    ][::-1]

    within_input = unit.rasterized_acres - unit.outside_se
    if within_input < 1e-6:
        within_input = 0

    results = {
        "name": name,
        "acres": unit.acres,
        "rasterized_acres": unit.rasterized_acres,
        "outside_se_acres": unit.outside_se,
        "outside_se_percent": 100 * unit.outside_se / unit.rasterized_acres,
        "inputs": [{**INPUTS[unit.input_id], "acres": within_input}],
        "input_ids": [unit.input_id],
        "promote_base": unit.input_id == "base",
        "blueprint": blueprint,
        "bounds": bounds,
    }

    if unit_type == "huc12":
        center, lta_search_radius = get_lta_search_info(
            df[["minx", "miny", "maxx", "maxy"]].values
        )
        results["center"] = center[0]
        results["lta_search_radius"] = lta_search_radius[0]

    return df, results
