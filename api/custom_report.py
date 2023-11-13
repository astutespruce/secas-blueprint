"""Create a custom report for a user-uploaded area of interest.
"""
import logging
import tempfile

import numpy as np
from pyogrio import read_dataframe
import shapely

from api.errors import DataError
from api.report.map import render_maps
from api.report import create_report
from api.settings import LOGGING_LEVEL, TEMP_DIR, CUSTOM_REPORT_MAX_ACRES
from api.stats.custom_area import get_custom_area_results
from api.progress import set_progress

from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES
from analysis.lib.geometry import dissolve

log = logging.getLogger(__name__)
log.setLevel(LOGGING_LEVEL)


async def create_custom_report(ctx, zip_filename, dataset, layer, name=""):
    """Create a Blueprint report for a user-uploaded GIS file contained in a zip.
    Zip must contain either a shapefile or a file geodatabase.

    Parameters
    ----------
    ctx : job context
    zip_filename : str
        full path to zip filename
    dataset : str
        full path to dataset within zip file
    layer : str
        name of layer within dataset
    name : str, optional (default: "")
        Name of area of interest (included in output report)

    Returns
    -------
    str
        path to output file

    Raises
    ------
    DataError
        Raised if bounds are too large or if area of interest doesn't overalap SA region
    """

    errors = []

    await set_progress(ctx["redis"], ctx["job_id"], 0, "Preparing area of interest")

    path = f"/vsizip/{zip_filename}/{dataset}"

    df = read_dataframe(path, layer=layer, columns=[]).to_crs(DATA_CRS)

    # estimate area and reject if too big
    extent_area = shapely.area(shapely.box(*df.total_bounds)) * M2_ACRES
    if extent_area >= CUSTOM_REPORT_MAX_ACRES:
        raise DataError(
            f"The bounding box of your area of interest is too large ({extent_area:,.0f} acres), it must be < {CUSTOM_REPORT_MAX_ACRES:,.0f} acres."
        )

    df["geometry"] = shapely.make_valid(df.geometry.values)

    # check for non-polygon results of making valid and strip them out
    geom_types = np.unique(shapely.get_type_id(df.geometry.values))
    if set(geom_types) - {3, 6}:
        df = df.explode(ignore_index=True)
        df = df.loc[shapely.get_type_id(df.geometry.values) == 3].copy()
        print("Found non-polygon geometries; stripping them out")

        if len(df) == 0:
            raise ValueError(
                "No valid area boundaries available for analysis after making geometries valid.  This means that one or more of your features has an invalid geometry.  Please clean up your data and try again."
            )

    if len(df) > 1:
        try:
            df["group"] = 1
            df = dissolve(df.explode(ignore_index=True), by="group")
        except:
            raise DataError(
                "Could not dissolve features together for analysis.  Please make sure all features have valid geometries and are of the same type."
            )

    await set_progress(
        ctx["redis"], ctx["job_id"], 10, "Calculating results (this might take a while)"
    )

    # calculate results, data must be in DATA_CRS
    print("Calculating results...")
    results = get_custom_area_results(df)

    if results is None:
        raise DataError(
            "area of interest does not overlap Southeast Blueprint or area of interest did not overlap with the center of at least one 30m pixel in the Southeast Blueprint"
        )

    # compile indicator IDs across all ecosystems
    indicators = []
    for ecosystem in results.get("ecosystems", []):
        indicators.extend([i["id"] for i in ecosystem["indicators"]])

    await set_progress(
        ctx["redis"], ctx["job_id"], 25, "Creating maps (this might take a while)"
    )

    print("Rendering maps...")
    geo_df = df.to_crs(GEO_CRS)
    maps, scale, map_errors = await render_maps(
        geo_df.total_bounds,
        geometry=geo_df.geometry.values[0],
        indicators=indicators,
        corridors="corridors" in results,
        urban="urban" in results,
        slr="slr" in results and results["slr"].get("na", False) is not True,
        ownership="ownership" in results,
        protection="protection" in results,
    )

    if map_errors:
        log.error(f"Map rendering errors: {map_errors}")
        if "basemap" in map_errors:
            errors.append("Error creating basemap for all maps")

        if "aoi" in map_errors:
            errors.append("Error rendering area of interest on maps")

        if set(map_errors.keys()).difference(["basemap", "aoi"]):
            errors.append("Error creating one or more maps")

    await set_progress(
        ctx["redis"],
        ctx["job_id"],
        75,
        "Creating PDF (this might take a while)",
        errors=errors,
    )

    results["scale"] = scale

    pdf = create_report(maps=maps, results=results, name=name, is_custom_area=True)

    await set_progress(ctx["redis"], ctx["job_id"], 95, "Nearly done", errors=errors)

    fp, name = tempfile.mkstemp(suffix=".pdf", dir=TEMP_DIR)
    with open(fp, "wb") as out:
        out.write(pdf)

    await set_progress(ctx["redis"], ctx["job_id"], 100, "All done!", errors=errors)

    log.debug(f"Created PDF at: {name}")

    return name, errors
