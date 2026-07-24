from pathlib import Path
import time
from zipfile import ZipFile

from httpx import BasicAuth
import pytest

from api.lib.geo import get_dataset
from api.settings import API_TOKEN, API_SECRET

POLL_DELAY_SECONDS = 1


fixture_dir = Path("tests/fixtures")


async def poll_until_done(client, job_id, interval=POLL_DELAY_SECONDS):
    for i in range(0, 100):
        response = await client.get(f"/jobs/{job_id}")
        response.raise_for_status()
        result = response.json()
        status = result.get("status")

        if status in ["success", "failed"]:
            return result

        if i > 5 and status == "queued":
            raise RuntimeError("Job queued too long, are arq and redis running?")

        time.sleep(interval)

    raise RuntimeError("Max poll iterations reached without completing job")


@pytest.mark.parametrize(
    "zip_filename,error",
    [
        ("geojson.zip", "zip file must include a shapefile or file geodatabase"),
        ("zip_empty.zip", "zip file must include a shapefile or file geodatabase"),
        ("gdb_poly_multiple_files.zip", "zip file must include only one shapefile or file geodatabase"),
        ("shp_poly_multiple_files.zip", "zip file must include only one shapefile or file geodatabase"),
        ("gdb_poly_multiple_layers.zip", "data source must contain only one data layer"),
        ("shp_missing_shx.zip", "zip file must include"),
        ("gdb_point.zip", "data source must be a Polygon type"),
        ("gdb_line.zip", "data source must be a Polygon type"),
        ("shp_point.zip", "data source must be a Polygon type"),
        ("shp_line.zip", "data source must be a Polygon type"),
        ("shp_poly_too_many.zip", "data source contains too many features"),
    ],
)
def test_get_dataset_invalid_inputs(zip_filename, error):
    with ZipFile(fixture_dir / zip_filename) as zipfile:
        with pytest.raises(ValueError, match=error):
            get_dataset(zipfile)


@pytest.mark.parametrize(
    "zip_filename,filename,layer",
    [("gdb_poly_small.zip", "poly_small.gdb", "poly_small"), ("shp_poly_small.zip", "poly_small.shp", "poly_small")],
)
def test_get_dataset(zip_filename, filename, layer):
    with ZipFile(fixture_dir / zip_filename) as zipfile:
        actual_filename, actual_layer = get_dataset(zipfile)
        assert actual_filename == filename
        assert actual_layer == layer


@pytest.mark.anyio
@pytest.mark.parametrize("method", ["get", "head"])
async def test_health(client, method):
    func = getattr(client, method)
    response = await func("/health")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_jobs_list_invalid_auth(client):
    response = await client.get("/jobs")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

    response = await client.get("/jobs", auth=BasicAuth("invalid_user", "invalid_password"))
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

    response = await client.get("/jobs", auth=BasicAuth("admin", "invalid_password"))
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.anyio
async def test_jobs_list(client):
    response = await client.get("/jobs", auth=BasicAuth("admin", API_SECRET))
    assert response.status_code == 200
    result = response.json()
    # not checking empty lists because these may accrue state from other tests
    assert "queued" in result and isinstance(result["queued"], list)
    assert "completed" in result and isinstance(result["completed"], list)


@pytest.mark.anyio
async def test_job_invalid_id(client):
    response = await client.get("/jobs/123")
    assert response.status_code == 404
    assert "Job not found" in response.json()["detail"]


@pytest.mark.anyio
async def test_job_results_invalid_id(client):
    response = await client.get("/jobs/123/results")
    assert response.status_code == 404
    assert "Job not found" in response.json()["detail"]


@pytest.mark.anyio
async def test_summary_unit_report_missing_token(client):
    response = await client.post("/summary_unit_report/huc12/123/pdf")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_summary_unit_report_invalid_unit_type(client):
    response = await client.post(f"/summary_unit_report/invalid_type/invalid_id/pdf?token={API_TOKEN}")
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Input should be 'huc12' or 'marine_hex'"


