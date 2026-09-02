from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
import rasterio
import shapely

from analysis.constants import (
    BLUEPRINT,
    CORRIDORS,
    INDICATORS,
    M2_ACRES,
    PARCAS,
    PARCAS_POLY,
    PROTECTED_AREAS,
    PROTECTED_AREAS_POLY,
    REPORT_DATASETS,
    SECAS_STATES,
    SLR_DEPTH,
    SLR_PROJ,
    URBAN_BY_DECADE,
    URBAN_YEARS,
    WILDFIRE_RISK,
)
from analysis.lib.stats.blueprint import BLUEPRINT_BINS, CORRIDOR_BINS
from analysis.lib.stats.parcas import BINS as PARCAS_BINS
from analysis.lib.stats.parcas import extract_parcas_in_analysis_units
from analysis.lib.stats.protected_areas import BINS as PROTECTED_AREAS_BINS
from analysis.lib.stats.protected_areas import extract_protected_areas_in_analysis_areas
from analysis.lib.stats.rasterized_geometry import RasterizedGeometry
from analysis.lib.stats.slr import BINS as SLR_DEPTH_BINS
from analysis.lib.stats.slr import extract_slr_proj_in_analysis_areas
from analysis.lib.stats.urban import BINS as URBAN_BINS
from analysis.lib.stats.urban import PROBABILITIES as URBAN_PROBABILITIES
from analysis.lib.stats.wildfire_risk import BINS as WILDFIRE_RISK_BINS

data_dir = Path("data/inputs")
bnd_dir = data_dir / "boundaries"
states_filename = bnd_dir / "states.feather"
subregions_filename = bnd_dir / "subregions.feather"


