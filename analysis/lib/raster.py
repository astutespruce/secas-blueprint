import math

from affine import Affine
from progress.bar import Bar
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.errors import WindowError
from rasterio.mask import geometry_mask
from rasterio.vrt import WarpedVRT
from rasterio.windows import Window

from analysis.constants import OVERVIEW_FACTORS, DATA_CRS


def get_window(dataset, bounds, boundless=True):
    """Calculate the window into dataset that contains bounds, for boundless reading.

    Parameters
    ----------
    dataset : open rasterio dataset
    bounds : list-like of [xmin, ymin, xmax, ymax]
    boundless : bool, optional (default: True)
        if True, returned window may extend beyond the dataset

    Returns
    -------
    rasterio.windows.Window instance
    """
    window = dataset.window(*bounds)
    window_floored = window.round_offsets(op="floor", pixel_precision=3)
    col_off = window_floored.col_off
    row_off = window_floored.row_off
    w = math.ceil(window.width + window.col_off - window_floored.col_off)
    h = math.ceil(window.height + window.row_off - window_floored.row_off)

    if not boundless:
        if col_off < 0:
            w = w - col_off
            col_off = 0
        if row_off < 0:
            h = h - row_off
            row_off = 0
        if col_off + w > dataset.width:
            w = dataset.width - col_off

        if row_off + h > dataset.height:
            h = dataset.height - row_off

    return Window(col_off, row_off, w, h)


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
    mask = geometry_mask(
        shapes,
        transform=dataset.window_transform(window),
        out_shape=data.shape,
        all_touched=True,
    ) | (data == nodata)

    if np.any(data[~mask]):
        return True

    return False


def detect_data_by_mask(dataset, mask, window):
    """Detect if any data pixels are found based on mask.

    Typically this is performed against a reduced resolution version of a data
    file as a pre-screening step.

    Parameters
    ----------
    dataset : open rasterio.Dataset
    mask : 2d array
        True outside shapes
    window : rasterio.windows.Window
    Returns
    -------
    bool
        Returns True if there are data pixels present
    """

    data = dataset.read(1, window=window, boundless=True)
    nodata = np.uint8(dataset.nodata)

    all_masked = mask | (data == nodata)

    # if there are unmasked non-nodata pixels, then there are data
    if not all_masked.min():
        return True

    return False


def create_lowres_mask(filename, outfilename, resolution, ignore_zero=False):
    """Create a resampled lower resolution mask.

    This is used to pre-screen areas where data are present for higher-resolution
    analysis.

    Any non-nodata pixels are converted to 1 based on the max pixel value per
    resampled pixel.

    Parameters
    ----------
    filename : str
    outfilename : str
    resolution : int
        target resolution
    ignore_zero : bool, optional (default: False)
        if True, 0 values are treated as nodata
    """
    with rasterio.open(filename) as src:
        nodata = src.nodatavals[0]
        # output is still precisely aligned to same upper left coordinate
        dst_transform = Affine(
            resolution, 0, src.transform.c, 0, -resolution, src.transform.f
        )
        width = math.ceil((src.width * src.transform.a) / resolution)
        height = math.ceil((src.height * (-src.transform.e)) / resolution)

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


# def summarize_raster_by_geometry(
#     geometries, extract_func, outfilename, progress_label="", bounds=None, **kwargs
# ):
#     """Summarize values of input dataset by geometry and writes results to
#     a feather file, with one column for shape_mask and one for each raster value.

#     Parameters
#     ----------
#     geometries : Series of pygeos geometries, indexed by HUC12 / marine block
#     extract_func : function that extracts results for each geometry
#     outfilename : str
#     progress_label : str
#     """

#     if bounds is not None:
#         # select only those areas that overlap input area
#         tree = pg.STRtree(geometries)
#         ix = tree.query(pg.box(*bounds))
#         geometries = geometries.iloc[ix].copy()

#     if not len(geometries):
#         return

#     index = []
#     results = []
#     for ix, geometry in Bar(progress_label, max=len(geometries)).iter(
#         geometries.iteritems()
#     ):
#         zone_results = extract_func(
#             [to_dict(geometry)], bounds=pg.total_bounds(geometry), **kwargs
#         )
#         if zone_results is None:
#             continue

#         index.append(ix)
#         results.append(zone_results)

#     if not len(results):
#         return

#     df = pd.DataFrame(results, index=index)
#     df.index.name = geometries.index.name

#     df.reset_index().to_feather(outfilename)


