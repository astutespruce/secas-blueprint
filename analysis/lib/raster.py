import math
from pathlib import Path

from affine import Affine
import numpy as np
import pandas as pd
import rasterio
from rasterio.errors import WindowError
from rasterio.features import bounds
from rasterio.mask import raster_geometry_mask, geometry_mask
from rasterio.windows import Window


def get_window(dataset, bounds):
    """Calculate the window into dataset that contains bounds, for boundless reading.

    Parameters
    ----------
    dataset : open rasterio dataset
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    rasterio.windows.Window instance
    """
    window = dataset.window(*bounds)
    window_floored = window.round_offsets(op="floor", pixel_precision=3)
    w = math.ceil(window.width + window.col_off - window_floored.col_off)
    h = math.ceil(window.height + window.row_off - window_floored.row_off)
    window = Window(window_floored.col_off, window_floored.row_off, w, h)

    return window


def boundless_raster_geometry_mask(dataset, shapes, bounds, all_touched=True):
    """Alternative to rasterio.mask::raster_geometry_mask that allows boundless
    reads from raster data sources.

    Parameters
    ----------
    dataset : open rasterio dataset
    shapes : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]
    all_touched : bool, optional (default: True)
    """

    window = get_window(dataset, bounds)

    transform = dataset.window_transform(window)
    out_shape = (int(window.height), int(window.width))
    mask = geometry_mask(
        shapes, transform=transform, out_shape=out_shape, all_touched=all_touched
    )

    return mask, transform, window


def extract_count_in_geometry(filename, geometry_mask, window, bins, boundless=False):
    """Apply the geometry mask to values read from filename, and generate a list
    of pixel counts for each bin in bins.

    Parameters
    ----------
    filename : str
        input GeoTIFF filename
    geometry_mask : 2D boolean ndarray
        True for all pixels outside geometry, False inside.
    window : rasterio.windows.Window
        Window that defines the footprint of the geometry_mask within the raster.
    bins : list-like
        List-like of values ranging from 0 to max value (not sparse!).
        Counts will be generated that correspond to this list of bins.
    boundless : bool (default: False)
        If True, will use boundless reads of the data.  This must be used
        if the window extends beyond the extent of the dataset.

    Returns
    -------
    ndarray
        Total number of pixels for each bin
    """

    with rasterio.open(filename) as src:
        data = src.read(1, window=window, boundless=boundless)
        nodata = src.nodatavals[0]

    mask = (data == nodata) | geometry_mask

    # slice out flattened array of values that are not masked
    values = data[~mask]

    # count number of pixels in each bin
    return np.bincount(values, minlength=len(bins)).astype("uint32")


def extract_zonal_mean(filename, geometry_mask, window, boundless=False):
    """Apply the geometry mask to values read from filename and calculate
    the mean within that area.

    Parameters
    ----------
    filename : str
        input GeoTIFF filename
    geometry_mask : 2D boolean ndarray
        True for all pixels outside geometry, False inside.
    window : rasterio.windows.Window
        Window that defines the footprint of the geometry_mask within the raster.
    boundless : bool (default: False)
        If True, will use boundless reads of the data.  This must be used
        if the window extends beyond the extent of the dataset.
    Returns
    -------
    float
        will be nan where there is no data within mask
    """

    with rasterio.open(filename) as src:
        data = src.read(1, window=window, boundless=boundless)
        nodata = src.nodatavals[0]

    mask = (data == nodata) | geometry_mask

    # since mask is True everywhere it is masked OUT, if the min is
    # True, then there is no data
    if mask.min():
        return np.nan

    # slice out flattened array of values that are not masked
    # and calculate the mean
    return data[~mask].mean()


def detect_data(dataset, shapes, bounds):
    """Detect if any data pixels are found in shapes.

    Typically this is performed against a reduced resolution version of a data
    file as a pre-screening step.

    Parameters
    ----------
    dataset : open rasterio dataset
    shapes : list-like of GeoJSON features
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    bool
        Returns True if there are data pixels present
    """
    window = get_window(dataset, bounds)
    raster_window = Window(0, 0, dataset.width, dataset.height)

    try:
        # This will raise a WindowError if windows do not overlap
        window = window.intersection(raster_window)
    except WindowError:
        # no overlap => no data
        return False

    data = dataset.read(1, window=window)
    nodata = int(dataset.nodata)

    if not np.any(data != nodata):
        # entire window is nodata
        return False

    # create mask
    mask = geometry_mask(
        shapes,
        transform=dataset.window_transform(window),
        out_shape=data.shape,
        all_touched=True,
    ) | (data == nodata)

    if np.any(data[~mask]):
        return True

    return False