async def get_analysis_unit_results(df: gp.GeoDataFrame, datasets: set[str], progress_callback=None):
    """Calculate statistics for each analysis unit

    Parameters
    ----------
    df : GeoDataFrame
        each row is a separate analysis unit
    datasets : set
        set of dataset IDs to query
    progress_callback : function, optional (default: None)
        function to call each after each analysis unit is processed

    Returns
    -------
    DataFrame
    """

    # NOTE: states might be null if area is offshore marine
    states = gp.read_feather(states_filename, columns=["state", "id", "geometry"])
    states = states.loc[states.id.isin(SECAS_STATES)]
    left, right = shapely.STRtree(states.geometry.values).query(df.geometry.values, predicate="intersects")
    state_join = (
        pd.DataFrame({"state": states.state.values.take(right)}, index=df.index.values.take(left))
        .groupby(level=0)
        .state.unique()
        .apply(sorted)
        .apply(lambda x: ", ".join(x))
        .rename("states")
    )

    subregions = gp.read_feather(subregions_filename, columns=["subregion", "region", "geometry"])
    left, right = shapely.STRtree(subregions.geometry.values).query(df.geometry.values, predicate="intersects")
    subregion_join = (
        pd.DataFrame(
            {"subregions": subregions.subregion.values.take(right), "regions": subregions.region.values.take(right)},
            index=df.index.values.take(left),
        )
        .groupby(level=0)
        .agg({"subregions": "unique", "regions": "unique"})
    )
    for col in ["subregions", "regions"]:
        subregion_join[col] = subregion_join[col].apply(sorted).apply(lambda x: ", ".join(x))

    # if area does not intersect any of the subregions, there will be no results
    if len(subregion_join) == 0:
        return None

    df = df.join(state_join).join(subregion_join)
    df["count"] = shapely.get_num_geometries(df.geometry.values)
    df["acres"] = shapely.area(df.geometry.values) * M2_ACRES
    df["bounds"] = shapely.bounds(df.geometry.values).tolist()

    results = []

    try:
        files = {}
        for id in datasets:
            dataset = REPORT_DATASETS[id]
            if dataset["filename"].endswith(".tif") and id not in {}:
                if id == URBAN_BY_DECADE["id"]:
                    for year in URBAN_YEARS:
                        files[f"{URBAN_BY_DECADE['id']}_{year}"] = rasterio.open(
                            data_dir / URBAN_BY_DECADE["filename"].format(year=year)
                        )
                else:
                    files[id] = rasterio.open(data_dir / dataset["filename"])

        for i, (index, row) in enumerate(df.iterrows()):
            rasterized_geometry = RasterizedGeometry(row.geometry)

            overlap_acres = rasterized_geometry.acres - rasterized_geometry.outside_extent_acres
            if overlap_acres < 1e-6:
                overlap_acres = 0

            result = {
                "pixels": rasterized_geometry.pixels,
                "overlap_acres": overlap_acres,
                "rasterized_acres": rasterized_geometry.acres,
                "outside_extent_acres": rasterized_geometry.outside_extent_acres,
            }

            # short-circuit if there are no overlapping pixels
            if np.isclose(rasterized_geometry.outside_extent_acres, rasterized_geometry.acres):
                results.append(result)

                if progress_callback is not None:
                    await progress_callback(100 * i / len(df))

                continue

            if PARCAS["id"] in datasets:
                result[PARCAS["id"]] = rasterized_geometry.get_acres_by_bin(files[PARCAS["id"]], PARCAS_BINS)

            if PROTECTED_AREAS["id"] in datasets:
                result[PROTECTED_AREAS["id"]] = rasterized_geometry.get_acres_by_bin(
                    files[PROTECTED_AREAS["id"]], PROTECTED_AREAS_BINS
                )

            if BLUEPRINT["id"] in datasets:
                result[BLUEPRINT["id"]] = rasterized_geometry.get_acres_by_bin(files[BLUEPRINT["id"]], BLUEPRINT_BINS)

            if CORRIDORS["id"] in datasets:
                result[CORRIDORS["id"]] = rasterized_geometry.get_acres_by_bin(files[CORRIDORS["id"]], CORRIDOR_BINS)

            for indicator in INDICATORS:
                if indicator["id"] in datasets:
                    bins = range(0, indicator["values"][-1]["value"] + 1)
                    indicator_acres = rasterized_geometry.get_acres_by_bin(files[indicator["id"]], bins)
                    # Some indicators exclude 0 values, remove them from results
                    if indicator["values"][0]["value"] > 0:
                        indicator_acres = indicator_acres[1:]

                    result[indicator["id"]] = indicator_acres

            if SLR_DEPTH["id"] in datasets:
                slr_acres = rasterized_geometry.get_acres_by_bin(files[SLR_DEPTH["id"]], SLR_DEPTH_BINS)
                # accumulate values for depths 0-10ft
                slr_acres[:11] = np.cumsum(slr_acres[:11])
                result[SLR_DEPTH["id"]] = slr_acres

            #     # Extract urban
            if URBAN_BY_DECADE["id"] in datasets:
                # store already urban in index 0, then 2030-2100 from index 1 onward
                # not urban by 2100 stored in next to last value
                # area outside urban is stored in last value
                urban_acres = np.zeros((len(URBAN_YEARS) + 3,))
                for year_index, year in enumerate(URBAN_YEARS):
                    urban_prob_acres = rasterized_geometry.get_acres_by_bin(
                        files[f"{URBAN_BY_DECADE['id']}_{year}"], URBAN_BINS
                    )
                    # total urbanization is sum of acres by probability bin * probability
                    urban_acres[year_index + 1] = (urban_prob_acres * URBAN_PROBABILITIES).sum()

                    if year == 2030:
                        urban_acres[0] = urban_prob_acres[51]
                    elif year == 2100:
                        # important: we calculate nodata area based on all pixels that had >= 0 probability;
                        # for most other layer we just sum their acres to calculate this
                        urban_nodata = (
                            rasterized_geometry.acres
                            - rasterized_geometry.outside_extent_acres
                            - urban_prob_acres.sum()
                        )

                        noturban_2100 = urban_prob_acres.sum() - urban_acres[year_index + 1]
                        if noturban_2100 < 1e-6:
                            noturban_2100 = 0.0
                        urban_acres[-2] = noturban_2100

                        if urban_nodata < 1e-6:
                            urban_nodata = 0.0
                        urban_acres[-1] = urban_nodata

                result[URBAN_BY_DECADE["id"]] = urban_acres

            if WILDFIRE_RISK["id"] in datasets:
                result[WILDFIRE_RISK["id"]] = rasterized_geometry.get_acres_by_bin(
                    files[WILDFIRE_RISK["id"]], WILDFIRE_RISK_BINS
                )

            results.append(result)

            if progress_callback is not None:
                await progress_callback(100 * i / len(df))

    finally:
        for raster in files.values():
            raster.close()

    out = df[["states", "subregions", "regions", "count", "acres"]].join(pd.DataFrame(results, index=df.index))

    if PARCAS_POLY["id"] in datasets:
        parcas = extract_parcas_in_analysis_units(df)
        if parcas is not None:
            out = out.join(parcas)  # .rename(f"{PARCAS['id']}_poly"))

    if PROTECTED_AREAS_POLY["id"] in datasets:
        protected_areas = extract_protected_areas_in_analysis_areas(df)
        if protected_areas is not None:
            out = out.join(protected_areas)  # .rename(f"{PROTECTED_AREAS['id']}_poly"))

    if SLR_PROJ["id"] in datasets:
        slr_proj = extract_slr_proj_in_analysis_areas(df)
        if slr_proj is not None:
            out = out.join(slr_proj)

    return out