def summarize_raster_by_geometry(
    df, units_dataset, value_dataset, bins, progress_label="Summarizing data..."
):
    """Calculate counts of pixels per bin for each unit in df

    Parameters
    ----------
    df : DataFrame
        must have a column "value" that corresponds to the value in units_dataset.
        units must not extend beyond extent of value_dataset and must have
        result of df.bounds joined in
    units_dataset : open rasterio Dataset
    value_dataset : open rasterio Dataset
    bins : array-like of value bins
    message : str, optional

    Returns
    -------
    ndarray of shape(n, m) where n=len(df) and m=len(bins), in same order as df
    """
    nodata = np.uint8(value_dataset.nodata)
    num_bins = len(bins)

    # both rasters have same origin point
    same_origin = (
        units_dataset.transform.c == value_dataset.transform.c
        and units_dataset.transform.f == value_dataset.transform.f
    )

    # get read window for df
    value_read_window = get_window(value_dataset, df.total_bounds, boundless=False)
    if same_origin:
        unit_read_window = value_read_window

    else:
        unit_read_window = get_window(units_dataset, df.total_bounds, boundless=False)

    with Bar("Reading data", max=2) as bar:
        unit_data = units_dataset.read(1, window=unit_read_window)
        bar.next()
        value_data = value_dataset.read(1, window=value_read_window)
        bar.next()

    # TODO: consider moving this loop to Cython
    out = np.zeros((len(df), len(bins)), dtype="uint")
    for i, (_, row) in Bar(progress_label, max=len(df)).iter(enumerate(df.iterrows())):
        value_window = get_window(
            value_dataset, (row.minx, row.miny, row.maxx, row.maxy), boundless=False
        )
        value_window = Window(
            value_window.col_off - value_read_window.col_off,
            value_window.row_off - value_read_window.row_off,
            value_window.width,
            value_window.height,
        )

        if same_origin:
            unit_window = value_window
        else:
            unit_window = get_window(
                units_dataset, (row.minx, row.miny, row.maxx, row.maxy), boundless=False
            )
            unit_window = Window(
                unit_window.col_off - unit_read_window.col_off,
                unit_window.row_off - unit_read_window.row_off,
                unit_window.width,
                unit_window.height,
            )

        values = value_data[value_window.toslices()]
        in_unit = unit_data[unit_window.toslices()] == row.value
        values_in_unit = values[in_unit & (values != nodata)]
        out[i, :] = np.bincount(values_in_unit, minlength=num_bins).astype("uint")

        # DEBUG: write value and unit rasters
        # outfilename = "/tmp/values.tif"
        # write_raster(
        #     outfilename,
        #     np.where(in_unit, values, nodata),
        #     transform=value_dataset.window_transform(
        #         get_window(value_dataset, (row.minx, row.miny, row.maxx, row.maxy))
        #     ),
        #     crs=value_dataset.crs,
        #     nodata=nodata,
        # )
        # if value_dataset.colormap(1):
        #     with rasterio.open(outfilename, "r+") as out_raster:
        #         out_raster.write_colormap(1, value_dataset.colormap(1))

        # write_raster(
        #     "/tmp/unit.tif",
        #     np.where(in_unit, 1, 0).astype("uint8"),
        #     transform=units_dataset.window_transform(
        #         get_window(units_dataset, (row.minx, row.miny, row.maxx, row.maxy))
        #     ),
        #     crs=units_dataset.crs,
        #     nodata=0,
        # )

    return out


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


def write_raster(filename, data, transform, crs, nodata):
    """Write data to a GeoTIFF.

    Parameters
    ----------
    filename : str
    data : 2d ndarray
    transform : rasterio transform object
    crs : rasterio.crs object
    nodata : int
    """

    meta = {
        "driver": "GTiff",
        "dtype": data.dtype,
        "nodata": nodata,
        "width": data.shape[1],
        "height": data.shape[0],
        "count": 1,
        "crs": crs,
        "transform": transform,
        "compress": "lzw",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
    }
    with rasterio.open(filename, "w", **meta) as out:
        out.write(data, 1)


def offset_window(window_origin, target_origin, resolution, window):
    """Calculate window for a target grid with a different origin.

    Origins must only differ by an integer number of pixels.

    Parameters
    ----------
    window_origin : list
        [xmin, ymin] of grid corresponding to window
    target_origin : list
        [xmin, ymin] of grid corresponding to dataset to align to
    resolution : float
    window : rasterio.windows.Window

    Returns
    -------
    rasterio.windows.Window
    """

    offset_cols = int((target_origin[0] - window_origin[0]) / resolution)
    offset_rows = int((window_origin[1] - target_origin[1]) / resolution)
    return Window(
        window.col_off - offset_cols,
        window.row_off - offset_rows,
        window.width,
        window.height,
    )
