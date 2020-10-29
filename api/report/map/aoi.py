from copy import deepcopy

from analysis.lib.pygeos_util import to_dict

from .util import render_mbgl_map


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


async def get_aoi_map_image(geometry, center, zoom, width, height):
    """Create a rendered map image of the area of interest.

    Parameters
    ----------
    geometry : pygeos Geometry object (singular)
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
        map = await render_mbgl_map(params)

    except Exception as ex:
        return None, f"Error generating aoi image ({type(ex)}): {ex}"

    return map, None
