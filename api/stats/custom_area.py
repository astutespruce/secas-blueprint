from pathlib import Path

import geopandas as gp
import numpy as np
import shapely

from analysis.constants import M2_ACRES
from analysis.lib.stats.blueprint import summarize_blueprint_in_aoi
from analysis.lib.stats.ownership import summarize_ownership_in_aoi
from analysis.lib.stats.parca import get_parcas_for_aoi
from analysis.lib.stats.rasterized_geometry import RasterizedGeometry
from analysis.lib.stats.slr import summarize_slr_in_aoi
from analysis.lib.stats.urban import summarize_urban_in_aoi
from analysis.lib.stats.wildfire_risk import summarize_wildfire_risk_in_aoi

data_dir = Path("data/inputs")
bnd_dir = data_dir / "boundaries"
subregions_filename = bnd_dir / "subregions.feather"


async def get_custom_area_results(df, progress_callback=None):
    """Calculate statistics for custom area

    df : GeoDataFrame
        expected to only have one row representing the analysis area
    progress_callback : async function
        If not None, is an async function that is called with the percent that
        this task is complete
    """

    # full_start = time()
    if len(df) > 1:
        raise ValueError(
            f"DataFrame for custom area had more rows than expected: {len(df)}"
        )

    geometry = df.geometry.values[0]
    acres = shapely.area(geometry) * M2_ACRES

    subregion_df = gp.read_feather(
        subregions_filename, columns=["subregion", "geometry"]
    )
    tree = shapely.STRtree(subregion_df.geometry.values)
    subregions = set(
        subregion_df.subregion.take(
            np.unique(tree.query(geometry, predicate="intersects"))
        )
    )

    # if area does not intersect any of the subregions, there will be no results
    if len(subregions) == 0:
        return None

    # start = time()
    rasterized_geometry = RasterizedGeometry(geometry)
    # print(f"rasterized geom creation elapsed: {time() - start:.4f}s")

    if progress_callback is not None:
        await progress_callback(5)

    # there was an intersection but no data once rasterized (e.g., slivers)
    if rasterized_geometry.acres == 0:
        return None

    results = {
        "subregions": subregions,
        "acres": acres,
        "rasterized_acres": rasterized_geometry.acres,
        "outside_se_acres": rasterized_geometry.outside_se_acres,
        "outside_se_percent": 100
        * rasterized_geometry.outside_se_acres
        / rasterized_geometry.acres,
    }

    async def blueprint_progress_callback(percent):
        if progress_callback is not None:
            # blueprint progress scales between 5 and 60% of total progress
            await progress_callback(5 + int(round((percent / 100) * 55)))

    # start = time()
    blueprint = await summarize_blueprint_in_aoi(
        rasterized_geometry, subregions, progress_callback=blueprint_progress_callback
    )
    # print(f"blueprint elapsed: {time() - start:.4f}s")
    results.update(blueprint)

    if progress_callback is not None:
        await progress_callback(60)

    async def urban_progress_callback(percent):
        if progress_callback is not None:
            # urban progress scales between 60 and 80% of total progress
            await progress_callback(60 + int(round((percent / 100) * 20)))

    # start = time()
    urban = await summarize_urban_in_aoi(
        rasterized_geometry, progress_callback=urban_progress_callback
    )
    # print(f"urban elapsed: {time() - start:.4f}s")
    if urban is not None:
        results["urban"] = urban

    if progress_callback is not None:
        await progress_callback(80)

    # start = time()
    slr = summarize_slr_in_aoi(rasterized_geometry, geometry=geometry)
    # print(f"slr elapsed: {time() - start:.4f}s")
    if slr is not None:
        results["slr"] = slr

    if progress_callback is not None:
        await progress_callback(90)

    wildfire_risk = summarize_wildfire_risk_in_aoi(rasterized_geometry)
    if wildfire_risk is not None:
        results["wildfire_risk"] = wildfire_risk

    if progress_callback is not None:
        await progress_callback(95)

    # start = time()
    ownership = summarize_ownership_in_aoi(rasterized_geometry, df)
    # print(f"ownership elapsed: {time() - start:.4f}s")
    if ownership is not None:
        results["ownership"] = ownership

    if progress_callback is not None:
        await progress_callback(99)

    parca = get_parcas_for_aoi(df)
    if parca is not None:
        results["parca"] = parca

    if progress_callback is not None:
        await progress_callback(100)

    return results
