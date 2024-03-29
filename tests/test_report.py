import asyncio
import json
import os
from base64 import b64decode, b64encode
from pathlib import Path
from time import time

from pyogrio.geopandas import read_dataframe
import shapely
from progress.bar import Bar

from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES
from analysis.lib.geometry import dissolve
from api.report import create_report
from api.report.map import render_maps
from api.stats.custom_area import get_custom_area_results
from api.stats.summary_units import get_summary_unit_results

# if True, cache maps if not previously created, then reuse
CACHE_MAPS = False


def write_cache(maps, scale, path):
    if not path.exists():
        os.makedirs(path)

    for name, data in maps.items():
        if data is not None:
            with open(path / f"{name.replace(':', '__')}.png", "wb") as out:
                out.write(b64decode(data))

    with open(path / "scale.json", "w") as out:
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
    # {"name": "Gulf_SECAS_CBRS_Polygons", "path": "Gulf_SECAS_CBRS_Polygons"},
    # {"name": "Caribbean_SECAS_CBRS_Polygons", "path": "Caribbean_SECAS_CBRS_Polygons"},
    # {"name": "Atlantic_SECAS_CBRS_Polygons", "path": "Atlantic_SECAS_CBRS_Polygons"},
    # {"name": "SECAS_CBRS_Polygons", "path": "SECAS_CBRS_Polygons"},
    # {"name": "", "path": "large_poly"}
    # {"name": "", "path": "no_urban"}
    # {"name": "GA Sentinal Landscapes: Fort Benning Area", "path": "benareautm_polygon"},
    # {
    #     "name": "GA Sentinal Landscapes: Coastal Area",
    #     "path": "coastareautm_polygon",
    # },
    # {
    #     "name": "GA Sentinal Landscapes: Savannah River Area",
    #     "path": "savboundutm_polygon",
    # },
    # {"name": "", "path": "Bayou P FLP"}
    # {
    #     "name": "West Central Longleaf and Streams",
    #     "path": "West_Central_Longleaf_and_Streams",
    # }
    # {
    #     "name": "SASMI MigSpace65 county boundary",
    #     "path": "SASMI_MigSpace65_county_boundary",
    # }
    # {"name": "test", "path": "TestRect"},
    # {"name": "test", "path": "test_base_flm"},
    # {"name": "SLR test area", "path": "fl_slr_test"},
    # {"name": "Test", "path": "030902030700"}
    # {"name": "Yazoo Watershed, MS", "path": "YazooUse"},
    # {"name": "Weyerhaeuser (Andrews)", "path": "Weyerhaeuser_Andrews"},
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
    # {"name": "South Carolina", "path": "SC_SECAS_states"},
    # {"name": "Tennessee", "path": "TN_SECAS_states"},
    # {"name": "FL test", "path": "EvergladesHeadwaterComplex_APPTYPE_0"},
    # {"name": "Guild Tracts", "path": "GuildTracts"}
    # {"name": "Florida Panhandle Boundary", "path": "FL_panhadle_boundary"},
    {"name": "Dell Murphy wetlands", "path": "Dell Murphy wetlands"},
    # {"name": "TRB GA", "path": "TRB_GA"},
    # {"name": "Florida 5 Star County Boundary", "path": "FL_5StarCounty_Boundary"}
    # {"name": "Cumberland Plateau Focus Area", "path": "NFWF_Cumberland_Fund_TN"}
    # {"name": "Enviva Hamlet", "path": "Enviva_Hamlet_80_mile_sourcing_radius"},
    # {"name": "LCP: Black River", "path": "LCP_BlackRiver"},
    # {"name": "Green River proposed boundary", "path": "GreenRiver_ProposedBoundary"},
    # {"name": "LCP: Broad", "path": "LCP_Broad"},
    # {"name": "Caledonia area, MS", "path": "caledonia"},
    # {"name": "Napoleonville area, LA", "path": "Napoleonville"},
    # {"name": "Area in El Yunque National Forest, PR", "path": "yunque"},
    # {"name": "San Juan area, PR", "path": "SanJuan"},
    # {"name": "Area near Magnet, TX", "path": "magnet"},
    # {"name": "TriState area at junction of MO, OK, KS", "path": "TriState"},
    # {"name": "Quincy, FL area", "path": "Quincy"},
    # {"name": "Doyle Springs, TN area", "path": "DoyleSprings"},
    # {"name": "Cave Spring, VA area", "path": "CaveSpring"},
    # {"name": "South Atlantic Offshore", "path": "SAOffshore"},
    # {"name": "Florida Offshore", "path": "FLOffshore"},
    # {"name": "Razor", "path": "Razor"},
    # {"name":"Single Test Area", "path": "SingleTest"}
]

