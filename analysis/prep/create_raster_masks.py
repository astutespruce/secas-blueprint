import os
from pathlib import Path
from math import ceil

from affine import Affine
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT


def create_mask(filename, outfilename, factor, ignore_zero=False):
    """Create a resampled mask based on dimensions of raster / factor.

    This is used to pre-screen areas where data are present for higher-resolution
    analysis.

    Any non-nodata pixels are converted to 1 based on the max pixel value per
    resampled pixel.

    Parameters
    ----------
    filename : str
    outfilename : str
    factor : int
    ignore_zero : bool, optional (default: False)
        if True, 0 values are treated as nodata
    """
    with rasterio.open(filename) as src:

        nodata = src.nodatavals[0]
        width = ceil(src.width / factor)
        height = ceil(src.height / factor)
        dst_transform = src.transform * Affine.scale(
            src.width / width, src.height / height
        )

        with WarpedVRT(
            src,
            width=width,
            height=height,
            nodata=nodata,
            transform=dst_transform,
            resampling=Resampling.max,
        ) as vrt:

            data = vrt.read()

            if ignore_zero:
                data[data == 0] = nodata

            data[data != nodata] = 1

            meta = src.profile.copy()
            meta.update({"width": width, "height": height, "transform": dst_transform})

            # add compression
            meta["compress"] = "lzw"

            with rasterio.open(outfilename, "w", **meta) as out:
                out.write(data)


print("Creating Blueprint mask...")
src_dir = Path("data/inputs")
create_mask(
    src_dir / "se_blueprint2020.tif",
    src_dir / "se_blueprint2020_mask.tif",
    factor=16,
    ignore_zero=True,
)


print("Creating urban mask...")
src_dir = Path("data/inputs/threats/urban")
create_mask(
    src_dir / "urban_2100.tif", src_dir / "urban_mask.tif", factor=8, ignore_zero=True
)
