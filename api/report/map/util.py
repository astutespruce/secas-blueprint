from base64 import b64encode
from io import BytesIO
import math
import time

import httpx
from PIL import Image
from analysis.constants import M_MILES
from api.settings import MBGL_SERVER_URL

from .errors import MapRenderError


CONNECTION_TIMEOUT = 120  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 0.5  # seconds


def get_center(bounds):
    """
    Calculate center point from bounds in longitude, latitude format.

    Parameters
    ----------
    bounds : list-like of (west, south, east, north) in geographic coordinates
        geographic bounds of the map

    Returns
    -------
    list: [longitude, latitude]
    """

    return [
        ((bounds[2] - bounds[0]) / 2.0) + bounds[0],
        ((bounds[3] - bounds[1]) / 2.0) + bounds[1],
    ]


def merge_maps(maps):
    """Merge maps together in order provided

    Parameters
    ----------
    maps: list-like of PIL Image objects

    Returns
    -------
    PIL Image
    """

    maps = [map for map in maps if map is not None]

    if not maps:
        return None

    img = maps[0]

    for map in maps[1:]:
        img = Image.alpha_composite(img, map)

    return img


def pad_bounds(bounds, percent=0):
    """Pad the bounds by a percentage

    Parameters
    ----------
    bounds : list-like of (west, south, east, north)
    percent : int, optional
        percent to pad the bounds

    Returns
    -------
    (west, south, east, north)
    """

    xmin, ymin, xmax, ymax = bounds
    x_pad = (xmax - xmin) * (percent / 100)
    y_pad = (ymax - ymin) * (percent / 100)

    return [xmin - x_pad, ymin - y_pad, xmax + x_pad, ymax + y_pad]


def to_geojson(series):
    """Return a GeoJSON geometry collection from the series (must be in EPSG:4326).
    Did not use the builtin for the series since it introduces a lot of bloat.
    """

    return {
        "type": "GeometryCollection",
        "geometries": series.apply(lambda x: x.__geo_interface__).to_list(),
    }


def to_base64(img):
    """Convert a PIL Image to base64 encoded PNG.

    Parameters
    ----------
    img : PIL Image object

    Returns
    -------
    bytes
        base64 encoded byte string
    """
    if img is None:
        return None

    buffer = BytesIO()

    # Compression costs time, but since this is all transported in memory
    # we can likely handle larger files
    img.save(buffer, format="PNG", compress_level=1)
    return b64encode(buffer.getvalue()).decode("utf-8")


class Retry(object):
    def __init__(self, max_retries=3):
        self.max_retries = 0

    async def __aenter__(self, func, *args, **kwargs):
        result = None

        for i in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                return result

            except httpx.RequestError as ex:
                pass

            except Exception as ex:
                raise ex

        if result is None:
            raise MapRenderError("Max retries exceeded without success")

    async def __aexit__(self, *args, **kwargs):
        pass


async def render_mbgl_map(params):
    """Render map using mbgl-renderer service.

    Parameters
    ----------
    params : dict
        map rendering parameters

    Returns
    -------
    Image object
        rendered map image
    """

    async with httpx.AsyncClient() as client:

        async def _render_mbgl_map():
            r = await client.post(
                MBGL_SERVER_URL, json=params, timeout=CONNECTION_TIMEOUT
            )

            if r.status_code != 200:
                raise MapRenderError(
                    f"Error rendering map image (HTTP: {r.status_code}): {r.text[:500]}"
                )

            img_bytes = BytesIO(r.content)
            img = Image.open(img_bytes)
            img.load()  # force image to be read into memory
            img_bytes.close()
            return img

        # Wrap above function in a loop so that we retry on connection timeouts
        result = None
        for i in range(MAX_RETRIES):
            try:
                result = await _render_mbgl_map()
                return result

            except httpx.RequestError as ex:
                # wait a little bit then try again
                time.sleep(RETRY_DELAY)

            except Exception as ex:
                raise ex

        if result is None:
            raise MapRenderError("Max connection retries exceeded without success")

