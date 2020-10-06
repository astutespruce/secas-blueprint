from io import BytesIO
import logging

import httpx
from PIL import Image

from api.settings import MBGL_SERVER_URL


log = logging.getLogger(__name__)


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
        async with httpx.AsyncClient() as client:
            r = await client.post(MBGL_SERVER_URL, json=params)

        if r.status_code != 200:
            log.error(
                f"Error generating basemap image, HTTP status not 200: {r.text[:255]}"
            )
            return None

        return Image.open(BytesIO(r.content))

    except Exception as ex:
        log.error(f"Unhandled exception generating basemap image")
        log.error(ex)
        return None
