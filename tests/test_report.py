import asyncio
from base64 import b64decode, b64encode
import json
import os
from pathlib import Path
from time import time

import numpy as np
import pygeos as pg
from pyogrio.geopandas import read_dataframe


from analysis.constants import GEO_CRS, DATA_CRS, M2_ACRES
from analysis.lib.geometry import to_crs
from api.report import create_report
from api.report.map import render_maps
from api.stats import SummaryUnits, CustomArea


# if True, cache maps if not previously created, then reuse
CACHE_MAPS = False


def write_cache(maps, scale, path):
    if not path.exists():
        os.makedirs(path)

    for name, data in maps.items():
        if data is not None:
            with open(path / f"{name.replace(':', '__')}.png", "wb") as out:
                out.write(b64decode(data))

    with open(path / f"scale.json", "w") as out:
        out.write(json.dumps(scale))


def read_cache(path):
    if not path.exists():
        # cache miss
        return None, None

    maps = {}
    for filename in path.glob("*.png"):
        name = filename.stem.replace("__", ":")
        maps[name] = b64encode(open(filename, "rb").read()).decode("utf-8")

    scale = json.loads(open(path / "scale.json").read())

    print("CACHE: loaded maps from cache")

    return maps, scale


### Create reports for an AOI
aois = [
    # {"name": "Greenway Priority 123 Merge", "path": "Greenway_priority123_Merge_Diss"},
    # {"name": "South Carolina", "path": "SC_SECAS_states"},
    # {
    #     "name": "NWFL Sentinel Landscapes Geography",
    #     "path": "NWFL_SentinelLandscapesGeography_20210812",
    # }
    # {"name": "Alabama", "path": "AL_SECAS_states"},
    # {"name": "Arkansas", "path": "AR_SECAS_states"},
    # {"name": "Florida", "path": "FL_SECAS_states"},
    # {"name": "Georgia", "path": "GA_SECAS_states"},
    # {"name": "Kentucky", "path": "KY_SECAS_states"},
    # {"name": "Louisiana", "path": "LA_SECAS_states"},  # TODO: FIX this geometry
    # {"name": "Mississippi", "path": "MS_SECAS_states"},
    # {"name": "North Carolina", "path": "NC_SECAS_states"},
    # {"name": "Tennessee", "path": "TN_SECAS_states"},
    # {"name": "FL test", "path": "EvergladesHeadwaterComplex_APPTYPE_0"}
    # {"name": "Guild Tracts", "path": "GuildTracts"}
    # {"name": "Florida Panhandle Boundary", "path": "FL_panhadle_boundary"}
    # {"name": "Dell Murphy wetlands", "path": "Dell Murphy wetlands"},
    # {"name": "TRB GA", "path": "TRB_GA"},
    # {"name": "Florida 5 Star County Boundary", "path": "FL_5StarCounty_Boundary"}
    # {"name": "Cumberland Plateau Focus Area", "path": "NFWF_Cumberland_Fund_TN"}
    # {"name": "Enviva Hamlet", "path": "Enviva_Hamlet_80_mile_sourcing_radius"},
    # {"name": "LCP: Black River", "path": "LCP_BlackRiver"},
    # {"name": "Green River proposed boundary", "path": "GreenRiver_ProposedBoundary"},
    # {"name": "LCP: Broad", "path": "LCP_Broad"},
    # {"name": "Caledonia area, MS", "path": "caledonia"},
    {"name": "Napoleonville area, LA", "path": "Napoleonville"},
    # {"name": "Area in El Yunque National Forest, PR", "path": "yunque"},
    # {"name": "San Juan area, PR", "path": "SanJuan"},
    # {"name": "Area near Magnet, TX", "path": "magnet"},
    # {"name": "TriState area at junction of MO, OK, KS", "path": "TriState"},
    # {"name": "Quincy, FL area", "path": "Quincy"},
    # {"name": "Doyle Springs, TN area", "path": "DoyleSprings"},
    # {"name": "Cave Spring, VA area", "path": "CaveSpring"},
    # {"name": "South Atlantic Offshore", "path": "SAOffshore"},
    # {"name": "Florida Offshore", "path": "FLOffshore"},
    # {"name": "Razor", "path": "Razor"}
]


