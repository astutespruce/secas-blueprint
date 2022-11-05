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

import geopandas as gp
import numpy as np
import pandas as pd

from analysis.constants import (
    GEO_CRS,
    CORRIDORS,
    INPUTS,
    BLUEPRINT,
    INDICATORS,
    SLR_DEPTH_BINS,
    SLR_NODATA_COLS,
    SLR_PROJ_SCENARIOS,
    SLR_YEARS,
    URBAN_YEARS,
)
from analysis.lib.attribute_encoding import encode_values, delta_encode_values
from analysis.lib.stats.ownership import get_lta_search_info


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


def encode_base_blueprint(df):
    """Encode Base Blueprint, Corridors, and Indicators

    Parameters
    ----------
    df : DataFrame
        must include "rasterized_acres"

    Returns
    -------
    DataFrame
    """
    priority_cols = [f"priority_{v['value']}" for v in INPUTS["base"]["values"]]
    base_blueprint = encode_values(
        df[priority_cols],
        df.rasterized_acres,
        1000,
    ).rename("base")

    corridor_cols = [f"corridors_{v['value']}" for v in CORRIDORS]
    corridors = encode_values(
        df[corridor_cols],
        df.rasterized_acres,
        1000,
    ).rename("corridors")

    # only check areas of indicators actually present in summaries for unit type
    check_indicators = {
        e["id"]: e for e in INDICATORS["base"] if f"{e['id']}_outside" in df.columns
    }

    # Create a DataFrame with one encoded column per indicator
    indicators = df[[]]

    # serialized indictor ID is its position in full indicators list
    for i, id in enumerate([i["id"] for i in INDICATORS["base"]]):
        if not id in check_indicators:
            continue

        indicator = check_indicators[id]
        values = indicator["values"]
        cols = [f"{id}_value_{v['value']}" for v in values]
        indicator_acres = df[cols]
        total_acres = indicator_acres.sum(axis=1)

        indicator_acres = indicator_acres.loc[total_acres > 0]

        # NOTE: we always keep the indicator even if only 0 values are present

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
        .rename("base_indicators")
    )

    return pd.DataFrame(base_blueprint).join(corridors).join(indicators)


data_dir = Path("data")
out_dir = data_dir / "for_tiles"
out_dir.mkdir(exist_ok=True, parents=True)

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
            "acres",
            "rasterized_acres",
            "outside_se",
            "input_id",
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

blueprint_cols = [f"value_{v['value']}" for v in BLUEPRINT]
blueprint = encode_values(
    blueprint_results[blueprint_cols], blueprint_results.rasterized_acres, 1000
).rename("blueprint")


# Base Blueprint
print("Encoding Base Blueprint...")
base_results = (
    pd.read_feather(results_dir / "base.feather")
    .set_index("id")
    .join(huc12.rasterized_acres)
)
base = encode_base_blueprint(base_results)

### Caribbean
# Dictionary encode <priority>:<percent>, only for priorities > 0
print("Encoding Caribbean LCD...")


def encode_caribbean_priorities(row):
    row = row.dropna().astype("uint")
    return ",".join([f"{row.index[i]}:{v}" for i, v in enumerate(row.values)])


cols = [f"priority_{v['value']}" for v in INPUTS["car"]["values"]]
col_map = {f"priority_{v['value']}": v["value"] for v in INPUTS["car"]["values"]}

car_df = (
    pd.read_feather(results_dir / "car.feather")
    .set_index("id")
    .join(huc12.rasterized_acres)
)

# convert to percent * 10 and fill with nan so that we can drop them at row level
car_df[cols] = (1000 * car_df[cols].divide(car_df.rasterized_acres, axis=0)).round()
for col in cols:
    ix = car_df[col] == 0
    car_df.loc[ix, col] = np.nan

# rename columns to integer priority to make encoding easier
caribbean = (
    car_df[cols].rename(columns=col_map).apply(encode_caribbean_priorities, axis=1)
).rename("car")

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

