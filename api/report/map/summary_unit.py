from copy import deepcopy

from .util import render_mbgl_map


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
        map = await render_mbgl_map(params)

    except Exception as ex:
        return None, f"Error generating summary_unit image ({type(ex)}): {ex}"

    return map, None
