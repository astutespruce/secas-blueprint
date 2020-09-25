"""
Create coarser resolution overviews in raster files.
"""


from pathlib import Path
from math import ceil

import geopandas as gp
from affine import Affine
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

# from analysis.constants import INDICATORS, URBAN_YEARS


# 32 is OK for regional level maps; 16 is more typical for big areas like ACF
factors = [2, 4, 8, 16, 32]

src_dir = Path("data/inputs")
blueprint_filename = src_dir / "blueprint_4.tif"
corridors_filename = src_dir / "corridors.tif"

# indicators_dir = src_dir / "indicators"
# urban_dir = src_dir / "threats/urban"
# slr_dir = src_dir / "threats/slr"


with rasterio.open(blueprint_filename, "r+") as src:
    src.build_overviews(factors, Resampling.nearest)


# for filename in [blueprint_filename, corridors_filename]:
#     print(f"Processing {filename.name}...")
#     with rasterio.open(filename, "r+") as src:
#         src.build_overviews(factors, Resampling.nearest)

# for year in URBAN_YEARS:
#     print(f"Processing urban {year}...")
#     with rasterio.open(urban_dir / f"urb_indexed_{year}.tif", "r+") as src:
#         src.build_overviews(factors, Resampling.nearest)


# for indicator in INDICATORS:
#     print(f"Processing {indicator['id']}...")

#     with rasterio.open(indicators_dir / indicator["filename"], "r+") as src:
#         src.build_overviews(factors, Resampling.nearest)
