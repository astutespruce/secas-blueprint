import asyncio
from pathlib import Path
from time import time

from pyogrio import read_dataframe

from analysis.constants import DATA_CRS, GEO_CRS, SECAS_STATES
from api.report import create_report
from api.report.map import render_maps
from api.stats.custom_area import get_custom_area_results


out_dir = Path("/tmp/secas")
out_dir.mkdir(exist_ok=True)


states = (
    read_dataframe(
        "source_data/boundaries/BlueprintStatesForReports/2023StatesForBrendan.shp"
    )
    .to_crs(DATA_CRS)
    .sort_values(by="NAME")
)
states = states.loc[~states.NAME.isnull()]


for state in states.NAME.values:
    print(f"Creating report for {state}")

    start = time()

    df = states.loc[states.NAME == state]
    results = get_custom_area_results(df)

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
    )

    maps, scale, errors = asyncio.run(task)

    if errors:
        print("Errors", errors)

    results["scale"] = scale

    pdf = create_report(maps=maps, results=results, name=state)

    with open(
        out_dir / f"{state.replace(' ', '_')}_Blueprint2023_report.pdf", "wb"
    ) as out:
        out.write(pdf)

    print("Elapsed {:.2f}s".format(time() - start))
