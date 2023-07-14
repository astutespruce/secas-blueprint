import json

from PIL import Image
from pymgl import Map

from api.settings import TILE_DIR
from analysis.constants import PROTECTION


# interleave keys and colors for mapbox
color_expr = (
    ["match", ["get", "GAP_Sts"]]
    + [v for k, e in PROTECTION.items() for v in (k, e["color"])]
    + ["#FFF"]
)


STYLE = json.dumps(
    {
        "version": 8,
        "sources": {
            "features": {
                "type": "vector",
                "url": f"mbtiles://{TILE_DIR}/se_other_features.mbtiles",
                "minzoom": 4,
                "maxzoom": 14,
            }
        },
        "layers": [
            {
                "id": "fill",
                "source": "features",
                "source-layer": "ownership",
                "type": "fill",
                "paint": {"fill-opacity": 0.7, "fill-color": color_expr},
            },
            {
                "id": "outline",
                "source": "features",
                "source-layer": "ownership",
                "type": "line",
                "paint": {
                    "line-width": 0.5,
                    "line-color": "#AAAAAA",
                    "line-opacity": 1,
                },
            },
        ],
    }
)


def get_protection_map_image(center, zoom, width, height):
    """Create a rendered map image of protection values (GAP status) from ownership data.

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
        return None, f"Error generating protection image ({type(ex)}): {ex}"
