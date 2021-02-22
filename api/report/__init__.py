from base64 import b64encode
from collections import OrderedDict
from datetime import date
from io import BytesIO
from operator import itemgetter
from pathlib import Path

from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

from api.settings import SITE_URL
from analysis.constants import (
    BLUEPRINT,
    URBAN_LEGEND,
    SLR_LEGEND,
    OWNERSHIP,
    PROTECTION,
    DEBUG,
)
from api.report.format import format_number, format_percent


def reverse_filter(iterable):
    return list(iterable)[::-1]


assets_dir = Path(__file__).parent / "templates/assets"


def load_asset(path):
    prefix = ""
    data = ""

    if path.endswith(".png"):
        prefix = "data:image/png;base64,"

    elif path.endswith(".svg"):
        prefix = "data:image/svg+xml;base64,"

    else:
        raise NotImplementedError(f"{path} not a handled type")

    data = b64encode(open(assets_dir / path, "rb").read()).decode("utf-8")
    return f"{prefix}{data}"


template_path = Path(__file__).parent.resolve() / "templates"

env = Environment(loader=FileSystemLoader(template_path))
env.filters["reverse"] = reverse_filter
env.filters["format_number"] = format_number
env.filters["format_percent"] = format_percent
env.filters["load_asset"] = load_asset
env.filters["sum"] = sum

template = env.get_template("report.html")
css_template = env.get_template("report.css")


def create_report(maps, results):
    title = "Southeast Conservation Blueprint Summary"
    subtitle = ""
    if "name" in results and results["name"] is not None:
        subtitle = f"for {results['name']}"
        if "type" in results:
            subtitle += " " + results["type"]

    ownership_acres = sum([e["acres"] for e in results.get("ownership", [])])
    protection_acres = sum([e["acres"] for e in results.get("protection", [])])

    legends = {
        # sort Blueprint descending order
        "blueprint": BLUEPRINT[::-1]
    }

    if "urban" in results:
        legends["urban"] = (
            URBAN_LEGEND[1:3]
            + URBAN_LEGEND[5:6]
            + URBAN_LEGEND[8:9]
            + URBAN_LEGEND[11:12]
            + URBAN_LEGEND[-1:]
        )

    if "slr" in results:
        legends["slr"] = SLR_LEGEND

    if "ownership" in results:
        legends["ownership"] = list(OWNERSHIP.values())

    if "protection" in results:
        legends["protection"] = list(PROTECTION.values())

    context = {
        "date": date.today().strftime("%m/%d/%Y"),
        "title": title,
        "subtitle": subtitle,
        "url": SITE_URL,
        "maps": maps,
        "legends": legends,
        "ownership_acres": ownership_acres,
        "protection_acres": protection_acres,
        "results": results,
    }

    # Render variables as needed into the CSS
    css = css_template.render(**context)
    context["css"] = css

    print("Creating report...")

    # if DEBUG:
    with open("/tmp/test.html", "w") as out:
        out.write(template.render(**context))

    return HTML(BytesIO((template.render(**context)).encode())).write_pdf()
