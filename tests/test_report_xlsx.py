import pytest
from pyogrio import read_dataframe

from analysis.constants import (
    DATA_CRS,
    BLUEPRINT,
    INDICATORS,
    CORRIDORS,
    PARCAS,
    PROTECTED_AREAS,
    SLR_DEPTH,
    SLR_PROJ,
    URBAN_BY_DECADE,
    WILDFIRE_RISK,
)
from analysis.lib.stats.prescreen import get_available_datasets


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

    assert len(datasets) == 30

    expected_datasets = [
        BLUEPRINT["id"],
        CORRIDORS["id"],
        PARCAS["id"],
        PROTECTED_AREAS["id"],
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
