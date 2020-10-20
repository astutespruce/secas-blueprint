"""
Calculate statistics for each HUC12 and marine lease block using
the Blueprint, SLR, Urbanization, and ownership datasets.
"""

import os
from pathlib import Path
from time import time

import pandas as pd
import geopandas as gp

from analysis.lib.stats import (
    summarize_bluprint_by_unit,
    summarize_urban_by_huc12,
    summarize_slr_by_huc12,
    summarize_ownership_by_unit,
    summarize_counties_by_huc12,
    summarize_chat_by_huc12,
    summarize_gulf_hypoxia_by_huc12,
    summarize_caribbean_by_huc12,
    summarize_natures_network_by_huc12,
    summarize_naturescape_by_huc12,
    summarize_southatlantic_by_huc12,
)


data_dir = Path("data")
huc12_filename = data_dir / "inputs/summary_units/huc12.feather"
marine_filename = data_dir / "inputs/summary_units/marine_blocks.feather"


start = time()

#########################################################################
########### Subwatersheds (HUC12) #######################################
#########################################################################

out_dir = data_dir / "results/huc12"
if not out_dir.exists():
    os.makedirs(out_dir)

print("Reading HUC12 boundaries")
units_df = gp.read_feather(huc12_filename, columns=["id", "geometry"]).set_index("id")

# transform to pandas Series instead of GeoSeries to get pygeos geometries for iterators below
geometries = pd.Series(units_df.geometry.values.data, index=units_df.index)

# Summarize Blueprint and input areas
summarize_bluprint_by_unit(geometries, out_dir)

# Summarize current and projected urbanization
summarize_urban_by_huc12(geometries, out_dir)

# Summarize projected sea level rise
summarize_slr_by_huc12(geometries, out_dir)

# Calculate overlap with ownership and protection
summarize_ownership_by_unit(units_df, out_dir)

# Calculate overlap with counties
summarize_counties_by_huc12(units_df, out_dir)

# Summarize CHAT for OK / TX
summarize_chat_by_huc12(units_df, out_dir)

# Calculate overlap with Caribbean priority watersheds
summarize_caribbean_by_huc12(units_df, out_dir)

# Calculate area for Gulf Hypoxia
summarize_gulf_hypoxia_by_huc12(geometries, out_dir)

# Calculate area for Nature's Network
summarize_natures_network_by_huc12(geometries, out_dir)

# Calculate area for NatureScape
summarize_naturescape_by_huc12(geometries, out_dir)

# Summarize South Atlantic
summarize_southatlantic_by_huc12(geometries, out_dir)

print(
    "Processed {:,} zones in {:.2f}m".format(len(geometries), (time() - start) / 60.0)
)


# #########################################################################
# ########### Marine Lease Blocks #########################################
# #########################################################################


out_dir = data_dir / "results/marine_blocks"
if not out_dir.exists():
    os.makedirs(out_dir)

print("Reading marine blocks boundaries")
units_df = gp.read_feather(marine_filename, columns=["id", "geometry"]).set_index("id")

geometries = pd.Series(units_df.geometry.values.data, index=units_df.index)

# Summarize Blueprint and input areas
summarize_bluprint_by_unit(geometries, out_dir)

# Calculate overlap with ownership and protection
summarize_ownership_by_unit(units_df, out_dir)

print(
    "Processed {:,} zones in {:.2f}m".format(len(geometries), (time() - start) / 60.0)
)
