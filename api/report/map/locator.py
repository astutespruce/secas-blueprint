from copy import deepcopy
from io import BytesIO
import logging

import httpx
from PIL import Image
import pygeos as pg

from api.settings import MBGL_SERVER_URL
from analysis.lib.pygeos_util import to_dict


log = logging.getLogger(__name__)

ZOOM = 1.75
CENTER = [-85.941, 29.283]
WIDTH = 250
HEIGHT = 150


# basemap from: "https://services.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}"

LOCATOR_STYLE = {
    "version": 8,
    "sources": {
        "basemap": {
            "type": "raster",
            "url": "mbtiles://basemap_esri_ocean",
            "tileSize": 256,
        },
        "states": {"type": "vector", "url": "mbtiles://states"},
        "map_units": {"type": "vector", "url": "mbtiles://se_map_units"},
    },
    "layers": [
        {"id": "basemap", "type": "raster", "source": "basemap"},
        {
            "id": "states",
            "source": "states",
            "source-layer": "states",
            "type": "line",
            "paint": {"line-color": "#444444", "line-width": 1, "line-opacity": 1},
        },
        {
            "id": "mask",
            "source": "map_units",
            "source-layer": "mask",
            "type": "fill",
            "paint": {"fill-color": "#333333", "fill-opacity": 0.5},
        },
        {
            "id": "marker",
            "source": "marker",
            "type": "circle",
            "paint": {
                "circle-color": "#FF0000",
                "circle-radius": 4,
                "circle-opacity": 1,
            },
        },
        {
            "id": "feature-outline",
            "source": "feature",
            "type": "line",
            "paint": {"line-color": "#FF0000", "line-width": 3, "line-opacity": 1},
        },
    ],
}


async def get_locator_map_image(longitude, latitude, bounds, geometry=None):
    """
    Create a rendered locator map image.

    If the bounds cover a large area, `geometry` will be rendered if available,
    otherwise a box covering the bounds will be rendered.  Otherwise, a
    representative point will be displayed on the map.

    Parameters
    ----------
    latitude : float
        latitude of area of interest marker
    longitude : float
        longitude of area of interest marker
    bounds : list-like of xmin, ymin, xmax, ymax
        bounds of geometry to locate on map
    geometry : pygeos.Geometry, optional (default: None)
        If present, will be used to render the area of interest if the bounds
        are very large.

    Returns
    -------
    Image object
    """

    style = deepcopy(LOCATOR_STYLE)

    xmin, ymin, xmax, ymax = bounds

    # If boundary is a large extent (more than 0.5 degree on edge)
    # and has big enough area then render geometry or a box instead of a point
    # NOTE: some multipart features cover large extent and small area, so these
    # drop out if we do not use area threshold.
    if xmax - ymax >= 0.5 or ymax - ymin >= 0.5:
        if geometry and pg.area(geometry) > 0.1:
            geometry = to_dict(geometry)

        else:
            geometry = (
                {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [xmin, ymin],
                            [xmin, ymax],
                            [xmax, ymax],
                            [xmax, ymin],
                            [xmin, ymin],
                        ]
                    ],
                },
            )

        style["sources"]["feature"] = {"type": "geojson", "data": geometry}

    else:
        style["sources"]["marker"] = {
            "type": "geojson",
            "data": {"type": "Point", "coordinates": [longitude, latitude]},
        }

    params = {
        "style": style,
        "center": CENTER,
        "zoom": ZOOM,
        "width": WIDTH,
        "height": HEIGHT,
    }

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(MBGL_SERVER_URL, json=params)

            if r.status_code != 200:
                log.error(f"Error generating locator image: {r.text[:255]}")
                return None

            return Image.open(BytesIO(r.content))

    except Exception as ex:
        log.error(f"Unhandled exception generating locator image: {ex}")
        return None
