from collections import defaultdict
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gp
import pygeos as pg


from analysis.constants import (
    BLUEPRINT,
    INPUTS,
    INPUT_AREA_VALUES,
    OWNERSHIP,
    PROTECTION,
    ACRES_PRECISION,
)

from analysis.lib.stats import (
    get_caribbean_huc12_results,
    get_chat_huc12_results,
    get_florida_huc12_results,
    get_gulf_hypoxia_huc12_results,
    get_midse_huc12_results,
    get_naturescape_huc12_results,
    get_natures_network_huc12_results,
    get_southatlantic_unit_results,
)


input_dir = Path("data/inputs")
results_dir = Path("data/results")

raster_huc12_result_funcs = {
    "fl": get_florida_huc12_results,
    "gh": get_gulf_hypoxia_huc12_results,
    "ms": get_midse_huc12_results,
    "app": get_naturescape_huc12_results,
    "nn": get_natures_network_huc12_results,
}


class SummaryUnits(object):
    def __init__(self, unit_type="huc12"):
        print(f"Loading {unit_type} summary data...")
        self.unit_type = unit_type

        self.working_dir = results_dir / unit_type

        self.units = gp.read_feather(
            input_dir / "summary_units" / f"{unit_type}_wgs84.feather"
        ).set_index("id")

        self.blueprint = pd.read_feather(
            self.working_dir / "blueprint.feather"
        ).set_index("id")

        self.ownership = pd.read_feather(
            self.working_dir / "ownership.feather"
        ).set_index("id")

        self.protection = pd.read_feather(
            self.working_dir / "protection.feather"
        ).set_index("id")

        if unit_type == "huc12":
            self.slr = pd.read_feather(self.working_dir / "slr.feather").set_index("id")
            self.urban = pd.read_feather(self.working_dir / "urban.feather").set_index(
                "id"
            )

            self.counties = pd.read_feather(
                self.working_dir / "counties.feather"
            ).set_index("id")

    def get_results(self, id):
        if not id in self.units.index:
            raise ValueError("ID not in units index")

        unit = self.units.loc[id]
        results = unit[unit.index.difference(["geometry"])].to_dict()
        results["bounds"] = pg.bounds(pg.from_shapely(unit.geometry)).tolist()
        results["type"] = (
            "subwatershed" if self.unit_type == "huc12" else "marine lease block"
        )
        results["is_marine"] = self.unit_type == "marine_blocks"

        blueprint = None
        try:
            blueprint = self.blueprint.loc[id]

        except KeyError:
            # no Blueprint results, there won't be other results
            return results

        # unpack blueprint values
        blueprint_values = np.array(
            [
                getattr(blueprint, c)
                for c in blueprint.index
                if c.startswith("blueprint_")
            ]
        )
        results["blueprint"] = blueprint_values.tolist()
        results["blueprint_total"] = blueprint_values.sum()

        results["analysis_acres"] = blueprint.shape_mask

        remainder = abs(blueprint.shape_mask - results["blueprint_total"])
        # there are small rounding errors, only keep if > 1
        results["analysis_remainder"] = remainder if remainder >= 1 else 0

        # only pull in Blueprint inputs that are present, and flatten
        # overlapping inputs
        inputs = dict()
        has_overlapping_inputs = False
        input_cols = [c for c in blueprint.index if c.startswith("inputs_")]
        for i, col in enumerate(input_cols):
            input_ids = INPUT_AREA_VALUES[i]["id"].split(",")
            acres = blueprint[col]
            if acres > 0:
                if len(input_ids) > 1:
                    has_overlapping_inputs = True

                for input_id in input_ids:
                    if not input_id in inputs:
                        input = deepcopy(INPUTS[input_id])
                        input["acres"] = acres
                        inputs[input_id] = input
                    else:
                        inputs[input_id]["acres"] += acres

        inputs = sorted(inputs.values(), key=lambda x: x["acres"], reverse=True)

        # read in input_priorities
        for entry in inputs:
            input_id = entry["id"]

            if input_id in ["okchat", "txchat"]:
                state = input_id[:2]
                chat_results = get_chat_huc12_results(
                    id,
                    state,
                    results["acres"] - results["analysis_remainder"],
                    results["acres"],
                )
                entry.update(chat_results)

                continue

            if input_id == "car":
                caribbean_results = get_caribbean_huc12_results(
                    id,
                    results["acres"] - results["analysis_remainder"],
                    results["acres"],
                )
                entry.update(caribbean_results)

                continue

            # Remaining inputs are raster-based
            analysis_acres = results["analysis_acres"] - results["analysis_remainder"]
            total_acres = results["analysis_acres"]

            # South Atlantic is a special case because it also has marine and HUC12 results
            if input_id == "sa":
                southatlantic_results = get_southatlantic_unit_results(
                    self.unit_type, id, analysis_acres, total_acres
                )
                if southatlantic_results is not None:
                    entry.update(southatlantic_results)

                continue

            results_func = raster_huc12_result_funcs.get(input_id, None)
            if not results_func:
                print(f"TODO: {input_id}")
                continue

            raster_results = results_func(id, analysis_acres, total_acres)
            if raster_results is not None:
                entry.update(raster_results)

        results["inputs"] = inputs
        results["has_overlapping_inputs"] = has_overlapping_inputs

        try:
            ownership = self.ownership.loc[self.ownership.index.isin([id])]
            ownerships_present = ownership.Own_Type.unique()
            # use the native order of OWNERSHIP to drive order of results
            ownership_results = [
                {
                    "label": value["label"],
                    "acres": ownership.loc[ownership.Own_Type == key].iloc[0].acres,
                }
                for key, value in OWNERSHIP.items()
                if key in ownerships_present
            ]
            results["ownership"] = ownership_results

        except KeyError:
            pass

        try:
            protection = self.protection.loc[self.protection.index.isin([id])]
            protection_present = protection.GAP_Sts.unique()
            # use the native order of PROTECTION to drive order of results
            protection_results = [
                {
                    "label": value["label"],
                    "acres": protection.loc[protection.GAP_Sts == key].iloc[0].acres,
                }
                for key, value in PROTECTION.items()
                if key in protection_present
            ]

            results["protection"] = protection_results

        except KeyError:
            pass

        if self.unit_type == "marine_blocks":
            return results

        try:
            counties = self.counties.loc[self.counties.index.isin([id])].sort_values(
                by=["state", "county"]
            )
            results["counties"] = counties.to_dict(orient="records")

        except KeyError:
            pass

        try:
            slr = self.slr.loc[id]
            if slr[1:].max():
                results["slr_acres"] = slr.shape_mask
                results["slr"] = slr[1:].tolist()

        except KeyError:
            pass

        try:
            # only keep through 2060
            urban = self.urban.loc[id][:7]
            if urban[1:].max():
                results["urban_acres"] = urban.shape_mask
                results["urban"] = urban[1]
                results["proj_urban"] = urban[2:].tolist()

        except KeyError:
            pass

        return results
