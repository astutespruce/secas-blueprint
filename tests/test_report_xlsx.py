import os
from io import BytesIO

import numpy as np
import pandas as pd
import pytest
from dotenv import load_dotenv
from pyogrio import read_dataframe

from analysis.constants import (
    BLUEPRINT,
    CORRIDORS,
    DATA_CRS,
    INDICATORS,
    INDICATORS_INDEX,
    PARCAS,
    PARCAS_POLY,
    PROTECTED_AREAS,
    PROTECTED_AREAS_POLY,
    REPORT_DATASETS,
    SLR_DEPTH,
    SLR_PROJ,
    URBAN_BY_DECADE,
    WILDFIRE_RISK,
)
from analysis.lib.geometry import dissolve
from analysis.lib.stats.analysis_units import get_analysis_unit_results
from analysis.lib.stats.prescreen import get_available_datasets
from analysis.lib.xlsx.basic import get_value_columns
from analysis.lib.xlsx.report import create_report, get_value_order
from analysis.lib.xlsx.slr import depth_value_columns as slr_depth_value_cols
from analysis.lib.xlsx.slr import proj_value_columns as slr_proj_value_cols
from analysis.lib.xlsx.urban import value_columns as urban_value_cols

load_dotenv()

# add to .env file to name saving test files
SAVE_XLSX = bool(os.getenv("TEST_SAVE_XLSX", False))

# value cols not provided by specific modules (these come from xlsx/basic.py)
blueprint_value_cols = get_value_columns(BLUEPRINT["values"])
corridor_value_cols = get_value_columns(CORRIDORS["values"])
wildfire_risk_value_cols = get_value_columns(WILDFIRE_RISK["values"])

outside_data_extent_col = "Outside extent of this dataset but within Southeast data extent\n(acres)"


@pytest.mark.parametrize("format", ["shp", "gdb"])
def test_get_available_datasets_single_area(format):
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


@pytest.mark.parametrize("format", ["shp", "gdb"])
def test_get_available_datasets_no_overlap(format):
    filename = f"{format}_poly_no_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    datasets = get_available_datasets(df)
    assert len(datasets) == 0


@pytest.mark.parametrize("format", ["shp", "gdb"])
def test_get_available_datasets_multiple_areas_partial_overlap(format):
    # just a test that this runs, not checking specific ones
    filename = f"{format}_poly_multiple_partial_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    datasets = get_available_datasets(df)
    assert len(datasets) == 31


