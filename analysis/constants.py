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

# 32 is OK for regional level maps; 16 is more typical for big areas like ACF
OVERVIEW_FACTORS = [2, 4, 8, 16, 32]

# Use 480m cells for mask
MASK_FACTOR = 16

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
    "USVI",
    "WV",
]


json_dir = Path("constants")

BLUEPRINT = json.loads(open(json_dir / "blueprint.json").read())
BLUEPRINT_COLORS = {
    i: entry["color"]
    for i, entry in enumerate(BLUEPRINT)
    if "color" in entry and entry["value"] > 0
}

INPUTS = {e["id"]: e for e in json.loads(open(json_dir / "inputs.json").read())}
INPUT_AREA_VALUES = json.loads(open(json_dir / "input_area_values.json").read())


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
    {"label": "Current (already flooded at high tide)", "color": "#002673"},
    {"label": "1 foot", "color": "#003BA1"},
    {"label": "2 feet", "color": "#0053D0"},
    {"label": "3 feet", "color": "#006EFF"},
    {"label": "4 feet", "color": "#40A0FF"},
    {"label": "5 feet", "color": "#80C9FF"},
    {"label": "6 feet", "color": "#BFE9FF"},
]


# everything is on a 0 - 6 range (0 is NODATA)
CHAT_CATEGORIES = [0, 1, 2, 3, 4, 5, 6]

# Bounds are in DATA_CRS and are used for filtering areas of interest for
# potential overlaps with input areas
OKCHAT_BOUNDS = [-622242.1977, 1171575.80999999, 142996.3598, 1574946.4713]
TXCHAT_BOUNDS = [-1001835.1092, 310419.3859, 238110.7568, 1519532.92749999]
GULF_HYPOXIA_BOUNDS = [18925.0875, 1453115.574, 608245.08747, 1963775.574]
CARIBBEAN_BOUNDS = [3039491.3248, -78234.1061, 3321630.2684, 39575.8386]
NATURES_NETWORK_BOUNDS = [1079305.0874, 1566755.574, 2268265.0875, 3023045.574]
NATURESCAPE_BOUNDS = [645325.0874, 1093385.574, 1343365.0875, 2064065.574]
SOUTHATLANTIC_BOUNDS = [933865.0874, 758285.574, 2200555.0875, 1819415.574]
FLORIDA_BOUNDS = [796765.0874, 269495.5740, 1600825.0875, 961145.574]
FLORIDA_MARINE_BOUNDS = [811825.0874, 177875.574, 1894105.0875, 1018475.574]
MIDSE_BOUNDS = [120775.0874, 669545.574, 1218685.0875, 1872785.574]
