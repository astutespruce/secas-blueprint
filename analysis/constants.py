from pathlib import Path
from collections import OrderedDict
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

SE_STATES = [
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
    "WV",
]


json_dir = Path("constants")

BLUEPRINT = json.loads(open(json_dir / "blueprint.json").read())
OWNERSHIP = OrderedDict(
    {e["value"]: e for e in json.loads(open(json_dir / "ownership.json").read())}
)
PROTECTION = OrderedDict(
    {e["value"]: e for e in json.loads(open(json_dir / "protection.json").read())}
)

INPUTS = {e["id"]: e for e in json.loads(open(json_dir / "inputs.json").read())}
INPUT_AREA_VALUES = json.loads(open(json_dir / "input_area_values.json").read())


BLUEPRINT_COLORS = {
    i: entry["color"]
    for i, entry in enumerate(BLUEPRINT)
    if "color" in entry and entry["value"] > 0
}


URBAN_YEARS = [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]

URBAN_LEGEND = [
    None,  # spacer; not actually displayed
    {"label": "Urban in 2009", "color": "#696969"},
    {"label": "< 2.5% probability", "color": "#FFEBD6"},
    {"label": "5%", "color": "#F8D7BE"},
    {"label": "10%", "color": "#F2C2A5"},
    {"label": "20%", "color": "#EBAE8D"},
    {"label": "30%", "color": "#E79D7D"},
    {"label": "40%", "color": "#E28C6D"},
    {"label": "50%", "color": "#DE7B5D"},
    {"label": "60%", "color": "#DA694F"},
    {"label": "70%", "color": "#D55740"},
    {"label": "80%", "color": "#D14532"},
    {"label": "90%", "color": "#CE3628"},
    {"label": "95%", "color": "#CB281E"},
    {"label": "97.5%", "color": "#C71914"},
    {"label": "> 97.5% probability", "color": "#C40A0A"},
]


SLR_LEGEND = [
    {"label": "< 1 foot", "color": "#002673"},
    {"label": "1", "color": "#003BA1"},
    {"label": "2", "color": "#0053D0"},
    {"label": "3", "color": "#006EFF"},
    {"label": "4", "color": "#40A0FF"},
    {"label": "5", "color": "#80C9FF"},
    {"label": "≥ 6 feet", "color": "#BFE9FF"},
]


# in DATA_CRS
# everything is on a 0 - 6 range (0 is NODATA)
CHAT_CATEGORIES = [0, 1, 2, 3, 4, 5, 6]
OKCHAT_BOUNDS = [-622242.1977, 1171575.80999999, 142996.3598, 1574946.4713]
TXCHAT_BOUNDS = [-1001835.1092, 310419.3859, 238110.7568, 1519532.92749999]

GULF_HYPOXIA_BOUNDS = [18925.0875, 1453115.574, 608245.08747, 1963775.574]

CARIBBEAN_BOUNDS = [3039491.3248, -78234.1061, 3321630.2684, 39575.8386]

NATURES_NETWORK_BOUNDS = [1079305.0874, 1566755.574, 2268265.0875, 3023045.574]

