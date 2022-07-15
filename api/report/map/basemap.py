import json

from PIL import Image
from pymgl import Map

from api.settings import MAPBOX_ACCESS_TOKEN


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
        img_data = Map(
            "mapbox://styles/mapbox/light-v9",
            width,
            height,
            1,
            *center,
            zoom=zoom,
            provider="mapbox",
            token=MAPBOX_ACCESS_TOKEN,
        ).renderBuffer()
        return Image.frombytes("RGBA", (width, height), img_data), None

    except Exception as ex:
        return None, f"Error generating basemap image ({type(ex)}): {ex}"
