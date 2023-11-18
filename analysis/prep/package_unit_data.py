"""
Extract summary unit data created using tabulate_summary_units.py and
postprocess into structure needed for vector tiles.

The following code compacts values in a few ways.  These were tested against
versions of the vector tiles that retained individual integer columns, and the
compacted version here ended up being smaller.

Blueprint is encoded to a pipe-delimited series of percents * 10
(to preserve 1 decimal place in frontend), omitting any 0 values:
<value0>|<value1>|...

Time-series values (SLR, urban) were converted to percent * 10 then delta encoded
into caret-delimited strings:
<baseline>^<delta_value0>^<delta_value1>

Areas where there were no values present were converted to empty strings.  Areas
where there was no change from the baseline just include the baseline.

Values that could have multiple key:value entries (ownership, protection) are dictionary-encoded:
FED:<fed_%>,LOC:<loc_%>,...
"""

from pathlib import Path
from itertools import product
import warnings

import geopandas as gp
import pandas as pd

from analysis.constants import (
    GEO_CRS,
    CORRIDORS,
    BLUEPRINT,
    INDICATORS,
    SLR_DEPTH_BINS,
    SLR_NODATA_COLS,
    NLCD_INDEXES,
    NLCD_YEARS,
    URBAN_YEARS,
)
from analysis.lib.attribute_encoding import encode_values, delta_encode_values
from analysis.lib.stats.ownership import get_lta_search_info

# ignore future warning about concat; this is because we join to empty data frames
# with the full summary unit index
warnings.filterwarnings(
    "ignore",
    message=".*The behavior of array concatenation with empty entries is deprecated.*",
)


def encode_ownership_protection(df, field):
    """Calculate dictionary-encoded values for land ownership or protection

    For example:
        FED:<fed_percent * 10>,LOC: <loc_percent * 10>, ...

    Parameters
    ----------
    df : DataFrame
        must include field, "acres", "total_acres"
    field : str
        name of field to dictionary encode

    Returns
    -------
    Series
    """
    # calculate percent * 10% (percent at 1 decimal place)
    df["percent"] = (1000 * df.acres / df.total_acres).round().astype("uint")
    # drop anything that rounded to 0%
    df = df.loc[df.percent > 0].copy()

    return pd.Series(
        (df[field] + ":" + df.percent.astype("str"))
        .groupby(level=0)
        .apply(lambda r: ",".join(v for v in r))
    )


def encode_blueprint(df):
    """Encode Blueprint, Corridors, and Indicators

    Parameters
    ----------
    df : DataFrame
        must include "rasterized_acres"

    Returns
    -------
    DataFrame
    """
    blueprint_cols = [f"blueprint_{v['value']}" for v in BLUEPRINT]
    blueprint = encode_values(
        df[blueprint_cols],
        df.rasterized_acres,
        1000,
    ).rename("blueprint")

    corridor_cols = [f"corridors_{v['value']}" for v in CORRIDORS]
    corridors = encode_values(
        df[corridor_cols],
        df.rasterized_acres,
        1000,
    ).rename("corridors")

    # only check areas of indicators actually present in summaries for unit type
    check_indicators = {
        e["id"]: e for e in INDICATORS if f"{e['id']}_outside" in df.columns
    }

    # NOTE: serialized indicator ID is its position in full indicators list
    # join to empty data frame to have full index
    indicators = df[[]]
    for i, id in enumerate([i["id"] for i in INDICATORS]):
        if id not in check_indicators:
            continue

        indicator = check_indicators[id]
        values = indicator["values"]
        cols = [f"{id}_value_{v['value']}" for v in values]
        indicator_acres = df[cols]
        total_acres = indicator_acres.sum(axis=1)

        # drop any entries where they are not present or are only 0 values for
        # indicators with 0 values
        indicator_acres = indicator_acres.loc[
            (total_acres > 0)
            & ~(
                (values[0]["value"] == 0) & (indicator_acres[cols[1:]].max(axis=1) == 0)
            )
        ]

        if len(indicator_acres) == 0:
            continue

        indicator_acres = indicator_acres.join(df.rasterized_acres)
        encoded = encode_values(
            indicator_acres[cols], indicator_acres.rasterized_acres, 1000
        ).rename(i)

        indicators = indicators.join(encoded, how="left")

    indicators = (
        indicators.fillna("")
        .apply(lambda row: ",".join((f"{k}:{v}" for k, v in row.items() if v)), axis=1)
        .rename("indicators")
    )

    return pd.DataFrame(blueprint).join(corridors).join(indicators)


