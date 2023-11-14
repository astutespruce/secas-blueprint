from base64 import b64decode
import os
from pathlib import Path
import json

import asyncio
from pyogrio.geopandas import read_dataframe
import shapely

from analysis.constants import DATA_CRS, GEO_CRS


from analysis.lib.geometry import dissolve
from api.report.map import render_maps
from api.stats.custom_area import get_custom_area_results
from api.stats.summary_units import get_summary_unit_results

aoi_names = ["Razor"]
# aoi_names = ["OCMU_SRS_StudyArea"]
# aoi_names = ["caledonia"]
# aoi_names = ["caledonia"]
# aoi_names = ["Fort_Mill_townlimits"]
# aoi_names = ["Enviva_Hamlet_80_mile_sourcing_radius"]
# aoi_names = ["Razor"]
# aoi_names = ["ACF_area"]
# aoi_names = ["NC"]
# aoi_names = ["SA_boundary"]

for aoi_name in aoi_names:
    print(f"Making maps for {aoi_name}...")

    ### Write maps for an aoi
    out_dir = Path("/tmp/aoi") / aoi_name / "maps"
    if not out_dir.exists():
        os.makedirs(out_dir)

    path = aoi_name
    df = read_dataframe(f"examples/{path}.shp", columns=[]).to_crs(DATA_CRS)
    df["geometry"] = shapely.make_valid(df.geometry.values)
    df["group"] = 1
    df = dissolve(df.explode(ignore_index=True), by="group")

    print("Calculating results...")
    results = get_custom_area_results(df)
    # compile indicator IDs across all inputs
    indicators = []
    for ecosystem in results.get("ecosystems", []):
        indicators.extend([i["id"] for i in ecosystem["indicators"]])

    print("Creating maps...")
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
    )

    maps, scale, errors = asyncio.run(task)

    if errors:
        print("Errors", errors)

    for name, data in maps.items():
        if data is not None:
            with open(out_dir / f"{name}.png", "wb") as out:
                out.write(b64decode(data))

    with open(out_dir / "scale.json", "w") as out:
        out.write(json.dumps(scale))


### Write maps for a summary unit

ids = {
    # "huc12": [
    # "210100050503"  # PR
    # "110702071001"  # at junction of gulf_hypoxia, okchat, midse
    # "031200030902"  # at overlap area between FL, MidSE, and SA
    # "060200020506"  # in AppLCC area
    # "030101010301"  # in Nature's Network  / South Atlantic overlap area
    # ],
    # "marine_hex": [],
}


for summary_type in ids:
    for id in ids[summary_type]:
        print(f"Making maps for {id}...")

        results = get_summary_unit_results(summary_type, id)

        # compile indicator IDs across all inputs
        indicators = []
        for input_area in results["inputs"]:
            for ecosystem in input_area.get("ecosystems", []):
                indicators.extend([i["id"] for i in ecosystem["indicators"]])

        out_dir = Path(f"/tmp/{id}/maps")
        if not out_dir.exists():
            os.makedirs(out_dir)

        print("Rendering maps...")
        task = render_maps(
            results["bounds"],
            summary_unit_id=id,
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

        for name, data in maps.items():
            if data is not None:
                with open(out_dir / f"{name}.png", "wb") as out:
                    out.write(b64decode(data))

        with open(out_dir / "scale.json", "w") as out:
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
