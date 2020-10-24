"""Create a custom report for a user-uploaded area of interest.

TODO:
* wrap in try / except
"""
import logging
from pathlib import Path
import tempfile

import numpy as np
from pyogrio import read_dataframe
import pygeos as pg

from api.errors import DataError
from api.report.map import render_maps
from api.report import create_report
from api.settings import LOGGING_LEVEL, TEMP_DIR
from api.stats import CustomArea
from api.progress import set_progress

from analysis.lib.pygeos_util import to_crs
from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES

MAX_DIM = 5  # degrees


log = logging.getLogger(__name__)
log.setLevel(LOGGING_LEVEL)


async def create_custom_report(ctx, zip_filename, dataset, layer, name=""):
    """Create a Blueprint report for a user-uploaded GIS file contained in a zip.
    Zip must contain either a shapefile or a file geodatabase.

    Parameters
    ----------
    ctx : job context
    zip_filename : str
        full path to zip filename
    dataset : str
        full path to dataset within zip file
    layer : str
        name of layer within dataset
    name : str, optional (default: "")
        Name of area of interest (included in output report)

    Returns
    -------
    str
        path to output file

    Raises
    ------
    DataError
        Raised if bounds are too large or if area of interest doesn't overalap SA region
    """
    await set_progress(ctx["job_id"], 0)

    path = f"/vsizip/{zip_filename}/{dataset}"

    df = read_dataframe(path, layer=layer)

    geometry = pg.make_valid(df.geometry.values.data)

    await set_progress(ctx["job_id"], 5)

    # dissolve
    geometry = np.asarray([pg.union_all(geometry)])

    geo_geometry = to_crs(geometry, df.crs, GEO_CRS)
    bounds = pg.total_bounds(geo_geometry)

    # estimate area
    extent_area = (
        pg.area(pg.box(*pg.total_bounds(to_crs(geometry, df.crs, DATA_CRS)))) * M2_ACRES
    )
    if extent_area >= 2e6:
        raise DataError("Area of interest is too large, it must be < 2 million acres.")

    await set_progress(ctx["job_id"], 10)

    ### calculate results, data must be in DATA_CRS
    print("Calculating results...")
    results = CustomArea(geometry, df.crs, name).get_results()

    if results is None:
        raise DataError("area of interest does not overlap Southeast Blueprint")

    if name:
        results["name"] = name

    has_urban = "proj_urban" in results and results["proj_urban"][4] > 0
    has_slr = "slr" in results
    has_ownership = "ownership" in results
    has_protection = "protection" in results

    await set_progress(ctx["job_id"], 25)

    print("Rendering maps...")
    maps, scale = await render_maps(
        bounds,
        geometry=geo_geometry[0],
        # indicators=results["indicators"],
        urban=has_urban,
        slr=has_slr,
        ownership=has_ownership,
        protection=has_protection,
    )

    await set_progress(ctx["job_id"], 75)

    results["scale"] = scale

    pdf = create_report(maps=maps, results=results)

    await set_progress(ctx["job_id"], 95)

    fp, name = tempfile.mkstemp(suffix=".pdf", dir=TEMP_DIR)
    with open(fp, "wb") as out:
        out.write(pdf)

    await set_progress(ctx["job_id"], 100)

    log.debug(f"Created PDF at: {name}")

    return name