data_dir = Path("data")
out_dir = data_dir / "for_tiles"
out_dir.mkdir(exist_ok=True, parents=True)

subregions = (
    pd.read_feather(
        data_dir / "inputs/boundaries/subregions.feather",
        columns=["value", "subregion"],
    )
    .set_index("subregion")
    .value.to_dict()
)


###################################################################
### HUC12
###################################################################

results_dir = data_dir / "results/huc12"

print("Reading HUC12 units...")
huc12 = (
    gp.read_feather(
        data_dir / "inputs/summary_units" / "huc12.feather",
        columns=[
            "id",
            "geometry",
            "name",
            "subregions",
            "acres",
            "rasterized_acres",
            "outside_se",
            "minx",
            "miny",
            "maxx",
            "maxy",
        ],
    )
    .set_index("id")
    .to_crs(GEO_CRS)
)
huc12["type"] = "subwatershed"
huc12["subregions"] = huc12.subregions.apply(
    lambda x: ",".join(str(subregions[s]) for s in x)
)

### Encode center / radius as x,y,radius(miles)
center, lta_search_radius = get_lta_search_info(
    huc12[["minx", "miny", "maxx", "maxy"]].values
)
center = center.round(5)
lta_search_df = pd.DataFrame(center, index=huc12.index, columns=["x", "y"]).astype(
    "str"
)
lta_search_df["miles"] = lta_search_radius.astype("str")
lta_search = lta_search_df.apply(lambda row: ",".join(row.values), axis=1).rename(
    "lta_search"
)


### Southeast Blueprint
# convert integer percents * 10, and pack into pipe-delimited string
print("Encoding Southeast Blueprint...")
blueprint_results = (
    pd.read_feather(results_dir / "blueprint.feather")
    .set_index("id")
    .join(huc12.rasterized_acres)
)
blueprint = encode_blueprint(blueprint_results)

### SLR Depth
# delta encode percent * 10; dict encode nodata values
print("Encoding SLR depth and projections...")
slr_results = (
    pd.read_feather(results_dir / "slr.feather")
    .set_index("id")
    .join(huc12.rasterized_acres)
)
depth_cols = [f"depth_{d}" for d in SLR_DEPTH_BINS]

slr_depth = delta_encode_values(
    slr_results[depth_cols], huc12.rasterized_acres.loc[slr_results.index], 1000
).rename("slr_depth")

slr_nodata = encode_values(
    slr_results[SLR_NODATA_COLS], huc12.rasterized_acres.loc[slr_results.index], 1000
).rename("slr_nodata")

slr = pd.DataFrame(slr_depth).join(slr_nodata)


### Urban
# Combine NLCD 2001-2021 with future urban 2030-2060
print("Encoding urban...")
urban_indexes = [i for i in NLCD_INDEXES if "Developed" in NLCD_INDEXES[i]["label"]]
cols = ["id"] + [f"{year}_{i}" for year, i in product(NLCD_YEARS, urban_indexes)]
nlcd_results = pd.read_feather(results_dir / "nlcd.feather", columns=cols).set_index(
    "id"
)

for year in NLCD_YEARS:
    cols = [f"{year}_{i}" for i in urban_indexes]
    nlcd_results[str(year)] = nlcd_results[cols].sum(axis=1)

