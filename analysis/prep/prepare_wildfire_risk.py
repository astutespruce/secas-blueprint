from itertools import product
from pathlib import Path
import subprocess

from progress.bar import Bar
import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from analysis.constants import (
    MASK_RESOLUTION,
    DATA_CRS,
    WILDFIRE_RISK_BINS,
    WILDFIRE_RISK,
)
from analysis.lib.colors import hex_to_uint8
from analysis.lib.raster import (
    write_raster,
    add_overviews,
    create_lowres_mask,
    clip_window,
)

# read window size in pixels
WINDOW_SIZE = 4096

NODATA = 255


bnd_dir = Path("data/inputs/boundaries")
src_dir = Path("source_data/wildfire_risk")
out_dir = Path("data/inputs/threats/wildfire_risk")
tmp_dir = Path("/tmp")

out_dir.mkdir(parents=True, exist_ok=True)

# NOTE: PR and USVI are not available, so we only create this dataset for the contiguous inland Southeast
bnd_raster = rasterio.open(bnd_dir / "contiguous_southeast_inland_mask.tif")


### Build VRT using GDAL CLI
print("Building VRT")

files = list(src_dir.glob("BP_*.tif"))

# NOTE: data are already at 30m in same CRS
vrt_filename = src_dir / "wildfire_risk.vrt"
ret = subprocess.run(
    [
        "gdalbuildvrt",
        "-overwrite",
        str(vrt_filename),
    ]
    + files
)
ret.check_returncode()

# create a set of windows aligned with bnd_raster
windows = [
    clip_window(
        Window(row_off=row_off, col_off=col_off, width=WINDOW_SIZE, height=WINDOW_SIZE),
        bnd_raster.width,
        bnd_raster.height,
    )
    for row_off, col_off in product(
        range(0, bnd_raster.height, WINDOW_SIZE),
        range(0, bnd_raster.width, WINDOW_SIZE),
    )
]

# DEBUG: uncomment the following to output a GIS file of window boundaries
# import geopandas as gp
# from pyogrio import write_dataframe

# window_boxes = [shapely.box(*bnd_raster.window_bounds(window)) for window in windows]
# write_dataframe(
#     gp.GeoDataFrame(
#         {"window": range(0, len(windows))}, geometry=window_boxes, crs=DATA_CRS
#     ),
#     "/tmp/windows.fgb",
# )


out = np.ones(bnd_raster.shape, dtype="uint8") * np.uint8(255)
with rasterio.open(vrt_filename) as src:
    # warp to match the SE Blueprint; there is a very slight shift because their
    # origin points aren't identical
    vrt = WarpedVRT(
        src,
        width=bnd_raster.width,
        height=bnd_raster.height,
        transform=bnd_raster.transform,
        crs=DATA_CRS,
        resampling=Resampling.nearest,
        dtype="float32",
    )

    # TODO: read in smaller windows and bin by window, then mask
    # data = vrt.read()[0]
    for window in Bar("Processing wildfire risk", max=len(windows)).iter(windows):
        data = vrt.read(window=window)[0]
        mask = bnd_raster.read(1, window=window)

        binned = np.digitize(data, bins=WILDFIRE_RISK_BINS, right=True).astype("uint8")
        # FIXME: remove
        # binned[(data == src.nodata)] = NODATA
        # FIXME: enable
        binned[(data == src.nodata) | (mask == 0)] = NODATA

        out[window.toslices()] = binned


outfilename = out_dir / "wildfire_risk.tif"

write_raster(
    outfilename,
    out,
    transform=bnd_raster.transform,
    crs=bnd_raster.crs,
    nodata=NODATA,
)

del out

colormap = {
    e["value"]: hex_to_uint8(e["color"])
    if e["color"] is not None
    else (255, 255, 255, 0)
    for e in WILDFIRE_RISK
}

with rasterio.open(outfilename, "r+") as out:
    out.write_colormap(1, colormap)

add_overviews(outfilename)


create_lowres_mask(
    outfilename,
    out_dir / "wildfire_risk_mask.tif",
    resolution=MASK_RESOLUTION,
    ignore_zero=False,
)
