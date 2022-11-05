from pathlib import Path
from itertools import product
import json

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
STANDARD_RESOLUTION = 30  # meters
PIXEL_ACRES = STANDARD_RESOLUTION * STANDARD_RESOLUTION * M2_ACRES

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

# Note: value field is the value in the input_areas raster, bounds are in
# EPSG:5070
INPUTS = {e["id"]: e for e in json.loads(open(json_dir / "inputs.json").read())}

CORRIDORS = json.loads(open(json_dir / "corridors.json").read())
CORRIDORS_COLORS = {
    i: entry["color"]
    for i, entry in enumerate(CORRIDORS)
    if entry.get("color", None) is not None
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

OWNERSHIP = {
    e["value"]: e for e in json.loads(open(json_dir / "ownership.json").read())
}
PROTECTION = {
    e["value"]: e for e in json.loads(open(json_dir / "protection.json").read())
}


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
    {"label": "Urban in 2019", "color": "#696969"},
    {"label": "Not likely to urbanize", "color": None},
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

# depth in 1 foot increments from 0
SLR_DEPTH_BINS = list(range(11))
SLR_NODATA_VALUES = [
    {"value": 11, "label": "Not projected to be inundated by up to 10 feet"},
    {"value": 12, "label": "Sea-level rise data unavailable"},
    {"value": 13, "label": "Sea-level rise unlikely to be a threat (inland counties)"},
]
SLR_NODATA_COLS = ["not_inundated", "nodata", "not_applicable"]

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

SRL_NODATA_COLORS = [
    # Not inundated to 10 ft
    {"label": "11", "color": "#FFFFFF"},
    # Sea-level rise data unavailable
    {"label": "12", "color": "#880000"},
    # Sea-level rise unlikely to be a threat (inland counties)
    {"label": "13", "color": "#333333"},
]


# Original codes
NLCD_CODES = {
    11: {"label": "Open water", "color": "#466B9F"},
    12: {"label": "Perennial ice/snow", "color": "#D1DEF8"},
    21: {"label": "Developed (open space)", "color": "#DEC5C5"},
    22: {"label": "Developed (low intensity)", "color": "#D99282"},
    23: {"label": "Developed (medium intensity)", "color": "#EB0000"},
    24: {"label": "Developed (high intensity)", "color": "#AB0000"},
    31: {"label": "Barren land", "color": "#B3AC9F"},
    41: {"label": "Deciduous forest", "color": "#68AB5F"},
    42: {"label": "Evergreen forest", "color": "#1C5F2C"},
    43: {"label": "Mixed forest", "color": "#B5C58F"},
    52: {"label": "Shrub/scrub", "color": "#CCB879"},
    71: {"label": "Grassland/herbaceous", "color": "#DFDFC2"},
    81: {"label": "Pasture/hay", "color": "#DCD939"},
    82: {"label": "Cultivated crops", "color": "#AB6C28"},
    90: {"label": "Woody wetlands", "color": "#B8D9EB"},
    95: {"label": "Emergent herbaceous wetlands", "color": "#6C9FB8"},
}

NLCD_INDEXES = {i: e for i, e in enumerate(NLCD_CODES.values())}

LTA_SEARCH_RADIUS_BINS = [
    25,
    50,
    100,
    250,
    500,
]
