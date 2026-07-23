from enum import StrEnum
from pathlib import Path
import shutil
import tempfile
from typing import Optional
from zipfile import ZipFile

import arq
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.security.api_key import APIKey

from api.lib.geo import get_dataset
from api.logger import log
from api.settings import REDIS, REDIS_QUEUE, TEMP_DIR
from api.lib.validation import validate_content_type, validate_token


class ReportType(StrEnum):
    pdf = "pdf"
    xlsx = "xlsx"


def save_file(file: UploadFile) -> Path:
    """Save file to a temporary directory and return the path.

    The caller is responsible for deleting the file.

    Parameters
    ----------
    file : UploadFile
        file received from API endpoint.

    Returns
    -------
    Path
    """

    try:
        suffix = Path(file.filename).suffix

        fp, name = tempfile.mkstemp(suffix=suffix, dir=TEMP_DIR)
        with open(fp, "wb") as out:
            shutil.copyfileobj(file.file, out)

    finally:
        # always close the file handle from the API handler
        file.file.close()

    return Path(name)


router = APIRouter()


@router.post("/custom_report/{report_type}")
async def custom_report_endpoint(
    report_type: ReportType,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    token: APIKey = Depends(validate_token),
):
    validate_content_type(file)

    filename = save_file(file)
    log.debug(f"upload saved to: {filename}")

    # validate that upload has a shapefile or file geodatabase
    try:
        dataset, layer = get_dataset(ZipFile(filename))

    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

    # Create report task
    task = f"create_custom_{report_type}_report"
    try:
        redis = await arq.create_pool(REDIS)
        job = await redis.enqueue_job(
            task,
            filename,
            dataset,
            layer,
            name=name,
            _queue_name=REDIS_QUEUE,
        )
        return {"job": job.job_id}

    except Exception as ex:
        log.error(f"Error creating {task} task, is Redis offline?  {ex}")
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        await redis.aclose()
