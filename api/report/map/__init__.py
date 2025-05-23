import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from .aoi import get_aoi_map_image
from .basemap import get_basemap_image
from .locator import get_locator_map_image
from .raster import render_raster
from .summary_unit import get_summary_unit_map_image
from .mercator import get_zoom, get_map_bounds, get_map_scale
from .util import pad_bounds, get_center, merge_maps, to_png_bytes


from analysis.constants import (
    BLUEPRINT_COLORS,
    CORRIDORS_COLORS,
    PROTECTED_AREAS_COLORS,
    URBAN_COLORS,
    SLR_LEGEND,
    INDICATORS_INDEX,
    WILDFIRE_RISK_COLORS,
)
from api.settings import MAP_RENDER_THREADS


WIDTH = 740
HEIGHT = 420
PADDING = 5


src_dir = Path("data/inputs")
blueprint_filename = src_dir / "blueprint.tif"
corridors_filename = src_dir / "corridors.tif"
protected_areas_filename = src_dir / "boundaries/protected_areas.tif"
urban_filename = src_dir / "threats/urban/urban_2060_binned.tif"
slr_filename = src_dir / "threats/slr/slr.tif"
wildfire_risk_filename = src_dir / "threats/wildfire_risk/wildfire_risk.tif"
indicators_dir = src_dir / "indicators"


def render_raster_map(bounds, scale, basemap_image, aoi_image, id, path, colors):
    """Render raster dataset map based on bounds.  Merge this over basemap image
    and under aoi_image.

    Parameters
    ----------
    bounds : list-like of [xmin, ymin, xmax, ymax]
        bounds of map
    scale : dict
        map scale info
    basemap_image : Image object
    aoi_image : Image object
    id : str
        map ID
    path : str
        path to raster dataset
    colors : list-like of colors
        colors to render map image based on values in raster

    Returns
    -------
    id, Image object
        Image object is None if it could not be rendered or does not overlap bounds
    """
    raster_img = render_raster(path, bounds, scale, WIDTH, HEIGHT, colors)
    map_image = merge_maps([basemap_image, raster_img, aoi_image])
    map_image = to_png_bytes(map_image)

    return id, map_image


async def render_raster_maps(
    bounds,
    scale,
    basemap_image,
    aoi_image,
    indicators,
    corridors=False,
    urban=False,
    slr=False,
    wildfire_risk=False,
    protected_areas=False,
):
    """Asynchronously render Raster maps.

    Parameters
    ----------
    bounds : list-like of [xmin, ymin, xmax, ymax]
        bounds of map
    scale : dict
        map scale info
    basemap_image : Image object
    aoi_image : Image object
    indicators : list-like of indicator IDs
    corridors : bool (default False)
        if True, will render corridors for Blueprint
    urban : bool (default False)
        if True, will render urban map
    slr : bool (default False)
        if True, will render SLR map
    wildfire_risk : bool (default False)
        if True, will render wildfire_risk map
    protected_areas : bool (default False)
        if True, will render protected_areas map

    Returns
    -------
    dict, dict
        tuple of (maps, errors) keyed by map ID
    """
    executor = ThreadPoolExecutor(max_workers=MAP_RENDER_THREADS)
    loop = asyncio.get_event_loop()

    base_args = (bounds, scale, basemap_image, aoi_image)

    task_args = [("blueprint", blueprint_filename, BLUEPRINT_COLORS)]

    for id in indicators:
        indicator = INDICATORS_INDEX[id]
        colors = {
            e["value"]: e["color"]
            for e in indicator["values"]
            if e["color"] is not None
        }
        task_args.append(
            (
                id,
                indicators_dir / indicator["filename"],
                colors,
            )
        )

    if corridors:
        task_args.append(("corridors", corridors_filename, CORRIDORS_COLORS))

    if urban:
        task_args.append(
            (
                "urban_2060",
                urban_filename,
                URBAN_COLORS,
            )
        )

    if slr:
        colors = {e["value"]: e["color"] for i, e in enumerate(SLR_LEGEND)}
        task_args.append(("slr", slr_filename, colors))

    if wildfire_risk:
        colors = WILDFIRE_RISK_COLORS
        task_args.append(("wildfire_risk", wildfire_risk_filename, colors))

    if protected_areas:
        colors = PROTECTED_AREAS_COLORS
        task_args.append(("protected_areas", protected_areas_filename, colors))

    # NOTE: have to have handle on pending or task loop gets closed too soon
    completed, pending = await asyncio.wait(
        [
            loop.run_in_executor(executor, render_raster_map, *base_args, *args)
            for args in task_args
        ]
    )

    results = [t.result() for t in completed]
    maps = {k: v for k, v in results if v is not None}

    # TODO: capture and return errors
    errors = {}

    return maps, errors


async def render_maps(
    bounds,
    geometry=None,
    summary_unit_id=None,
    indicators=None,
    corridors=False,
    urban=False,
    slr=False,
    wildfire_risk=False,
    protected_areas=False,
    add_mask=False,
):
    """Render maps for locator and each raster dataset that overlaps with area
    of interest.

    Parameters
    ----------
    bounds : list-like of [xmin, ymin, xmax, ymax]
        bounds of area of interest, will be used to derive map bounds.
    geometry : shapely.Geometry, optional (default: None)
        If present, will be used to render the area of interest
    summary_unit_id : [type], optional (default: None)
        If present, will be used to identify the selected summary unit
    indicators : list-like, optional (default: None)
        If present, is a list of all indicator IDs to render.
    corridors : bool, optional (default: False)
        If True, corridors will be rendered
    urban : bool, optional (default: False)
        If True, urban will be rendered.
    slr : bool, optional (default: False)
        If True, sea level rise will be rendered.
    wildfire_risk : bool, optional (default: False)
        If True, wildfire risk will be rendered.
    protected_areas : bool, optional (default: False)
        If True, protected areas will be rendered.
    add_mask : bool, optional (default: False)
        If True, will add a light transparent mask outside geometry

    Returns
    -------
    (dict, dict, dict)
        Tuple of (maps, scale, errors)
        Dictionary of map IDs to base64 data
        Dictionary of map scale information
        Dictionary of map IDs to rendering errors
    """

    maps = {}
    errors = {}

    bounds = pad_bounds(bounds, PADDING)
    center = get_center(bounds)
    zoom = get_zoom(bounds, WIDTH, HEIGHT)

    bounds = get_map_bounds(center, zoom, WIDTH, HEIGHT)
    scale = get_map_scale(bounds, WIDTH)

    locator_image, error = get_locator_map_image(
        *center, bounds=bounds, geometry=geometry
    )
    if error:
        errors["locator"] = error
    else:
        maps["locator"] = locator_image

    basemap_image, error = get_basemap_image(center, zoom, WIDTH, HEIGHT)
    if error:
        errors["basemap"] = error

    aoi_image = None

    if geometry:
        aoi_image, error = get_aoi_map_image(
            geometry, center, zoom, WIDTH, HEIGHT, add_mask=add_mask
        )
        if error:
            errors["aoi"] = error

    elif summary_unit_id:
        aoi_image, error = get_summary_unit_map_image(
            summary_unit_id, center, zoom, WIDTH, HEIGHT
        )
        if error:
            errors["aoi"] = error

    # Use background threads for rendering rasters
    raster_maps, raster_map_errors = await render_raster_maps(
        bounds,
        scale,
        basemap_image,
        aoi_image,
        indicators or [],
        corridors,
        urban,
        slr,
        wildfire_risk,
        protected_areas,
    )

    maps.update(raster_maps)
    errors.update(raster_map_errors)

    return maps, scale, errors
