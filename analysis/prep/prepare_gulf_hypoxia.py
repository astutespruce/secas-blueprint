from pathlib import Path
import os

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from analysis.constants import DATA_CRS, MASK_FACTOR
from analysis.lib.io import write_raster
from analysis.lib.input_areas import get_input_area_mask
from analysis.lib.raster import add_overviews, create_lowres_mask


data_dir = Path("data/inputs")
src_dir = Path("source_data/gulf_hypoxia")
out_dir = data_dir / "indicators/gulf_hypoxia"
outfilename = out_dir / "gulf_hypoxia.tif"

if not out_dir.exists():
    os.makedirs(out_dir)


print("Extracting Gulf Hypoxia input area mask...")
mask, transform, window = get_input_area_mask("gh")

with rasterio.open(src_dir / "Missouri_cfa_huc_sum2.tif") as src:
    nodata = int(src.nodata)

    print("Reading and warping gulf hypoxia...")
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

write_raster(outfilename, data, transform, crs=DATA_CRS, nodata=nodata)

add_overviews(outfilename)

create_lowres_mask(
    outfilename,
    str(outfilename).replace(".tif", "_mask.tif"),
    factor=MASK_FACTOR,
    ignore_zero=False,
)
