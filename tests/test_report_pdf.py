import asyncio
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from pyogrio import read_dataframe
import pytest

from analysis.constants import DATA_CRS, GEO_CRS, INDICATORS
from analysis.lib.pdf.map import render_maps
from analysis.lib.pdf.report import create_report
from analysis.lib.stats.aoi import get_aoi_results
from analysis.lib.stats.summary_units import get_summary_unit_results
from api.lib.geo import get_dataset

from tests.lib.image import image_matches


fixture_dir = Path("tests/fixtures")


@pytest.mark.parametrize("unit_type", [None, "", "invalid_unit_type"])
def test_summary_unit_results_invalid_type(unit_type):
    with pytest.raises(ValueError, match="unit_type must be one of"):
        get_summary_unit_results(unit_type, None)


@pytest.mark.parametrize("unit_type", ["huc12", "marine_hex"])
@pytest.mark.parametrize("unit_id", [None, 1])
def test_summary_unit_results_invalid_id_type(unit_type, unit_id):
    with pytest.raises(ValueError, match="unit_id must be a string"):
        get_summary_unit_results(unit_type, unit_id)


@pytest.mark.parametrize("unit_type", ["huc12", "marine_hex"])
@pytest.mark.parametrize("unit_id", ["", "1"])
def test_summary_unit_results_invalid_id(unit_type, unit_id):
    # None signals that unit was not found
    assert get_summary_unit_results(unit_type, unit_id) is None


def test_summary_unit_results_huc12():
    # NOTE: this needs to be updated for each blueprint version; this is just a
    # smoke test that values do not change except during Blueprint version updates

    results = get_summary_unit_results("huc12", "030601040506")
    assert results is not None
    assert results["name"] == "Clark Creek subwatershed"
    assert np.isclose(results["acres"], 33248.8807)
    assert np.isclose(results["rasterized_acres"], 33250.201695)
    assert results["outside_se_acres"] == 0
    assert np.allclose(
        results["bounds"],
        [-82.88331988387216, 33.78085952464868, -82.74141409346743, 33.945315480643465],
    )

    assert results["subregions"] == {"Piedmont"}
    assert results["regions"] == {"continental"}

    assert "blueprint" in results
    assert len(results["blueprint"]) == 5
    assert results["blueprint"][0]["value"] == 4
    assert np.isclose(results["blueprint"][0]["acres"], 867.116)

    assert "corridors" in results
    assert len(results["corridors"]) == 3
    assert results["corridors"][0]["value"] == 1
    assert np.isclose(results["corridors"][1]["acres"], 1408.424)

    assert len(results["indicator_groups"]) == 2
    assert len(results["indicator_groups"][0]["indicators"]) == 11
    assert len(results["indicator_groups"][1]["indicators"]) == 6

    assert "protected_areas" in results
    assert len(results["protected_areas"]["entries"]) == 2
    assert np.isclose(results["protected_areas"]["entries"][0]["acres"], 33186.3744735)
    assert len(results["protected_areas"]["protected_areas"]) == 1
    assert results["protected_areas"]["num_protected_areas"] == 1

    assert "slr" in results
    assert results["slr"] == {"na": True}

    assert "urban" in results
    assert len(results["urban"]["entries"]) == 9
    assert np.isclose(results["urban"]["entries"][0]["acres"], 1236.9582)

    assert "wildfire_risk" in results
    assert len(results["wildfire_risk"]["entries"]) == 11
    assert np.isclose(results["wildfire_risk"]["entries"][0]["acres"], 143.8892)

    assert "legend" in results


def test_summary_unit_results_marine_hex():
    # NOTE: this needs to be updated for each blueprint version; this is just a
    # smoke test that values do not change except during Blueprint version updates

    results = get_summary_unit_results("marine_hex", "154309")
    assert results is not None
    assert results["name"] == "Hex ID: 154309 "
    assert np.isclose(results["acres"], 9613.7778)
    assert np.isclose(results["rasterized_acres"], 9610.3335)
    assert results["outside_se_acres"] == 0
    assert np.allclose(
        results["bounds"],
        [-89.8582540305896, 27.507620329841565, -89.78008262157722, 27.570339701836122],
    )

    assert results["subregions"] == {"Gulf"}
    assert results["regions"] == {"marine"}

    assert "blueprint" in results
    assert len(results["blueprint"]) == 5
    assert results["blueprint"][0]["value"] == 4
    assert np.isclose(results["blueprint"][0]["acres"], 18.4587)

    # no corridors in this particular area
    assert "corridors" not in results

    assert len(results["indicator_groups"]) == 1
    assert len(results["indicator_groups"][0]["indicators"]) == 5

    assert "protected_areas" in results
    assert len(results["protected_areas"]["entries"]) == 2
    assert np.isclose(results["protected_areas"]["entries"][0]["acres"], 9610.3335)
    assert len(results["protected_areas"]["protected_areas"]) == 0
    assert results["protected_areas"]["num_protected_areas"] == 0

    assert "slr" not in results
    assert "urban" not in results
    assert "wildfire_risk" not in results

    assert "legend" in results


@pytest.mark.anyio
async def test_summary_unit_maps_huc12():
    unit_id = "030601040506"
    results = get_summary_unit_results("huc12", unit_id)
    # intentionally skip most maps for this test; these are tested for AOI below
    maps, scale, map_errors = await render_maps(results["bounds"], summary_unit_id=unit_id)

    assert scale["width"] == 250
    assert scale["increments"] == [62, 125]
    assert scale["miles"] == 9
    assert np.isclose(scale["resolution"], 57.742)

    assert len(map_errors) == 0
    assert "locator" in maps
    assert "blueprint" in maps

    locator_img_filename = fixture_dir / f"maps/{unit_id}_locator.png"
    # uncomment this each Blueprint update
    # with open(locator_img_filename, "wb") as outfile:
    #     _ = outfile.write(maps["locator"])

    assert image_matches(maps["locator"], locator_img_filename)

    blueprint_img_filename = fixture_dir / f"maps/{unit_id}_blueprint.png"
    # with open(blueprint_img_filename, "wb") as outfile:
    #     _ = outfile.write(maps["blueprint"])

    assert image_matches(maps["blueprint"], blueprint_img_filename)


