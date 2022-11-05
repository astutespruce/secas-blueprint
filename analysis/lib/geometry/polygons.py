import numpy as np
import pygeos as pg
import pandas as pd


def drop_all_holes(geometries):
    """Return geometries, dropping any holes.

    Parameters
    ----------
    geometries : ndarray of pygeos geometries

    Returns
    -------
    ndarray of pygeos geometries
    """
    parts, index = pg.get_parts(geometries, return_index=True)
    parts = pg.polygons(pg.get_exterior_ring(parts))

    return (
        pd.DataFrame({"geometry": parts}, index=index)
        .groupby(level=0)
        .geometry.apply(np.array)
        .apply(lambda g: pg.multipolygons(g) if len(g) > 1 else g[0])
        .values
    )


def get_holes(geometries):
    """Extract the holes from geometries and return as new polygons

    Parameters
    ----------
    geometries : ndarray of pygeos geometries

    Returns
    -------
    tuple of ndarray of geomtries, original index
    """
    parts, index = pg.get_parts(geometries, return_index=True)
    num_rings = pg.get_num_interior_rings(parts)

    ix = num_rings > 0
    index = np.arange(len(parts))[ix]
    out_index = np.repeat(index, num_rings[ix])

    holes = []

    for i in index:
        holes.extend(
            pg.get_interior_ring(parts[i], range(pg.get_num_interior_rings(parts[i])))
        )

    return pg.polygons(holes), out_index
