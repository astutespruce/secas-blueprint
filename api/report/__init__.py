from datetime import date, datetime, timezone
from io import BytesIO
from pathlib import Path
import sys

from weasyprint import HTML, default_url_fetcher
from jinja2 import Environment, FileSystemLoader

from api.settings import SITE_URL
from analysis.constants import (
    BLUEPRINT,
    CORRIDORS,
    URBAN_LEGEND,
    SLR_LEGEND,
    OWNERSHIP,
    PROTECTION,
)
from api.report.format import format_number, format_percent


def reverse_filter(iterable):
    return list(iterable)[::-1]


assets_dir = Path(__file__).parent / "templates/assets"
asset_cache = {}


def load_asset(path):
    global asset_cache

    if path.startswith("assets:"):
        path = path.replace("assets:", "")
        if path in asset_cache:
            return asset_cache[path]

        mime_type = None
        if path.endswith(".png"):
            mime_type = "image/png"

        elif path.endswith(".svg"):
            mime_type = "image/svg+xml"

        else:
            raise NotImplementedError(f"{path} not a handled type")

        value = {"string": open(assets_dir / path, "rb").read(), "mime_type": mime_type}
        asset_cache[path] = value

        return value

    return default_url_fetcher(path)


template_path = Path(__file__).parent.resolve() / "templates"

env = Environment(loader=FileSystemLoader(template_path))
env.filters["reverse"] = reverse_filter
env.filters["format_number"] = format_number
env.filters["format_percent"] = format_percent
env.filters["load_asset"] = load_asset
env.filters["sum"] = sum

template = env.get_template("report.html")
css_template = env.get_template("report.css")


def create_report(maps, results, name=None, area_type="custom"):
    """Create PDF report with maps and results

    Parameters
    ----------
    maps : dict
    results : dict
    name : str, optional (default: None)
        name of area to show as report title / header
    area_type : str, optional (default: "custom")
        one of {"custom", "huc12", "marine_hex"}

    Returns
    -------
    bytes
    """

    title = "Southeast Conservation Blueprint Summary"
    subtitle = f"for {name}" if name is not None else ""

    ownership_acres = sum([e["acres"] for e in results.get("ownership", [])])
    protection_acres = sum([e["acres"] for e in results.get("protection", [])])

    legends = {
        # sort Blueprint descending order
        "blueprint": BLUEPRINT[::-1]
    }

    if "corridors" in results:
        # show legend entries only for types that are present
        legends["corridors"] = [
            e for e in CORRIDORS if e["type"] in results["corridors"]["types"]
        ] + CORRIDORS[:1]

    if "urban" in results:
        legends["urban"] = URBAN_LEGEND

    if "slr" in results:
        legends["slr"] = SLR_LEGEND

    if "ownership" in results:
        legends["ownership"] = list(OWNERSHIP.values())

    if "protection" in results:
        legends["protection"] = list(PROTECTION.values())

    context = {
        "date": date.today().strftime("%m/%d/%Y"),
        # write date in ISO format for embedding in PDF metadata
        "create_date": datetime.now(timezone.utc).isoformat(),
        "name": name,
        "area_type": area_type,
        "title": title,
        "subtitle": subtitle,
        "url": SITE_URL,
        "maps": maps,
        "legends": legends,
        "ownership_acres": ownership_acres,
        "protection_acres": protection_acres,
        "results": results,
        # have to flip the crosshatch horizontally due to bug in WeasyPrint
        "flip_crosshatch": sys.platform == "darwin",
    }

    # Render variables as needed into the CSS
    css = css_template.render(**context)
    context["css"] = css

    print("Creating report...")

    def url_fetcher(path):
        if path.startswith("maps:"):
            return {
                "string": maps[path.replace("maps:", "")],
                "mime_type": "image/png",
            }

        return load_asset(path)

    # if DEBUG:
    # TODO: will need to fill in images / convert to base64
    # with open("/tmp/test.html", "w") as out:
    #     out.write(template.render(**context))

    kwargs = {}

    # TODO: enable pdf/ua once accessibility features have been fixed in Weasyprint
    # kwargs["variant"] = "pdf/ua-1"

    pdf = HTML(
        BytesIO((template.render(**context)).encode()), url_fetcher=url_fetcher
    ).write_pdf(**kwargs)

    return pdf
