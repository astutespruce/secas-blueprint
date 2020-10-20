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

from analysis.constants import URBAN_YEARS


# 32 is OK for regional level maps; 16 is more typical for big areas like ACF
factors = [2, 4, 8, 16, 32]

src_dir = Path("data/inputs")
blueprint_filename = src_dir / "se_blueprint2020.tif"
input_areas_filename = src_dir / "input_areas.tif"

urban_dir = src_dir / "threats/urban"

indicators_dir = src_dir / "indicators"


# for filename in [blueprint_filename, input_areas_filename]:
#     print(f"Processing {filename.name}...")
#     with rasterio.open(filename, "r+") as src:
#         src.build_overviews(factors, Resampling.nearest)

# for year in URBAN_YEARS:
#     print(f"Processing urban {year}...")
#     with rasterio.open(urban_dir / f"urban_{year}.tif", "r+") as src:
#         src.build_overviews(factors, Resampling.nearest)


for filename in indicators_dir.rglob("*.tif"):
    if "_mask" in str(filename):
        continue

    print(f"Processing {filename.name}...")
    with rasterio.open(filename, "r+") as src:
        src.build_overviews(factors, Resampling.nearest)
