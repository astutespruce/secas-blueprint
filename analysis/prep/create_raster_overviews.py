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
blueprint_filename = src_dir / "blueprint_4.tif"
hubs_connectors_filename = src_dir / "hubs_connectors.tif"

urban_dir = src_dir / "threats/urban"


for filename in [blueprint_filename, hubs_connectors_filename]:
    print(f"Processing {filename.name}...")
    with rasterio.open(filename, "r+") as src:
        src.build_overviews(factors, Resampling.nearest)

for year in URBAN_YEARS:
    print(f"Processing urban {year}...")
    with rasterio.open(urban_dir / f"urban_{year}.tif", "r+") as src:
        src.build_overviews(factors, Resampling.nearest)
