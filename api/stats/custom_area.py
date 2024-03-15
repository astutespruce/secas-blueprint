from pathlib import Path

import geopandas as gp
import numpy as np
import shapely

from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES
from analysis.lib.geometry import to_crs
from analysis.lib.stats.blueprint import summarize_blueprint_in_aoi
from analysis.lib.stats.ownership import get_lta_search_info, summarize_ownership_in_aoi
from analysis.lib.stats.parca import get_parcas_for_aoi
from analysis.lib.stats.rasterized_geometry import RasterizedGeometry
from analysis.lib.stats.slr import summarize_slr_in_aoi
from analysis.lib.stats.urban import summarize_urban_in_aoi

data_dir = Path("data/inputs")
bnd_dir = data_dir / "boundaries"
subregions_filename = bnd_dir / "subregions.feather"


def get_custom_area_results(df, max_acres=None):
    """Calculate statistics for custom area

    df : GeoDataFrame
        expected to only have one row representing the analysis area
    max_area : float (in acres)
        If not None, will raise error if geometry area is greater than this value
    """

    if len(df) > 1:
        raise ValueError(
            f"DataFrame for custom area had more rows than expected: {len(df)}"
        )

    geometry = df.geometry.values[0]
    acres = shapely.area(geometry) * M2_ACRES

    if max_acres is not None and acres > max_acres:
        raise ValueError(
            f"Your area of interest is too large ({acres:,.0f} acres); it must be < {max_acres:,.0f} acres"
        )

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

    rasterized_geometry = RasterizedGeometry(geometry)

    # there was an intersection but no data once rasterized (e.g., slivers)
    if rasterized_geometry.acres == 0:
        return None

    geo_bounds = shapely.bounds(
        to_crs(np.array([shapely.box(*rasterized_geometry.bounds)]), DATA_CRS, GEO_CRS)
    )
    center, lta_search_radius = get_lta_search_info(geo_bounds)
    center = center[0]
    lta_search_radius = lta_search_radius[0]

    results = {
        "subregions": subregions,
        "acres": acres,
        "center": center,
        "lta_search_radius": lta_search_radius,
        "rasterized_acres": rasterized_geometry.acres,
        "outside_se_acres": rasterized_geometry.outside_se_acres,
        "outside_se_percent": 100
        * rasterized_geometry.outside_se_acres
        / rasterized_geometry.acres,
    }

    blueprint = summarize_blueprint_in_aoi(rasterized_geometry, subregions)
    results.update(blueprint)

    urban = summarize_urban_in_aoi(rasterized_geometry)
    if urban is not None:
        results["urban"] = urban

    slr = summarize_slr_in_aoi(rasterized_geometry, geometry=geometry)
    if slr is not None:
        results["slr"] = slr

    ownership_info = summarize_ownership_in_aoi(df, total_acres=acres)
    if ownership_info is not None:
        results.update(ownership_info)

    parca = get_parcas_for_aoi(df)
    if parca is not None:
        results["parca"] = parca

    return results
