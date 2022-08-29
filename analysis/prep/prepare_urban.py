from pathlib import Path
import math
from time import time

from progress.bar import Bar
import numpy as np
import rasterio
import pygeos as pg
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
from rasterio.windows import Window

from analysis.constants import URBAN_YEARS, DATA_CRS, MASK_FACTOR
from analysis.lib.raster import add_overviews, create_lowres_mask
from analysis.lib.io import write_raster

CHUNK_SIZE = 500  # number of rows to read at a time
NODATA = 255

# NOTE: bins are in counts of runs projected to urbanize
# bins are 0: 0, 1: 0.25 - 0.5, 2: > 0.5, 3: already urban
BINS = [0, 0.9999, 25]


start = time()

bnd_dir = Path("data/boundaries")
src_dir = Path("source_data/urban")
out_dir = Path("data/inputs/threats/urban")
tmp_dir = Path("/tmp")

out_dir.mkdir(parents=True, exist_ok=True)

bnd_raster = rasterio.open(bnd_dir / "nonmarine_mask.tif")
bnd = pg.box(*bnd_raster.bounds)


### Find the overlapping window for the SE Blueprint extent
# NOTE: the urban layers are basically in same projection but use NAD83 instead of WGS84
with rasterio.open(src_dir / "probability_SSP2_2020.tif") as src:
    window = src.window(*pg.total_bounds(bnd))
    window_floored = window.round_offsets(op="floor", pixel_precision=3)
    w = math.ceil(window.width + window.col_off - window_floored.col_off)
    h = math.ceil(window.height + window.row_off - window_floored.row_off)
    window = Window(window_floored.col_off, window_floored.row_off, w, h)
    # make sure that window is within extent of data
    window = window.intersection(Window(0, 0, src.width, src.height))
    transform = src.window_transform(window)

full_window = window

### Calculate windows for extracting data
# The full raster is too big to read into memory and digitize, so
# we process in chunks based on the window
# NOTE: data are provided using a blocksize that is full width and 1px high
offsets = list(range(0, full_window.height + 1, CHUNK_SIZE))
heights = ([CHUNK_SIZE] * (len(offsets) - 1)) + [full_window.height - offsets[-1]]
windows = [
    Window(
        full_window.col_off,
        full_window.row_off + offsets[i],
        full_window.width,
        heights[i],
    )
    for i in range(len(offsets))
]


### Extract data
# Derive already urban from 2020 (where probability is 1)
# NOTE: the source data do not distinguish between NODATA outside analysis area
# and areas not projected to urbanize

already_urban = np.zeros((full_window.height, full_window.width), dtype="bool")

for year in URBAN_YEARS:
    year_start = time()
    outfilename = out_dir / f"urban_{year}.tif"

    # can't skip 2020, need it for already urban mask
    if outfilename.exists() and year > 2020:
        print(f"Skipping {year} (already exists)")
        continue

    with rasterio.open(src_dir / f"probability_SSP2_{year}.tif") as src:
        out = np.zeros((full_window.height, full_window.width), dtype="uint8")

        for window in Bar(f"Processing {year}", max=len(windows)).iter(windows):
            out_offset = window.row_off - full_window.row_off
            data = src.read(1, window=window)
            # nan is areas not projected to urbanize and actual NODATA
            data[np.isnan(data)] = np.float32(0.0)

            if year == 2020:
                already_urban[out_offset : out_offset + window.height, :] = data == 1

            # probability values are number of runs out of 50 that predicted
            # urbanization; convert back to the number of runs
            binned = (data * np.float32(50.0)).astype("uint8")

            out[out_offset : out_offset + window.height, :] = binned

        # set a value of 51 where already urban
        out = np.where(already_urban, np.uint8(51), out)

        print("Writing temporary raster")
        tmp_filename = tmp_dir / f"urban_{year}_binned.tif"
        write_raster(tmp_filename, out, transform, crs=src.crs, nodata=NODATA)

    ### Warp and extract to SE Blueprint extent
    print("Warping to align with SE Blueprint")
    with rasterio.open(tmp_filename) as src:
        vrt = WarpedVRT(
            src,
            width=bnd_raster.width,
            height=bnd_raster.height,
            nodata=NODATA,
            transform=bnd_raster.transform,
            crs=DATA_CRS,
            resampling=Resampling.nearest,
        )

        data = vrt.read()[0]

    ### Set areas outside the SE Blueprint to NODATA
    print("Masking to inland areas in the SE")
    outside = bnd_raster.read(1) == 0
    data[outside] = NODATA

    print("Writing final dataset")
    write_raster(outfilename, data, bnd_raster.transform, bnd_raster.crs, nodata=NODATA)

    print("Adding overviews")
    add_overviews(outfilename)

    print(f"Done with {year} in {time()-year_start:.2f}s")

bnd_raster.close()


### Create mask of where urban pixels are present through 2060
print("Creating urban mask")
create_lowres_mask(
    out_dir / f"urban_2060.tif",
    out_dir / "urban_mask.tif",
    factor=MASK_FACTOR,
    ignore_zero=True,
)


### Reclassify 2060 into bins for report and tiles
print("Reclassifying 2060 for mapping")
with rasterio.open(out_dir / "urban_2060.tif") as src:
    data = src.read(1)

    binned = np.digitize(data, BINS, right=True).astype("uint8") - np.uint8(1)
    binned[data == 51] = 3
    binned[data == NODATA] = NODATA

    outfilename = out_dir / "urban_2060_binned.tif"
    write_raster(
        outfilename,
        binned,
        transform=src.transform,
        crs=src.crs,
        nodata=NODATA,
    )

    add_overviews(outfilename)


print(f"All done in {time()-start:.2f}s")
