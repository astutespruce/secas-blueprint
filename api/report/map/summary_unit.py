from io import BytesIO
from copy import deepcopy
import logging

import httpx
from PIL import Image

from api.settings import MBGL_SERVER_URL

log = logging.getLogger(__name__)


STYLE = {
    "version": 8,
    "sources": {"map_units": {"type": "vector", "url": "mbtiles://se_map_units"}},
    "layers": [
        {
            "id": "mask",
            "source": "map_units",
            "source-layer": "mask",
            "type": "fill",
            "paint": {"fill-color": "#333333", "fill-opacity": 0.5},
        },
        {
            "id": "units-outline",
            "source": "map_units",
            "source-layer": "units",
            "type": "line",
            "paint": {"line-width": 3, "line-color": "#000000", "line-opacity": 1},
        },
    ],
}


async def get_summary_unit_map_image(id, center, zoom, width, height):
    """Create a rendered map image of an existing summary unit.

    Parameters
    ----------
    id : str
        ID of summary unit
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

    style = deepcopy(STYLE)
    # filter IN current unit
    style["layers"][1]["filter"] = ["==", ["get", "id"], id]

    params = {
        "style": style,
        "center": center,
        "zoom": zoom,
        "width": width,
        "height": height,
    }

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(MBGL_SERVER_URL, json=params)

            if r.status_code != 200:
                log.error(f"Error generating summary unit image: {r.text[:255]}")
                return None

            return Image.open(BytesIO(r.content))

    except Exception as ex:
        log.error("Unhandled exception generating summary unit image")
        log.error(ex)
        return None
