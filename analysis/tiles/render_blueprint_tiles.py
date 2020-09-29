"""
Render tiles to mbtiles files, zooms 0-14

NOTE: this is sensitive to the version of GDAL / rasterio; otherwise it raises errors about negative dimensions.
This appears to work properly on locally-built rasterio / GDAL.

Creating blueprint tiles takes at least 10 hours sequentially.
"""

from time import time
from pathlib import Path

from tilecutter.mbtiles import render_tif_to_mbtiles
from pymbtiles.ops import union, extend
from pymbtiles import MBtiles

from analysis.constants import BLUEPRINT


src_dir = Path("data/inputs")
tile_dir = Path("tiles")
tmp_dir = Path("/tmp")


blueprint_filename = src_dir / "blueprint_4.tif"
tileset_filename = tile_dir / "blueprint_4.mbtiles"

# rendering times
# 0 - 12: approx 2 hours
# 13 2:15 hours
# 14 6 hours

### Render Blueprint sequentially
start = time()
render_tif_to_mbtiles(
    blueprint_filename,
    tileset_filename,
    colormap={i + 1: entry["color"] for i, entry in enumerate(BLUEPRINT[1:])},
    min_zoom=0,
    # max_zoom=15, # TODO:
    max_zoom=14,
    tile_size=512,
    metadata={
        "name": "Southeast Blueprint v4.0",
        "description": "Southeast Blueprint v4.0",
        "attribution": "Southeast Blueprint v4.0",
    },
)
print("Tiles done in {:.2f} min".format((time() - start) / 60.0))
