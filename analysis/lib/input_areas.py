from pathlib import Path
import math

import numpy as np
import rasterio
from rasterio.windows import Window

from analysis.constants import INPUT_AREA_VALUES, INPUT_AREA_BOUNDS


data_dir = Path("data/inputs")
bnd_dir = data_dir / "boundaries"


def get_input_area_mask(input_area):
    """Get input area mask, window, and transform for a given input area.

    Parameters
    ----------
    input_area : str
        one of the major input area codes: {"base", "flm", "car"}

    Returns
    -------
    mask, transform, window
        mask is 1 INSIDE input area, 0 outside
    """

    ### Get window into raster for bounds of input area
    with rasterio.open(bnd_dir / "input_areas.tif") as src:
        window = src.window(*INPUT_AREA_BOUNDS[input_area])
        window_floored = window.round_offsets(op="floor", pixel_precision=3)
        w = math.ceil(window.width + window.col_off - window_floored.col_off)
        h = math.ceil(window.height + window.row_off - window_floored.row_off)
        window = Window(window_floored.col_off, window_floored.row_off, w, h)
        window = window.intersection(Window(0, 0, src.width, src.height))
        transform = src.window_transform(window)

        data = src.read(1, window=window)

    mask = np.zeros(shape=data.shape, dtype="uint8")
    mask[data == INPUT_AREA_VALUES[input_area]] = 1

    return mask, transform, window
