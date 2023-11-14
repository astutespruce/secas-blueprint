from pathlib import Path

from analysis.lib.stats.blueprint import get_blueprint_unit_results
from analysis.lib.stats.ownership import get_lta_search_info, get_ownership_unit_results
from analysis.lib.stats.parca import get_parca_results
from analysis.lib.stats.urban import get_urban_unit_results
from analysis.lib.stats.slr import get_slr_unit_results
from analysis.lib.stats.summary_units import read_unit_from_feather

data_dir = Path("data")


def get_summary_unit_results(unit_type, unit_id):
    """Get statistics for a single summary unit (HUC12 / marine hex)

    Parameters
    ----------
    unit_type : str, one of {"huc12", "marine_hex"}
    unit_id : str

    Returns
    -------
    dict (None if id not present)
    """
    results_dir = data_dir / "results" / unit_type

    units_filename = "huc12.feather" if unit_type == "huc12" else "marine_hex.feather"

    df = read_unit_from_feather(
        data_dir / "inputs/summary_units" / units_filename,
        unit_id,
        columns=[
            "id",
            "name",
            "acres",
            "rasterized_acres",
            "outside_se",
            "minx",
            "miny",
            "maxx",
            "maxy",
            "subregions",
        ],
    )
    df["subregions"] = df.subregions.apply(set)

    if len(df) == 0:
        # no unit with that ID
        return None

    unit = df.iloc[0]

    name_suffix = "subwatershed" if unit_type == "huc12" else ""
    name = f"{unit['name']} {name_suffix}"
    bounds = unit[["minx", "miny", "maxx", "maxy"]].tolist()

    results = {
        "name": name,
        "acres": unit.acres,
        "rasterized_acres": unit.rasterized_acres,
        "outside_se_acres": unit.outside_se,
        "outside_se_percent": 100 * unit.outside_se / unit.rasterized_acres,
        "bounds": bounds,
    }

    if unit_type == "huc12":
        center, lta_search_radius = get_lta_search_info(
            df[["minx", "miny", "maxx", "maxy"]].values
        )
        results["center"] = center[0]
        results["lta_search_radius"] = lta_search_radius[0]

    blueprint_results = get_blueprint_unit_results(results_dir, unit)
    if blueprint_results is not None:
        results.update(blueprint_results)

    results.update(get_ownership_unit_results(results_dir, unit))

    if unit_type == "huc12":
        parca_results = get_parca_results(results_dir, unit)
        if parca_results is not None:
            results["parca"] = parca_results

        slr_results = get_slr_unit_results(results_dir, unit)
        if slr_results is not None:
            results["slr"] = slr_results

        urban_results = get_urban_unit_results(results_dir, unit)
        if urban_results is not None:
            results["urban"] = urban_results

    return results
