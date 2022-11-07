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
    or Marine Lease Block

    Parameters
    ----------
    ctx : job context
    unit_type : str
        one of "huc12", "marine_blocks"
    unit_id : str
    """

    errors = []
    await set_progress(ctx["redis"], ctx["job_id"], 0, "Calculating results")

    results = get_summary_unit_results(unit_type, unit_id)
    if results is None:
        raise DataError(
            "Unit id is not valid (not an existing subwatershed or marine lease block ID)"
        )

    await set_progress(
        ctx["redis"], ctx["job_id"], 50, "Creating maps (this might take a while)"
    )

    has_corridors = "corridors" in results
    has_urban = "urban" in results
    has_nlcd = "nlcd" in results
    has_slr = "slr" in results
    has_ownership = "ownership" in results
    has_protection = "protection" in results

    # compile indicator IDs across all inputs
    indicators = []
    for input_area in results["inputs"]:
        for ecosystem in input_area.get("ecosystems", []):
            indicators.extend([i["id"] for i in ecosystem["indicators"]])

    maps, scale, map_errors = await render_maps(
        results["bounds"],
        summary_unit_id=unit_id,
        input_ids=results["input_ids"],
        indicators=indicators,
        corridors=has_corridors,
        nlcd=has_nlcd,
        urban=has_urban,
        slr=has_slr,
        ownership=has_ownership,
        protection=has_protection,
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

    pdf = create_report(maps=maps, results=results)

    await set_progress(ctx["redis"], ctx["job_id"], 95, "Nearly done", errors=errors)

    fp, name = tempfile.mkstemp(suffix=".pdf", dir=TEMP_DIR)
    with open(fp, "wb") as out:
        out.write(pdf)

    await set_progress(ctx["redis"], ctx["job_id"], 100, "All done!", errors=errors)

    log.debug(f"Created PDF at: {name}")

    return name, errors
