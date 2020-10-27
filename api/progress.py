import arq

from api.settings import REDIS, JOB_TIMEOUT


JOB_PREFIX = "arq:job-progress:"
EXPIRATION = JOB_TIMEOUT + 3600


async def set_progress(job_id, progress=0, message="", errors=None):
    """Store job progress to redis, and expire after EXPIRATION seconds.

    Parameters
    ----------
    job_id : str
    progress : int, optional (default 0)
    message : str (optional, default '')
        short status message, if any
    errors : list-like (optional, default None)
        list of short error message, if any
    """

    error_str = ",".join(errors) if errors else ""

    redis = await arq.create_pool(REDIS)
    await redis.setex(
        f"{JOB_PREFIX}{job_id}", EXPIRATION, f"{progress}|{message}|{error_str}"
    )
    redis.close()
    await redis.wait_closed()


async def get_progress(job_id):
    """Get job progress from redis, or None if the job_id is not found.

    Parameters
    ----------
    job_id : str

    Returns
    -------
    (int, str, list)
        tuple of progress percent, message, errors
    """
    redis = await arq.create_pool(REDIS)
    progress = await redis.get(f"{JOB_PREFIX}{job_id}")
    redis.close()
    await redis.wait_closed()

    if progress is None:
        return 0, "", []

    progress, message, errors = progress.split("|")
    errors = errors.split(",") if errors else []

    return int(progress), message, errors