@pytest.mark.anyio
@pytest.mark.parametrize("unit_type", ["huc12", "marine_hex"])
async def test_summary_unit_report_invalid_id(client, unit_type):
    response = await client.post(f"/summary_unit_report/{unit_type}/invalid_id/pdf?token={API_TOKEN}")
    assert response.status_code == 200
    job_id = response.json()["job"]

    result = await poll_until_done(client, job_id)
    assert result["status"] == "failed"
    assert "result" not in result
    assert "Unit id is not valid" in result["detail"]

    response = await client.get(f"/jobs/{job_id}/results")
    assert response.status_code == 400
    assert "Job failed" in response.json()["detail"]


@pytest.mark.anyio
@pytest.mark.parametrize("unit_type,unit_id", [["huc12", "031501060512"], ["marine_hex", "128050"]])
async def test_summary_unit_report(client, unit_type, unit_id):
    response = await client.post(f"/summary_unit_report/{unit_type}/{unit_id}/pdf?token={API_TOKEN}")
    assert response.status_code == 200
    job_id = response.json()["job"]
    result_url = f"/jobs/{job_id}/results"

    response = await client.get(result_url)
    assert "Job not complete" in response.json()["detail"]

    result = await poll_until_done(client, job_id)
    assert result["status"] == "success"
    assert result.get("result").replace("/api", "") == result_url

    response = await client.get(result_url)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"].startswith("attachment;")


