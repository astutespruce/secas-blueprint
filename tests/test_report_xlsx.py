import pytest
from pyogrio import read_dataframe
import numpy as np

from analysis.constants import (
    DATA_CRS,
    BLUEPRINT,
    INDICATORS,
    CORRIDORS,
    PARCAS,
    PARCAS_POLY,
    PROTECTED_AREAS,
    PROTECTED_AREAS_POLY,
    SLR_DEPTH,
    SLR_PROJ,
    URBAN_BY_DECADE,
    WILDFIRE_RISK,
)
from analysis.lib.geometry import dissolve
from analysis.lib.stats.prescreen import get_available_datasets
from analysis.lib.stats.analysis_units import get_analysis_unit_results
from analysis.lib.xlsx.report import create_report
from api.settings import API_TOKEN
from tests.lib.jobs import poll_until_done


@pytest.mark.parametrize("format", ["shp", "gdb"])
def test_get_available_datasets_no_overlap(format):
    filename = f"{format}_poly_no_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    datasets = get_available_datasets(df)
    assert len(datasets) == 0


@pytest.mark.parametrize("format", ["shp", "gdb"])
def test_get_available_datasets(format):
    # NOTE: this needs to be updated for each blueprint version; this is just a
    # smoke test that values do not change except during Blueprint version updates

    filename = f"{format}_poly_small.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    datasets = set(get_available_datasets(df))

    assert len(datasets) == 32

    expected_datasets = [
        BLUEPRINT["id"],
        CORRIDORS["id"],
        PARCAS["id"],
        PARCAS_POLY["id"],
        PROTECTED_AREAS["id"],
        PROTECTED_AREAS_POLY["id"],
        SLR_DEPTH["id"],
        SLR_PROJ["id"],
        URBAN_BY_DECADE["id"],
        WILDFIRE_RISK["id"],
    ]
    for dataset in expected_datasets:
        assert dataset in datasets

    # does not overlap with marine or Caribbean, so there should be no associated indicators
    unexpected_datasets = [
        indicator["id"]
        for indicator in INDICATORS
        if indicator["id"].startswith("m_") or "caribbean" in indicator["id"]
    ]
    for dataset in unexpected_datasets:
        assert dataset not in datasets


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_get_analysis_unit_results_single_area(format):
    # NOTE: this needs to be updated for each blueprint version; this is just a
    # smoke test that values do not change except during Blueprint version updates

    filename = f"{format}_poly_small.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)
    datasets = set(get_available_datasets(df))
    results = await get_analysis_unit_results(df, datasets)

    assert len(results) == len(df)
    for col in ["states", "subregions", "regions", "count", "acres"]:
        assert col in results.columns

    row = results.iloc[0]

    assert row.states == "Alabama"
    assert row.regions == "continental"
    assert row.subregions == "Piedmont"
    assert row["count"] == 1
    assert np.isclose(row.acres, 51.026)
    assert np.isclose(row.rasterized_acres, 50.7059)
    assert np.isclose(row.outside_se_acres, 0)

    assert np.allclose(row[BLUEPRINT["id"]], [0, 0, 0, 10.674936, 40.03101])
    assert np.allclose(row[CORRIDORS["id"]], [0, 37.362276, 13.34367])
    assert np.allclose(row["t_imperiledamphibiansandreptiles"], [0.6671835, 0, 0, 3.113523, 42.254955, 4.6702845])
    assert np.allclose(row["f_permeablesurface"], [0, 0, 0, 50.705946])

    assert np.allclose(row[PARCAS["id"]], [0, 50.705946])
    parcas_poly = row[PARCAS_POLY["id"]]
    assert len(parcas_poly) == 1
    assert parcas_poly[0]["name"] == "Talladega"
    assert np.isclose(parcas_poly[0]["acres"], 51.026)

    assert np.allclose(row[PROTECTED_AREAS["id"]], [16.6795875, 34.0263585])
    protected_areas_poly = row[PROTECTED_AREAS_POLY["id"]]
    assert len(protected_areas_poly) == 1
    assert protected_areas_poly[0]["name"] == "Talladega National Forest"
    assert protected_areas_poly[0]["owner"] == "USDA Forest Service"
    assert np.isclose(protected_areas_poly[0]["acres"], 34.5465)

    slr_depth = row[SLR_DEPTH["id"]]
    assert len(slr_depth) == 14
    assert np.allclose(slr_depth, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 50.705946, 0])

    urban = row[URBAN_BY_DECADE["id"]]
    assert len(urban) == 10
    assert np.allclose(urban, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    assert np.allclose(row[WILDFIRE_RISK["id"]], [0, 0, 0, 0, 0, 50.705946, 0, 0, 0, 0, 0])


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_get_analysis_unit_results_multiple_areas(format):
    # NOTE: this needs to be updated for each blueprint version; this is just a
    # smoke test that values do not change except during Blueprint version updates

    filename = f"{format}_poly_multiple.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)
    datasets = set(get_available_datasets(df))
    results = await get_analysis_unit_results(df, datasets)

    assert len(results) == len(df)
    for col in ["states", "subregions", "regions", "count", "acres"]:
        assert col in results.columns

    assert results.states.fillna("").values.tolist() == ["Georgia", "Florida", "Mississippi", "Puerto Rico", ""]
    assert results.regions.values.tolist() == ["continental", "continental", "continental", "caribbean", "marine"]
    assert results.subregions.values.tolist() == [
        "Appalachians",
        "Florida Peninsula",
        "Mississippi Alluvial Valley",
        "Puerto Rico",
        "Atlantic",
    ]
    assert results["count"].values.tolist() == [1] * 5
    assert np.allclose(results["acres"], [313.13876187, 40.55673456, 99.02771972, 147.19913421, 5386.09794185])
    assert np.allclose(results["rasterized_acres"], [312.241878, 40.698, 99.187947, 147.0027645, 5386.1723955])
    assert np.allclose(results["outside_se_acres"], [0, 0, 0, 0, 0])

    ga_poly = results.iloc[0]
    fl_poly = results.iloc[1]
    pr_poly = results.iloc[3]
    marine_poly = results.iloc[4]

    assert np.allclose(ga_poly[BLUEPRINT["id"]], [98.5207635, 0, 153.896994, 52.929891, 6.8942295])
    assert np.allclose(marine_poly[BLUEPRINT["id"]], [0, 0, 3549.6386145000006, 1836.533781, 0])
    assert np.allclose(ga_poly[CORRIDORS["id"]], [312.241878, 0.0, 0.0])
    assert np.allclose(marine_poly[CORRIDORS["id"]], [4045.355955, 0, 1340.8164405])
    assert np.allclose(
        ga_poly["t_imperiledamphibiansandreptiles"], [40.03101, 20.460294, 73.834974, 3.113523, 171.9109485, 2.8911285]
    )
    assert np.allclose(ga_poly["f_permeablesurface"], [0, 0, 0, 312.241878])
    assert np.allclose(marine_poly["f_permeablesurface"], [0, 0, 0, 0])

    assert np.allclose(
        np.array(results[PARCAS["id"]].values.tolist()),
        [
            [312.241878, 0],
            [40.698, 0],
            [99.187947, 0],
            [0, 0],
            [0, 0],
        ],
    )

    assert np.allclose(
        np.array(results[PROTECTED_AREAS["id"]].values.tolist()),
        [
            [312.241878, 0],
            [0, 40.698],
            [99.187947, 0],
            [81.1739925, 65.828772],
            [5386.1723955, 0],
        ],
    )

    fl_protected_areas_poly = fl_poly[PROTECTED_AREAS_POLY["id"]]
    assert len(fl_protected_areas_poly) == 3
    assert fl_protected_areas_poly[0]["name"] == "Crystal River Preserve State Park"
    assert np.isclose(fl_protected_areas_poly[0]["acres"], 27.801745)

    assert np.allclose(
        fl_poly[SLR_DEPTH["id"]],
        [
            25.1305785,
            38.9190375,
            40.6981935,
            40.6981935,
            40.6981935,
            40.6981935,
            40.6981935,
            40.6981935,
            40.6981935,
            40.6981935,
            40.6981935,
            0,
            0,
            0,
        ],
    )

    assert np.allclose(pr_poly[SLR_DEPTH["id"]], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 147.0027645, 0, 0])

    pr_slr_proj = pr_poly[SLR_PROJ["id"]]
    assert len(pr_slr_proj) == 5
    assert pr_slr_proj[0]["scenario"] == "h"
    assert np.allclose(
        pr_slr_proj[0]["values"],
        [0.2624672, 0.492126, 0.82021, 1.312336, 2.0669292, 3.0511812, 4.1994752, 5.4461944, 6.7913388],
    )

    assert np.allclose(
        ga_poly[URBAN_BY_DECADE["id"]],
        [
            22.9066335,
            23.15571534,
            24.16538637,
            24.31216674,
            25.56202383,
            26.68734,
            27.2655657,
            27.57247011,
            28.00391544,
            0,
        ],
    )

    assert np.allclose(marine_poly[URBAN_BY_DECADE["id"]], [0, 0, 0, 0, 0, 0, 0, 0, 0, 5386.1723955])

    assert np.allclose(ga_poly[WILDFIRE_RISK["id"]], [0, 0, 0, 0, 0, 0.6671835, 311.5746945, 0, 0, 0, 0])


