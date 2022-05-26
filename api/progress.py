from api.settings import JOB_TIMEOUT


JOB_PREFIX = "arq:job-progress:"
EXPIRATION = JOB_TIMEOUT + 3600


async def set_progress(redis, job_id, progress=0, message="", errors=None):
    """Store job progress to redis, and expire after EXPIRATION seconds.

    Parameters
    ----------
    redis: redis connection pool
    job_id : str
    progress : int, optional (default 0)
    message : str (optional, default '')
        short status message, if any
    errors : list-like (optional, default None)
        list of short error message, if any
    """

    error_str = ",".join(errors) if errors else ""

    await redis.setex(
        f"{JOB_PREFIX}{job_id}", EXPIRATION, f"{progress}|{message}|{error_str}"
    )


async def get_progress(redis, job_id):
    """Get job progress from redis, or None if the job_id is not found.

    Parameters
    ----------
    redis: redis connection pool
    job_id : str

    Returns
    -------
    (int, str, list)
        tuple of progress percent, message, errors
    """
    progress = await redis.get(f"{JOB_PREFIX}{job_id}")
    redis.close()

    if progress is None:
        return 0, "", []

    progress, message, errors = progress.decode("UTF8").split("|")
    errors = errors.split(",") if errors else []

    return int(progress), message, errors
