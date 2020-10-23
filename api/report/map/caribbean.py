from io import BytesIO
from copy import deepcopy
import logging

import httpx
from PIL import Image

from api.settings import MBGL_SERVER_URL
from analysis.constants import OWNERSHIP

log = logging.getLogger(__name__)


# interleave keys and colors for mapbox
color_expr = (
    ["match", ["get", "Own_Type"]]
    + [v for k, e in OWNERSHIP.items() for v in (k, e["color"])]
    + ["#FFF"]
)

# Note: only shows watersheds that are high or medium priority
STYLE = {
    "version": 8,
    "sources": {"caribbean": {"type": "vector", "url": "mbtiles://caribbean"}},
    "layers": [
        {
            "id": "fill",
            "source": "caribbean",
            "source-layer": "caribbean",
            "type": "fill",
            "filter": ["<=", ["get", "carrank"], 12],
            "paint": {
                "fill-opacity": 0.7,
                "fill-color": [
                    "case",
                    ["<=", ["get", "carrank"], 8],
                    "#005a32",
                    "#807dba",
                ],
            },
        },
        {
            "id": "outline",
            "source": "caribbean",
            "source-layer": "caribbean",
            "type": "line",
            "filter": ["<=", ["get", "carrank"], 12],
            "paint": {"line-width": 0.5, "line-color": "#AAAAAA", "line-opacity": 1},
        },
    ],
}


async def get_caribbean_map_image(center, zoom, width, height):
    """Create a rendered map image of Caribbean priority watershed values from ownership data.

    Parameters
    ----------
    center : [longitude, latitude]
    zoom : float
    width : int
        map width
    height : int
        map height

    Returns
    -------
    Image object
    """

    params = {
        "style": STYLE,
        "center": center,
        "zoom": zoom,
        "width": width,
        "height": height,
    }

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(MBGL_SERVER_URL, json=params)

            if r.status_code != 200:
                log.error(
                    f"Error generating Caribbean image (HTTP {r.status_code}): {r.text[:255]}"
                )
                return None

        return Image.open(BytesIO(r.content))

    except Exception as ex:
        log.error("Unhandled exception Caribbean ownership image")
        log.error(ex)
        return None
