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
    "VI",
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


CORRIDORS = json.loads(open(json_dir / "corridors.json").read())
CORRIDORS_COLORS = {
    entry["value"]: entry["color"]
    for entry in CORRIDORS
    if entry.get("color", None) is not None
}
ECOSYSTEMS = json.loads(open(json_dir / "ecosystems.json").read())


INDICATORS = json.loads(open(json_dir / "indicators.json").read())
INDICATORS_INDEX = {indicator["id"]: indicator for indicator in INDICATORS}


PROTECTED_AREAS = json.loads(open(json_dir / "protected_areas.json").read())
PROTECTED_AREAS_COLORS = {
    entry["value"]: entry["color"]
    for entry in PROTECTED_AREAS
    if entry.get("color", None) is not None
}


URBAN_YEARS = [2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]


# Classified Urban 2060
# NOTE: value 5 is not urbanized
URBAN = json.loads(open(json_dir / "urban.json").read())
URBAN_COLORS = {e["value"]: e["color"] for e in URBAN if e["color"] is not None}
URBAN_LEGEND = URBAN

# depth in 1 foot increments from 0
SLR_DEPTH_BINS = list(range(11))
SLR_NODATA_VALUES = [
    {"value": 11, "label": "Not projected to be inundated by up to 10 feet"},
    {"value": 12, "label": "Sea-level rise unlikely to be a threat (inland counties)"},
    {"value": 13, "label": "Sea-level rise data unavailable"},
]
SLR_NODATA_COLS = ["not_inundated", "not_applicable", "nodata"]

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

SLR = json.loads(open(json_dir / "slr.json").read())
SLR_LEGEND = SLR[:11]
SLR_NODATA = SLR[11:]


NLCD_YEARS = [2001, 2004, 2006, 2008, 2011, 2013, 2016, 2019, 2021]

# Original codes
NLCD_CODES = {
    11: {"label": "Open water", "color": "#466B9F"},
    12: {
        "label": "Perennial ice/snow",
        "color": "#FFFFFF",
    },  # original color: "#D1DEF8"
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
NLCD_COLORS = landcover_colormap = {k: v["color"] for k, v in NLCD_INDEXES.items()}
NLCD_LEGEND = list(NLCD_CODES.values())


WILDFIRE_RISK = json.loads(open(json_dir / "wildfire_risk.json").read())
WILDFIRE_RISK_COLORS = {
    entry["value"]: entry["color"]
    for entry in WILDFIRE_RISK
    if entry.get("color", None) is not None
}
# NOTE: we use a simplified legend for this instead of all detailed categories;
# saved in descending probability order
WILDFIRE_RISK_LEGEND = [
    dict([key, value])
    for key, value in
    (
        # this dict used to preserve original order and only keep unique label / colors
        dict(
            (("label", e["label"].split(" (")[0]), ("color", e["color"]))
            for e in WILDFIRE_RISK
        ).items()
    )
][::-1]

# precise cutoff points for the categories listed in wildfire_risk.json
# NOTE: the final value is >1 to ensure that bin extends well beyond observed max
WILDFIRE_RISK_BINS = [
    0,
    0.0001,
    0.0002154,
    0.0004642,
    0.001,
    0.0021544,
    0.0046416,
    0.01,
    0.0215443,
    0.0464159,
    2,
]
