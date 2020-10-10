"""
Extract summary unit data created using tabulate_area.py and postprocess to join
into vector tiles.

The following code compacts values in a few ways.  These were tested against
versions of the vector tiles that retained individual integer columns, and the
compacted version here ended up being smaller.

Blueprint and inputs were encoded to a pipe-delimited series of percents * 10
(to preserve 1 decimal place in frontend), omitting any 0 values:
<value0>|<value1>|...

Time-series values (SLR, urban) were converted to percent * 10 then delta encoded
into caret-delimited strings:
<baseline>^<delta_value0>^<delta_value1>

Areas where there were no values present were converted to empty strings.  Areas
where there was no change from the baseline just include the baseline.


Values that could have multiple key:value entries (ownership, protection) are dictionary-encoded:
FED:<fed_%>,LOC:<loc_%>,...

Counties are encoded as:
<FIPS>:state|county,<FIPS>|...


"""

from pathlib import Path
import csv

import numpy as np
import pandas as pd


from analysis.constants import URBAN_YEARS, DEBUG, INPUTS, CHAT_CATEGORIES
from analysis.lib.attribute_encoding import encode_values, delta_encode_values


data_dir = Path("data")
results_dir = data_dir / "results"
out_dir = data_dir / "for_tiles"

### HUC12
working_dir = results_dir / "huc12"

print("Reading HUC12 units...")
huc12 = pd.read_feather(
    data_dir / "inputs/summary_units" / "huc12.feather", columns=["id", "name", "acres"]
).set_index("id")
huc12.acres = huc12.acres.round().astype("uint")
huc12["type"] = "subwatershed"


print("Encoding HUC12 Blueprint & input values...")
blueprint = pd.read_feather(results_dir / "huc12/blueprint.feather").set_index("id")

# Unpack blueprint values
blueprint_cols = [c for c in blueprint.columns if c.startswith("blueprint_")]
input_cols = [c for c in blueprint.columns if c.startswith("inputs_")]
blueprint_total = blueprint[blueprint_cols].sum(axis=1).rename("blueprint_total")
shape_mask = blueprint.shape_mask

# convert Blueprint to integer percents * 10, and pack into pipe-delimited string
blueprint_percent = encode_values(blueprint[blueprint_cols], shape_mask, 1000).rename(
    "blueprint"
)

# convert input areas to integer percents * 10, and pack into pipe-delimited string
inputs_percent = encode_values(blueprint[input_cols], shape_mask, 1000).rename("inputs")


blueprint_df = (
    blueprint[["shape_mask"]]
    .round()
    .astype("uint")
    .join(blueprint_total.round().astype("uint"))
    .join(blueprint_percent)
    .join(inputs_percent)
)
blueprint_df.blueprint_total = blueprint_df.blueprint_total.fillna(0)
blueprint_df = blueprint_df.fillna("")


### Convert SLR and urban to integer acres, and delta encode
print("Encoding SLR values...")
slr = (
    pd.read_feather(working_dir / "slr.feather").set_index("id").round().astype("uint")
)

slr = delta_encode_values(
    slr.drop(columns=["shape_mask"]), slr.shape_mask, 1000
).rename("slr")


print("Encoding urban values...")
urban = (
    pd.read_feather(working_dir / "urban.feather")
    .set_index("id")
    .round()
    .astype("uint")
)

urban = delta_encode_values(
    urban.drop(columns=["shape_mask"]), urban.shape_mask, 1000
).rename("urban")

### Dictionary encode ownership and protection for each HUC12:
# FED:<fed_acres>,LOC: <loc_acres>, ...
ownership = (
    pd.read_feather(working_dir / "ownership.feather")
    .set_index("id")
    .join(huc12.acres.rename("total_acres"))
)

ownership["percent"] = (
    (1000 * ownership.acres / ownership.total_acres).round().astype("uint")
)
# drop anything at 0%
ownership = ownership.loc[ownership.percent > 0].copy()

ownership = pd.Series(
    (ownership.Own_Type + ":" + ownership.percent.astype("str"))
    .groupby(level=0)
    .apply(lambda r: ",".join(v for v in r)),
    name="ownership",
)

protection = (
    pd.read_feather(working_dir / "protection.feather")
    .set_index("id")
    .join(huc12.acres.rename("total_acres"))
)

protection["percent"] = (
    (1000 * protection.acres / protection.total_acres).round().astype("uint")
)
# drop anything at 0%
protection = protection.loc[protection.percent > 0].copy()


protection = pd.Series(
    (protection.GAP_Sts.astype("str") + ":" + protection.percent.astype("str"))
    .groupby(level=0)
    .apply(lambda r: ",".join(v for v in r)),
    name="protection",
)

