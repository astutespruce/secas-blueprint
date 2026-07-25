import tempfile

import numpy as np
from pyogrio import read_dataframe, read_info
import shapely

from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES, STANDARD_RESOLUTION
from analysis.lib.geometry import dissolve
from analysis.lib.stats.prescreen import get_available_datasets
from api.errors import DataError
from api.settings import TEMP_DIR, CUSTOM_REPORT_MAX_ACRES, MAX_POLYGONS, MAX_VERTICES
from api.logger import log
from api.lib.geo import extract_dataset
from api.lib.progress import set_progress


VALID_ID_FIELD_DTYPES = {"object", "int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "uint64"}


async def get_xlsx_report_inputs(ctx, zip_filename, dataset, layer, uuid):
    await set_progress(ctx["redis"], ctx["job_id"], 0, "Extracting analysis areas")

    path = f"/vsizip/{zip_filename}/{dataset}"
    info = read_info(path, layer=layer)

    # pass along uuid from task context
    results = {
        "uuid": uuid,
        "count": info["features"],
        "fields": {},
        "datasets": {},
    }

    # prescreen columns to read to exclude floating point, dates
    id_fields = [field for field, dtype in zip(info["fields"], info["dtypes"]) if dtype in VALID_ID_FIELD_DTYPES]

    df = extract_dataset(path, layer=layer, columns=id_fields)

    # drop any fields that are completely null
    results["fields"] = {col: len(df[col].unique()) for col in id_fields if not df[col].isnull().all()}

    # Save as feather file for subsequent steps
    outfilename = str(zip_filename).replace(".zip", ".feather")
    df[["geometry"] + list(results["fields"].keys())].to_feather(outfilename)

    ### prescreen datasets available (using only analysis units that overlap)
    await set_progress(ctx["redis"], ctx["job_id"], 50, "Checking available datasets")
    results["datasets"] = get_available_datasets(df)

    if len(results["datasets"]) == 0:
        raise DataError(
            "area of interest does not overlap Southeast Blueprint or area of interest did not overlap with the center of at least one 30m pixel in the Southeast Blueprint"
        )

    await set_progress(ctx["redis"], ctx["job_id"], 100, "All done!")

    return {"payload": results}, []
