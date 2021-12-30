import math

from affine import Affine
from progress.bar import Bar
import numpy as np
import pandas as pd
import pygeos as pg
import rasterio
from rasterio.enums import Resampling
from rasterio.errors import WindowError
from rasterio.mask import geometry_mask
from rasterio.vrt import WarpedVRT
from rasterio.windows import Window

from analysis.constants import OVERVIEW_FACTORS, DATA_CRS
from analysis.lib.pygeos_util import to_dict


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


def boundless_raster_geometry_mask(dataset, shapes, bounds, all_touched=False):
    """Alternative to rasterio.mask::raster_geometry_mask that allows boundless
    reads from raster data sources.

    Parameters
    ----------
    dataset : open rasterio dataset
    shapes : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]
    all_touched : bool, optional (default: False)
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

    # DEBUG
    # print(
    #     f"Memory of data ({filename}): {data.size * data.itemsize / (1024 * 1024):0.2f} MB",
    #     data.dtype,
    # )

    # count number of pixels in each bin
    return np.bincount(
        values, minlength=len(bins) if bins is not None else None
    ).astype("uint32")


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
    # note: this intentionally uses all_touched=True
    mask = (
        geometry_mask(
            shapes,
            transform=dataset.window_transform(window),
            out_shape=data.shape,
            all_touched=True,
        )
        | (data == nodata)
    )

    if np.any(data[~mask]):
        return True

    return False


def create_lowres_mask(filename, outfilename, factor, ignore_zero=False):
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
        width = math.ceil(src.width / factor)
        height = math.ceil(src.height / factor)
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


def summarize_raster_by_geometry(
    geometries, extract_func, outfilename, progress_label="", bounds=None, **kwargs
):
    """Summarize values of input dataset by geometry and writes results to
    a feather file, with one column for shape_mask and one for each raster value.

    Parameters
    ----------
    geometries : Series of pygeos geometries, indexed by HUC12 / marine block
    extract_func : function that extracts results for each geometry
    outfilename : str
    progress_label : str
    """

    if bounds is not None:
        # select only those areas that overlap input area
        tree = pg.STRtree(geometries)
        ix = tree.query(pg.box(*bounds))
        geometries = geometries.iloc[ix].copy()

    if not len(geometries):
        return

    index = []
    results = []
    for ix, geometry in Bar(progress_label, max=len(geometries)).iter(
        geometries.iteritems()
    ):
        zone_results = extract_func(
            [to_dict(geometry)], bounds=pg.total_bounds(geometry), **kwargs
        )
        if zone_results is None:
            continue

        index.append(ix)
        results.append(zone_results)

    if not len(results):
        return

    df = pd.DataFrame(results, index=index)

    results = df[["shape_mask"]].copy()
    results.index.name = "id"

    avg_cols = [c for c in df.columns if c.endswith("_avg")]

    # each column is an array of counts for each
    for col in df.columns.difference(["shape_mask"] + avg_cols):
        s = df[col].apply(pd.Series).fillna(0)
        s.columns = [f"{col}_{c}" for c in s.columns]
        results = results.join(s)

    if len(avg_cols) > 0:
        results = results.join(df[avg_cols]).round()

    results.reset_index().to_feather(outfilename)


def add_overviews(filename):
    """Add overviews to file for faster rendering.

    Parameters
    ----------
    filename : str
    """
    with rasterio.open(filename, "r+") as src:
        src.build_overviews(OVERVIEW_FACTORS, Resampling.nearest)


def calculate_percent_overlap(filename, shapes, bounds):
    """Calculate percent of any pixels touched by shapes that is not NODATA.

    Parameters
    ----------
    filename : str
    shapes : list-like of GeoJSON features
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    float
        percent overlap of non-nodata values in mask
    """
    with rasterio.open(filename) as src:
        shape_mask, transform, window = boundless_raster_geometry_mask(
            src, shapes, bounds, all_touched=False
        )

    counts = extract_count_in_geometry(
        filename, shape_mask, window, bins=None, boundless=True
    )

    return 100 * counts.sum() / (~shape_mask).sum()


def extract_window(src, window, transform, nodata):
    """Extract raster data from src within window, and warp to DATA_CRS

    Parameters
    ----------
    src : open rasterio Dataset
    window : rasterio Window boject
    transform : rasterio Transform object
    nodata : int or float

    Returns
    -------
    2d array
    """
    vrt = WarpedVRT(
        src,
        width=window.width,
        height=window.height,
        nodata=nodata,
        transform=transform,
        crs=DATA_CRS,
        resampling=Resampling.nearest,
    )

    return vrt.read()[0]
