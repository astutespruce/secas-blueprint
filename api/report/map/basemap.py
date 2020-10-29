from .util import render_mbgl_map


STYLE = {
    "version": 8,
    "sources": {
        "basemap": {
            "type": "raster",
            "tiles": [
                "https://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"
            ],
            "tileSize": 256,
        }
    },
    "layers": [{"id": "basemap", "type": "raster", "source": "basemap"}],
}


async def get_basemap_image(center, zoom, width, height):
    """Create a rendered map image of the basemap.

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
        return None, f"Error generating basemap image ({type(ex)}): {ex}"

    return map, None
