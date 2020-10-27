from copy import deepcopy

from analysis.constants import INPUTS

from .util import render_mbgl_map


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
        map = await render_mbgl_map(params)

    except Exception as ex:
        return None, f"Error generating {state} CHAT image ({type(ex)}): {ex}"

    return map, None
