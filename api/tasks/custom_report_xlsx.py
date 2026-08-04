import tempfile

import geopandas as gp
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

    # prescreen columns to read to exclude floating point, dates
    id_fields = [field for field, dtype in zip(info["fields"], info["dtypes"]) if dtype in VALID_ID_FIELD_DTYPES]
    df = extract_dataset(path, layer=layer, columns=id_fields)

    # drop any fields that are completely null
    fields = {col: len(df[col].unique()) for col in id_fields if not df[col].isnull().all()}

    # Save as feather file for subsequent steps
    outfilename = str(zip_filename).replace(".zip", ".feather")
    df[["geometry"] + list(fields.keys())].to_feather(outfilename)

    ### prescreen datasets available (using only analysis units that overlap)
    await set_progress(ctx["redis"], ctx["job_id"], 50, "Checking available datasets")
    datasets = get_available_datasets(df)

    if len(datasets) == 0:
        raise DataError(
            "area of interest does not overlap Southeast Blueprint or area of interest did not overlap with the center of at least one 30m pixel in the Southeast Blueprint"
        )

    await set_progress(ctx["redis"], ctx["job_id"], 100, "All done!")

    return {
        "payload": {
            # pass along uuid from task context
            "uuid": uuid,
            "count": info["features"],
            "fields": fields,
            "datasets": datasets,
        }
    }, []


# FIXME: use name in XLSX
async def create_custom_xlsx_report(ctx, uuid, datasets, field=None, name=None):
    datasets = datasets.split(",") if datasets else []

    await set_progress(ctx["redis"], ctx["job_id"], 0, "Reading dataset")

    filename = (TEMP_DIR / f"{uuid}.feather").resolve()

    # double-check that it exists; this should not occur here
    # because we check for it before submitting job
    if not filename.exists():
        log.error(f"Dataset does not exist for uuid: {uuid}")
        raise ValueError("Dataset does not exist")

    columns = [field] if field else []
    df = gp.read_feather(filename, columns=["geometry"] + columns)

    if not field:
        field = "__analysis_unit"
        df[field] = "all areas"

    if len(df) > 1:
        await set_progress(ctx["redis"], ctx["job_id"], 5, "Aggregating boundaries")

        try:
            df = dissolve(df, by=field).set_index(field)

        except Exception as ex:
            log.error(f"Failed to dissolve dataframe: {filename} on field: {field}")
            log.error(ex)
            raise DataError("Could not aggregate boundaries for analysis")

    else:
        df = df.set_index(field)

    await set_progress(ctx["redis"], ctx["job_id"], 10, "Calculating statistics (may take a while)")

    async def progress_callback(percent):
        await set_progress(
            ctx["redis"],
            ctx["job_id"],
            # ranges 10-75%
            int(round(10 + (percent / 100) * 65)),
            "Calculating statistics (may take a while)",
        )

    # FIXME: enable
    # results = await get_analysis_unit_results(df, datasets, progress_callback=progress_callback)
    # if results is None:
    #     raise DataError("Dataset does not overlap Southeast states")

    # await set_progress(ctx["redis"], ctx["job_id"], 75, "Creating XLSX file")
    # xlsx = create_xlsx(results, datasets)

    # await set_progress(ctx["redis"], ctx["job_id"], 95, "Nearly done")

    # fp, outfilename = tempfile.mkstemp(suffix=".xlsx", dir=TEMP_DIR)
    # with open(fp, "wb") as out:
    #     out.write(xlsx)

    # await set_progress(ctx["redis"], ctx["job_id"], 100, "All done!")

    # return {
    #     "filename": outfilename,
    #     "payload": f"/api/jobs/{ctx['job_id']}/xlsx",
    # }, []