nlcd_results = nlcd_results[[str(year) for year in NLCD_YEARS]]

# UI is limited to 2030 - 2060
cols = ["id"] + [f"urban_proj_{year}" for year in URBAN_YEARS[:4]]
urban_results = pd.read_feather(results_dir / "urban.feather", columns=cols).set_index(
    "id"
)

urban_results = nlcd_results.join(urban_results).fillna(0)

urban = delta_encode_values(
    urban_results, huc12.rasterized_acres.loc[urban_results.index], 1000
).rename("urban")

### Ownership / protection
# Dictionary encode ownership and protection
print("Encoding ownership / protection...")
ownership_results = (
    pd.read_feather(results_dir / "ownership.feather")
    .set_index("id")
    .join(huc12.acres.rename("total_acres"), how="inner")
)
ownership = encode_ownership_protection(ownership_results, "Own_Type").rename(
    "ownership"
)

protection_results = (
    pd.read_feather(results_dir / "protection.feather")
    .set_index("id")
    .join(huc12.acres.rename("total_acres"), how="inner")
)
protection = encode_ownership_protection(protection_results, "GAP_Sts").rename(
    "protection"
)


huc12 = (
    huc12[["geometry", "name", "subregions", "type"]]
    .join(huc12[["acres", "rasterized_acres", "outside_se"]].round().astype("int"))
    .join(lta_search, how="left")
    .join(blueprint, how="left")
    .join(slr, how="left")
    .join(urban, how="left")
    .join(ownership, how="left")
    .join(protection, how="left")
)


###################################################################
### Marine
###################################################################

results_dir = data_dir / "results/marine_hex"

print("--------------------------------")
print("Reading marine_hex...")
marine = (
    gp.read_feather(
        data_dir / "inputs/summary_units/marine_hex.feather",
        columns=[
            "id",
            "geometry",
            "name",
            "subregions",
            "acres",
            "rasterized_acres",
            "outside_se",
        ],
    )
    .set_index("id")
    .to_crs(GEO_CRS)
)
marine["type"] = "marine hex"
marine["subregions"] = marine.subregions.apply(
    lambda x: ",".join(str(subregions[s]) for s in x)
)


### Southeast Blueprint
# convert integer percents * 10, and pack into pipe-delimited string
print("Encoding Southeast Blueprint...")
blueprint_results = (
    pd.read_feather(results_dir / "blueprint.feather")
    .set_index("id")
    .join(marine.rasterized_acres)
)
blueprint = encode_blueprint(blueprint_results)


### Ownership / protection
# Dictionary encode ownership and protection

print("Encoding ownership / protection...")
ownership_results = (
    pd.read_feather(results_dir / "ownership.feather")
    .set_index("id")
    .join(marine.acres.rename("total_acres"), how="inner")
)
ownership = encode_ownership_protection(ownership_results, "Own_Type").rename(
    "ownership"
)

protection_results = (
    pd.read_feather(results_dir / "protection.feather")
    .set_index("id")
    .join(marine.acres.rename("total_acres"), how="inner")
)
protection = encode_ownership_protection(protection_results, "GAP_Sts").rename(
    "protection"
)

marine = (
    marine[["geometry", "name", "subregions", "type"]]
    .join(marine[["acres", "rasterized_acres", "outside_se"]].round().astype("int"))
    .join(blueprint, how="left")
    .join(ownership, how="left")
    .join(protection, how="left")
)

##################################

### Merge HUC12 and Marine hexes into single dataframe

out = pd.concat(
    [huc12.reset_index(), marine.reset_index()], ignore_index=True, sort=False
).reset_index(drop=True)


for col in (
    [
        "lta_search",
        "ownership",
        "protection",
        "urban",
    ]
    + blueprint.columns.tolist()
    + slr.columns.tolist()
):
    out[col] = out[col].fillna("")


out.to_feather(out_dir / "summary_units.feather")
