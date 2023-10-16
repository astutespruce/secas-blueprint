from pathlib import Path

import geopandas as gp
import numpy as np
import rasterio
import shapely

from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES
from analysis.lib.geometry import to_dict, to_crs
from analysis.lib.stats.blueprint import (
    extract_blueprint_by_mask,
)
from analysis.lib.raster import boundless_raster_geometry_mask, shift_window
from analysis.lib.stats.ownership import get_lta_search_info, get_ownership_for_aoi
from analysis.lib.stats.parca import get_parcas_for_aoi
from analysis.lib.stats.slr import extract_slr_by_mask_and_geometry
from analysis.lib.stats.urban import extract_urban_by_mask

data_dir = Path("data/inputs")
bnd_dir = data_dir / "boundaries"
boundary_filename = bnd_dir / "se_boundary.feather"
slr_bounds_filename = data_dir / "threats/slr/slr_bounds.feather"
extent_filename = bnd_dir / "blueprint_extent.tif"
extent_mask_filename = bnd_dir / "blueprint_extent_mask.tif"
blueprint_filename = data_dir / "blueprint.tif"


class AOIMaskConfig(object):
    """Class to store prescreen and rasterized mask information for masking
    other raster datasets"""

    def __init__(self, shapes, bounds):
        """_summary_

        Parameters
        ----------
        shapes : list-like of geometry objects that provide __geo_interface__
        bounds : list-like of [xmin, ymin, xmax, ymax]
        """
        # create lowres shape mask and window (used to presecreen some datasets)
        with rasterio.open(extent_mask_filename) as src:
            (
                self.prescreen_mask,
                self._prescreen_transform,
                self._prescreen_window,
            ) = boundless_raster_geometry_mask(src, shapes, bounds, all_touched=True)

        # create mask and window
        with rasterio.open(extent_filename) as src:
            (
                self.shape_mask,
                self._mask_transform,
                self._mask_window,
            ) = boundless_raster_geometry_mask(src, shapes, bounds, all_touched=False)

            self.cellsize = src.res[0] * src.res[1] * M2_ACRES
            self.mask_acres = (~self.shape_mask).sum() * self.cellsize

            data = src.read(1, window=self._mask_window, boundless=True)
            # count 0 values within shape_mask
            self.outside_se_acres = (data[~self.shape_mask] == 0).sum()
            if self.outside_se_acres < 1e-6:
                self.outside_se_acres = 0

    def get_prescreen_window(self, target_transform):
        return shift_window(
            self._prescreen_window, self._prescreen_transform, target_transform
        )

    def get_mask_window(self, target_transform):
        return shift_window(self._mask_window, self._mask_transform, target_transform)


def get_custom_area_results(df):
    """Calculate statistics for custom area

    df : GeoDataFrame
        expected to only have one row representing the analysis area
    """

    if len(df) > 1:
        raise ValueError(
            f"DataFrame for custom area had more rows than expected: {len(df)}"
        )

    geometry = df.geometry.values[0]
    polygon_acres = shapely.area(geometry) * M2_ACRES
    shapes = [to_dict(geometry)]
    bounds = shapely.bounds(geometry)

    # if area of interest does not intersect SE region boundary,
    # there will be no results
    se_bnd = gp.read_feather(boundary_filename).geometry.values
    shapely.prepare(se_bnd)
    if not shapely.intersects(geometry, se_bnd).any():
        return None

    mask_config = AOIMaskConfig(shapes, bounds)

    # there was an intersection but no data once rasterized (e.g., slivers)
    if mask_config.mask_acres == 0:
        return None

    geo_bounds = shapely.bounds(
        to_crs(np.array([shapely.box(*bounds)]), DATA_CRS, GEO_CRS)
    )
    center, lta_search_radius = get_lta_search_info(geo_bounds)
    center = center[0]
    lta_search_radius = lta_search_radius[0]

    results = {
        "acres": polygon_acres,
        "center": center,
        "lta_search_radius": lta_search_radius,
        "rasterized_acres": mask_config.mask_acres,
        "outside_se_acres": mask_config.outside_se_acres,
        "outside_se_percent": 100
        * mask_config.outside_se_acres
        / mask_config.mask_acres,
    }

    blueprint = extract_blueprint_by_mask(mask_config)
    results.update(blueprint)

    urban = extract_urban_by_mask(mask_config)
    if urban is not None:
        results["urban"] = urban

    slr = extract_slr_by_mask_and_geometry(mask_config, geometry=geometry)
    if slr is not None:
        results["slr"] = slr

    ownership_info = get_ownership_for_aoi(df, total_acres=polygon_acres)
    if ownership_info is not None:
        results.update(ownership_info)

    parca = get_parcas_for_aoi(df)
    if parca is not None:
        results["parca"] = parca

    return results
