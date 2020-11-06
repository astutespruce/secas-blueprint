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

###################################################################
### HUC12
###################################################################

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
    .join(huc12.acres.rename("total_acres"), how="inner")
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
    .join(huc12.acres.rename("total_acres"), how="inner")
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


### Add in other inputs

# Gulf Hypoxia
gh_df = pd.read_feather(working_dir / "gulf_hypoxia.feather").set_index("id")
gh_cols = [c for c in gh_df.columns if c.startswith("gh_")]
gh_percent = encode_values(gh_df[gh_cols], gh_df.shape_mask, 1000).rename(
    "gulf_hypoxia"
)

# Caribbean
car_df = pd.read_feather(working_dir / "caribbean.feather").set_index("id")


# Florida
fl_df = pd.read_feather(working_dir / "florida.feather").set_index("id")
fl_cols = [c for c in fl_df.columns if c.startswith("fl_")]
fl_percent = encode_values(fl_df[fl_cols], fl_df.shape_mask, 1000).rename(
    "fl_blueprint"
)

# Middle Southeast
ms_df = pd.read_feather(working_dir / "midse.feather").set_index("id")
ms_cols = [c for c in ms_df.columns if c.startswith("ms_")]
ms_percent = encode_values(ms_df[ms_cols], ms_df.shape_mask, 1000).rename(
    "midse_blueprint"
)


# Nature's Network
nn_df = pd.read_feather(working_dir / "natures_network.feather").set_index("id")
nn_cols = [c for c in nn_df.columns if c.startswith("nn_")]
nn_percent = encode_values(nn_df[nn_cols], nn_df.shape_mask, 1000).rename("nn_priority")

# NatureScape
ns_df = pd.read_feather(working_dir / "naturescape.feather").set_index("id")
ns_cols = [c for c in ns_df.columns if c.startswith("app_")]
ns_percent = encode_values(ns_df[ns_cols], ns_df.shape_mask, 1000).rename("ns_priority")


# South Atlantic
sa_df = pd.read_feather(working_dir / "southatlantic.feather").set_index("id")
sa_cols = [c for c in sa_df.columns if c.startswith("sa_")]
sa_percent = encode_values(sa_df[sa_cols], sa_df.shape_mask, 1000).rename(
    "sa_blueprint"
)


huc12 = (
    huc12.join(gh_percent, how="left")
    .join(car_df, how="left")
    .join(fl_percent, how="left")
    .join(ms_percent, how="left")
    .join(nn_percent, how="left")
    .join(ns_percent, how="left")
    .join(sa_percent, how="left")
)


### Convert CHAT
for state in ["ok", "tx"]:
    chat = (
        pd.read_feather(working_dir / f"{state}chat.feather")
        .set_index("id")
        .join(huc12.acres)
    )

    # extract CHAT overall rank
    rank_fields = [f"chatrank_{i}" for i in CHAT_CATEGORIES]
    for field in rank_fields:
        if not field in chat.columns:
            chat[field] = 0

    chat_rank_percent = encode_values(chat[rank_fields], chat.total_acres, 1000).rename(
        f"{state}chatrank"
    )

    # calculate areas outside SE and outside CHAT
    huc12 = huc12.join(chat_rank_percent, how="left")


###################################################################
### Marine
###################################################################

working_dir = results_dir / "marine_blocks"

print("--------------------------------")
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

### Marine input areas

# Florida (marine)
fl_df = pd.read_feather(working_dir / "florida.feather").set_index("id")
fl_cols = [c for c in fl_df.columns if c.startswith("flm_")]
fl_percent = encode_values(fl_df[fl_cols], fl_df.shape_mask, 1000).rename(
    "flm_blueprint"
)

# South Atlantic (marine)
sa_df = pd.read_feather(working_dir / "southatlantic.feather").set_index("id")
sa_cols = [c for c in sa_df.columns if c.startswith("sa_")]
sa_percent = encode_values(sa_df[sa_cols], sa_df.shape_mask, 1000).rename(
    "sa_blueprint"
)

marine = marine.join(sa_percent, how="left").join(fl_percent, how="left")


out = huc12.reset_index().append(marine.reset_index(), ignore_index=True, sort=False)


# fill specifics fields as needed
out.carrank = out.carrank.fillna(0).astype("uint8")

# everything else is blank strings
out = out.fillna("")


if DEBUG:
    out.to_feather("/tmp/tile_attributes.feather")


out.to_csv(out_dir / "unit_atts.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)

