from pathlib import Path

import numpy as np
import rasterio

from analysis.constants import BLUEPRINT, INPUTS, ACRES_PRECISION, M2_ACRES
from analysis.lib.raster import (
    detect_data,
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    summarize_raster_by_geometry,
)


src_dir = Path("data/inputs")
blueprint_filename = src_dir / "se_blueprint2021.tif"
bp_inputs_filename = src_dir / "input_areas.tif"
bp_inputs_mask_filename = src_dir / "input_areas_mask.tif"


def extract_by_geometry(geometries, bounds):
    """Calculate the area of overlap between geometries and Blueprint grids.

    NOTE: Blueprint and inputs are on the same grid

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    dict or None (if does not overlap Blueprint data)
        {"shape_mask": <shape_mask_area>, "blueprint": [...], ...}
    """

    # prescreen to make sure data are present
    with rasterio.open(bp_inputs_mask_filename) as src:
        if not detect_data(src, geometries, bounds):
            return None

    results = {}

    # create mask and window
    with rasterio.open(blueprint_filename) as src:
        shape_mask, transform, window = boundless_raster_geometry_mask(
            src, geometries, bounds, all_touched=False
        )

        # square meters to acres
        cellsize = src.res[0] * src.res[1] * M2_ACRES

    # DEBUG:
    # print(
    #     f"Memory of shape mask: {shape_mask.size * shape_mask.itemsize / (1024 * 1024):0.2f} MB",
    #     shape_mask.dtype,
    # )

    results = {
        "shape_mask": (
            ((~shape_mask).sum() * cellsize).round(ACRES_PRECISION).astype("float32")
        )
    }

    # Nothing in shape mask, return None
    if results["shape_mask"] == 0:
        return None

    blueprint_counts = extract_count_in_geometry(
        blueprint_filename,
        shape_mask,
        window,
        np.arange(len(BLUEPRINT)),
        boundless=True,
    )
    results["blueprint"] = (
        (blueprint_counts * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    bp_input_counts = extract_count_in_geometry(
        bp_inputs_filename,
        shape_mask,
        window,
        bins=range(0, len(INPUTS)),
        boundless=True,
    )
    results["inputs"] = (
        (bp_input_counts * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    return results


def summarize_by_unit(geometries, out_dir):
    """Summarize by HUC12 or marine lease block

    Parameters
    ----------
    geometries : Series of pygeos geometries, indexed by HUC12 / marine lease block id
    out_dir : str
    """

    summarize_raster_by_geometry(
        geometries,
        extract_by_geometry,
        outfilename=out_dir / "blueprint.feather",
        progress_label="Summarizing Blueprint and Input Areas",
    )
