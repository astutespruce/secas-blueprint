from pathlib import Path
from collections import OrderedDict
from itertools import product
import json
from rasterio.windows import Window


# Set to True to output intermediate rasters for validation (uncomment in map.raster module)
# Set to True to output /tmp/test.html for reports
DEBUG = False

DATA_CRS = "EPSG:5070"
GEO_CRS = "EPSG:4326"
MAP_CRS = "EPSG:3857"

ACRES_PRECISION = 1
# meters to acres
M2_ACRES = 0.000247105
M_MILES = 0.000621371

# 32 is OK for regional level maps; 16 is more typical for big areas like ACF
OVERVIEW_FACTORS = [2, 4, 8, 16, 32]

MASK_RESOLUTION = 480  # meters

SECAS_STATES = [
    "AL",
    "AR",
    "FL",
    "GA",
    "KY",
    "LA",
    "MS",
    "MO",
    "MS",
    "NC",
    "OK",
    "PR",
    "SC",
    "TN",
    "TX",
    "VA",
    # "USVI",  # expected to be added in 2023
    "WV",
]

SECAS_HUC2 = [2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 21]


json_dir = Path("constants")

BLUEPRINT = json.loads(open(json_dir / "blueprint.json").read())
BLUEPRINT_COLORS = {
    i: entry["color"]
    for i, entry in enumerate(BLUEPRINT)
    if "color" in entry and entry["value"] > 0
}

INPUTS = {e["id"]: e for e in json.loads(open(json_dir / "inputs.json").read())}
INPUT_AREA_VALUES = {
    e["id"]: e["value"]
    for e in json.loads(open(json_dir / "input_area_values.json").read())
}
# Bounds are in DATA_CRS and are used for filtering areas of interest for
# potential overlaps with input areas
INPUT_AREA_BOUNDS = {
    "base": [-1000334.18062565, 258944.14681537, 2201235.81937435, 2064044.14681537],
    "car": [3039495.81937435, -78225.85318463, 3321615.81937435, 39584.14681537],
    "flm": [816225.81937435, 178034.14681537, 1891275.81937435, 1015394.14681537],
}


ECOSYSTEMS = json.loads(open(json_dir / "ecosystems.json").read())

# Combine all constants/indicators/*.json files into a single data structure
raw_indicators = [
    json.loads(open(filename).read())
    for filename in (json_dir / "indicators").glob("*.json")
]
# convert to dict keyed by input ID
INDICATORS = {e["input"]: e["indicators"] for e in raw_indicators}
INDICATOR_INDEX = {}
for indicators in INDICATORS.values():
    for indicator in indicators:
        INDICATOR_INDEX[indicator["id"]] = indicator

OWNERSHIP = OrderedDict(
    {e["value"]: e for e in json.loads(open(json_dir / "ownership.json").read())}
)
PROTECTION = OrderedDict(
    {e["value"]: e for e in json.loads(open(json_dir / "protection.json").read())}
)


URBAN_YEARS = [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]


# values are # out of 50 runs, and 51 = currently urban in 2019 NLCD
# 0 (not urbanized) is deliberately excluded from colors
URBAN_COLORS = {
    1: "#F3C6A8",  # moderate
    2: "#DA6C51",  # high
    3: "#C40A0A",  # very high
    4: "#696969",  # already urban
}

# Note: for legend already urban is toward the top but it is value 3
URBAN_LEGEND = [
    {"label": "Not likely to urbanize", "color": None},
    {"label": "Urban in 2019", "color": "#696969"},
    {
        "label": "Moderate likelihood of urbanization (2 - 25% probability)",
        "color": "#F3C6A8",
    },
    {
        "label": "High likelihood of urbanization (25 - 50% probability)",
        "color": "#DA6C51",
    },
    {
        "label": "Very high likelihood of urbanization (>50% probability)",
        "color": "#C40A0A",
    },
]

SLR_YEARS = [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]
SLR_PROJ_SCENARIOS = {
    "l": "Low",
    "il": "Intermediate-low",
    "i": "Intermediate",
    "ih": "Intermediate-high",
    "h": "High",
}
SLR_PROJ_COLUMNS = [
    f"{decade}_{scenario}"
    for decade, scenario in product(SLR_YEARS, SLR_PROJ_SCENARIOS)
]


SLR_LEGEND = [
    {"label": "0", "color": "#00094E"},
    {"label": "1", "color": "#031386"},
    {"label": "2", "color": "#0821BD"},
    {"label": "3", "color": "#1136E0"},
    {"label": "4", "color": "#1E50EE"},
    {"label": "5", "color": "#2D6BFC"},
    {"label": "6", "color": "#2D8CFC"},
    {"label": "7", "color": "#2CADFC"},
    {"label": "8", "color": "#47D4FC"},
    {"label": "9", "color": "#7DF5FD"},
    {"label": "10", "color": "#B3FEF7"},
]