@pytest.mark.anyio
async def test_create_xlsx_file():
    df = read_dataframe("/vsizip/tests/fixtures/shp_poly_small.zip/poly_small.shp", columns=[], use_arrow=True).to_crs(
        DATA_CRS
    )
    # dissolve like API endpoint
    field = "__analysis_unit"
    df[field] = "all areas"
    df = dissolve(df, by=field).set_index(field)

    datasets = set(get_available_datasets(df))
    results = await get_analysis_unit_results(df, datasets)
    xlsx = create_report(results, datasets, name="Test area")

    # FIXME: remove
    with open("/tmp/test.xlsx", "wb") as out:
        _ = out.write(xlsx)


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_custom_xlsx_report_api_single_area(client, format):
    with open(f"tests/fixtures/{format}_poly_small.zip", "rb") as infile:
        response = await client.post(f"/custom_report/xlsx?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 200
    job_id = response.json()["job"]

    result = await poll_until_done(client, job_id)
    assert result["status"] == "success"

    result_payload = result["result"]
    uuid = result_payload["uuid"]
    assert uuid is not None
    assert result_payload["count"] == 1

    fields = result_payload["fields"]
    assert fields["ID"] == 1
    assert fields["Name"] == 1

    datasets = set(result_payload["datasets"])
    assert len(datasets) == 32

    expected_datasets = [
        BLUEPRINT["id"],
        CORRIDORS["id"],
        PARCAS["id"],
        PARCAS_POLY["id"],
        PROTECTED_AREAS["id"],
        PROTECTED_AREAS_POLY["id"],
        SLR_DEPTH["id"],
        SLR_PROJ["id"],
        URBAN_BY_DECADE["id"],
        WILDFIRE_RISK["id"],
    ]
    for dataset in expected_datasets:
        assert dataset in datasets

    # does not overlap with marine or Caribbean, so there should be no associated indicators
    unexpected_datasets = [
        indicator["id"]
        for indicator in INDICATORS
        if indicator["id"].startswith("m_") or "caribbean" in indicator["id"]
    ]
    for dataset in unexpected_datasets:
        assert dataset not in datasets

    ### submit finalize job
    response = await client.post(
        f"/custom_report/xlsx/{uuid}/finalize?token={API_TOKEN}", data={"datasets": ",".join(datasets)}
    )
    assert response.status_code == 200

    job_id = response.json()["job"]

    result = await poll_until_done(client, job_id)
    assert result["status"] == "success"


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_custom_xlsx_report_api_get_inputs_multiple_areas(client, format):
    with open(f"tests/fixtures/{format}_poly_multiple.zip", "rb") as infile:
        response = await client.post(f"/custom_report/xlsx?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 200
    job_id = response.json()["job"]

    result = await poll_until_done(client, job_id)
    assert result["status"] == "success"

    result_payload = result["result"]
    assert "uuid" in result_payload
    assert result_payload["count"] == 5

    fields = result_payload["fields"]
    assert fields["ID"] == 5
    assert fields["Name"] == 5
    assert fields["Region"] == 3
    assert fields["Common"] == 1

    datasets = set(result_payload["datasets"])
    assert len(datasets) == 59

    expected_datasets = [
        BLUEPRINT["id"],
        CORRIDORS["id"],
        PARCAS["id"],
        PARCAS_POLY["id"],
        PROTECTED_AREAS["id"],
        PROTECTED_AREAS_POLY["id"],
        SLR_DEPTH["id"],
        SLR_PROJ["id"],
        URBAN_BY_DECADE["id"],
        WILDFIRE_RISK["id"],
    ]
    for dataset in expected_datasets:
        assert dataset in datasets


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_custom_xlsx_report_api_get_inputs_multiple_areas_partial_overlap(client, format):
    with open(f"tests/fixtures/{format}_poly_multiple_partial_overlap.zip", "rb") as infile:
        response = await client.post(f"/custom_report/xlsx?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 200
    job_id = response.json()["job"]

    result = await poll_until_done(client, job_id)
    assert result["status"] == "success"

    result_payload = result["result"]
    assert "uuid" in result_payload
    assert result_payload["count"] == 3

    fields = result_payload["fields"]
    assert fields["ID"] == 3
    assert fields["Name"] == 3
    assert fields["Blueprint"] == 3
    assert fields["Common"] == 1

    datasets = set(result_payload["datasets"])
    assert len(datasets) == 31

    expected_datasets = [
        BLUEPRINT["id"],
        CORRIDORS["id"],
        PARCAS["id"],
        PARCAS_POLY["id"],
        PROTECTED_AREAS["id"],
        PROTECTED_AREAS_POLY["id"],
        SLR_DEPTH["id"],
        SLR_PROJ["id"],
        URBAN_BY_DECADE["id"],
        WILDFIRE_RISK["id"],
    ]
    for dataset in expected_datasets:
        assert dataset in datasets


@pytest.mark.anyio
async def test_finalize_xlsx_report_api_missing_token(client):
    response = await client.post("/custom_report/xlsx/123/finalize")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_finalize_xlsx_report_api_invalid_uuid(client):
    response = await client.post(f"/custom_report/xlsx/123/finalize?token={API_TOKEN}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Dataset not found"
