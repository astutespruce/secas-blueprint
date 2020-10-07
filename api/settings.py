from pathlib import Path
import os

from arq.connections import RedisSettings
from dotenv import load_dotenv


load_dotenv()
TEMP_DIR = Path(os.getenv("TEMP_DIR", "/tmp/se-report"))
MBGL_SERVER_URL = os.getenv("MBGL_SERVER_URL", "http://localhost:8002/render")
API_TOKEN = os.getenv("API_TOKEN")
API_SECRET = os.getenv("API_SECRET")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
SENTRY_DSN = os.getenv("SENTRY_DSN")

REDIS = RedisSettings(host=REDIS_HOST, port=REDIS_PORT)

REDIS_QUEUE = "southeast"

# retain files for 4 hours
FILE_RETENTION = 14400

# time jobs out after 10 minutes
JOB_TIMEOUT = 600


if not TEMP_DIR.exists():
    os.makedirs(TEMP_DIR)
