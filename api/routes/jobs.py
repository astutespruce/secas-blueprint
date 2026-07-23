from datetime import datetime
from secrets import compare_digest
import time

import arq
from arq.jobs import Job, JobStatus
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from api.errors import DataError
from api.settings import REDIS, REDIS_QUEUE, API_SECRET
from api.logger import log
from api.lib.progress import get_progress


router = APIRouter()
security = HTTPBasic()


# This endpoint is only available to admins over HTTP Basic Auth
@router.get("/jobs")
async def get_jobs(credentials: HTTPBasicCredentials = Depends(security)):
    """Return summary information about queued and completed jobs"""

    correct_username = compare_digest(credentials.username, "admin")
    correct_password = compare_digest(credentials.password, API_SECRET)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    redis = await arq.create_pool(REDIS)

    try:
        queued = [
            {"job": job.function, "args": job.args, "start": job.enqueue_time}
            for job in await redis.queued_jobs(queue_name=REDIS_QUEUE)
        ]

        results = [
            {
                "job": job.function,
                "args": job.args,
                "start": job.enqueue_time,
                "success": job.success,
                "elapsed": job.finish_time - job.enqueue_time,
            }
            for job in await redis.all_job_results()
        ]

        return {"queued": queued, "completed": results}

    finally:
        await redis.aclose()


@router.get("/jobs/{job_id}")
async def job_status_endpoint(job_id: str):
    """Return the status of a job.

    Job status values derived from JobStatus enum at:
    https://github.com/samuelcolvin/arq/blob/master/arq/jobs.py
    ['deferred', 'queued', 'in_progress', 'complete', 'not_found']

    We add ['success', 'failed'] status values here.

    Parameters
    ----------
    job_id : str

    Returns
    -------
    JSON
        {"status": "...", "progress": 0-100, "result": "...only if complete...", "detail": "...only if failed..."}
    """

    # loop until return or hit number of retries
    retry = 0
    while retry <= 5:
        redis = None

        try:
            redis = await arq.create_pool(REDIS)

            job = Job(job_id, redis=redis, _queue_name=REDIS_QUEUE)
            status = await job.status()

            if status == JobStatus.not_found:
                raise HTTPException(
                    status_code=404,
                    detail="Job not found; it may have been cancelled, timed out, or the server restarted.  Please try again.",
                )

            if status == JobStatus.queued:
                job_info = await job.info()
                elapsed_time = datetime.now(tz=job_info.enqueue_time.tzinfo) - job_info.enqueue_time

                queued = [
                    j[0]
                    for j in sorted(
                        [(job.job_id, job.enqueue_time) for job in await redis.queued_jobs(queue_name=REDIS_QUEUE)],
                        key=lambda x: x[1],
                    )
                ]

                return {
                    "status": status,
                    "progress": 0,
                    "queue_position": queued.index(job_id),
                    "elapsed_time": elapsed_time.seconds,
                }

            if status != JobStatus.complete:
                progress, message, errors = await get_progress(redis, job_id)

                return {
                    "status": status,
                    "progress": progress,
                    "message": message,
                    "errors": errors,
                }

            info = await job.result_info()

            try:
                # this re-raises the underlying exception raised in the worker
                filename, out_filename, errors = await job.result()

                if info.success:
                    return {
                        "status": "success",
                        "result": f"/api/jobs/{job_id}/results",
                        "errors": errors,
                    }

            except DataError as ex:
                message = str(ex)

            # raise timeout to outer retry loop
            except TimeoutError as ex:
                raise ex

            except Exception as ex:
                log.error(ex)
                message = "Internal server error"
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error",
                )

            return {"status": "failed", "detail": message}

        # in case we hit a Redis timeout while polling job status, make sure we don't break until connection cannot be re-established
        except TimeoutError as ex:
            retry += 1
            log.error(f"Redis connection timeout, retry {retry}")
            time.sleep(1)

            if retry >= 5:
                raise ex

        finally:
            if redis is not None:
                await redis.aclose()


@router.get("/jobs/{job_id}/results")
async def report_pdf_endpoint(job_id: str):
    redis = await arq.create_pool(REDIS)

    try:
        job = Job(job_id, redis=redis, _queue_name=REDIS_QUEUE)
        status = await job.status()

        if status == JobStatus.not_found:
            raise HTTPException(
                status_code=404,
                detail="Job not found; it may have been cancelled, timed out, or the server restarted.  Please try again.",
            )

        if status != JobStatus.complete:
            raise HTTPException(status_code=400, detail="Job not complete")

        info = await job.result_info()

        if not info.success:
            raise HTTPException(
                status_code=400,
                detail="Job failed, cannot return results.  Please contact us to report an issue.",
            )

        path, out_filename, errors = info.result

        if "_pdf_" in info.function:
            media_type = "application/pdf"

        else:
            raise NotImplementedError("TODO: media type for xlsx")

        return FileResponse(path, filename=out_filename, media_type=media_type)

    finally:
        await redis.aclose()
