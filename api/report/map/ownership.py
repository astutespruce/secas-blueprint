from analysis.constants import OWNERSHIP

from .util import render_mbgl_map


# interleave keys and colors for mapbox
color_expr = (
    ["match", ["get", "Own_Type"]]
    + [v for k, e in OWNERSHIP.items() for v in (k, e["color"])]
    + ["#FFF"]
)


STYLE = {
    "version": 8,
    "sources": {
        "ownership": {
            "type": "vector",
            "url": "mbtiles://se_ownership",
            "tileSize": 256,
        }
    },
    "layers": [
        {
            "id": "fill",
            "source": "ownership",
            "source-layer": "ownership",
            "type": "fill",
            "paint": {"fill-opacity": 0.7, "fill-color": color_expr},
        },
        {
            "id": "outline",
            "source": "ownership",
            "source-layer": "ownership",
            "type": "line",
            "paint": {"line-width": 0.5, "line-color": "#AAAAAA", "line-opacity": 1},
        },
    ],
}


async def get_ownership_map_image(center, zoom, width, height):
    """Create a rendered map image of land owner values from ownership data.

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
        map = await render_mbgl_map(params)

    except Exception as ex:
        return None, f"Error generating ownership image ({type(ex)}): {ex}"

    return map, None
