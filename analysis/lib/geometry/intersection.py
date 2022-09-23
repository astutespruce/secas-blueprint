import geopandas as gp
import numpy as np
import pandas as pd
import pygeos as pg


def intersection(left, right, grid_size=0):
    """Intersect the geometries from the left with the right.

    New, intersected geometries are stored in "geometry_right".

    Uses spatial index operations for faster operations.  Wholly contained
    geometries from right are copied intact, only those that intersect but are
    not wholly contained are intersected.

    Parameters
    ----------
    left : GeoDataFrame
    right : GeoDataFrame
    grid_size : int, optional (default: None)
        if present, geometries and results from intersection will be
        snapped to this precision grid

    Returns
    -------
    DataFrame or None
        output geometries are in "geometry_right"
        None if there are no intersections
    """

    tree = pg.STRtree(right.geometry.values.data)
    ix = tree.query_bulk(left.geometry.values.data, predicate="intersects")

    if len(ix[0]) == 0:
        return None

    # copy original geometries; they will be clipped below if needed
    intersects = gp.GeoDataFrame(
        {
            "geometry": left.geometry.values.data.take(ix[0]),
            "index_right": right.index.values.take(ix[1]),
            "geometry_right": right.geometry.values.data.take(ix[1]),
        },
        index=left.index.take(ix[0]),
        crs=left.crs,
    )

    pg.prepare(intersects.geometry.values.data)
    contains = pg.contains_properly(
        intersects.geometry.values.data, intersects.geometry_right.values
    )

    # clip any that are not fully contained
    tmp = intersects[~contains]
    intersects.loc[~contains, "geometry_right"] = pg.intersection(
        tmp.geometry.values.data, tmp.geometry_right.values, grid_size=grid_size
    )

    return left.join(intersects.drop(columns=["geometry"])).join(
        right.drop(columns=["geometry"]), on="index_right"
    )
