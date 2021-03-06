from .util import render_mbgl_map


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
        map = await render_mbgl_map(params)

    except Exception as ex:
        return None, f"Error generating Caribbean image ({type(ex)}): {ex}"

    return map, None
