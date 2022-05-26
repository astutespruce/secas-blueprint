import json

from PIL import Image
from pymgl import Map


STYLE = json.dumps(
    {
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
)


def get_basemap_image(center, zoom, width, height):
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

    try:
        img_data = Map(STYLE, width, height, 1, *center, zoom=zoom).renderBuffer()
        return Image.frombytes("RGBA", (width, height), img_data), None

    except Exception as ex:
        return None, f"Error generating basemap image ({type(ex)}): {ex}"
