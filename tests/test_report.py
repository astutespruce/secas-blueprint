import asyncio
from base64 import b64decode, b64encode
import json
import os
from pathlib import Path
from time import time

import pandas as pd
import numpy as np
import pygeos as pg
from pyogrio.geopandas import read_dataframe

from api.report import create_report
from api.report.map import render_maps
from analysis.constants import BLUEPRINT, GEO_CRS, DATA_CRS
from api.report.format import format_number
from api.stats import SummaryUnits, CustomArea
from analysis.lib.pygeos_util import to_crs


# if True, cache maps if not previously created, then reuse
CACHE_MAPS = True


def write_cache(maps, scale, path):
    if not path.exists():
        os.makedirs(path)

    for name, data in maps.items():
        if data is not None:
            with open(path / f"{name}.png", "wb") as out:
                out.write(b64decode(data))

    with open(path / f"scale.json", "w") as out:
        out.write(json.dumps(scale))


def read_cache(path):
    if not path.exists():
        # cache miss
        return None, None

    maps = {}
    for filename in path.glob("*.png"):
        name = filename.stem
        maps[name] = b64encode(open(filename, "rb").read()).decode("utf-8")

    scale = json.loads(open(path / "scale.json").read())

    print("CACHE: loaded maps from cache")

    return maps, scale


### Create reports for an AOI
aois = [
    {"name": "Caledonia area, MS", "path": "caledonia"},
    {"name": "Napoleonville area, LA", "path": "Napoleonville"}
    # {"name": "Area in El Yunque National Forest, PR", "path": "yunque"},
    # {"name":"Area near Magnet, TX", "path": "magnet"},
]


for aoi in aois:
    name = aoi["name"]
    path = aoi["path"]
    print(f"Creating report for {name}...")

    start = time()
    df = read_dataframe(f"examples/{path}.shp", columns=[])
    geometry = pg.make_valid(df.geometry.values.data)

    # dissolve
    geometry = np.asarray([pg.union_all(geometry)])

    ### calculate results, data must be in DATA_CRS
    print("Calculating results...")
    results = CustomArea(geometry, df.crs, name=name).get_results()

    if results is None:
        print(f"AOI: {path} does not overlap Blueprint")
        continue

    out_dir = Path("/tmp/aoi") / path
    if not out_dir.exists():
        os.makedirs(out_dir)

    cache_dir = out_dir / "maps"

    maps = None
    scale = None
    if CACHE_MAPS:
        maps, scale = read_cache(cache_dir)

    if not maps:
        print("Rendering maps...")
        geometry = to_crs(geometry, df.crs, GEO_CRS)
        bounds = pg.total_bounds(geometry)

        has_urban = "proj_urban" in results and results["proj_urban"][4] > 0
        has_slr = "slr" in results
        has_ownership = "ownership" in results
        has_protection = "protection" in results

        task = render_maps(
            bounds,
            geometry=geometry[0],
            # indicators=results["indicators"],
            urban=has_urban,
            slr=has_slr,
            ownership=has_ownership,
            protection=has_protection,
        )

        maps, scale = asyncio.run(task)

        if CACHE_MAPS:
            write_cache(maps, scale, cache_dir)

    results["scale"] = scale

    pdf = create_report(maps=maps, results=results)

    with open(out_dir / f"{path}_report.pdf", "wb") as out:
        out.write(pdf)

    print("Elapsed {:.2f}s".format(time() - start))


### Create reports for summary units
ids = {
    # "huc12": [
    #     #     "130301020902", # far western edge
    #     #     "031501060512",  # partial overlap with SA raster inputs
    #     "031700080402"
    # ],
    # "marine_blocks": [
    #     # "NI18-07-6210", # Atlantic coast
    #     # "NG16-03-299",  # Gulf coast
    #     "NG17-10-6583"  # Florida keys, overlaps with protected areas
    # ]
}


for summary_type in ids:
    units = SummaryUnits(summary_type)

    for id in ids[summary_type]:
        print(f"Creating report for for {id}...")

        out_dir = Path(f"/tmp/{id}")
        cache_dir = out_dir / "maps"

        if not out_dir.exists():
            os.makedirs(out_dir)

        # Fetch results
        results = units.get_results(id)

        has_urban = "proj_urban" in results and results["proj_urban"][4] > 0
        has_slr = "slr" in results
        has_ownership = "ownership" in results
        has_protection = "protection" in results

        maps = None
        if CACHE_MAPS:
            maps, scale = read_cache(cache_dir)

        if not maps:
            print("Rendering maps...")
            task = render_maps(
                results["bounds"],
                summary_unit_id=id,
                # indicators=results["indicators"],
                urban=has_urban,
                slr=has_slr,
                ownership=has_ownership,
                protection=has_protection,
            )
            maps, scale = asyncio.run(task)

            if CACHE_MAPS:
                write_cache(maps, scale, cache_dir)

        results["scale"] = scale

        pdf = create_report(maps=maps, results=results)

        with open(out_dir / f"{id}_report.pdf", "wb") as out:
            out.write(pdf)