for aoi in aois:
    name = aoi["name"]
    path = aoi["path"]
    print(f"Creating report for {name}...")

    start = time()
    df = read_dataframe(f"examples/{path}.shp", columns=[]).to_crs(DATA_CRS)
    geometry = pg.make_valid(df.geometry.values.data)

    # dissolve
    geometry = np.asarray([pg.union_all(geometry)])

    extent_area = pg.area(pg.box(*pg.total_bounds(geometry))) * M2_ACRES
    print(
        f"Area of extent: {extent_area:,.0f}",
    )

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

        has_corridors = "corridors" in results
        has_urban = "proj_urban" in results and results["proj_urban"][-1] > 0
        has_slr = "slr" in results
        has_ownership = "ownership" in results
        has_protection = "protection" in results

        # compile indicator IDs across all inputs
        indicators = []
        for input_area in results["inputs"]:
            for ecosystem in input_area.get("ecosystems", []):
                indicators.extend([i["id"] for i in ecosystem["indicators"]])

        task = render_maps(
            bounds,
            geometry=geometry[0],
            indicators=indicators,
            input_ids=results["input_ids"],
            corridors=has_corridors,
            urban=has_urban,
            slr=has_slr,
            ownership=has_ownership,
            protection=has_protection,
        )

        maps, scale, errors = asyncio.run(task)

        if errors:
            print("Errors", errors)

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
    #     "030502050309"
    #     #     #     #     # "111102050103"  # has no protected areas
    # "210100050503",  # PR
    # "110702071001",  # at junction of gulf_hypoxia, okchat, midse
    #     # "031501100102",  # has overlaps with MidSE, SA, and NatureScape
    # "120100040301",  # at junction of txchat, midse
    #     "031200030902",  # at overlap area between FL, MidSE, and SA
    #     #     #     #     #     #     # "060200020506",  # in AppLCC area
    #     #     # "050302030503",  # in Nature's Network area
    #     #     # "030101010301",  # in Nature's Network  / South Atlantic overlap area
    #     #     #     #     #     #     ##################
    #     #     #     #     #     #     #     #     "130301020902", # far western edge
    #     #     #     #     #     #     #     #     "031501060512",  # partial overlap with SA raster inputs
    #     #     #     #     #     #     #     "031700080402"
    # "030101030404",  # Nature's Network at edge of input area
    # "031101020903",  # Florida with inland marine indicators
    # "031102050805",  # Florida gulf coast
    # ],
    # "marine_blocks": [
    #     # "NI18-07-6210",  # Atlantic coast
    #     #     # #     "NG16-03-299",  # Gulf coast
    #     "NG17-10-6583"  # Florida keys, overlaps with protected areas
    # ],
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

        has_corridors = "corridors" in results
        has_urban = "proj_urban" in results and results["proj_urban"][-1] > 0
        has_slr = "slr" in results
        has_ownership = "ownership" in results
        has_protection = "protection" in results

        # compile indicator IDs across all inputs
        indicators = []
        for input_area in results["inputs"]:
            for ecosystem in input_area.get("ecosystems", []):
                indicators.extend([i["id"] for i in ecosystem["indicators"]])

        maps = None
        if CACHE_MAPS:
            maps, scale = read_cache(cache_dir)

        if not maps:
            print("Rendering maps...")
            task = render_maps(
                results["bounds"],
                summary_unit_id=id,
                indicators=indicators,
                input_ids=results["input_ids"],
                corridors=has_corridors,
                urban=has_urban,
                slr=has_slr,
                ownership=has_ownership,
                protection=has_protection,
            )
            maps, scale, errors = asyncio.run(task)

            if errors:
                print("Errors", errors)

            if CACHE_MAPS:
                write_cache(maps, scale, cache_dir)

        results["scale"] = scale

        pdf = create_report(maps=maps, results=results)

        with open(out_dir / f"{id}_report.pdf", "wb") as out:
            out.write(pdf)
