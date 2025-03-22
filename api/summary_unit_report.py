import logging
import tempfile

from api.errors import DataError
from api.report.map import render_maps
from api.report import create_report
from api.settings import LOGGING_LEVEL, TEMP_DIR
from api.stats.summary_units import get_summary_unit_results
from api.progress import set_progress

log = logging.getLogger(__name__)
log.setLevel(LOGGING_LEVEL)


async def create_summary_unit_report(ctx, unit_type, unit_id):
    """Generate Southeast Blueprint Report for a HUC12
    or marine hex grid cell

    Parameters
    ----------
    ctx : job context
    unit_type : str
        one of "huc12", "marine_hex"
    unit_id : str
    """

    errors = []
    await set_progress(ctx["redis"], ctx["job_id"], 0, "Calculating results")

    results = get_summary_unit_results(unit_type, unit_id)
    if results is None:
        raise DataError(
            "Unit id is not valid (not an existing subwatershed or marine hex grid ID)"
        )

    name = results["name"]
    print("unit type", unit_type)
    if unit_type == "marine_hex":
        name = "Marine " + name.replace(":", " ")

    filename = f"Southeast Blueprint Summary Report - {name}.pdf"

    await set_progress(
        ctx["redis"], ctx["job_id"], 50, "Creating maps (this might take a while)"
    )

    # compile indicator IDs across all ecosystems
    indicators = []
    for ecosystem in results.get("ecosystems", []):
        indicators.extend([i["id"] for i in ecosystem["indicators"]])

    maps, scale, map_errors = await render_maps(
        results["bounds"],
        summary_unit_id=unit_id,
        indicators=indicators,
        corridors="corridors" in results,
        urban="urban" in results,
        slr="slr" in results and results["slr"].get("na", False) is not True,
        wildfire_risk="wildfire_risk" in results,
        ownership="ownership" in results,
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

    pdf = create_report(
        maps=maps, results=results, name=results["name"], area_type=unit_type
    )

    await set_progress(ctx["redis"], ctx["job_id"], 95, "Nearly done", errors=errors)

    fp, name = tempfile.mkstemp(suffix=".pdf", dir=TEMP_DIR)
    with open(fp, "wb") as out:
        out.write(pdf)

    await set_progress(ctx["redis"], ctx["job_id"], 100, "All done!", errors=errors)

    log.debug(f"Created PDF at: {name}")

    return name, filename, errors
