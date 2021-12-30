from pathlib import Path
import math

import numpy as np
import geopandas as gp
import pygeos as pg
import rasterio
from rasterio.windows import Window

from analysis.constants import INPUT_AREA_VALUES


data_dir = Path("data/inputs")
bnd_dir = data_dir / "boundaries"


def get_input_area_boundary(input_area):
    """Extract and union polygons associated with input area into a single
    boundary (Multi)Polygon.

    Parameters
    ----------
    input_area : str
        id of input area

    Returns
    -------
    (Multi)Polygon
    """
    # have to make valid or we get errors during union for FL
    values = [
        e["value"] for e in INPUT_AREA_VALUES if input_area in set(e["id"].split(","))
    ]

    inputs_df = gp.read_feather(bnd_dir / "input_areas.feather")

    bnd = pg.union_all(
        pg.make_valid(inputs_df.loc[inputs_df.value.isin(values)].geometry.values.data)
    )

    return bnd


def get_input_area_mask(input_area):
    """Get input area mask, window, and transform for a given input area.

    Parameters
    ----------
    input_area : str
        one of the major input area codes, e.g., "gh", "sa", etc

    Returns
    -------
    mask, transform, window
        mask is 1 INSIDE input area, 0 outside
    """

    values = [
        e["value"] for e in INPUT_AREA_VALUES if input_area in set(e["id"].split(","))
    ]

    bnd = get_input_area_boundary(input_area)

    ### Get window into raster for bounds of input area
    with rasterio.open(data_dir / "input_areas.tif") as src:
        window = src.window(*pg.total_bounds(bnd))
        window_floored = window.round_offsets(op="floor", pixel_precision=3)
        w = math.ceil(window.width + window.col_off - window_floored.col_off)
        h = math.ceil(window.height + window.row_off - window_floored.row_off)
        window = Window(window_floored.col_off, window_floored.row_off, w, h)
        window = window.intersection(Window(0, 0, src.width, src.height))
        transform = src.window_transform(window)

        data = src.read(1, window=window)

    mask = np.zeros(shape=data.shape, dtype="uint8")
    for value in values:
        mask[data == value] = 1

    return mask, transform, window
