import os
from pathlib import Path

from analysis.lib.raster import create_lowres_mask

FACTOR = 16


### NOT USED
print("Creating Blueprint mask...")
src_dir = Path("data/inputs")
create_lowres_mask(
    src_dir / "se_blueprint2020.tif",
    src_dir / "se_blueprint2020_mask.tif",
    factor=FACTOR,
    ignore_zero=True,
)


print("Creating urban mask...")
# Note: this uses a different factor due to different underlying cell size
src_dir = Path("data/inputs/threats/urban")
create_lowres_mask(
    src_dir / "urban_2100.tif", src_dir / "urban_mask.tif", factor=8, ignore_zero=True
)

