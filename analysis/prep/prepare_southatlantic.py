from pathlib import Path
import os

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT


from analysis.constants import DATA_CRS, MASK_FACTOR, INDICATORS as ALL_INDICATORS
from analysis.lib.io import write_raster
from analysis.lib.input_areas import get_input_area_mask
from analysis.lib.raster import add_overviews, create_lowres_mask


INDICATORS = ALL_INDICATORS["sa"]

# companion sa-blueprint project has pre-processed blueprint / indicator data
# we pull in here
src_dir = Path("../sa-blueprint-sv/data/inputs")
bnd_dir = Path("data/boundaries")
data_dir = Path("data/inputs")
out_dir = data_dir / "indicators/southatlantic"

if not out_dir.exists():
    os.makedirs(out_dir)

### Get input area mask
print("Extracting SA input area mask...")
mask, transform, window = get_input_area_mask("sa")

print("Reading and warping SA Blueprint...")
outfilename = out_dir / "sa_blueprint.tif"
with rasterio.open(src_dir / "blueprint2021.tif") as src:
    nodata = int(src.nodata)
    vrt = WarpedVRT(
        src,
        width=window.width,
        height=window.height,
        nodata=nodata,
        transform=transform,
        crs=DATA_CRS,
        resampling=Resampling.nearest,
    )

    data = vrt.read()[0]

# apply mask
data = np.where(mask == 1, data, nodata).astype("uint8")

write_raster(outfilename, data, transform=transform, crs=DATA_CRS, nodata=nodata)

add_overviews(outfilename)

create_lowres_mask(
    outfilename,
    str(outfilename).replace(".tif", "_mask.tif"),
    factor=MASK_FACTOR,
    ignore_zero=False,
)


### Process indicators
for indicator in INDICATORS:
    id = indicator["id"]
    filename = indicator["filename"]
    outfilename = out_dir / filename

    print(f"Reading and warping {id}...")

    with rasterio.open(src_dir / "indicators" / filename) as src:
        nodata = int(src.nodata)
        vrt = WarpedVRT(
            src,
            width=window.width,
            height=window.height,
            nodata=nodata,
            transform=transform,
            crs=DATA_CRS,
            resampling=Resampling.nearest,
        )

        data = vrt.read()[0]

    # apply mask
    data = np.where(mask == 1, data, nodata).astype("uint8")

    write_raster(outfilename, data, transform=transform, crs=DATA_CRS, nodata=nodata)

    add_overviews(outfilename)

    create_lowres_mask(
        outfilename,
        str(outfilename).replace(".tif", "_mask.tif"),
        factor=MASK_FACTOR,
        ignore_zero=False,
    )

