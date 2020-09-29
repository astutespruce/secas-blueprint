""" Calculate the bounds of each SLR GeoTIFF and save for spatial index later """
from pathlib import Path

import rasterio
import geopandas as gp
import pygeos as pg

from analysis.constants import DATA_CRS


data_dir = Path("data/inputs")
src_dir = data_dir / "threats/slr"

boxes = []
for filename in (src_dir).glob("*.tif"):
    with rasterio.open(filename) as src:
        boxes.append(pg.box(*src.bounds))

df = gp.GeoDataFrame({"geometry": boxes}, crs=DATA_CRS)
df.to_feather(src_dir / "slr_bounds.feather")