@pytest.mark.anyio
@pytest.mark.parametrize("report_type", ["pdf", "xlsx"])
async def test_custom_report_missing_token(client, report_type):
    response = await client.post(f"/custom_report/{report_type}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_custom_report_invalid_unit_type(client):
    response = await client.post(f"/custom_report/invalid_type?token={API_TOKEN}")
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Input should be 'pdf' or 'xlsx'"


@pytest.mark.anyio
@pytest.mark.parametrize("report_type", ["pdf", "xlsx"])
async def test_custom_report_missing_file(client, report_type):
    response = await client.post(f"/custom_report/{report_type}?token={API_TOKEN}")
    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["msg"] == "Field required"
    assert error["loc"][1] == "file"


@pytest.mark.anyio
@pytest.mark.parametrize("report_type", ["pdf", "xlsx"])
async def test_custom_report_empty_zip(client, report_type):
    with open("tests/fixtures/zip_empty.zip", "rb") as infile:
        response = await client.post(f"/custom_report/{report_type}?token={API_TOKEN}", files={"file": infile})
        assert response.status_code == 400
        assert response.json()["detail"] == "zip file must include a shapefile or file geodatabase"


@pytest.mark.anyio
@pytest.mark.parametrize("report_type", ["pdf", "xlsx"])
async def test_custom_report_invalid_type(client, report_type):
    with open("tests/fixtures/zip_empty.zip", "rb") as infile:
        # spoof an invalid mime type and filename
        response = await client.post(
            f"/custom_report/{report_type}?token={API_TOKEN}",
            files={"file": ("zip_empty.not-zip", infile, "invalid-mime-type")},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "file must be a zip file containing shapefile or file geodatabase"


@pytest.mark.anyio
@pytest.mark.parametrize("report_type", ["pdf", "xlsx"])
async def test_custom_report_unsupported_format(client, report_type):
    with open("tests/fixtures/geojson.zip", "rb") as infile:
        response = await client.post(f"/custom_report/{report_type}?token={API_TOKEN}", files={"file": infile})
        assert response.status_code == 400
        assert response.json()["detail"] == "zip file must include a shapefile or file geodatabase"


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
@pytest.mark.parametrize("geometry_type", ["point", "line"])
@pytest.mark.parametrize("report_type", ["pdf", "xlsx"])
async def test_custom_report_invalid_geometry(client, format, geometry_type, report_type):
    with open(f"tests/fixtures/{format}_{geometry_type}.zip", "rb") as infile:
        response = await client.post(f"/custom_report/{report_type}?token={API_TOKEN}", files={"file": infile})
        assert response.status_code == 400
        assert response.json()["detail"] == "data source must be a Polygon type"


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
@pytest.mark.parametrize("report_type", ["pdf", "xlsx"])
async def test_custom_report_multiple_files(client, format, report_type):
    with open(f"tests/fixtures/{format}_poly_multiple_files.zip", "rb") as infile:
        response = await client.post(f"/custom_report/{report_type}?token={API_TOKEN}", files={"file": infile})
        assert response.status_code == 400
        assert response.json()["detail"] == "zip file must include only one shapefile or file geodatabase"


@pytest.mark.anyio
@pytest.mark.parametrize("report_type", ["pdf", "xlsx"])
async def test_custom_report_multiple_layers(client, report_type):
    with open("tests/fixtures/gdb_poly_multiple_files.zip", "rb") as infile:
        response = await client.post(f"/custom_report/{report_type}?token={API_TOKEN}", files={"file": infile})
        assert response.status_code == 400
        assert response.json()["detail"] == "zip file must include only one shapefile or file geodatabase"


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
@pytest.mark.parametrize("report_type", ["pdf", "xlsx"])
async def test_custom_report_too_many_features(client, format, report_type):
    with open(f"tests/fixtures/{format}_poly_too_many.zip", "rb") as infile:
        response = await client.post(f"/custom_report/{report_type}?token={API_TOKEN}", files={"file": infile})
        assert response.status_code == 400
        assert "data source contains too many features" in response.json()["detail"]


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
@pytest.mark.parametrize(
    "report_type",
    [
        "pdf",
        #  "xlsx" # FIXME: enable once supported
    ],
)
async def test_custom_report_area_too_small(client, format, report_type):
    with open(f"tests/fixtures/{format}_poly_tiny.zip", "rb") as infile:
        response = await client.post(f"/custom_report/{report_type}?token={API_TOKEN}", files={"file": infile})
        assert response.status_code == 200
        job_id = response.json()["job"]

        result = await poll_until_done(client, job_id)
        assert result["status"] == "failed"
        assert (
            r"100% of the total area in the data source is in polygons less than a single 30x30m pixel"
            in result["detail"]
        )


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
@pytest.mark.parametrize(
    "report_type",
    [
        "pdf",
        #  "xlsx" # FIXME: enable once supported
    ],
)
async def test_custom_report_area_too_large(client, format, report_type):
    with open(f"tests/fixtures/{format}_poly_large.zip", "rb") as infile:
        response = await client.post(f"/custom_report/{report_type}?token={API_TOKEN}", files={"file": infile})
        assert response.status_code == 200
        job_id = response.json()["job"]

        result = await poll_until_done(client, job_id)
        assert result["status"] == "failed"
        assert "Your area of interest is too large" in result["detail"]


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
@pytest.mark.parametrize(
    "report_type",
    [
        "pdf",
        #  "xlsx" # FIXME: enable once supported
    ],
)
async def test_custom_report_no_overlap(client, format, report_type):
    with open(f"tests/fixtures/{format}_poly_no_overlap.zip", "rb") as infile:
        response = await client.post(f"/custom_report/{report_type}?token={API_TOKEN}", files={"file": infile})
        assert response.status_code == 200
        job_id = response.json()["job"]

        result = await poll_until_done(client, job_id)
        assert result["status"] == "failed"
        assert "area of interest does not overlap" in result["detail"]


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
@pytest.mark.parametrize(
    "report_type",
    [
        "pdf",
        #  "xlsx" # FIXME: enable once supported
    ],
)
async def test_custom_report(client, format, report_type):
    with open(f"tests/fixtures/{format}_poly_small.zip", "rb") as infile:
        response = await client.post(f"/custom_report/{report_type}?token={API_TOKEN}", files={"file": infile})
        assert response.status_code == 200
        job_id = response.json()["job"]
        result_url = f"/jobs/{job_id}/results"

        result = await poll_until_done(client, job_id)
        assert result["status"] == "success"
        assert result.get("result").replace("/api", "") == result_url

        response = await client.get(result_url)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"].startswith("attachment;")
