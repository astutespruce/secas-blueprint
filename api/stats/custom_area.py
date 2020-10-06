from copy import deepcopy
from pathlib import Path

import pandas as pd
import numpy as np
import pygeos as pg
import geopandas as gp

from analysis.pygeos_util import to_crs, to_dict, sjoin, sjoin_geometry, intersection
from analysis.constants import (
    BLUEPRINT,
    INPUTS,
    INPUT_AREA_VALUES,
    URBAN_YEARS,
    DATA_CRS,
    GEO_CRS,
    OWNERSHIP,
    PROTECTION,
    M2_ACRES,
)
from analysis.lib.stats import (
    extract_blueprint_area,
    extract_urbanization_area,
    extract_slr_area,
)


data_dir = Path("data/inputs")
boundary_filename = data_dir / "boundaries/se_boundary.feather"
county_filename = data_dir / "boundaries/counties.feather"
ownership_filename = data_dir / "boundaries/ownership.feather"
slr_bounds_filename = data_dir / "threats/slr/slr_bounds.feather"

# Load targets into memory for faster calculations below
sa_bnd = gp.read_feather(boundary_filename)
counties = gp.read_feather(county_filename)[["geometry", "FIPS", "state", "county"]]
ownership = gp.read_feather(ownership_filename)
slr_bounds = gp.read_feather(slr_bounds_filename).geometry


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
        # wrap geometry as a dict for rasterio
        self.shapes = np.asarray([to_dict(self.geometry[0])])
        self.name = name

    def get_blueprint(self):
        counts = extract_blueprint_area(
            self.shapes, bounds=pg.total_bounds(self.geometry)
        )

        if counts is None:
            return None

        blueprint_total = counts["blueprint"].sum()

        remainder = abs(counts["shape_mask"] - blueprint_total)
        # there are small rounding errors
        remainder = remainder if remainder >= 1 else 0

        # only pull in inputs that are present
        inputs = []
        for i, acres in enumerate(counts["inputs"]):
            input_ids = INPUT_AREA_VALUES[i]["id"].split(",")
            if acres > 0:
                for input_id in input_ids:
                    input = deepcopy(INPUTS[input_id])
                    input["acres"] = acres
                    inputs.append(input)

        results = {
            "analysis_acres": counts["shape_mask"],
            "analysis_remainder": remainder,
            "blueprint": counts["blueprint"].tolist(),
            "blueprint_total": blueprint_total,
            "inputs": inputs,
        }

        return results

    def get_urban(self):
        urban_results = extract_urbanization_area(
            self.shapes, bounds=pg.total_bounds(self.geometry)
        )

        if urban_results is None or urban_results["shape_mask"] == 0:
            return None

        # only keep through 2060
        proj_urban = [urban_results[year] for year in URBAN_YEARS[:5]]
        if not sum(proj_urban):
            return None

        return {
            "urban_acres": urban_results["shape_mask"],
            "urban": urban_results["urban"],
            "proj_urban": proj_urban,
        }

    def get_slr(self):
        idx = sjoin_geometry(self.geometry, slr_bounds.values.data, how="inner")
        if not len(idx):
            return None
        idx = idx.index.unique()

        slr_results = extract_slr_area(
            self.shapes.take(idx), bounds=pg.total_bounds(self.geometry.take(idx))
        )
        if slr_results is None or slr_results["shape_mask"] == 0:
            return None

        slr = [slr_results[i] for i in range(7)]
        if not sum(slr):
            return None

        return {"slr_acres": slr_results["shape_mask"], "slr": slr}

    def get_counties(self):
        df = (
            sjoin(pd.DataFrame({"geometry": self.geometry}), counties)[
                ["FIPS", "state", "county"]
            ]
            .reset_index(drop=True)
            .sort_values(by=["state", "county"])
        )

        if not len(df):
            return None

        return {"counties": df.to_dict(orient="records")}

    def get_ownership(self):
        df = intersection(pd.DataFrame({"geometry": self.geometry}), ownership)

        if not len(df):
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
            {"label": value["label"], "acres": by_protection[key]}
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

        # if area of interest does not intersect SA boundary, there will be no results
        if not pg.intersects(self.geometry, sa_bnd.geometry.values.data).max():
            return None

        results = {
            "type": "",
            "acres": pg.area(self.geometry).sum() * M2_ACRES,
            "name": self.name,
        }

        try:
            blueprint_results = self.get_blueprint()
            if blueprint_results is None:
                return None

            results.update(blueprint_results)

        except ValueError:
            # geometry does not overlap Blueprint.  There are no valid results here,
            # move along.
            return None

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
