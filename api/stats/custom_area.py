from pathlib import Path

import geopandas as gp
import numpy as np
import pygeos as pg


from analysis.lib.geometry import (
    to_crs,
    to_dict,
    intersection,
)
from analysis.constants import (
    INPUTS,
    URBAN_YEARS,
    DATA_CRS,
    OWNERSHIP,
    PROTECTION,
    M2_ACRES,
)

from analysis.lib.stats.core import (
    get_shape_mask,
    extract_input_areas_by_mask,
    extract_blueprint_by_mask,
)
from analysis.lib.stats.florida_marine import extract_florida_marine_by_mask
from analysis.lib.util import subset_dict

from analysis.lib.stats.base_blueprint import extract_base_blueprint_by_mask
from analysis.lib.stats.caribbean import extract_caribbean_by_mask
from analysis.lib.stats.slr import extract_slr_by_mask_and_geometry
from analysis.lib.stats.urban import extract_urban_by_mask

data_dir = Path("data/inputs")
boundary_filename = data_dir / "boundaries/se_boundary.feather"
county_filename = data_dir / "boundaries/counties.feather"
ownership_filename = data_dir / "boundaries/ownership.feather"
slr_bounds_filename = data_dir / "threats/slr/slr_bounds.feather"


def get_counties(df):
    """Get the counties that overlap the Data Frame

    Parameters
    ----------
    df : GeoDataFrame

    Returns
    -------
    list of dicts
        [{'FIPS': <FIPS>, 'state': <state>, 'county': <county>}]
    """
    counties = gp.read_feather(county_filename)[["geometry", "FIPS", "state", "county"]]

    df = (
        gp.sjoin(df, counties)[["FIPS", "state", "county"]]
        .reset_index(drop=True)
        .sort_values(by=["state", "county"])
    )

    if not len(df):
        return None

    return df.to_dict(orient="records")


def get_ownership(df):
    """Get ownership and protection levels and other statistics for the DataFrame

    Parameters
    ----------
    df : GeoDataFrame

    Returns
    -------
    dict
        {
            "ownership": [
                {
                    "label": <ownership type label>,
                    "acres": <acres of overlap>
                }
            ],
            "protection": [
                {
                    "label": <protection type label>,
                    "acres": <acres of overlap>
                }
            ],
            "protected_areas" [<top 25 protected area names and areas>],
            "num_protected_areas": <total number protected areas>
        }
    """
    ownership = gp.read_feather(ownership_filename)
    df = intersection(df, ownership)

    if df is None:
        return None

    df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES
    df = df.loc[df.acres > 0].copy()

    if not len(df):
        return None

    results = dict()

    by_owner = (
        df[["Own_Type", "acres"]]
        .groupby(by="Own_Type")
        .acres.sum()
        .astype("float32")
        .to_dict()
    )
    # use the native order of OWNERSHIP to drive order of results
    results["ownership"] = [
        {"label": value["label"], "acres": by_owner[key]}
        for key, value in OWNERSHIP.items()
        if key in by_owner
    ]

    by_protection = (
        df[["GAP_Sts", "acres"]]
        .groupby(by="GAP_Sts")
        .acres.sum()
        .astype("float32")
        .to_dict()
    )
    # use the native order of PROTECTION to drive order of results
    results["protection"] = [
        {
            "label": value["label"],
            "acres": by_protection[key],
        }
        for key, value in PROTECTION.items()
        if key in by_protection
    ]

    by_area = (
        df[["Loc_Nm", "Loc_Own", "acres"]]
        .groupby(by=[df.index.get_level_values(0), "Loc_Nm", "Loc_Own"])
        .acres.sum()
        .astype("float32")
        .round()
        .reset_index()
        .rename(columns={"level_0": "id", "Loc_Nm": "name", "Loc_Own": "owner"})
        .sort_values(by="acres", ascending=False)
    )
    # drop very small areas, these are not helpful
    by_area = by_area.loc[by_area.acres >= 1].copy()

    results["protected_areas"] = by_area.head(25).to_dict(orient="records")
    results["num_protected_areas"] = len(by_area)

    return results


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
    bounds = pg.bounds(geometry).tolist()
    shapes = [to_dict(geometry)]

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

            if input_info["promote_base"]:
                blueprint = base_results["priorities"]
                corridors = base_results["corridors"]

        elif id == "car":
            input_area.update(extract_caribbean_by_mask(**config))

        elif "flm":
            input_area.update(extract_florida_marine_by_mask(**config))

    # urban not available for PR
    if "base" in input_ids:
        urban = extract_urban_by_mask(**config)
    else:
        urban = None

    # SLR not applicable to FL Marine
    if input_ids != ["flm"]:
        slr = extract_slr_by_mask_and_geometry(**config, geometry=geometry)
    else:
        slr = None

    counties = get_counties(df)
    ownership_info = get_ownership(df)

    results = {
        "acres": pg.area(geometry) * M2_ACRES,
        **subset_dict(
            config, {"rasterized_acres", "inside_se_acres", "outside_se_acres"}
        ),
        "outside_se_percent": (
            100 * config["outside_se_acres"] / config["rasterized_acres"]
        ),
        "blueprint": blueprint,
        "corridors": corridors,
        "inputs": inputs,
        "input_ids": input_ids,
        "promote_base": input_info["promote_base"],
        "urban": urban,
        "slr": slr,
        "counties": counties,
    }

    if ownership_info is not None:
        results.update(ownership_info)

    return results
