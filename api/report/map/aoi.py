from copy import deepcopy
import json

from PIL import Image
from pymgl import Map

from analysis.lib.geometry import to_dict


STYLE = {
    "version": 8,
    "sources": {"aoi": {"type": "geojson", "data": ""}},
    "layers": [
        {
            "id": "aoi",
            "source": "aoi",
            "type": "line",
            "paint": {"line-width": 2, "line-color": "#000000", "line-opacity": 1},
        }
    ],
}


def get_aoi_map_image(geometry, center, zoom, width, height):
    """Create a rendered map image of the area of interest.

    Parameters
    ----------
    geometry : shapely Geometry object (singular)
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
    style["sources"]["aoi"]["data"] = to_dict(geometry)

    params = {
        "style": style,
        "center": center,
        "zoom": zoom,
        "width": width,
        "height": height,
    }

    try:
        img_data = Map(
            json.dumps(style), width, height, 1, *center, zoom=zoom
        ).renderBuffer()
        return Image.frombytes("RGBA", (width, height), img_data), None

    except Exception as ex:
        return None, f"Error generating aoi image ({type(ex)}): {ex}"
