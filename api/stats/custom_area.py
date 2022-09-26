from copy import deepcopy
from pathlib import Path

import numpy as np
import pygeos as pg
import geopandas as gp

from analysis.lib.geometry import (
    to_crs,
    to_dict,
    intersection,
)
from analysis.constants import (
    INPUTS,
    URBAN_YEARS,
    DATA_CRS,
    OWNERSHIP,
    PROTECTION,
    M2_ACRES,
)
from analysis.lib.stats import (
    extract_core_results_by_geometry,
    extract_urban_by_geometry,
    extract_slr_by_geometry,
    summarize_base_blueprint_by_aoi,
    summarize_caribbean_by_aoi,
    summarize_florida_marine_by_aoi,
)


data_dir = Path("data/inputs")
boundary_filename = data_dir / "boundaries/se_boundary.feather"
county_filename = data_dir / "boundaries/counties.feather"
ownership_filename = data_dir / "boundaries/ownership.feather"
slr_bounds_filename = data_dir / "threats/slr/slr_bounds.feather"

raster_result_funcs = {
    "base": summarize_base_blueprint_by_aoi,
    "flm": summarize_florida_marine_by_aoi,
    "car": summarize_caribbean_by_aoi,
}


class CustomArea(object):
    def __init__(self, geometry, crs, name):
        """Initialize a custom area from a pygeos geometry.

        Parameters
        ----------
        geometry : pygeos Geometry
        crs : pyproj CRS object
        name : string
            name of custom area
        """

        self.geometry = to_crs(geometry, crs, DATA_CRS)
        self.gdf = gp.GeoDataFrame({"geometry": self.geometry}, crs=DATA_CRS)
        self.bounds = pg.total_bounds(self.geometry)
        # wrap geometry as a dict for rasterio
        self.shapes = np.asarray([to_dict(self.geometry[0])])
        self.name = name

    def get_blueprint(self):
        core_results = extract_core_results_by_geometry(self.shapes, bounds=self.bounds)

        if core_results is None:
            return None

        results = {
            "promote_base": core_results["promote_base"],
            "analysis_acres": core_results["shape_mask"],
            "analysis_remainder": core_results["remainder"],
            "blueprint": core_results.get("blueprint", None),  # backfilled below
            "blueprint_total": core_results["blueprint_total"],
        }

        inputs = {
            id: {**INPUTS[id], "acres": acres}
            for id, acres in core_results["inputs"].items()
        }

        # sort by descending acres
        inputs = sorted(inputs.values(), key=lambda x: x["acres"], reverse=True)

        for entry in inputs:
            input_id = entry["id"]

            # Remaining inputs are raster-based
            results_func = raster_result_funcs.get(input_id, None)
            if not results_func:
                print(f"WARNING: missing AOI summary func for {input_id}")
                continue

            raster_results = results_func(
                self.shapes, self.bounds, outside_se_acres=core_results["remainder"]
            )

            if raster_results is not None:
                entry.update(raster_results)
            else:
                # this is an error, this should not occur
                print("Raster results are none for", input_id)

            if input_id == "base":
                if core_results["promote_base"]:
                    # backfill main blueprint from base
                    results["blueprint"] = [
                        e["acres"] for e in raster_results["priorities"]
                    ]

                if raster_results["corridors"] is not None:
                    results["corridors"] = raster_results["corridors"]
                    results["corridors_total"] = raster_results["corridors"].sum()

        results["inputs"] = inputs
        results["input_ids"] = [i["id"] for i in inputs]

        return results

    def get_urban(self):
        """Extract current and projected urbanization.

        Returns
        -------
        dict
            {
                "urban_acres": <urban analysis acres>,
                "urban": <current urban>,
                "proj_urban": [<urbanization 2020>, ..., <urbanization 2060>]
            }
        """
        urban = extract_urban_by_geometry(self.shapes, bounds=self.bounds)

        if urban is None or urban["shape_mask"] == 0:
            return None

        proj_urban = [urban[year] for year in URBAN_YEARS]
        if not sum(proj_urban):
            return None

        return {
            "urban_acres": urban["shape_mask"],
            "urban": urban["urban"],
            "proj_urban": proj_urban,
        }

    def get_slr(self):
        """Extract SLR inundation depth and projected depth for any geometries
        that overlap bounds where SLR is available

        Returns
        -------
        dict
            {
                "slr_acres": <acres>,
                "slr": [<slr_0ft>, <slr_1ft>, ..., <slr_6ft>],
                "slr_proj": {
                    "low": [2020 ft, ..., 2100 ft],
                    ...,
                    "high": [2020 ft, ..., 2100 ft],
                }
            }
        """

        # only extract SLR where there are overlaps
        slr_results = extract_slr_by_geometry(
            self.geometry[0],
            self.shapes,
            bounds=self.bounds,
        )
        # None only if no shape mask
        if slr_results is None:
            return None

        return {
            "slr_acres": slr_results["shape_mask"],
            "slr": slr_results["depth"],
            "slr_proj": slr_results["projections"],
        }

    def get_counties(self):
        """Get county and state names that overlap this area.

        Returns
        -------
        dict
            {"counties": [
                {"FIPS": <FIPS>, "state": <state name>, "county": <county_name>},
                ...
            ]
        """
        counties = gp.read_feather(county_filename)[
            ["geometry", "FIPS", "state", "county"]
        ]

        df = (
            gp.sjoin(self.gdf, counties)[["FIPS", "state", "county"]]
            .reset_index(drop=True)
            .sort_values(by=["state", "county"])
        )

        if not len(df):
            return None

        return {"counties": df.to_dict(orient="records")}

    def get_ownership(self):
        """Get ownership and protection levels and other statistics for this area

        Returns
        -------
        dict
            {
                "ownership": [
                    {
                        "label": <ownership type label>,
                        "acres": <acres of overlap>
                    }
                ],
                "protection": [
                    {
                        "label": <protection type label>,
                        "acres": <acres of overlap>
                    }
                ],
                "protected_areas" [<top 25 protected area names and areas>],
                "num_protected_areas": <total number protected areas>
            }
        """
        ownership = gp.read_feather(ownership_filename)
        df = intersection(self.gdf, ownership)

        if df is None:
            return None

        df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES
        df = df.loc[df.acres > 0].copy()

        if not len(df):
            return None

        results = dict()

        by_owner = (
            df[["Own_Type", "acres"]]
            .groupby(by="Own_Type")
            .acres.sum()
            .astype("float32")
            .to_dict()
        )
        # use the native order of OWNERSHIP to drive order of results
        results["ownership"] = [
            {"label": value["label"], "acres": by_owner[key]}
            for key, value in OWNERSHIP.items()
            if key in by_owner
        ]

        by_protection = (
            df[["GAP_Sts", "acres"]]
            .groupby(by="GAP_Sts")
            .acres.sum()
            .astype("float32")
            .to_dict()
        )
        # use the native order of PROTECTION to drive order of results
        results["protection"] = [
            {
                "label": value["label"],
                "acres": by_protection[key],
            }
            for key, value in PROTECTION.items()
            if key in by_protection
        ]

        by_area = (
            df[["Loc_Nm", "Loc_Own", "acres"]]
            .groupby(by=[df.index.get_level_values(0), "Loc_Nm", "Loc_Own"])
            .acres.sum()
            .astype("float32")
            .round()
            .reset_index()
            .rename(columns={"level_0": "id", "Loc_Nm": "name", "Loc_Own": "owner"})
            .sort_values(by="acres", ascending=False)
        )
        # drop very small areas, these are not helpful
        by_area = by_area.loc[by_area.acres >= 1].copy()

        results["protected_areas"] = by_area.head(25).to_dict(orient="records")
        results["num_protected_areas"] = len(by_area)

        return results

    def get_results(self):
        se_bnd = gp.read_feather(boundary_filename)

        # if area of interest does not intersect SE region boundary,
        # there will be no results
        if not pg.intersects(self.geometry, se_bnd.geometry.values.data).max():
            return None

        results = {
            "type": "",
            "acres": pg.area(self.geometry).sum() * M2_ACRES,
            "name": self.name,
        }

        blueprint_results = self.get_blueprint()
        if blueprint_results is None:
            return None

        results.update(blueprint_results)

        urban_results = self.get_urban()
        if urban_results is not None:
            results.update(urban_results)

        slr_results = self.get_slr()
        if slr_results is not None:
            results.update(slr_results)

        ownership_results = self.get_ownership()
        if ownership_results is not None:
            results.update(ownership_results)

        county_results = self.get_counties()
        if county_results is not None:
            results.update(county_results)

        return results