@pytest.mark.parametrize("format", ["shp", "gdb"])
def test_get_available_datasets_multiple_features(format):
    # just a test that this runs, not checking specific ones
    filename = f"{format}_poly_multiple.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    datasets = get_available_datasets(df)
    assert len(datasets) == 59


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
    assert np.isclose(row.outside_extent_acres, 0)

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
    assert len(urban) == 11
    assert np.allclose(urban, [0, 0, 0, 0, 0, 0, 0, 0, 0, 50.705946, 0])

    assert np.allclose(row[WILDFIRE_RISK["id"]], [0, 0, 0, 0, 0, 50.705946, 0, 0, 0, 0, 0])


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_get_analysis_unit_results_multiple_areas_partial_overlap(format):
    # NOTE: this needs to be updated for each blueprint version; this is just a
    # smoke test that values do not change except during Blueprint version updates

    filename = f"{format}_poly_multiple_partial_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)
    datasets = set(get_available_datasets(df))
    results = await get_analysis_unit_results(df, datasets)

    assert len(results) == len(df)
    for col in ["states", "subregions", "regions", "count", "acres"]:
        assert col in results.columns

    # features cover Southeast, Midwest, both
    assert results.states.fillna("").values.tolist() == ["North Carolina", "", "Missouri"]
    assert results.regions.fillna("").values.tolist() == ["continental", "", "continental"]
    assert results.subregions.fillna("").values.tolist() == ["Atlantic Coastal Plain", "", "Ozarks and Plains"]

    assert results["count"].values.tolist() == [1] * 3
    assert np.allclose(results["acres"], [280.4020, 394.7394, 68.8730])
    assert np.allclose(results["rasterized_acres"], [280.6619, 397.4190, 69.6095])
    assert np.allclose(results["outside_extent_acres"], [0, 397.4190, 0])

    nc_poly = results.iloc[0]
    mn_poly = results.iloc[1]
    mo_poly = results.iloc[2]

    assert np.allclose(nc_poly[BLUEPRINT["id"]], [0, 32.6920, 65.8288, 87.4010, 94.7401])
    assert np.isnan(mn_poly[BLUEPRINT["id"]])
    assert np.allclose(mo_poly[BLUEPRINT["id"]], [3.5583, 52.0403, 14.0109, 0, 0])

    assert np.allclose(nc_poly["f_permeablesurface"], [0, 0, 0, 280.6619])
    assert np.isnan(mn_poly["f_permeablesurface"])
    assert np.allclose(mo_poly["f_permeablesurface"], [0, 0, 5.7823, 63.8272])

    assert np.allclose(nc_poly[SLR_DEPTH["id"]], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 280.6619, 0])
    assert np.isnan(mn_poly[SLR_DEPTH["id"]])
    assert np.allclose(mo_poly[SLR_DEPTH["id"]], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 69.6095, 0])

    assert np.allclose(
        nc_poly[URBAN_BY_DECADE["id"]],
        [42.4773, 42.4773, 42.4773, 42.4773, 42.4773, 42.4773, 42.4773, 42.4773, 42.4773, 238.1845, 0],
    )
    assert np.isnan(mn_poly[URBAN_BY_DECADE["id"]])
    assert np.allclose(
        mo_poly[URBAN_BY_DECADE["id"]],
        [5.5599, 5.5599, 5.5599, 5.5599, 5.5599, 5.5599, 5.5599, 5.5599, 5.5599, 64.049616, 0],
    )


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_get_analysis_unit_results_multiple_areas_partial_overlap_dissolved(format):
    # NOTE: this is just a smoke test to ensure it runs without failure

    filename = f"{format}_poly_multiple_partial_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)
    df = dissolve(df.explode(ignore_index=True))
    datasets = set(get_available_datasets(df))
    results = await get_analysis_unit_results(df, datasets)

    assert results["count"].values.tolist() == [3]
    assert np.allclose(results["acres"], [744.0145])
    assert np.allclose(results["rasterized_acres"], [747.6903])
    assert np.allclose(results["outside_extent_acres"], [397.4190])


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
    assert np.allclose(results["outside_extent_acres"], [0, 0, 0, 0, 0])

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
        [25.1306, 38.9190, 40.6982, 40.6982, 40.6982, 40.6982, 40.6982, 40.6982, 40.6982, 40.6982, 40.6982, 0, 0, 0],
    )

    assert np.allclose(pr_poly[SLR_DEPTH["id"]], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 147.0028, 0, 0])

    pr_slr_proj = pr_poly[SLR_PROJ["id"]]
    assert len(pr_slr_proj) == 5
    assert pr_slr_proj[0]["scenario"] == "l"

    assert np.allclose(
        pr_slr_proj[0]["values"], [0.2625, 0.4921, 0.8202, 1.3123, 2.0669, 3.0512, 4.1995, 5.4462, 6.7913], atol=1e4
    )

    assert np.allclose(
        ga_poly[URBAN_BY_DECADE["id"]],
        [22.9066, 23.1557, 24.1654, 24.3122, 25.5620, 26.68734, 27.2656, 27.5725, 28.0039, 284.2380, 0],
    )

    assert np.allclose(marine_poly[URBAN_BY_DECADE["id"]], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5386.1724])

    assert np.allclose(ga_poly[WILDFIRE_RISK["id"]], [0, 0, 0, 0, 0, 0.6672, 311.5747, 0, 0, 0, 0], atol=1e4)


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_create_xlsx_file_single_area(format):
    filename = f"{format}_poly_small.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    # dissolve like API endpoint
    field = "__analysis_unit"
    df[field] = "all areas"
    df = dissolve(df.explode(ignore_index=True), by=field).set_index(field)

    # representative sample of datasets
    datasets = [
        "blueprint",
        "corridors",
        "f_permeablesurface",
        "t_imperiledamphibiansandreptiles",
        "slr_depth",
        "slr_proj",
        "parcas_poly",
        "protected_areas_poly",
        "urban_by_decade",
        "wildfire_risk",
    ]

    results = await get_analysis_unit_results(df, datasets)
    xlsx = create_report(results, datasets, name="Test area")

    if SAVE_XLSX:
        with open("/tmp/test_create_xlsx_file_single_area.xlsx", "wb") as out:
            _ = out.write(xlsx)

    reader = pd.ExcelFile(BytesIO(xlsx))

    assert len(reader.sheet_names) == len(datasets) + 3
    summary = reader.parse(sheet_name="Summary", skiprows=2)
    assert len(summary) == len(df)

    assert np.allclose(summary["GIS acres"], results.acres)
    assert np.allclose(summary["Analysis acres (rasterized to 30m pixels)"], results.rasterized_acres)
    assert np.allclose(summary["Number of 30m pixels in analysis unit"], results["pixels"])
    assert np.allclose(summary["Number of distinct areas in analysis unit"], results["count"])
    assert summary["State(s)"].tolist() == results.states.tolist()

    details = reader.parse(sheet_name="Data details", skiprows=2)
    assert len(details) == len(datasets)
    assert details["Name"].tolist() == [d["label"] for id, d in REPORT_DATASETS.items() if id in datasets]

    metadata = reader.parse(sheet_name="Analysis metadata", header=None, skiprows=2)
    assert len(metadata) == 3
    assert metadata[1][0] == "Test area"

    header = reader.parse(sheet_name="Blueprint priority", nrows=1)
    assert header.columns[0] == f"Table 3: {BLUEPRINT['caption']}."

    blueprint = reader.parse(sheet_name="Blueprint priority", skiprows=2)
    assert blueprint.columns.tolist() == ["Analysis unit", "Analysis acres"] + blueprint_value_cols[::-1]
    assert np.allclose(blueprint.iloc[0][blueprint_value_cols].values.astype("float64"), results.blueprint.iloc[0])

    corridors = reader.parse(sheet_name="Hubs and corridors", skiprows=2)
    assert corridors.columns.tolist() == ["Analysis unit", "Analysis acres"] + get_value_order[CORRIDORS["id"]](
        corridor_value_cols
    )
    assert np.allclose(corridors.iloc[0][corridor_value_cols].values.astype("float64"), results.corridors.iloc[0])

    indicator_id = "t_imperiledamphibiansandreptiles"
    indicator = INDICATORS_INDEX[indicator_id]
    sheet_name = indicator.get("sheet_name") or indicator["label"]
    indicator_sheet = reader.parse(sheet_name=sheet_name, skiprows=2)
    indicator_value_cols = get_value_columns(indicator["values"])
    assert indicator_sheet.columns.tolist() == ["Analysis unit", "Analysis acres"] + indicator_value_cols[::-1]
    assert np.allclose(
        indicator_sheet.iloc[0][indicator_value_cols].values.astype("float64"), results[indicator_id].iloc[0]
    )

    # this one has an extra row for good / not good condition
    indicator_id = "f_permeablesurface"
    indicator = INDICATORS_INDEX[indicator_id]
    sheet_name = indicator.get("sheet_name") or indicator["label"]
    indicator_header = reader.parse(sheet_name=sheet_name, skiprows=2, nrows=1)
    assert [c for c in indicator_header.columns if "condition" in c] == ["In good condition", "Not in good condition"]
    indicator_sheet = reader.parse(sheet_name=sheet_name, skiprows=3)
    indicator_value_cols = get_value_columns(indicator["values"])
    assert indicator_sheet.columns.tolist() == ["Analysis unit", "Analysis acres"] + indicator_value_cols[::-1]
    assert np.allclose(
        indicator_sheet.iloc[0][indicator_value_cols].values.astype("float64"), results[indicator_id].iloc[0]
    )

    slr_depth = reader.parse(sheet_name="SLR - area flooded by ft of SLR", skiprows=2)
    # only nodata is areas outside counties
    slr_depth_col_ix = list(range(11)) + [12]
    slr_value_cols = np.array(slr_depth_value_cols).take(slr_depth_col_ix).tolist()
    assert slr_depth.columns.tolist() == ["Analysis unit", "Analysis acres"] + slr_value_cols
    assert np.allclose(
        slr_depth.iloc[0][slr_value_cols].values.astype("float64"), results.slr_depth.iloc[0].take(slr_depth_col_ix)
    )

    # no projections here
    slr_proj = reader.parse(sheet_name="SLR - ft of SLR by year", skiprows=2)
    assert slr_proj.columns.tolist() == ["Analysis unit", "Analysis acres"] + slr_proj_value_cols
    assert slr_proj["Has projected SLR?"].tolist() == ["no"]

    parcas_poly = reader.parse(sheet_name="PARCA descriptions", skiprows=2)
    assert parcas_poly.columns.tolist() == ["Analysis unit", "GIS acres", "Overlap acres", "Name", "Description"]
    assert np.allclose(parcas_poly["GIS acres"], results.acres, atol=0.01)
    assert np.allclose(parcas_poly["Overlap acres"], results.acres, atol=0.01)
    assert parcas_poly["Name"].values.tolist() == ["Talladega"]
    assert parcas_poly["Description"].values[0].startswith("Talladega is the")

    protected_areas_poly = reader.parse(sheet_name="Protected areas by name", skiprows=2)
    assert protected_areas_poly.columns.tolist() == ["Analysis unit", "GIS acres", "Overlap acres", "Name", "Owner"]
    assert np.allclose(protected_areas_poly["GIS acres"], results.acres, atol=0.01)
    assert np.allclose(protected_areas_poly["Overlap acres"], [34.55], atol=0.01)
    assert protected_areas_poly["Name"].values.tolist() == ["Talladega National Forest"]
    assert protected_areas_poly["Owner"].values.tolist() == ["USDA Forest Service"]

    urban = reader.parse(sheet_name="Urban growth", skiprows=2)
    assert urban.columns.tolist() == ["Analysis unit", "Analysis acres"] + urban_value_cols
    # last column is nodata, omitted here
    assert np.allclose(urban.iloc[0][urban_value_cols].values.astype("float64"), results.urban_by_decade.iloc[0][:-1])

    wildfire_risk = reader.parse(sheet_name="Wildfire likelihood", skiprows=2)
    assert wildfire_risk.columns.tolist() == ["Analysis unit", "Analysis acres"] + wildfire_risk_value_cols
    assert np.allclose(
        wildfire_risk.iloc[0][wildfire_risk_value_cols].values.astype("float64"), results.wildfire_risk.iloc[0]
    )


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_create_xlsx_file_multiple_areas_partial_overlap(format):
    filename = f"{format}_poly_multiple_partial_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = (
        read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=["Blueprint"], use_arrow=True)
        .to_crs(DATA_CRS)
        .set_index("Blueprint")
    )

    # representative sample of datasets
    datasets = [
        "blueprint",
        "t_imperiledamphibiansandreptiles",
        "slr_depth",
        "slr_proj",
        "parcas_poly",
        "protected_areas_poly",
        "urban_by_decade",
        "wildfire_risk",
    ]

    results = await get_analysis_unit_results(df, datasets)
    xlsx = create_report(results, datasets, name="Test area")

    if SAVE_XLSX:
        with open("/tmp/test_create_xlsx_file_multiple_areas_partial_overlap.xlsx", "wb") as out:
            _ = out.write(xlsx)

    reader = pd.ExcelFile(BytesIO(xlsx))

    assert len(reader.sheet_names) == len(datasets) + 3
    summary = reader.parse(sheet_name="Summary", skiprows=2)
    assert len(summary) == len(df)

    assert np.allclose(summary["GIS acres"], results.acres)
    # when there is partial overlap, we have two rasterized area columns: within and outside
    assert np.allclose(summary["Acres within Southeast data extent (rasterized to 30m pixels)"], results.overlap_acres)
    assert np.allclose(
        summary["Acres outside Southeast data extent (rasterized to 30m pixels)"], results.outside_extent_acres
    )
    assert np.allclose(summary["Number of 30m pixels in analysis unit"], results.pixels)
    assert np.allclose(summary["Number of distinct areas in analysis unit"], results["count"])
    assert summary["State(s)"].tolist() == results.states.tolist()

    details = reader.parse(sheet_name="Data details", skiprows=2)
    assert len(details) == len(datasets)
    assert details["Name"].tolist() == [d["label"] for id, d in REPORT_DATASETS.items() if id in datasets]

    metadata = reader.parse(sheet_name="Analysis metadata", header=None, skiprows=2)
    assert len(metadata) == 3
    assert metadata[1][0] == "Test area"

    blueprint = reader.parse(sheet_name="Blueprint priority", skiprows=2)
    # when we have partial overlap, we have to update the label of the analysis area column
    assert (
        blueprint.columns.tolist()
        == ["Analysis unit", "Acres within Southeast data extent"] + blueprint_value_cols[::-1]
    )
    assert np.allclose(blueprint.iloc[0][blueprint_value_cols].values.astype("float64"), results.blueprint.iloc[0])
    assert np.isclose(blueprint["Acres within Southeast data extent"].iloc[1], 0.0)
    assert np.allclose(blueprint.iloc[2][blueprint_value_cols].values.astype("float64"), results.blueprint.iloc[2])

    indicator_id = "t_imperiledamphibiansandreptiles"
    indicator = INDICATORS_INDEX[indicator_id]
    sheet_name = indicator.get("sheet_name") or indicator["label"]
    indicator_sheet = reader.parse(sheet_name=sheet_name, skiprows=2)
    indicator_value_cols = get_value_columns(indicator["values"])
    assert (
        indicator_sheet.columns.tolist()
        == ["Analysis unit", "Acres within Southeast data extent"] + indicator_value_cols[::-1]
    )
    assert np.allclose(
        indicator_sheet.iloc[0][indicator_value_cols].values.astype("float64"), results[indicator_id].iloc[0]
    )
    assert np.isclose(indicator_sheet["Acres within Southeast data extent"].iloc[1], 0.0)
    assert np.allclose(
        indicator_sheet.iloc[2][indicator_value_cols].values.astype("float64"), results[indicator_id].iloc[2]
    )

    slr_depth = reader.parse(sheet_name="SLR - area flooded by ft of SLR", skiprows=2)
    slr_depth_col_ix = list(range(11)) + [12]
    slr_value_cols = np.array(slr_depth_value_cols).take(slr_depth_col_ix).tolist()
    assert slr_depth.columns.tolist() == ["Analysis unit", "Acres within Southeast data extent"] + slr_value_cols
    assert np.allclose(
        slr_depth.iloc[0][slr_value_cols].values.astype("float64"),
        results.slr_depth.iloc[0].take(list(range(11)) + [12]),
    )

    # no projections here
    slr_proj = reader.parse(sheet_name="SLR - ft of SLR by year", skiprows=2)
    assert slr_proj.columns.tolist() == ["Analysis unit", "Acres within Southeast data extent"] + slr_proj_value_cols
    assert slr_proj["Has projected SLR?"].tolist() == ["no"] * 3

    parcas_poly = reader.parse(sheet_name="PARCA descriptions", skiprows=2)
    assert parcas_poly.columns.tolist() == ["Analysis unit", "GIS acres", "Overlap acres", "Name", "Description"]
    assert np.allclose(parcas_poly["GIS acres"], results.acres, atol=0.01)
    assert np.allclose(parcas_poly["Overlap acres"], [280.40, 0, 0], atol=0.01)
    assert parcas_poly["Name"].values.tolist() == ["Sandhills"] + ["no PARCAs at this location"] * 2

    # protected_areas_poly = reader.parse("")
    protected_areas_poly = reader.parse(sheet_name="Protected areas by name", skiprows=2)
    assert protected_areas_poly.columns.tolist() == ["Analysis unit", "GIS acres", "Overlap acres", "Name", "Owner"]
    assert protected_areas_poly["Analysis unit"].tolist() == ["Southeast"] * 3 + ["Midwest", "Southeast,Midwest"]
    assert np.allclose(protected_areas_poly["GIS acres"], [280.40, 280.40, 280.40, 394.74, 68.87], atol=0.01)
    assert np.allclose(protected_areas_poly["Overlap acres"], [20.48, 165.11, 167.83, 0, 0], atol=0.01)
    assert (
        protected_areas_poly["Name"].values.tolist()
        == ["Bones Fork Pine and Shrub Community Registered Heritage Area"]
        + ["Sandhills Game Land"] * 2
        + ["no protected areas at this location"] * 2
    )
    assert protected_areas_poly["Owner"].fillna("").values.tolist() == [
        "State Fish and Wildlife",
        "NC Wildlife Resources Commission",
        "State Fish and Wildlife",
        "",
        "",
    ]

    urban = reader.parse(sheet_name="Urban growth", skiprows=2)
    assert urban.columns.tolist() == ["Analysis unit", "Acres within Southeast data extent"] + urban_value_cols
    # last column is nodata, omitted here
    assert np.allclose(urban.iloc[0][urban_value_cols].values.astype("float64"), results.urban_by_decade.iloc[0][:-1])
    assert np.isclose(urban["Acres within Southeast data extent"].iloc[1], 0.0)
    assert np.allclose(urban.iloc[2][urban_value_cols].values.astype("float64"), results.urban_by_decade.iloc[2][:-1])

    wildfire_risk = reader.parse(sheet_name="Wildfire likelihood", skiprows=2)
    assert (
        wildfire_risk.columns.tolist()
        == ["Analysis unit", "Acres within Southeast data extent"] + wildfire_risk_value_cols
    )
    assert np.allclose(
        wildfire_risk.iloc[0][wildfire_risk_value_cols].values.astype("float64"), results.wildfire_risk.iloc[0]
    )
    assert np.isclose(wildfire_risk["Acres within Southeast data extent"].iloc[1], 0.0)
    assert np.allclose(
        wildfire_risk.iloc[2][wildfire_risk_value_cols].values.astype("float64"), results.wildfire_risk.iloc[2]
    )


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_create_xlsx_file_multiple_areas(format):
    filename = f"{format}_poly_multiple.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=["Region"], use_arrow=True).to_crs(
        DATA_CRS
    )
    df = dissolve(df.explode(ignore_index=True), by="Region").set_index("Region")

    num_features = len(df)

    # representative sample of datasets
    datasets = [
        "blueprint",
        "t_imperiledamphibiansandreptiles",
        "slr_depth",
        "slr_proj",
        "parcas_poly",
        "protected_areas_poly",
        "urban_by_decade",
        "wildfire_risk",
    ]

    results = await get_analysis_unit_results(df, datasets)
    xlsx = create_report(results, datasets, name="Test area")

    if SAVE_XLSX:
        with open("/tmp/test_create_xlsx_file_multiple_areas.xlsx", "wb") as out:
            _ = out.write(xlsx)

    reader = pd.ExcelFile(BytesIO(xlsx))

    assert len(reader.sheet_names) == len(datasets) + 3
    summary = reader.parse(sheet_name="Summary", skiprows=2)
    assert len(summary) == len(df)
    assert np.allclose(summary["GIS acres"], results.acres)
    assert np.allclose(summary["Analysis acres (rasterized to 30m pixels)"], results.rasterized_acres)
    assert np.allclose(summary["Number of 30m pixels in analysis unit"], results["pixels"])
    assert np.allclose(summary["Number of distinct areas in analysis unit"], results["count"])
    assert summary["State(s)"].tolist() == results.states.tolist()

    details = reader.parse(sheet_name="Data details", skiprows=2)
    assert len(details) == len(datasets)
    assert details["Name"].tolist() == [d["label"] for id, d in REPORT_DATASETS.items() if id in datasets]

    metadata = reader.parse(sheet_name="Analysis metadata", header=None, skiprows=2)
    assert len(metadata) == 3
    assert metadata[1][0] == "Test area"

    blueprint = reader.parse(sheet_name="Blueprint priority", skiprows=2)
    assert blueprint.columns.tolist() == ["Analysis unit", "Analysis acres"] + blueprint_value_cols[::-1]
    assert np.allclose(results.blueprint.iloc[0], blueprint.iloc[0][blueprint_value_cols].values.astype("float64"))
    for i in range(num_features):
        assert np.allclose(blueprint.iloc[i][blueprint_value_cols].values.astype("float64"), results.blueprint.iloc[i])

    indicator_id = "t_imperiledamphibiansandreptiles"
    indicator = INDICATORS_INDEX[indicator_id]
    sheet_name = indicator.get("sheet_name") or indicator["label"]
    indicator_sheet = reader.parse(sheet_name=sheet_name, skiprows=2)
    indicator_value_cols = get_value_columns(indicator["values"])
    assert (
        indicator_sheet.columns.tolist()
        == ["Analysis unit", "Analysis acres", outside_data_extent_col] + indicator_value_cols[::-1]
    )
    for i in range(num_features):
        assert np.allclose(
            indicator_sheet.iloc[i][indicator_value_cols].values.astype("float64"), results[indicator_id].iloc[i]
        )

    slr_depth = reader.parse(sheet_name="SLR - area flooded by ft of SLR", skiprows=2)
    slr_depth_col_ix = [13] + list(range(13))
    slr_value_cols = np.array(slr_depth_value_cols).take(slr_depth_col_ix).tolist()
    assert slr_depth.columns.tolist() == ["Analysis unit", "Analysis acres"] + slr_value_cols
    for i in range(num_features):
        expected = results.slr_depth.iloc[i].take(slr_depth_col_ix)
        # area outside SLR is dynamically calculated as areas within the extent but with no SLR acres
        outside = results.overlap_acres.iloc[i] - expected.sum()
        if outside > 0:
            expected[0] = outside

        assert np.allclose(slr_depth.iloc[i][slr_value_cols].values.astype("float64"), expected)

    parcas_poly = reader.parse(sheet_name="PARCA descriptions", skiprows=2)
    assert parcas_poly.columns.tolist() == ["Analysis unit", "GIS acres", "Overlap acres", "Name", "Description"]
    assert np.allclose(parcas_poly["GIS acres"], results.acres, atol=0.01)
    assert np.allclose(parcas_poly["Overlap acres"], [0] * 3, atol=0.01)
    assert parcas_poly["Name"].values.tolist() == ["no PARCAs at this location"] * 3

    protected_areas_poly = reader.parse(sheet_name="Protected areas by name", skiprows=2)
    assert protected_areas_poly.columns.tolist() == ["Analysis unit", "GIS acres", "Overlap acres", "Name", "Owner"]
    assert protected_areas_poly["Analysis unit"].tolist() == ["caribbean"] + ["continental"] * 3 + ["marine"]
    assert np.allclose(protected_areas_poly["GIS acres"], [147.20, 452.72, 452.72, 452.72, 5386.10], atol=0.01)
    assert np.allclose(protected_areas_poly["Overlap acres"], [66.03, 27.80, 30.39, 40.56, 0], atol=0.01)
    assert protected_areas_poly["Name"].values.tolist() == ["Área Natural Protegida Río Encantado"] + [
        "Crystal River Preserve State Park"
    ] * 2 + ["St. Martins Marsh Aquatic Preserve", "no protected areas at this location"]
    assert protected_areas_poly["Owner"].fillna("").values.tolist() == [
        "Para la Naturaleza",
        "",
        "Trustees of the Internal Improvement Trust Fund",
        "",
        "",
    ]

    urban = reader.parse(sheet_name="Urban growth", skiprows=2)
    assert urban.columns.tolist() == ["Analysis unit", "Analysis acres", outside_data_extent_col] + urban_value_cols
    compare_cols = [outside_data_extent_col] + urban_value_cols
    for i in range(num_features):
        assert np.allclose(
            urban.iloc[i][compare_cols].values.astype("float64"),
            # last value is nodata, shuffled to the beginning
            results.urban_by_decade.iloc[i].take([len(urban_value_cols)] + list(range(len(urban_value_cols)))),
        )

    wildfire_risk = reader.parse(sheet_name="Wildfire likelihood", skiprows=2)
    assert (
        wildfire_risk.columns.tolist()
        == ["Analysis unit", "Analysis acres", outside_data_extent_col] + wildfire_risk_value_cols
    )
    for i in range(num_features):
        assert np.allclose(
            wildfire_risk.iloc[i][wildfire_risk_value_cols].values.astype("float64"), results.wildfire_risk.iloc[i]
        )
