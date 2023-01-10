import geopandas as gp
import shapely


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

    tree = shapely.STRtree(right.geometry.values)
    ix = tree.query(left.geometry.values, predicate="intersects")

    if len(ix[0]) == 0:
        return None

    # copy original geometries; they will be clipped below if needed
    intersects = gp.GeoDataFrame(
        {
            "geometry": left.geometry.values.take(ix[0]),
            "index_right": right.index.values.take(ix[1]),
            "geometry_right": right.geometry.values.take(ix[1]),
        },
        index=left.index.take(ix[0]),
        crs=left.crs,
    )

    shapely.prepare(intersects.geometry.values)
    contains = shapely.contains_properly(
        intersects.geometry.values, intersects.geometry_right.values
    )

    # clip any that are not fully contained
    tmp = intersects[~contains]
    intersects.loc[~contains, "geometry_right"] = shapely.intersection(
        tmp.geometry.values, tmp.geometry_right.values, grid_size=grid_size
    )

    return left.join(intersects.drop(columns=["geometry"]), how="inner").join(
        right.drop(columns=["geometry"]), on="index_right"
    )
