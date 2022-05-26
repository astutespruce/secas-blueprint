import json

from PIL import Image
from pymgl import Map

from api.settings import TILE_DIR

# Note: only shows watersheds that are high or medium priority
STYLE = json.dumps(
    {
        "version": 8,
        "sources": {
            "caribbean": {
                "type": "vector",
                "url": f"mbtiles://{TILE_DIR}/caribbean.mbtiles",
            }
        },
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
                "paint": {
                    "line-width": 0.5,
                    "line-color": "#AAAAAA",
                    "line-opacity": 1,
                },
            },
        ],
    }
)


def get_caribbean_map_image(center, zoom, width, height):
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

    try:
        img_data = Map(STYLE, width, height, 1, *center, zoom=zoom).renderBuffer()
        return Image.frombytes("RGBA", (width, height), img_data), None

    except Exception as ex:
        return None, f"Error generating Caribbean image ({type(ex)}): {ex}"