@pytest.mark.anyio
async def test_summary_unit_pdf_huc12():
    """this is just a smoke test that PDF generates"""
    unit_id = "030601040506"
    results = get_summary_unit_results("huc12", unit_id)
    maps, scale, map_errors = await render_maps(results["bounds"], summary_unit_id=unit_id)
    results["scale"] = scale
    pdf = create_report(maps=maps, results=results, name=results["name"], area_type="huc12")
    assert pdf is not None


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["gdb", "shp"])
async def test_aoi_results_no_overlap(format):
    zip_filename = fixture_dir / f"{format}_poly_no_overlap.zip"
    with ZipFile(zip_filename) as zipfile:
        dataset, layer = get_dataset(zipfile)

    df = read_dataframe(f"/vsizip/{zip_filename}/{dataset}", layer=layer, columns=[]).to_crs(DATA_CRS)
    results = await get_aoi_results(df)

    assert results is None


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["gdb", "shp"])
async def test_aoi_results_too_small(format):
    # NOTE: this is rejected by the API, but the backend just returns None
    zip_filename = fixture_dir / f"{format}_poly_tiny.zip"
    with ZipFile(zip_filename) as zipfile:
        dataset, layer = get_dataset(zipfile)

    df = read_dataframe(f"/vsizip/{zip_filename}/{dataset}", layer=layer, columns=[]).to_crs(DATA_CRS)
    results = await get_aoi_results(df)

    assert results is None


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["gdb", "shp"])
async def test_aoi_results(format):
    # NOTE: this needs to be updated for each blueprint version; this is just a
    # smoke test that values do not change except during Blueprint version updates

    zip_filename = fixture_dir / f"{format}_poly_small.zip"
    with ZipFile(zip_filename) as zipfile:
        dataset, layer = get_dataset(zipfile)

    df = read_dataframe(f"/vsizip/{zip_filename}/{dataset}", layer=layer, columns=[]).to_crs(DATA_CRS)

    results = await get_aoi_results(df)

    assert results is not None
    assert np.isclose(results["acres"], 51.026)
    assert np.isclose(results["rasterized_acres"], 50.7059)
    assert results["outside_se_acres"] == 0

    assert results["subregions"] == {"Piedmont"}
    assert results["regions"] == {"continental"}

    assert "blueprint" in results
    assert len(results["blueprint"]) == 5
    assert results["blueprint"][0]["value"] == 4
    assert np.isclose(results["blueprint"][0]["acres"], 40.03101)

    assert "corridors" in results
    assert len(results["corridors"]) == 3
    assert results["corridors"][0]["value"] == 1
    assert np.isclose(results["corridors"][1]["acres"], 13.34367)

    assert len(results["indicator_groups"]) == 2
    assert len(results["indicator_groups"][0]["indicators"]) == 8
    assert len(results["indicator_groups"][1]["indicators"]) == 1

    assert "protected_areas" in results
    assert len(results["protected_areas"]["entries"]) == 2
    assert np.isclose(results["protected_areas"]["entries"][0]["acres"], 16.6795)
    assert len(results["protected_areas"]["protected_areas"]) == 1
    assert results["protected_areas"]["num_protected_areas"] == 1

    assert "slr" in results
    assert results["slr"] == {"na": True}

    assert "urban" in results
    assert len(results["urban"]["entries"]) == 9
    assert np.isclose(results["urban"]["entries"][0]["acres"], 0)

    assert "wildfire_risk" in results
    assert len(results["wildfire_risk"]["entries"]) == 11
    assert np.isclose(results["wildfire_risk"]["entries"][0]["acres"], 0)

    assert "legend" in results


@pytest.mark.anyio
@pytest.mark.filterwarnings("ignore:.*no geotransform.*")
async def test_aoi_maps():
    zip_filename = fixture_dir / "shp_poly_small.zip"
    with ZipFile(zip_filename) as zipfile:
        dataset, layer = get_dataset(zipfile)

    df = read_dataframe(f"/vsizip/{zip_filename}/{dataset}", layer=layer, columns=[]).to_crs(DATA_CRS)
    geo_df = df.to_crs(GEO_CRS)

    # arbitrary set of indicators just to test mapping
    indicators = [e["id"] for e in INDICATORS[:3]]

    # this is just a smoke test to verify that maps are created  successfully
    maps, scale, map_errors = await render_maps(
        geo_df.total_bounds,
        geometry=geo_df.geometry.values[0],
        indicators=indicators,
        corridors=True,
        parcas=True,
        protected_areas=True,
        slr=True,
        urban=True,
        wildfire_risk=True,
    )

    assert len(map_errors) == 0

    assert scale["width"] == 230
    assert scale["increments"] == [57, 115]
    assert scale["miles"] == 0.2
    assert np.isclose(scale["resolution"], 1.39597)

    assert "locator" in maps
    assert "blueprint" in maps
    for id in indicators:
        assert id in maps

    assert "corridors" in maps
    assert "parcas" in maps
    assert "protected_areas" in maps
    assert "slr" in maps
    assert "urban" in maps
    assert "wildfire_risk" in maps
