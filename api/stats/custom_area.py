from pathlib import Path

import geopandas as gp
import numpy as np
import pygeos as pg

from analysis.constants import DATA_CRS, GEO_CRS, INPUTS, M2_ACRES
from analysis.lib.geometry import to_dict, to_crs
from analysis.lib.stats.base_blueprint import extract_base_blueprint_by_mask
from analysis.lib.stats.caribbean import extract_caribbean_by_mask
from analysis.lib.stats.core import (
    extract_blueprint_by_mask,
    extract_input_areas_by_mask,
    get_shape_mask,
)
from analysis.lib.stats.florida_marine import extract_florida_marine_by_mask
from analysis.lib.stats.ownership import get_lta_search_info, get_ownership_for_aoi
from analysis.lib.stats.parca import get_parcas_for_aoi
from analysis.lib.stats.slr import extract_slr_by_mask_and_geometry
from analysis.lib.stats.urban import extract_urban_by_mask
from analysis.lib.util import subset_dict

data_dir = Path("data/inputs")
bnd_dir = data_dir / "boundaries"
boundary_filename = bnd_dir / "se_boundary.feather"
slr_bounds_filename = data_dir / "threats/slr/slr_bounds.feather"


def get_custom_area_results(df):
    """Calculate statistics for custom area

    df : GeoDataFrame
        expected to only have one row representing the analysis area
    """

    if len(df) > 1:
        raise ValueError(
            f"DataFrame for custom area had more rows than expected: {len(df)}"
        )

    geometry = df.geometry.values.data[0]
    polygon_acres = pg.area(geometry) * M2_ACRES
    shapes = [to_dict(geometry)]
    bounds = pg.bounds(geometry)

    geo_bounds = pg.bounds(to_crs(np.array([pg.box(*bounds)]), DATA_CRS, GEO_CRS))

    center, lta_search_radius = get_lta_search_info(geo_bounds)
    center = center[0]
    lta_search_radius = lta_search_radius[0]

    # if area of interest does not intersect SE region boundary,
    # there will be no results
    se_bnd = gp.read_feather(boundary_filename)
    if not pg.intersects(geometry, se_bnd.geometry.values.data).max():
        return None

    config = get_shape_mask(shapes, bounds)

    # there was an intersection but no data once rasterized
    if config["rasterized_acres"] == 0:
        return None

    input_info = extract_input_areas_by_mask(
        config["shape_mask"], config["window"], config["cellsize"]
    )

    config.update(
        {
            "inside_se_acres": input_info["inside_se_acres"],
            "outside_se_acres": config["rasterized_acres"]
            - input_info["inside_se_acres"],
        }
    )

    # if area covers more than just base blueprint, extract SE blueprint
    if not input_info["promote_base"]:
        blueprint = extract_blueprint_by_mask(**config)

    # merge in main input info
    inputs = sorted(
        [
            {
                **INPUTS[id],
                "acres": acres,
            }
            for id, acres in input_info["inputs"].items()
        ],
        key=lambda x: x["acres"],
        reverse=True,
    )

    corridors = None

    input_ids = [i["id"] for i in inputs]
    for input_area in inputs:
        id = input_area["id"]
        if id == "base":
            base_results = extract_base_blueprint_by_mask(**config)
            input_area.update(base_results)
            corridors = base_results.get("corridors", None)

            if input_info["promote_base"]:
                blueprint = base_results["priorities"]

        elif id == "car":
            input_area.update(extract_caribbean_by_mask(**config))

        elif "flm":
            input_area.update(extract_florida_marine_by_mask(**config))

    # PARCAs and urban not available for PR
    if "base" in input_ids:
        urban = extract_urban_by_mask(**config)
        parca = get_parcas_for_aoi(df)

    else:
        urban = None
        parca = None

    # SLR not applicable to FL Marine
    if input_ids != ["flm"]:
        slr = extract_slr_by_mask_and_geometry(**config, geometry=geometry)
    else:
        slr = None

    ownership_info = get_ownership_for_aoi(df, total_acres=polygon_acres)

    results = {
        "acres": polygon_acres,
        "center": center,
        "lta_search_radius": lta_search_radius,
        **subset_dict(config, {"rasterized_acres", "outside_se_acres"}),
        "outside_se_percent": (
            100 * config["outside_se_acres"] / config["rasterized_acres"]
        ),
        "blueprint": blueprint,
        "inputs": inputs,
        "input_ids": input_ids,
        "promote_base": input_info["promote_base"],
    }

    if corridors is not None:
        results["corridors"] = corridors

    if slr is not None:
        results["slr"] = slr

    if urban is not None:
        results["urban"] = urban

    if parca is not None:
        results["parca"] = parca

    if ownership_info is not None:
        results.update(ownership_info)

    return results
