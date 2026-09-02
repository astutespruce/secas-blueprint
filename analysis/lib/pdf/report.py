import sys
from datetime import date, datetime, timezone
from io import BytesIO
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, default_url_fetcher
from weasyprint.urls import URLFetcherResponse

from analysis.constants import (
    BLUEPRINT,
    CORRIDORS,
    PARCAS,
    PROTECTED_AREAS,
    SLR_DEPTH,
    SLR_DEPTH_VALUES,
    SLR_PROJ,
    URBAN,
    URBAN_BY_DECADE,
    WILDFIRE_RISK,
    WILDFIRE_RISK_LEGEND,
)
from analysis.lib.pdf.format import format_number, format_percent


def reverse_filter(iterable):
    return list(iterable)[::-1]


assets_dir = Path(__file__).parent / "templates/assets"
asset_cache = {}


def load_asset(path):
    global asset_cache

    if path.startswith("assets:"):
        path = path.replace("assets:", "")
        if path in asset_cache:
            value = asset_cache[path]
            return URLFetcherResponse(url=path, body=value["body"], headers=value["headers"])

        mime_type = None
        if path.endswith(".png"):
            mime_type = "image/png"

        elif path.endswith(".svg"):
            mime_type = "image/svg+xml"

        else:
            raise NotImplementedError(f"{path} not a handled type")

        with open(assets_dir / path, "rb") as infile:
            body = infile.read()

        value = {"body": body, "headers": {"mime_type": mime_type}}
        asset_cache[path] = value

        return URLFetcherResponse(url=path, body=value["body"], headers=value["headers"])

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
    subtitle = f"for {name}" if name else ""

    legends = {
        # sort Blueprint descending order
        "blueprint": BLUEPRINT["values"][::-1],
        "corridors": CORRIDORS["values"][1:],
        "parcas": PARCAS["values"][::-1],
        "protected_areas": PROTECTED_AREAS["values"][::-1],
        "slr": [{**v, "label": v["label"].replace(" foot", "").replace(" feet", "")} for v in SLR_DEPTH_VALUES],
        "urban": URBAN["values"],
        "wildfire_risk": WILDFIRE_RISK_LEGEND,
    }

    # NOTE: full indicator objects are already in the results; no need to have caption entries
    captions = {
        dataset["id"]: dataset["caption"]
        for dataset in [
            BLUEPRINT,
            CORRIDORS,
            PARCAS,
            PROTECTED_AREAS,
            PROTECTED_AREAS,
            SLR_DEPTH,
            SLR_PROJ,
            # NOTE: table entry is urban by decade
            URBAN_BY_DECADE,
            WILDFIRE_RISK,
        ]
    }

    context = {
        "date": date.today().strftime("%m/%d/%Y"),
        # write date in ISO format for embedding in PDF metadata
        "create_date": datetime.now(timezone.utc).isoformat(),
        "name": name,
        "area_type": area_type,
        "title": title,
        "subtitle": subtitle,
        "maps": maps,
        "legends": legends,
        "captions": captions,
        "results": results,
        "is_marine_only": results.get("regions") == {"marine"},
        # have to flip the crosshatch horizontally due to bug in WeasyPrint
        "flip_crosshatch": sys.platform == "darwin",
    }

    # Render variables as needed into the CSS
    css = css_template.render(**context)
    context["css"] = css

    def url_fetcher(path):
        if path.startswith("maps:"):
            return URLFetcherResponse(
                url=path, body=maps[path.replace("maps:", "")], headers={"mime_type": "image/png"}
            )

        return load_asset(path)

    # if DEBUG:
    # TODO: will need to fill in images / convert to base64
    # with open("/tmp/test.html", "w") as out:
    #     out.write(template.render(**context))

    kwargs = {}

    # TODO: enable pdf/ua once accessibility features have been fixed in Weasyprint
    # kwargs["variant"] = "pdf/ua-1"

    pdf = HTML(BytesIO((template.render(**context)).encode()), url_fetcher=url_fetcher).write_pdf(**kwargs)

    return pdf
