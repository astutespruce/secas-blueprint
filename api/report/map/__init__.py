import asyncio
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import rasterio

from .aoi import get_aoi_map_image
from .basemap import get_basemap_image
from .locator import get_locator_map_image
from .ownership import get_ownership_map_image
from .protection import get_protection_map_image
from .raster import render_raster, extract_data_for_map
from .summary_unit import get_summary_unit_map_image
from .mercator import get_zoom, get_map_bounds, get_map_scale
from .util import pad_bounds, get_center, to_base64, merge_maps

# input area specific map handlers
from .caribbean import get_caribbean_map_image
from .chat import get_chat_map_image

from analysis.constants import BLUEPRINT_COLORS, URBAN_LEGEND, SLR_LEGEND, INPUTS
from api.settings import MAP_RENDER_THREADS


WIDTH = 740
HEIGHT = 440
PADDING = 5


src_dir = Path("data/inputs")
blueprint_filename = src_dir / "se_blueprint2020.tif"
urban_filename = src_dir / "threats/urban/urban_2060.tif"
slr_filename = src_dir / "threats/slr/slr.vrt"
inputs_dir = src_dir / "indicators"


async def render_mbgl_maps(**kwargs):
    results = await asyncio.gather(*kwargs.values())
    return {key: result for key, result in zip(kwargs.keys(), results)}


def render_raster_map(bounds, scale, basemap_image, aoi_image, id, path, colors):
    raster_img = render_raster(path, bounds, scale, WIDTH, HEIGHT, colors)

    map_image = None
    if raster_img is not None:
        map_image = merge_maps([basemap_image, raster_img, aoi_image])
        map_image = to_base64(map_image)

    return id, map_image


async def render_raster_maps(
    bounds, scale, basemap_image, aoi_image, raster_input_ids, indicators, urban, slr
):
    executor = ThreadPoolExecutor(max_workers=MAP_RENDER_THREADS)
    loop = asyncio.get_event_loop()

    base_args = (bounds, scale, basemap_image, aoi_image)

    task_args = [("blueprint", blueprint_filename, BLUEPRINT_COLORS)]

    for input_id in raster_input_ids:
        input_info = INPUTS[input_id]
        # FIXME: temporary just while waiting on FL Marine blueprint
        if not input_info["filename"]:
            print(f"TODO: render {input_id}")
            continue

        # exclude 0 values
        colors = {
            e["value"]: e["color"] for e in input_info["values"] if e["value"] != 0
        }
        task_args.append((input_id, inputs_dir / input_info["filename"], colors))

    if urban:
        colors = {i: e["color"] for i, e in enumerate(URBAN_LEGEND) if e is not None}
        task_args.append(("urban_2060", urban_filename, colors))

    if slr:
        colors = {i: e["color"] for i, e in enumerate(SLR_LEGEND)}
        task_args.append(("slr", slr_filename, colors))

    # NOTE: have to have handle on pending or task loop gets closed too soon
    completed, pending = await asyncio.wait(
        [
            loop.run_in_executor(executor, render_raster_map, *base_args, *args)
            for args in task_args
        ]
    )

    results = [t.result() for t in completed]
    maps = {k: v for k, v in results if v is not None}

    return maps


async def render_maps(
    bounds,
    geometry=None,
    summary_unit_id=None,
    input_ids=None,
    indicators=None,
    urban=False,
    slr=False,
    ownership=False,
    protection=False,
):
    """Render maps for locator and each raster dataset that overlaps with area
    of interest.

    Parameters
    ----------
    bounds : list-like of [xmin, ymin, xmax, ymax]
        bounds of area of interest, will be used to derive map bounds.
    geometry : pygeos.Geometry, optional (default: None)
        If present, will be used to render the area of interest
    summary_unit_id : [type], optional (default: None)
        If present, will be used to identify the selected summary unit
    input_ids : list-like, optional (default: None)
        If present, is a list of input area ids
    indicators : list-like, optional (default: None)
        If present, is a list of all indicator IDs to render.
    urban : bool, optional (default: False)
        If True, urban will be rendered.
    slr : bool, optional (default: False)
        If True, sea level rise will be rendered.
    ownership : bool, optional (default: False)
        If True, ownership will be rendered.
    protection : bool, optional (default: False)
        If True, ownership will be rendered.

    Returns
    -------
    dict
        Dictionary of map IDs to base64 data
    """

    maps = {}

    bounds = pad_bounds(bounds, PADDING)
    center = get_center(bounds)
    zoom = get_zoom(bounds, WIDTH, HEIGHT)

    bounds = get_map_bounds(center, zoom, WIDTH, HEIGHT)
    scale = get_map_scale(bounds, WIDTH)

    tasks = {
        "locator": get_locator_map_image(*center, bounds=bounds, geometry=geometry),
        "basemap": get_basemap_image(center, zoom, WIDTH, HEIGHT),
    }

    if geometry:
        tasks["aoi"] = get_aoi_map_image(geometry, center, zoom, WIDTH, HEIGHT)

    elif summary_unit_id:
        tasks["aoi"] = get_summary_unit_map_image(
            summary_unit_id, center, zoom, WIDTH, HEIGHT
        )

    if ownership:
        tasks["ownership"] = get_ownership_map_image(center, zoom, WIDTH, HEIGHT)

    if protection:
        tasks["protection"] = get_protection_map_image(center, zoom, WIDTH, HEIGHT)

    if input_ids:
        if "car" in input_ids:
            tasks["car"] = get_caribbean_map_image(center, zoom, WIDTH, HEIGHT)

        if "okchat" in input_ids:
            tasks["okchat"] = get_chat_map_image("ok", center, zoom, WIDTH, HEIGHT)

        if "txchat" in input_ids:
            tasks["txchat"] = get_chat_map_image("tx", center, zoom, WIDTH, HEIGHT)

    mbgl_maps = await render_mbgl_maps(**tasks)

    maps["locator"] = to_base64(mbgl_maps["locator"])
    basemap_image = mbgl_maps.get("basemap", None)
    aoi_image = mbgl_maps.get("aoi", None)

    # make sure that images are fully loaded before sending to other threads
    if basemap_image is not None:
        basemap_image.load()

    if aoi_image is not None:
        aoi_image.load()

    ownership_image = mbgl_maps.get("ownership", None)
    if ownership_image is not None:
        maps["ownership"] = to_base64(
            merge_maps([basemap_image, mbgl_maps["ownership"], aoi_image])
        )

    protection_image = mbgl_maps.get("protection", None)
    if protection_image is not None:
        maps["protection"] = to_base64(
            merge_maps([basemap_image, mbgl_maps["protection"], aoi_image])
        )

    if input_ids:
        for input_id in input_ids:
            if input_id in mbgl_maps:
                maps[input_id] = to_base64(
                    merge_maps([basemap_image, mbgl_maps[input_id], aoi_image])
                )

    raster_input_ids = (
        [i for i in input_ids if not i in {"car", "okchat", "txchat"}]
        if input_ids
        else []
    )

    # Use background threads for rendering rasters
    raster_maps = await render_raster_maps(
        bounds,
        scale,
        basemap_image,
        aoi_image,
        raster_input_ids,
        indicators or [],
        urban,
        slr,
    )

    maps.update(raster_maps)

    return maps, scale
