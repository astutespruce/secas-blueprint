"""Create a custom report for a user-uploaded area of interest."""

import tempfile

import numpy as np
from pyogrio import read_dataframe
import shapely

from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES, STANDARD_RESOLUTION
from analysis.lib.geometry import dissolve
from analysis.lib.pdf.map import render_maps
from analysis.lib.pdf.report import create_report
from analysis.lib.stats.aoi import get_aoi_results
from api.errors import DataError
from api.settings import TEMP_DIR, CUSTOM_REPORT_MAX_ACRES, MAX_POLYGONS, MAX_VERTICES
from api.logger import log
from api.lib.geo import extract_dataset
from api.lib.progress import set_progress


async def create_custom_pdf_report(ctx, zip_filename, dataset, layer, name=""):
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

    filename = f"Southeast Blueprint Summary Report - {name}.pdf" if name else "Southeast Blueprint Summary Report.pdf"

    errors = []

    await set_progress(ctx["redis"], ctx["job_id"], 0, "Preparing area of interest")

    df = extract_dataset(f"/vsizip/{zip_filename}/{dataset}", layer=layer, columns=[])

    if len(df) > 1:
        try:
            df = dissolve(df)

        except Exception:
            raise DataError(
                "Could not dissolve features together for analysis.  Please make sure all features have valid geometries and are of the same type."
            )

    await set_progress(ctx["redis"], ctx["job_id"], 10, "Calculating results (this might take a while)")

    # calculate results, data must be in DATA_CRS
    print("Calculating results...")

    async def progress_callback(percent):
        await set_progress(
            ctx["redis"],
            ctx["job_id"],
            int(round(10 + (percent / 100) * 50)),
            "Calculating results (this might take a while)",
        )

    results = await get_aoi_results(df, progress_callback=progress_callback)

    if results is None:
        raise DataError(
            "area of interest does not overlap Southeast Blueprint or area of interest did not overlap with the center of at least one 30m pixel in the Southeast Blueprint"
        )

    # compile indicator IDs across all indicator groups
    indicators = []
    for group in results.get("indicator_groups", []):
        indicators.extend([i["id"] for i in group["indicators"]])

    await set_progress(ctx["redis"], ctx["job_id"], 60, "Creating maps (this might take a while)")

    print("Rendering maps...")
    geo_df = df.to_crs(GEO_CRS)
    maps, scale, map_errors = await render_maps(
        geo_df.total_bounds,
        geometry=geo_df.geometry.values[0],
        indicators=indicators,
        corridors="corridors" in results,
        parcas="parcas" in results,
        protected_areas="protected_areas" in results,
        slr="slr" in results and results["slr"].get("na", False) is not True,
        urban="urban" in results,
        wildfire_risk="wildfire_risk" in results,
        add_mask=results["acres"] >= 10000000,
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
        80,
        "Creating PDF (this might take a while)",
        errors=errors,
    )

    results["scale"] = scale

    pdf = create_report(maps=maps, results=results, name=name, area_type="custom")

    await set_progress(ctx["redis"], ctx["job_id"], 95, "Nearly done", errors=errors)

    fp, name = tempfile.mkstemp(suffix=".pdf", dir=TEMP_DIR)
    with open(fp, "wb") as out:
        out.write(pdf)

    await set_progress(ctx["redis"], ctx["job_id"], 100, "All done!", errors=errors)

    log.debug(f"Created PDF at: {name}")

    return {
        "name": name,
        "filename": filename,
        "payload": f"/api/jobs/{ctx['job_id']}/pdf",
    }, errors
