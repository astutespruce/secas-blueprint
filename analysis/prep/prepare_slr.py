""" Calculate the bounds of each SLR GeoTIFF and save for spatial index later """
from pathlib import Path

import rasterio
import geopandas as gp
import pygeos as pg
from pyogrio import write_dataframe

from analysis.constants import DATA_CRS


data_dir = Path("data/inputs")
src_dir = data_dir / "threats/slr"

boxes = []
for filename in (src_dir).glob("*.tif"):
    with rasterio.open(filename) as src:
        boxes.append(pg.box(*src.bounds))

# union them together into a single polygon
bnd = pg.union_all(boxes)

df = gp.GeoDataFrame({"geometry": [bnd], "index": [0]}, crs=DATA_CRS)
df.to_feather(src_dir / "slr_bounds.feather")

# write_dataframe(df, "/tmp/slr_bounds.gpkg", driver="GPKG")

