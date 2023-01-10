from base64 import b64decode
import os
from pathlib import Path
import json

import asyncio
import numpy as np
from pyogrio.geopandas import read_dataframe
import shapely

from analysis.constants import BLUEPRINT_COLORS, DATA_CRS, MAP_CRS, GEO_CRS, DATA_CRS

from analysis.lib.geometry import to_crs
from api.report.map import render_maps
from api.stats import SummaryUnits, CustomArea

aoi_names = []
# aoi_names = ["caledonia"]
# aoi_names = ["caledonia"]
# aoi_names = ["Fort_Mill_townlimits"]
# aoi_names = ["Enviva_Hamlet_80_mile_sourcing_radius"]
# aoi_names = ["Razor", "Groton_all"]
# aoi_names = ["ACF_area"]
# aoi_names = ["NC"]
# aoi_names = ["SA_boundary"]

for aoi_name in aoi_names:
    print(f"Making maps for {aoi_name}...")

    ### Write maps for an aoi
    out_dir = Path("/tmp/aoi") / aoi_name / "maps"
    if not out_dir.exists():
        os.makedirs(out_dir)

    df = read_dataframe(f"examples/{aoi_name}.shp")
    geometry = shapely.make_valid(df.geometry.values)

    # dissolve
    geometry = np.asarray([shapely.union_all(geometry)])

    print("Calculating results...")
    results = CustomArea(geometry, df.crs, name="Test").get_results()
    # FIXME:
    # results = {"indicators": []}

    ### Convert to WGS84 for mapping
    geometry = to_crs(geometry, df.crs, GEO_CRS)
    bounds = shapely.total_bounds(geometry)

    has_corridors = "corridors" in results
    has_urban = "proj_urban" in results and results["proj_urban"][-1] > 0
    has_slr = "slr" in results
    has_ownership = "ownership" in results
    has_protection = "protection" in results

    print("Creating maps...")

    task = render_maps(
        bounds,
        geometry=geometry[0],
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

    for name, data in maps.items():
        if data is not None:
            with open(out_dir / f"{name}.png", "wb") as out:
                out.write(b64decode(data))

    with open(out_dir / f"scale.json", "w") as out:
        out.write(json.dumps(scale))


### Write maps for a summary unit

ids = {
    "huc12": [
        # "210100050503"  # PR
        "110702071001"  # at junction of gulf_hypoxia, okchat, midse
        "031200030902"  # at overlap area between FL, MidSE, and SA
        # "060200020506"  # in AppLCC area
        # "030101010301"  # in Nature's Network  / South Atlantic overlap area
    ],
    "marine_blocks": ["NI18-07-6210"],
}


for summary_type in ids:
    units = SummaryUnits(summary_type)

    for id in ids[summary_type]:
        print(f"Making maps for {id}...")

        results = units.get_results(id)

        has_corridors = "corridors" in results
        has_urban = "proj_urban" in results and results["proj_urban"][1] > 0
        has_slr = "slr" in results
        has_ownership = "ownership" in results
        has_protection = "protection" in results

        out_dir = Path(f"/tmp/{id}/maps")
        if not out_dir.exists():
            os.makedirs(out_dir)

        task = render_maps(
            results["bounds"],
            summary_unit_id=id,
            input_ids=results["input_ids"],
            corridors=has_corridors,
            urban=has_urban,
            slr=has_slr,
            ownership=has_ownership,
            protection=has_protection,
        )

        maps, scale, errors = asyncio.run(task)

        print("Rendered maps:", maps.keys())
        if errors:
            print("Errors", errors)

        for name, data in maps.items():
            if data is not None:
                with open(out_dir / f"{name}.png", "wb") as out:
                    out.write(b64decode(data))

        with open(out_dir / f"scale.json", "w") as out:
            out.write(json.dumps(scale))

### Write bounds as a polygon for display on map (DEBUG)
# xmin, ymin, xmax, ymax = bounds
# bounds_geojson = {
#     "type": "Polygon",
#     "coordinates": [
#         [[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin], [xmin, ymin]]
#     ],
# }
# with open("/tmp/bounds.json", "w") as out:
#     out.write(json.dumps(bounds_geojson))
