import logging

import pyogrio as pio


log = logging.getLogger(__name__)


def list_files(zip):
    """List files in a zipfile, excluding hidden files and directories

    Parameters
    ----------
    zip : ZipFile

    Returns
    -------
    list
        list of file names in the zipfile
    """
    return [f for f in zip.namelist() if not "__MACOSX" in f or ".DS_Store" in f]


def get_geo_files(zip):
    """List the geospatial files in the zipfile.

    Parameters
    ----------
    zip : ZipFile

    Returns
    -------
    list
        list of geospatial files
    """
    return


def get_dataset(zip):
    """Gets singular geospatial dataset and layer for analysis.

    Validates rules:
    - There must be only one data source (.shp or .gdb) in the zip file.
    - There must be only one data layer in that data source.
    - The data source must contain the required files (.prj for shapefile; .dbf is not used so not required)

    Parameters
    ----------
    zip : open ZipFile

    Returns
    -------
    (str, str)
        tuple of geospatial file within zip file, name of layer
    """
    files = set(list_files(zip))
    geo_files = [f for f in list_files(zip) if f.endswith(".shp") or f.endswith(".gdb")]

    num_files = len(geo_files)

    if num_files == 0:
        log.error(f"Upload zip file does not contain shp or FGDB files")

        raise ValueError("zip file must include a shapefile or FGDB")

    if num_files > 1:
        log.error(
            f"Upload zip file contains {num_files} shp or FGDB files:\n{geo_files}"
        )

        raise ValueError("zip file must include only one shapefile or FGDB")

    filename = geo_files[0]

    if filename.endswith(".shp"):
        missing = []
        for ext in (".prj", ".shx"):
            if not (filename.replace(".shp", ext) in files):
                missing.append(ext)

        if missing:
            log.error(f"Upload zip file contains .shp but not {','.join(missing)}")
            raise ValueError("zip file must include .shp, .prj, and .shx files")

    # Validate that dataset is a polygon and has only a single layer
    layers = pio.list_layers(f"/vsizip/{zip.fp.name}/{filename}")

    if layers.shape[0] > 1:
        log.error(f"Upload data source contains multiple data layers\n{layers}")
        raise ValueError("data source must contain only one data layer")

    if "Polygon" not in layers[0, 1]:
        log.error(f"Upload data source is not a polygon: {layers[0,1]}")
        raise ValueError("data source must be a Polygon type")

    return filename, layers[0, 0]
