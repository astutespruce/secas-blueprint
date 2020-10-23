""" Calculate the bounds of each SLR GeoTIFF and save for spatial index later """
from pathlib import Path

import rasterio
import geopandas as gp
import pygeos as pg
from pyogrio import write_dataframe

from analysis.constants import DATA_CRS
from analysis.lib.raster import add_overviews

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

# For debugging
# write_dataframe(df, "/tmp/slr_bounds.gpkg", driver="GPKG")

# Create overviews for each individual file in the VRT
# Note: these have varying resolution, but this creates lower resolutions for each
print("Adding overviews to SLR files...")
for filename in src_dir.glob("*.tif"):
    add_overviews(filename)
