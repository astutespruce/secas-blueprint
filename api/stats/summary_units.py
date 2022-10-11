from pathlib import Path

from analysis.lib.stats.core import get_unit_core_results
from analysis.lib.stats.base_blueprint import get_base_blueprint_unit_results
from analysis.lib.stats.caribbean import get_caribbean_unit_results
from analysis.lib.stats.florida_marine import get_florida_marine_unit_results
from analysis.lib.stats.ownership import get_ownership_unit_results
from analysis.lib.stats.urban import get_urban_unit_results
from analysis.lib.stats.slr import get_slr_unit_results

data_dir = Path("data")


def get_summary_unit_results(unit_type, unit_id):
    """Get statistics for a single summary unit (HUC12 / marine block)

    Parameters
    ----------
    unit_type : str, one of {"huc12", "marine_blocks"}
    unit_id : str

    Returns
    -------
    dict
    """
    results_dir = data_dir / "results" / unit_type

    df, results = get_unit_core_results(unit_type, unit_id)
    unit = df.iloc[0]

    results.update(get_ownership_unit_results(results_dir, unit_id, unit.acres))

    if unit_type == "huc12":
        slr_results = get_slr_unit_results(results_dir, unit_id, unit.rasterized_acres)
        if slr_results:
            results["slr"] = slr_results

        if unit.input_id == "base":
            base_blueprint_results = get_base_blueprint_unit_results(
                results_dir, unit_id, unit.rasterized_acres
            )
            results["inputs"][0].update(base_blueprint_results)
            if "corridors" in base_blueprint_results:
                results["corridors"] = base_blueprint_results["corridors"]

            urban_results = get_urban_unit_results(
                results_dir, unit_id, unit.rasterized_acres
            )
            if urban_results:
                results["urban"] = urban_results

        if unit.input_id == "car":
            results["inputs"][0].update(
                get_caribbean_unit_results(results_dir, unit_id, unit.rasterized_acres)
            )

    else:
        results["exclude_threats"] = True
        if unit.input_id == "flm":
            results["inputs"][0].update(
                get_florida_marine_unit_results(
                    results_dir, unit_id, unit.rasterized_acres
                )
            )

    return results
