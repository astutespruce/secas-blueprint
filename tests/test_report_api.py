from pathlib import Path
import os
import time
import httpx
from api.settings import API_TOKEN

# this assumes API server is running at :5000 and that worker is also running

DELAY = 2  # seconds

API_URL = "http://localhost:5000"
# API_URL = "http://localhost:8080"

OUT_DIR = Path("/tmp/api")

if not OUT_DIR.exists():
    os.makedirs(OUT_DIR)


def poll_until_done(job_id, current=0, max=100):
    r = httpx.get(f"{API_URL}/api/reports/status/{job_id}?token={API_TOKEN}")

    if r.status_code != 200:
        raise Exception(f"Error processing request (HTTP {r.status_code}): {r.text}")

    json = r.json()
    status = json.get("status")
    progress = json.get("progress")
    message = json.get("message")
    errors = json.get("errors")

    if status == "success":
        print(f"Results at: {json['result']}")
        print(f"Job errors: {json['errors']}")
        download_file(json["result"])
        return

    if status == "failed":
        print(f"Failed: {json['detail']}")
        return

    print(f"Progress: {progress}, message: {message}, errors: {errors}")

    current += 1
    if current == max:
        print("Max retries hit, stopping...")
        return

    time.sleep(DELAY)

    poll_until_done(job_id, current=current, max=max)


def download_file(url):
    filename = OUT_DIR / "test_report.pdf"
    print(f"Downloading report to {filename}")
    r = httpx.get(f"{API_URL}{url}")

    with open(filename, "wb") as out:
        out.write(r.read())


def test_upload_file(filename):
    files = {"file": open(filename, "rb")}
    r = httpx.post(
        f"{API_URL}/api/reports/custom?token={API_TOKEN}",
        data={"name": "foo"},
        files=files,
    )

    if r.status_code != 200:
        raise Exception(f"Error processing request (HTTP {r.status_code}): {r.text}")

    json = r.json()
    job_id = json.get("job")

    if job_id is None:
        raise Exception(json)

    poll_until_done(job_id)


def test_huc12_report(huc12_id):
    r = httpx.post(f"{API_URL}/api/reports/huc12/{huc12_id}?token={API_TOKEN}")

    if r.status_code != 200:
        raise Exception(f"Error processing request (HTTP {r.status_code}): {r.text}")

    json = r.json()

    if not json:
        raise Exception(r.status)

    job_id = json.get("job")

    if job_id is None:
        raise Exception(json)

    poll_until_done(job_id)


if __name__ == "__main__":
    # test_upload_file("examples/api/caledonia.zip")

    # test_huc12_report("0")

    test_huc12_report("031501060512")
    # test_huc12_report("031700080402")
