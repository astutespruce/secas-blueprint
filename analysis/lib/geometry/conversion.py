import numpy as np
import pygeos as pg


# GeoJSON geometry type names
GEOJSON_TYPE = {
    # -1: "", # Not a geometry
    0: "Point",
    1: "LineString",
    2: "LinearRing",  # NOTE: not valid GeoJSON, TODO: could be converted to LineString
    3: "Polygon",
    4: "MultiPoint",
    5: "MultiLineString",
    6: "MultiPolygon",
    7: "GeometryCollection",
}


def to_dict(geometry):
    """Convert pygeos Geometry object to a dictionary representation.
    Equivalent to structure of GeoJSON.

    Parameters
    ----------
    geometry : pygeos Geometry object (singular)

    Returns
    -------
    dict
        GeoJSON dict representation of geometry
    """
    geometry = pg.normalize(geometry)

    def get_ring_coords(polygon):
        # outer ring must be reversed to be counterclockwise[::-1]
        coords = [pg.get_coordinates(pg.get_exterior_ring(polygon)).tolist()]
        for i in range(pg.get_num_interior_rings(polygon)):
            # inner rings must be reversed to be clockwise[::-1]
            coords.append(pg.get_coordinates(pg.get_interior_ring(polygon, i)).tolist())

        return coords

    geom_type = GEOJSON_TYPE[pg.get_type_id(geometry)]
    coords = []

    if geom_type == "MultiPolygon":
        coords = []
        geoms = pg.get_geometry(geometry, range(pg.get_num_geometries(geometry)))
        for geom in geoms:
            coords.append(get_ring_coords(geom))

    elif geom_type == "Polygon":
        coords = get_ring_coords(geometry)

    else:
        raise NotImplementedError("Not built")

    return {"type": geom_type, "coordinates": coords}


# TODO: reimplement in Cython?
to_dict_all = np.vectorize(to_dict)
