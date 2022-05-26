from copy import deepcopy
import json

from PIL import Image
from pymgl import Map

from api.settings import TILE_DIR


STYLE = {
    "version": 8,
    "sources": {
        "map_units": {
            "type": "vector",
            "url": f"mbtiles://{TILE_DIR}/se_map_units.mbtiles",
        }
    },
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


def get_summary_unit_map_image(id, center, zoom, width, height):
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

    try:
        img_data = Map(
            json.dumps(style), width, height, 1, *center, zoom=zoom
        ).renderBuffer()
        return Image.frombytes("RGBA", (width, height), img_data), None

    except Exception as ex:
        return None, f"Error generating summary_unit image ({type(ex)}): {ex}"