# ### SLR scenario projections
# # TODO: not currently used
# # delta encode feet * 10 (1 decimal place) by ascending scenario; scenarios
# # are comma-delimited
# proj_results = None
# # div is just so we can reuse delta encoding logic and divide everything by 1
# slr_proj_results = slr_results.dropna()
# div = np.ones((len(slr_proj_results),))
# for scenario in SLR_PROJ_SCENARIOS:
#     proj_cols = [f"{year}_{scenario}" for year in SLR_YEARS]
#     proj = delta_encode_values(slr_proj_results[proj_cols], div, 10).rename(
#         f"slr_proj_{scenario}"
#     )

#     if proj_results is None:
#         proj_results = pd.DataFrame(proj)
#     else:
#         proj_results = proj_results.join(proj)

# slr_proj = proj_results.apply(lambda row: ",".join(row), axis=1).rename("slr_proj")

# slr = pd.DataFrame(slr_depth).join(slr_nodata).join(slr_proj)


slr = pd.DataFrame(slr_depth).join(slr_nodata)


### Urban
# delta encode urban 2019 and future projections
print("Encoding urban...")
cols = ["id", "urban_2019"] + [f"urban_proj_{year}" for year in URBAN_YEARS]
urban_results = pd.read_feather(results_dir / "urban.feather", columns=cols).set_index(
    "id"
)
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
    huc12[["geometry", "name", "input_id", "type"]]
    .join(huc12[["acres", "rasterized_acres", "outside_se"]].round().astype("int"))
    .join(lta_search, how="left")
    .join(blueprint, how="left")
    .join(base, how="left")
    .join(caribbean, how="left")
    .join(slr, how="left")
    .join(urban, how="left")
    .join(ownership, how="left")
    .join(protection, how="left")
)


###################################################################
### Marine
###################################################################

results_dir = data_dir / "results/marine_blocks"

print("--------------------------------")
print("Reading marine_blocks...")
marine = (
    gp.read_feather(
        data_dir / "inputs/summary_units/marine_blocks.feather",
        columns=[
            "id",
            "geometry",
            "name",
            "acres",
            "rasterized_acres",
            "outside_se",
            "input_id",
        ],
    )
    .set_index("id")
    .to_crs(GEO_CRS)
)
marine["type"] = "marine lease block"


### Southeast Blueprint
# convert integer percents * 10, and pack into pipe-delimited string
print("Encoding Southeast Blueprint...")
blueprint_results = (
    pd.read_feather(results_dir / "blueprint.feather")
    .set_index("id")
    .join(marine.rasterized_acres)
)

blueprint_cols = [f"value_{v['value']}" for v in BLUEPRINT]
blueprint = encode_values(
    blueprint_results[blueprint_cols], blueprint_results.rasterized_acres, 1000
).rename("blueprint")


### Base Blueprint
print("Encoding Base Blueprint...")
base_results = (
    pd.read_feather(results_dir / "base.feather")
    .set_index("id")
    .join(marine.rasterized_acres)
)
base = encode_base_blueprint(base_results)


### Florida Marine Blueprint
print("Encoding Florida Marine Blueprint...")
flm_results = (
    pd.read_feather(results_dir / "flm.feather")
    .set_index("id")
    .join(marine.rasterized_acres)
)
cols = [f"priority_{v['value']}" for v in INPUTS["flm"]["values"]]
flm = encode_values(flm_results[cols], flm_results.rasterized_acres, 1000).rename("flm")


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
    marine[["geometry", "name", "input_id", "type"]]
    .join(marine[["acres", "rasterized_acres", "outside_se"]].round().astype("int"))
    .join(blueprint, how="left")
    .join(base, how="left")
    .join(flm, how="left")
    .join(ownership, how="left")
    .join(protection, how="left")
)

##################################

### Merge HUC12 and Marine Blocks into single dataframe

out = pd.concat(
    [huc12.reset_index(), marine.reset_index()], ignore_index=True, sort=False
).reset_index(drop=True)


for col in (
    [
        "lta_search",
        "car",
        "flm",
        "ownership",
        "protection",
        "urban",
    ]
    + base.columns.tolist()
    + slr.columns.tolist()
):
    out[col] = out[col].fillna("")


out.to_feather(out_dir / "summary_units.feather")
