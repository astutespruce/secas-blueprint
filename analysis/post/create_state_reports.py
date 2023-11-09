import asyncio
from pathlib import Path
from time import time

from pyogrio import read_dataframe

from analysis.constants import GEO_CRS, SECAS_STATES
from api.report import create_report
from api.report.map import render_maps
from api.stats.custom_area import get_custom_area_results


bnd_dir = Path("data/boundaries")
out_dir = Path("/tmp/secas")
out_dir.mkdir(exist_ok=True)


states = read_dataframe(bnd_dir / "states.fgb").sort_values(by="state")


for state in SECAS_STATES:
    print(f"Creating report for {state}")

    start = time()

    df = states.loc[states.id == state]
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

    pdf = create_report(maps=maps, results=results, name=df.state.values[0])

    with open(out_dir / f"{state}_report.pdf", "wb") as out:
        out.write(pdf)

    print("Elapsed {:.2f}s".format(time() - start))
