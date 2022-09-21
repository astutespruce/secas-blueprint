from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from analysis.constants import DATA_CRS, INPUTS, MASK_RESOLUTION
from analysis.lib.colors import hex_to_uint8
from analysis.lib.input_areas import get_input_area_mask
from analysis.lib.raster import add_overviews, create_lowres_mask, write_raster


ID = "flm"
NODATA = 255


src_dir = Path("source_data/florida")
bnd_dir = Path("data/boundaries")
data_dir = Path("data/inputs")
out_dir = data_dir / "indicators/florida_marine"
out_dir.mkdir(exist_ok=True, parents=True)


# init colormap
colormap = {e["value"]: hex_to_uint8(e["color"]) for e in INPUTS[ID]["values"]}


print("Extracting Florida marine input area mask...")
mask, transform, window = get_input_area_mask(ID)

# data are originally at 2km; reproject to 30m, snapped to Blueprint extent,
# but data extent is only to the bounds of this input dataset
print("Reading and warping Florida Marine Blueprint...")
with rasterio.open(src_dir / "FLMarineBlueprintV2.tif") as src:
    vrt = WarpedVRT(
        src,
        width=window.width,
        height=window.height,
        nodata=NODATA,
        crs=DATA_CRS,
        transform=transform,
        resampling=Resampling.nearest,
    )

    data = vrt.read()[0].astype("uint8")

# apply input area mask
data = np.where(mask == 1, data, NODATA).astype("uint8")

outfilename = out_dir / "flm_blueprint.tif"
write_raster(outfilename, data, transform=transform, crs=DATA_CRS, nodata=NODATA)

with rasterio.open(outfilename, "r+") as out:
    out.write_colormap(1, colormap)

add_overviews(outfilename)

create_lowres_mask(
    outfilename,
    str(outfilename).replace(".tif", "_mask.tif"),
    resolution=MASK_RESOLUTION,
    ignore_zero=False,  # no 0 values present
)

# TODO: get updated indicators for v2
# ### Process indicators
# indicators = {
#     "anthropogenic_habitat": "anthropohab/anthropohab",
#     "nongame_biodiversity": "BioDivSpec/biodivspecies",
#     "blueways": "Blueways/blueways",
#     "managed_spp": "ManagedSppZip/managedspp",
#     "protected_spp": "protecspp/protectedspp",
#     "valued_habitat": "ValuedHabitat/valhab",
# }


# for id, indicator_filename in indicators.items():
#     print(f"Reading and warping Florida Blueprint Indicator {id}...")
#     with rasterio.open(src_dir / "indicators" / indicator_filename) as src:
#         nodata = -1
#         vrt = WarpedVRT(
#             src,
#             width=window.width,
#             height=window.height,
#             nodata=nodata,
#             crs=DATA_CRS,
#             transform=transform,
#             resampling=Resampling.nearest,
#         )

#         data = vrt.read()[0]

#     # update nodata
#     nodata = 255
#     data[data == -1] = nodata

#     # update data values if necessary
#     if id == "protected_spp":
#         data[data == 4] = 1
#         data[data == 5] = 2

#     if id in ["nongame_biodiversity", "managed_spp"]:
#         data[(data > 0) & (data < 255)] -= 1

#     # apply input area mask
#     data = np.where(mask == 1, data, nodata).astype("uint8")

#     outfilename = out_dir / f"{id}.tif"

#     write_raster(outfilename, data, transform=transform, crs=DATA_CRS, nodata=nodata)

#     add_overviews(outfilename)

#     create_lowres_mask(
#         outfilename,
#         str(outfilename).replace(".tif", "_mask.tif"),
#         factor=MASK_FACTOR,
#         ignore_zero=True,
#     )
