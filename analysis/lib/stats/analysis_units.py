from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
import rasterio
import shapely

from analysis.constants import (
    M2_ACRES,
    SECAS_STATES,
    BLUEPRINT,
    CORRIDORS,
    INDICATORS,
    PARCAS,
    PROTECTED_AREAS,
    SLR_DEPTH,
    SLR_PROJ,
    URBAN_BY_DECADE,
    WILDFIRE_RISK,
    REPORT_DATASETS,
    URBAN_YEARS,
)
from analysis.lib.stats.blueprint import summarize_blueprint_in_aoi
from analysis.lib.stats.parcas import extract_parcas_in_analysis_units, BINS as PARCAS_BINS
from analysis.lib.stats.protected_areas import extract_protected_areas_in_analysis_areas, BINS as PROTECTED_AREAS_BINS
from analysis.lib.stats.rasterized_geometry import RasterizedGeometry
from analysis.lib.stats.slr import summarize_slr_in_aoi, extract_slr_proj_in_analysis_areas, BINS as SLR_DEPTH_BINS
from analysis.lib.stats.urban import BINS as URBAN_BINS, PROBABILITIES as URBAN_PROBABILITIES
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

    datasets = {id: REPORT_DATASETS[id] for id in datasets}

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
        files = {
            id: rasterio.open(data_dir / d["filename"])
            for id, d in datasets.items()
            if d["filename"].endswith(".tif") and id not in {URBAN_BY_DECADE["id"]}
        }
        for year in URBAN_YEARS:
            files[f"{URBAN_BY_DECADE['id']}_{year}"] = rasterio.open(
                data_dir / URBAN_BY_DECADE["filename"].format(year=year)
            )

        # TODO: scale progress updates
        for i, (index, row) in enumerate(df.iterrows()):
            rasterized_geometry = RasterizedGeometry(row.geometry)

            result = {
                "pixels": rasterized_geometry.pixels,
                "rasterized_acres": rasterized_geometry.acres,
                "outside_se_acres": rasterized_geometry.outside_se_acres,
            }

            # short-circuit if there are no overlapping pixels
            if np.isclose(rasterized_geometry.outside_se_acres, rasterized_geometry.acres):
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

            #     # TODO: Extract Blueprint, corridors, indicators
            #     if BLUEPRINT["id"] in datasets:
            #         # FIXME: this needs a separate handler than below
            #         result[BLUEPRINT["id"]] = summarize_blueprint_in_aoi(rasterized_geometry)

            if SLR_DEPTH["id"] in datasets:
                slr_acres = rasterized_geometry.get_acres_by_bin(files[SLR_DEPTH["id"]], SLR_DEPTH_BINS)
                # TODO: set NODATA into value 13 in XLSX sheet code (similar to other nodata handling for other sheets)
                # slr_nodata_acres = rasterized_geometry.acres - rasterized_geometry.outside_se_acres - slr_acres.sum()
                # slr_acres[13] += slr_nodata_acres
                # accumulate values for depths 0-10ft
                slr_acres[:11] = np.cumsum(slr_acres[:11])
                result[SLR_DEPTH["id"]] = slr_acres

            #     # Extract urban
            if URBAN_BY_DECADE["id"] in datasets:
                # store already urban in index 0, then 2030-2100 from index 1 onward
                urban_acres = np.zeros((len(URBAN_YEARS) + 1,))
                for i, year in enumerate(URBAN_YEARS):
                    urban_prob_acres = rasterized_geometry.get_acres_by_bin(
                        files[f"{URBAN_BY_DECADE['id']}_{year}"], URBAN_BINS
                    )
                    # total urbanization is sum of acres by probability bin * probability
                    urban_acres[i + 1] = (urban_prob_acres * URBAN_PROBABILITIES).sum()

                    if year == 2030:
                        urban_acres[0] = urban_prob_acres[51]

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

    if PARCAS["id"] in datasets:
        parcas = extract_parcas_in_analysis_units(df)
        if parcas is not None:
            out = out.join(parcas.rename(f"{PARCAS['id']}_poly"))

    if PROTECTED_AREAS["id"] in datasets:
        protected_areas = extract_protected_areas_in_analysis_areas(df)
        if protected_areas is not None:
            out = out.join(protected_areas.rename(f"{PROTECTED_AREAS['id']}_poly"))

    if SLR_PROJ["id"] in datasets:
        slr_proj = extract_slr_proj_in_analysis_areas(df)
        if slr_proj is not None:
            out = out.join(slr_proj)

    return out
