from copy import deepcopy
import json

from pymgl import Map
import shapely

from api.settings import MAPBOX_ACCESS_TOKEN, TILE_DIR
from analysis.lib.geometry import to_dict


ZOOM = 1.75
CENTER = [-85.941, 29.283]
WIDTH = 230
HEIGHT = 150


# basemap from: "https://services.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}"

LOCATOR_STYLE = {
    "version": 8,
    "sources": {
        "basemap": {
            "type": "raster",
            "url": f"mbtiles://{TILE_DIR}/basemap_esri_ocean.mbtiles",
            "tileSize": 256,
        },
        "states": {"type": "vector", "url": f"mbtiles://{TILE_DIR}/states.mbtiles"},
        "map_units": {
            "type": "vector",
            "url": f"mbtiles://{TILE_DIR}/se_map_units.mbtiles",
        },
        "mask": {
            "type": "vector",
            "url": f"mbtiles://{TILE_DIR}/se_mask.mbtiles",
        },
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
            "source": "mask",
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


def get_locator_map_image(longitude, latitude, bounds, geometry=None):
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
    geometry : shapely.Geometry, optional (default: None)
        If present, will be used to render the area of interest if the bounds
        are very large.

    Returns
    -------
    bytes
        PNG image bytes
    """

    style = deepcopy(LOCATOR_STYLE)

    xmin, ymin, xmax, ymax = bounds

    # If boundary is a large extent (more than 0.5 degree on edge)
    # and has big enough area then render geometry or a box instead of a point
    # NOTE: some multipart features cover large extent and small area, so these
    # drop out if we do not use area threshold.

    if xmax - xmin >= 0.5 or ymax - ymin >= 0.5:
        if geometry:
            if shapely.area(geometry) > 0.1:
                geometry = to_dict(geometry)
            else:
                geometry = to_dict(shapely.envelope(geometry))
        else:
            geometry = to_dict(shapely.box(xmin, ymin, xmax, ymax))

        style["sources"]["feature"] = {"type": "geojson", "data": geometry}

    else:
        style["sources"]["marker"] = {
            "type": "geojson",
            "tolerance": 0.1,
            "data": {"type": "Point", "coordinates": [longitude, latitude]},
        }

    try:
        return (
            Map(
                json.dumps(style),
                WIDTH,
                HEIGHT,
                1,
                *CENTER,
                zoom=ZOOM,
                token=MAPBOX_ACCESS_TOKEN,
                provider="mapbox",
            ).renderPNG(),
            None,
        )

    except Exception as ex:
        return None, f"Error generating locator image ({type(ex)}): {ex}"
