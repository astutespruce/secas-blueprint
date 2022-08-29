from pathlib import Path

from progress.bar import Bar
import numpy as np
import pandas as pd
import pygeos as pg
import geopandas as gp
import rasterio

from analysis.constants import ACRES_PRECISION, M2_ACRES
from analysis.lib.raster import (
    detect_data,
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
)
from analysis.lib.pygeos_util import to_dict


src_dir = Path("data/inputs/threats/slr")
slr_mask_filename = src_dir / "slr_mask.tif"
vrt_filename = src_dir / "slr.tif"

results_filename = "data/results/huc12/slr.feather"


def extract_by_geometry(geometries, bounds):
    """Calculate the area of overlap between geometries and each level of SLR
    between 0 (currently inundated) and 6 meters.

    Values are cumulative; the total area inundated is added to each higher
    level of SLR

    This is only applicable to inland (non-marine) areas that are near the coast.

    NOTE: SLR is in a VRT with a cell size derived from the underlying rasters.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
        Should be limited to features that intersect with bounds of SLR datasets
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    dict
        keys are mask, <decade>, ...
        values are the area of incremental (not total!) sea level rise by foot
    """

    # prescreen to make sure data are present
    with rasterio.open(slr_mask_filename) as src:
        if not detect_data(src, geometries, bounds):
            return None

    results = {}

    # create mask and window
    with rasterio.open(vrt_filename) as src:
        try:
            shape_mask, transform, window = boundless_raster_geometry_mask(
                src, geometries, bounds, all_touched=False
            )

        except ValueError:
            return None

        # square meters to acres
        cellsize = src.res[0] * src.res[1] * M2_ACRES

        data = src.read(1, window=window, boundless=True)
        nodata = src.nodatavals[0]
        mask = (data == nodata) | shape_mask
        data = np.where(mask, nodata, data)

    results["shape_mask"] = (
        ((~shape_mask).sum() * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    if results["shape_mask"] == 0:
        return None

    bins = np.arange(11)
    counts = extract_count_in_geometry(
        vrt_filename, shape_mask, window, bins=bins, boundless=True
    )

    # accumulate values
    for bin in bins[1:]:
        counts[bin] = counts[bin] + counts[bin - 1]

    acres = (counts * cellsize).round(ACRES_PRECISION).astype("float32")
    results.update({i: a for i, a in enumerate(acres)})

    return results


def summarize_by_huc12(geometries):
    """Summarize by HUC12

    Parameters
    ----------
    geometries : Series of pygeos geometries, indexed by HUC12 id
    """

    # find the indexes of the geometries that overlap with SLR bounds; these are the only
    # ones that need to be analyzed for SLR impacts

    results = []
    index = []
    for huc12, geometry in Bar(
        "Calculating SLR counts for HUC12", max=len(geometries)
    ).iter(geometries.iteritems()):
        zone_results = extract_by_geometry(
            [to_dict(geometry)], bounds=pg.total_bounds(geometry)
        )
        if zone_results is None:
            continue

        index.append(huc12)
        results.append(zone_results)

    df = pd.DataFrame(results, index=index)

    # reorder columns
    df = df[["shape_mask"] + list(df.columns.difference(["shape_mask"]))]
    # extract only areas that actually had SLR pixels
    df = df[df[df.columns[1:]].sum(axis=1) > 0]
    df.columns = [str(c) for c in df.columns]
    df = df.reset_index().rename(columns={"index": "id"}).round()
    df.to_feather(results_filename)
