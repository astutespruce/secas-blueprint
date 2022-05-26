from copy import deepcopy
import json

from PIL import Image
from pymgl import Map

from api.settings import TILE_DIR
from analysis.constants import INPUTS


# Note: only shows watersheds that are high or medium priority
STYLE = {
    "version": 8,
    "sources": {
        "chat": {"type": "vector", "url": f"mbtiles://{TILE_DIR}/chat.mbtiles"}
    },
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


def get_chat_map_image(state, center, zoom, width, height):
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

    try:
        img_data = Map(
            json.dumps(style), width, height, 1, *center, zoom=zoom
        ).renderBuffer()
        return Image.frombytes("RGBA", (width, height), img_data), None

    except Exception as ex:
        return None, f"Error generating Caribbean image ({type(ex)}): {ex}"
