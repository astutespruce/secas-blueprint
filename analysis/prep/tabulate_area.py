from pathlib import Path
from time import time

import pandas as pd
import geopandas as gp

# from analysis.lib.stats import (
#     summarize_core_results_by_unit,
#     summarize_urban_by_huc12,
#     summarize_slr_by_huc12,
#     summarize_ownership_by_unit,
#     summarize_counties_by_huc12,
#     summarize_caribbean_by_huc12,
#     summarize_florida_by_marine_block,
#     summarize_base_blueprint_by_unit,
# )


from analysis.lib.stats.core import summarize_blueprint_by_unit
from analysis.lib.stats.base_blueprint import summarize_base_blueprint_by_unit


data_dir = Path("data")
huc12_filename = data_dir / "inputs/summary_units/huc12.feather"
marine_filename = data_dir / "inputs/summary_units/marine_blocks.feather"


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

# Summarize Blueprint
summarize_blueprint_by_unit(units_df, out_dir, marine=False)

# Summarize Base Blueprint
summarize_base_blueprint_by_unit(
    units_df.loc[units_df.input_id == "base"], out_dir, marine=False
)


# ############### old below

# # transform to pandas Series instead of GeoSeries to get pygeos geometries for iterators below
# geometries = pd.Series(units_df.geometry.values.data, index=units_df.index)

# # Summarize Blueprint and input areas
# summarize_core_results_by_unit(geometries, out_dir=out_dir)

# # Summarize Base Blueprint
# summarize_base_blueprint_by_unit(geometries, out_dir=out_dir, marine=False)

# # TODO: backfill blueprint and set corridors


# # Summarize current and projected urbanization
# summarize_urban_by_huc12(geometries)

# # Summarize projected sea level rise
# summarize_slr_by_huc12(geometries)

# # Calculate overlap with ownership and protection
# summarize_ownership_by_unit(units_df, out_dir=out_dir)

# # Calculate overlap with counties
# summarize_counties_by_huc12(units_df)


# # Calculate overlap with Caribbean priority watersheds
# summarize_caribbean_by_huc12(units_df)


print(
    "Processed {:,} zones in {:.2f}m".format(len(geometries), (time() - start) / 60.0)
)


#########################################################################
########### Marine Lease Blocks #########################################
#########################################################################


out_dir = data_dir / "results/marine_blocks"
out_dir.mkdir(exist_ok=True, parents=True)

print("Reading marine blocks boundaries")


units_df = gp.read_feather(
    marine_filename,
    columns=["id", "value", "rasterized_acres", "outside_se", "input_id", "geometry"],
).set_index("id")
units_df = units_df.join(units_df.bounds)

# Summarize Blueprint
summarize_blueprint_by_unit(units_df, out_dir, marine=True)


########### old below


# units_df = gp.read_feather(marine_filename, columns=["id", "geometry"]).set_index("id")

# geometries = pd.Series(units_df.geometry.values.data, index=units_df.index)

# # Summarize Blueprint and input areas
# summarize_bluprint_by_unit(geometries, out_dir=out_dir)

# # Calculate overlap with ownership and protection
# summarize_ownership_by_unit(units_df, out_dir=out_dir)

# # Summarize South Atlantic (marine)
# summarize_southatlantic_by_unit(geometries, out_dir=out_dir, marine=True)

# # Summarize Florida Marine Blueprint
# summarize_florida_by_marine_block(geometries)


# print(
#     "Processed {:,} zones in {:.2f}m".format(len(geometries), (time() - start) / 60.0)
# )
