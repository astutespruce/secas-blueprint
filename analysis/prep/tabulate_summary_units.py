from pathlib import Path
from time import time

import geopandas as gp
import rasterio

from analysis.lib.raster import SummaryUnitGrid
from analysis.lib.stats.base_blueprint import summarize_base_blueprint_by_units_grid
from analysis.lib.stats.caribbean import summarize_caribbean_by_units_grid
from analysis.lib.stats.core import summarize_blueprint_by_units_grid
from analysis.lib.stats.florida_marine import summarize_florida_marine_by_units_grid
from analysis.lib.stats.ownership import summarize_ownership_by_units
from analysis.lib.stats.slr import summarize_slr_by_units_grid
from analysis.lib.stats.urban import summarize_urban_by_units_grid

data_dir = Path("data")
bnd_dir = data_dir / "boundaries"
huc12_filename = data_dir / "inputs/summary_units/huc12.feather"
huc12_raster_filename = bnd_dir / "huc12.tif"
marine_filename = data_dir / "inputs/summary_units/marine_blocks.feather"
marine_raster_filename = bnd_dir / "marine_blocks.tif"


# NOTE: no need to calculate overlap with input areas; each summary unit is
# assigned to an input area during prep

start = time()

#########################################################################
########### Subwatersheds (HUC12) #######################################
#########################################################################
out_dir = data_dir / "results/huc12"
out_dir.mkdir(exist_ok=True, parents=True)

print("Reading HUC12 boundaries")
units_df = gp.read_feather(
    huc12_filename,
    columns=["id", "value", "rasterized_acres", "outside_se", "input_id", "geometry"],
).set_index("id")
units_df = units_df.join(units_df.bounds)


print("Reading HUC12 grid")
with rasterio.open(huc12_raster_filename) as units_dataset:
    units_grid = SummaryUnitGrid(units_dataset, units_df.total_bounds)

    # Summarize Blueprint
    summarize_blueprint_by_units_grid(units_df, units_grid, out_dir)

    # Summarize Base Blueprint
    summarize_base_blueprint_by_units_grid(
        units_df.loc[units_df.input_id == "base"], units_grid, out_dir, marine=False
    )

    # Summarize Caribbean
    summarize_caribbean_by_units_grid(
        units_df.loc[units_df.input_id == "car"], units_grid, out_dir
    )

    # Summarize ownership
    summarize_ownership_by_units(units_df, out_dir)

    # Summarize current and projected urbanization (only available in area of base blueprint)
    summarize_urban_by_units_grid(
        units_df.loc[units_df.input_id == "base"], units_grid, out_dir
    )

    summarize_slr_by_units_grid(units_df, units_grid, out_dir)

print(f"Processed {len(units_df):,} zones in {(time() - start) / 60.0:.2f}m")


#########################################################################
########### Marine Lease Blocks #########################################
#########################################################################
print("\n\n--------------------------------------------------\n\n")
out_dir = data_dir / "results/marine_blocks"
out_dir.mkdir(exist_ok=True, parents=True)


print("Reading marine blocks boundaries")
units_df = gp.read_feather(
    marine_filename,
    columns=["id", "value", "rasterized_acres", "outside_se", "input_id", "geometry"],
).set_index("id")
units_df = units_df.join(units_df.bounds)


print("Reading marine blocks grid")
with rasterio.open(marine_raster_filename) as units_dataset:
    units_grid = SummaryUnitGrid(units_dataset, units_df.total_bounds)

    # Summarize Blueprint
    summarize_blueprint_by_units_grid(units_df, units_grid, out_dir)

    # Summarize Base Blueprint (offshore areas of East Coast)
    summarize_base_blueprint_by_units_grid(
        units_df.loc[units_df.input_id == "base"], units_grid, out_dir, marine=True
    )

    # Summarize Florida Marine
    summarize_florida_marine_by_units_grid(
        units_df.loc[units_df.input_id == "flm"], units_grid, out_dir
    )

    # Summarize ownership
    summarize_ownership_by_units(units_df, out_dir)


print(f"Processed {len(units_df):,} zones in {(time() - start) / 60.0:.2f}m")
