import os
from pathlib import Path

from analysis.lib.raster import create_lowres_mask


print("Creating Blueprint mask...")
src_dir = Path("data/inputs")
create_lowres_mask(
    src_dir / "se_blueprint2020.tif",
    src_dir / "se_blueprint2020_mask.tif",
    factor=16,
    ignore_zero=True,
)


print("Creating urban mask...")
src_dir = Path("data/inputs/threats/urban")
create_lowres_mask(
    src_dir / "urban_2100.tif", src_dir / "urban_mask.tif", factor=8, ignore_zero=True
)


print("Creating Nature's Network mask...")
src_dir = Path("data/inputs/indicators/natures_network")
for filename in src_dir.glob("*.tif"):
    if "_mask" in str(filename):
        continue

    print(f"Processing {filename}... ")
    create_lowres_mask(
        filename,
        str(filename).replace(".tif", "_mask.tif"),
        factor=8,
        ignore_zero=False,
    )


print("Creating NatureScape masks...")
src_dir = Path("data/inputs/indicators/naturescape")
for filename in src_dir.glob("*.tif"):
    if "_mask" in str(filename):
        continue

    print(f"Processing {filename}... ")
    create_lowres_mask(
        filename,
        str(filename).replace(".tif", "_mask.tif"),
        factor=8,
        ignore_zero=False,
    )
