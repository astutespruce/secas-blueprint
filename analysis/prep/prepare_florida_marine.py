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
from analysis.lib.speedups import remap

src_dir = Path("source_data/florida/Marine")
bnd_dir = Path("data/boundaries")
data_dir = Path("data/inputs")
out_dir = data_dir / "indicators/florida_marine"
outfilename = out_dir / "flm_blueprint.tif"

if not out_dir.exists():
    os.makedirs(out_dir)


### Marine
print("Extracting Florida marine input area mask...")
mask, transform, window = get_input_area_mask("flm")

print("Reading and warping Florida Marine Blueprint...")
with rasterio.open(src_dir / "FLBlueprintVer1.tif") as src:
    nodata = 255
    vrt = WarpedVRT(
        src,
        width=window.width,
        height=window.height,
        nodata=nodata,
        crs=DATA_CRS,
        transform=transform,
        resampling=Resampling.nearest,
    )

    data = vrt.read()[0].astype("uint8")


# remap data
remap_table = np.array([[1, 1], [2, 2], [3, 3]], dtype="uint8")
data = remap(data, remap_table, nodata=255)

# apply input area mask
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
indicators = {
    # "anthropogenic_habitat": "anthropohab/anthropohab",
    "nongame_biodiversity": "BioDivSpec/biodivspecies",
    # "blueways": "Blueways/blueways",
    "managed_spp": "ManagedSppZip/managedspp",
    # "protected_spp": "protecspp/protectedspp",
    # "valued_habitat": "ValuedHabitat/valhab",
}


for id, indicator_filename in indicators.items():
    print(f"Reading and warping Florida Blueprint Indicator {id}...")
    with rasterio.open(src_dir / "indicators" / indicator_filename) as src:
        nodata = -1
        vrt = WarpedVRT(
            src,
            width=window.width,
            height=window.height,
            nodata=nodata,
            crs=DATA_CRS,
            transform=transform,
            resampling=Resampling.nearest,
        )

        data = vrt.read()[0]

    # update nodata
    nodata = 255
    data[data == -1] = nodata

    # update data values if necessary
    if id == "protected_spp":
        data[data == 4] = 1
        data[data == 5] = 2

    if id in ["nongame_biodiversity", "managed_spp"]:
        data[(data > 0) & (data < 255)] -= 1

    # apply input area mask
    data = np.where(mask == 1, data, nodata).astype("uint8")

    outfilename = out_dir / f"{id}.tif"

    write_raster(outfilename, data, transform=transform, crs=DATA_CRS, nodata=nodata)

    add_overviews(outfilename)

    create_lowres_mask(
        outfilename,
        str(outfilename).replace(".tif", "_mask.tif"),
        factor=MASK_FACTOR,
        ignore_zero=True,
    )
