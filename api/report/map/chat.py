from io import BytesIO
from copy import deepcopy
import logging

import httpx
from PIL import Image

from api.settings import MBGL_SERVER_URL
from analysis.constants import INPUTS


log = logging.getLogger(__name__)


# Note: only shows watersheds that are high or medium priority
STYLE = {
    "version": 8,
    "sources": {"chat": {"type": "vector", "url": "mbtiles://chat"}},
    "layers": [],
}


def get_layer(state):
    return {
        "id": "fill",
        "source": "chat",
        "source-layer": f"{state}chat",
        "type": "fill",
        "paint": {
            "fill-opacity": 0.7,
            "fill-color": ["match", ["get", "chatrank"]]
            + [
                item
                for entry in INPUTS[f"{state}chat"]["values"][1:]
                for item in (entry["value"], entry["color"])
            ]
            + ["#EEE"],
        },
    }


async def get_chat_map_image(state, center, zoom, width, height):
    """Create a rendered map image of CHAT Rank for a given state.

    Parameters
    ----------
    state : str, one of ['ok', 'tx']
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
    style["layers"].append(get_layer(state))

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
                log.error(
                    f"Error generating CHAT Rank image for state {state} (HTTP {r.status_code}): {r.text[:255]}"
                )
                return None

        return Image.open(BytesIO(r.content))

    except Exception as ex:
        log.error(f"Unhandled exception generating CHAT Rank image for state {state}")
        log.error(ex)
        return None
