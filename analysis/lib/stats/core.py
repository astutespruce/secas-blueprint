from pathlib import Path

import rasterio

from analysis.constants import BLUEPRINT, INPUTS, M2_ACRES
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    summarize_raster_by_geometry,
)
from analysis.lib.util import pluck

src_dir = Path("data/inputs")
blueprint_filename = src_dir / "se_blueprint_2022.tif"
bp_inputs_filename = src_dir / "boundaries/input_areas.tif"
bp_inputs_mask_filename = src_dir / "boundaries/input_areas_mask.tif"

bnd_dir = Path("data/boundaries")
huc12_raster_filename = bnd_dir / "huc12.tif"
marine_raster_filename = bnd_dir / "marine_blocks.tif"


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


def summarize_by_unit(df, out_dir, marine=False):
    """Summarize by HUC12 or marine lease block

    Parameters
    ----------
    df : GeoDataFrame
        must have a "value" column with same values as used for corresponding units
        raster, and must have result of df.bounds joined in
    out_dir : str
    marine : bool
        if True, will summarize marine lease blocks, otherwise HUC12s
    """

    units_raster_filename = marine_raster_filename if marine else huc12_raster_filename
    with rasterio.open(units_raster_filename) as units_dataset, rasterio.open(
        blueprint_filename
    ) as value_dataset:
        bins = range(0, len(BLUEPRINT))

        blueprint_counts = summarize_raster_by_geometry(
            df,
            units_dataset,
            value_dataset,
            bins=bins,
            progress_label="Summarizing Southeast Blueprint",
        )

    # no need to calculate overlap with inputs; that is done in advance and there
    # is only one Blueprint input per summary unit

    # use the sum of the blueprint area to calculate area outside SE
    blueprint_totals = blueprint_counts.sum(axis=1)
    remainder = df.pixels - blueprint_totals

    outfilename = (out_dir / "core.feather",)