for aoi in aois:
    name = aoi["name"]
    path = aoi["path"]
    print(f"Creating report for {name}...")

    start = time()
    df = read_dataframe(f"examples/{path}.shp", columns=[], force_2d=True).to_crs(
        DATA_CRS
    )
    df["geometry"] = shapely.make_valid(df.geometry.values)
    df["group"] = 1
    df = dissolve(df.explode(ignore_index=True), by="group")

    extent_area = shapely.area(shapely.box(*df.total_bounds)) * M2_ACRES
    print(
        f"Area of extent: {extent_area:,.0f} acres",
    )
    print(f"Area of geometry: {df.area.sum() *M2_ACRES:,.0f} acres")

    ### calculate results, data must be in DATA_CRS
    bar = Bar("Summarizing rasters", max=100, suffix="%(percent)d%%")

    async def progress_callback(percent):
        bar.next(percent)

    print("Calculating results...")
    task = get_custom_area_results(df, progress_callback=progress_callback)
    results = asyncio.run(task)

    bar.finish()

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

        # compile indicator IDs across all ecosystems
        indicators = []
        for ecosystem in results.get("ecosystems", []):
            indicators.extend([i["id"] for i in ecosystem["indicators"]])

        geo_df = df.to_crs(GEO_CRS)
        task = render_maps(
            geo_df.total_bounds,
            geometry=geo_df.geometry.values[0],
            indicators=indicators,
            corridors="corridors" in results,
            urban="urban" in results,
            slr="slr" in results,
            ownership="ownership" in results,
            protection="protection" in results,
            add_mask=results["acres"] >= 1e9,
        )

        maps, scale, errors = asyncio.run(task)

        if errors:
            print("Errors", errors)

        if CACHE_MAPS:
            write_cache(maps, scale, cache_dir)

    results["scale"] = scale

    pdf = create_report(maps=maps, results=results, name=name)

    with open(out_dir / f"{path}_report.pdf", "wb") as out:
        out.write(pdf)

    print("Elapsed {:.2f}s".format(time() - start))

############################################################

## Create reports for summary units
ids = {
    "huc12": [
        # "030502100102",  # duplicate PARCA bug
        # "020403030502",
        # "051402060702",
        #     #     # "050500030804"  # in WV
        #     #     # "030902030700"  # in base blueprint but missing SLR (Dry Tortugas)
        #     #     # "031002010205",  # in base blueprint but with SLR present
        #     #     #     #     #     # "210100070101",  # in Caribbean
        #     #     # "031101020903",  # Florida with inland marine indicators
        #     #     #     #     #     # "031102050805",  # Florida gulf coast
        #     #     # "030902061101"  # area with SLR not modeled
        #     "030102051002"  # area with both marine and inland hubs / corridors
    ],
    "marine_hex": [
        # "154309",
        # "407103"
    ],
}


for unit_type in ids:
    for unit_id in ids[unit_type]:
        print(f"Creating report for for {unit_id}...")

        out_dir = Path(f"/tmp/{unit_id}")
        cache_dir = out_dir / "maps"

        if not out_dir.exists():
            os.makedirs(out_dir)

        # Fetch results
        results = get_summary_unit_results(unit_type, unit_id)

        # compile indicator IDs across all inputs
        indicators = []
        for ecosystem in results.get("ecosystems", []):
            indicators.extend([i["id"] for i in ecosystem["indicators"]])

        maps = None
        if CACHE_MAPS:
            maps, scale = read_cache(cache_dir)

        if not maps:
            print("Rendering maps...")
            task = render_maps(
                results["bounds"],
                summary_unit_id=unit_id,
                indicators=indicators,
                corridors="corridors" in results,
                urban="urban" in results,
                slr="slr" in results,
                ownership="ownership" in results,
                protection="protection" in results,
            )
            maps, scale, errors = asyncio.run(task)

            if errors:
                print("Errors", errors)

            if CACHE_MAPS:
                write_cache(maps, scale, cache_dir)

        results["scale"] = scale

        pdf = create_report(
            maps=maps, results=results, name=results["name"], area_type=unit_type
        )

        with open(out_dir / f"{unit_id}_report.pdf", "wb") as out:
            out.write(pdf)
