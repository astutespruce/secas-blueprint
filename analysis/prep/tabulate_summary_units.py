from pathlib import Path
from time import time

import geopandas as gp
import rasterio
import shapely

from analysis.lib.raster import SummaryUnitGrid

from analysis.lib.stats.blueprint import summarize_blueprint_by_units_grid
from analysis.lib.stats.nlcd import summarize_nlcd_by_units_grid
from analysis.lib.stats.protected_areas import summarize_protected_areas_by_units
from analysis.lib.stats.parca import summarize_parcas_by_units
from analysis.lib.stats.slr import summarize_slr_by_units_grid
from analysis.lib.stats.urban import summarize_urban_by_units_grid
from analysis.lib.stats.wildfire_risk import summarize_wildfire_risk_by_units_grid

data_dir = Path("data")
bnd_dir = data_dir / "boundaries"
huc12_filename = data_dir / "inputs/summary_units/huc12.feather"
huc12_raster_filename = bnd_dir / "huc12.tif"
marine_filename = data_dir / "inputs/summary_units/marine_hex.feather"
marine_raster_filename = bnd_dir / "marine_hex.tif"
subregion_df = gp.read_feather(data_dir / "inputs/boundaries/subregions.feather")


start = time()

#########################################################################
########### Subwatersheds (HUC12) #######################################
#########################################################################
out_dir = data_dir / "results/huc12"
out_dir.mkdir(exist_ok=True, parents=True)


print("Reading HUC12 boundaries")
units_df = gp.read_feather(
    huc12_filename,
    columns=["id", "value", "rasterized_acres", "outside_se", "geometry"],
).set_index("id")
units_df = units_df.join(units_df.bounds)


print("Reading HUC12 grid")
with rasterio.open(huc12_raster_filename) as units_dataset:
    units_grid = SummaryUnitGrid(units_dataset, units_df.total_bounds)

    # # Summarize Blueprint
    # summarize_blueprint_by_units_grid(units_df, units_grid, out_dir, marine=False)

    # # Summarize parcas
    # summarize_parcas_by_units(units_df, out_dir)

    # Summarize protected areas
    summarize_protected_areas_by_units(units_df, units_grid, out_dir)

    # # SLR is available for inland continental and Caribbean
    # summarize_slr_by_units_grid(units_df, units_grid, out_dir)

    # # NLCD, urbanization, and wildfire risk are only available in inland continental part of
    # # Blueprint, not Caribbean
    # tree = shapely.STRtree(units_df.geometry.values)
    # ix = ~units_df.index.isin(
    #     units_df.index.values.take(
    #         tree.query(
    #             subregion_df.loc[subregion_df.subregion == "Caribbean"].geometry.values[
    #                 0
    #             ],
    #             predicate="intersects",
    #         )
    #     )
    # )

    # # Summarize NLCD
    # summarize_nlcd_by_units_grid(units_df.loc[ix], units_grid, out_dir)

    # # Summarize current / projected urbanization
    # summarize_urban_by_units_grid(units_df.loc[ix], units_grid, out_dir)

    # # Summarize wildfire risk
    # summarize_wildfire_risk_by_units_grid(units_df.loc[ix], units_grid, out_dir)


print(f"Processed {len(units_df):,} zones in {(time() - start) / 60.0:.2f}m")
print("\n\n--------------------------------------------------\n\n")

#########################################################################
########### Marine Hexes ################################################
#########################################################################

out_dir = data_dir / "results/marine_hex"
out_dir.mkdir(exist_ok=True, parents=True)


print("Reading marine hex boundaries")
units_df = gp.read_feather(
    marine_filename,
    columns=["id", "value", "rasterized_acres", "outside_se", "geometry"],
).set_index("id")
units_df = units_df.join(units_df.bounds)


print("Reading marine hex grid")
with rasterio.open(marine_raster_filename) as units_dataset:
    units_grid = SummaryUnitGrid(units_dataset, units_df.total_bounds)

    # # Summarize Blueprint
    # summarize_blueprint_by_units_grid(units_df, units_grid, out_dir, marine=True)

    # Summarize protected areas
    summarize_protected_areas_by_units(units_df, units_grid, out_dir)


print(f"Processed {len(units_df):,} zones in {(time() - start) / 60.0:.2f}m")