### Convert counties into a dict encoded string per HUC12,
# dividing state and county by "|" and entries by ","
# <FIPS>:state|county,
counties = pd.Series(
    pd.read_feather(working_dir / "counties.feather")
    .set_index("id")
    .apply(
        lambda r: ":".join([r.values[0], "|".join((str(v) for v in r.values[1:]))]),
        axis=1,
    )
    .groupby(level=0)
    .apply(lambda g: ",".join((v for v in g.values))),
    name="counties",
)

huc12 = (
    huc12.join(blueprint_df, how="left")
    .join(slr, how="left")
    .join(urban, how="left")
    .join(ownership, how="left")
    .join(protection, how="left")
    .join(counties, how="left")
)

huc12.blueprint_total = huc12.blueprint_total.fillna(0)


### Convert CHAT
for state in ["ok", "tx"]:
    chat = (
        pd.read_feather(working_dir / f"{state}chat.feather")
        .set_index("id")
        .join(huc12.acres)
    )
    # fields = ["chatrank"] + [e["id"] for e in INPUTS[f"{state}chat"]["indicators"]]

    # extract CHAT overall rank
    rank_fields = [f"chatrank_{i}" for i in CHAT_CATEGORIES]
    for field in rank_fields:
        if not field in chat.columns:
            chat[field] = 0

    chat_rank_percent = encode_values(chat[rank_fields], chat.acres, 1000).rename(
        f"{state}chatrank"
    )

    huc12 = huc12.join(chat_rank_percent, how="left")


huc12 = huc12.fillna("")

### Read in marine data
working_dir = results_dir / "marine_blocks"

print("Reading marine_blocks...")
marine = pd.read_feather(
    data_dir / "inputs/summary_units/marine_blocks.feather",
    columns=["id", "name", "acres"],
).set_index("id")
marine.acres = marine.acres.round().astype("uint")
marine = marine.loc[marine.acres > 0].dropna()
marine["type"] = "marine lease block"


print("Encoding marine Blueprint & inputs...")
blueprint = (
    pd.read_feather(working_dir / "blueprint.feather")
    .rename(columns={"index": "id"})
    .set_index("id")
)

# Unpack blueprint values
blueprint_cols = [c for c in blueprint.columns if c.startswith("blueprint_")]
input_cols = [c for c in blueprint.columns if c.startswith("inputs_")]
blueprint_total = blueprint[blueprint_cols].sum(axis=1).rename("blueprint_total")
shape_mask = blueprint.shape_mask

# convert Blueprint to integer percents * 10, and pack into pipe-delimited string
blueprint_percent = encode_values(blueprint[blueprint_cols], shape_mask, 1000).rename(
    "blueprint"
)


# convert input areas to integer percents * 10, and pack into pipe-delimited string
inputs_percent = encode_values(blueprint[input_cols], shape_mask, 1000).rename("inputs")


blueprint_df = (
    blueprint[["shape_mask"]]
    .round()
    .astype("uint")
    .join(blueprint_total.round().astype("uint"))
    .join(blueprint_percent)
    .join(inputs_percent)
)

### Dictionary encode ownership and protection for each HUC12:
# FED:<fed_acres>,LOC: <loc_acres>, ...
ownership = (
    pd.read_feather(working_dir / "ownership.feather")
    .set_index("id")
    .join(marine.acres.rename("total_acres"), how="left")
    .dropna()
)

ownership["percent"] = (
    (1000 * ownership.acres / ownership.total_acres).round().astype("uint")
)
# drop anything at 0%
ownership = ownership.loc[ownership.percent > 0].copy()

ownership = pd.Series(
    (ownership.Own_Type + ":" + ownership.percent.astype("str"))
    .groupby(level=0)
    .apply(lambda r: ",".join(v for v in r)),
    name="ownership",
)

protection = (
    pd.read_feather(working_dir / "protection.feather")
    .set_index("id")
    .join(marine.acres.rename("total_acres"), how="left")
    .dropna()
)

protection["percent"] = (
    (1000 * protection.acres / protection.total_acres).round().astype("uint")
)
# drop anything at 0%
protection = protection.loc[protection.percent > 0].copy()


protection = pd.Series(
    (protection.GAP_Sts.astype("str") + ":" + protection.percent.astype("str"))
    .groupby(level=0)
    .apply(lambda r: ",".join(v for v in r)),
    name="protection",
)


marine = (
    marine.join(blueprint_df, how="inner")
    .join(ownership, how="left")
    .join(protection, how="left")
)
marine.blueprint_total = marine.blueprint_total.fillna(0)
marine = marine.fillna("")

out = (
    huc12.reset_index()
    .append(marine.reset_index(), ignore_index=True, sort=False)
    .fillna("")
)


if DEBUG:
    out.to_feather("/tmp/tile_attributes.feather")


out.to_csv(out_dir / "unit_atts.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)

