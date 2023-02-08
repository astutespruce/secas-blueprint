from pathlib import Path
from math import ceil, log2

from progress.bar import Bar
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import get_data_window
import geopandas as gp
import shapely


from analysis.constants import INDICATORS, CORRIDORS
from analysis.lib.raster import write_raster

data_dir = Path("data/inputs")
indicators_dir = data_dir / "indicators/base"
out_dir = Path("data/for_tiles")

# NOTE: all tiles are limited to extent of base blueprint (indicators not available elsewhere)
blueprint_filename = indicators_dir / "base_blueprint.tif"
inland_corridors_filename = out_dir / "inland_corridors.tif"
marine_corridors_filename = out_dir / "marine_corridors.tif"
urban_filename = data_dir / "threats/urban/urban_2060_binned.tif"
slr_filename = data_dir / "threats/slr/slr.tif"
bnd_filename = data_dir / "boundaries/input_areas.feather"


# very small amount added to numbers to make sure that log2 gives us current number of bytes
EPS = 1e-6


# only base has indicators
INDICATORS = INDICATORS["base"]


### Create dataframe with info about bits required, groups, etc
indicators = pd.DataFrame(
    [
        [
            e["id"].split("_")[0].replace("base:", ""),
            e["id"],
            indicators_dir / e["filename"],
            min([v["value"] for v in e["values"]]),
            max([v["value"] for v in e["values"]]),
        ]
        for e in INDICATORS
    ],
    columns=["ecosystem", "id", "filename", "min_value", "max_value"],
)

core = pd.DataFrame(
    [
        # blueprint is included so that it can be rendered after applying filters in UI
        {
            "ecosystem": "",
            "id": "blueprint",
            "filename": blueprint_filename,
            "min_value": 0,
            "max_value": 4,
        },
        # Corridors are split into inland and marine for pixel mode
        {
            "ecosystem": "",
            "id": "inland_corridors",
            "filename": inland_corridors_filename,
            "min_value": 0,
            "max_value": 2,
        },
        {
            "ecosystem": "",
            "id": "marine_corridors",
            "filename": marine_corridors_filename,
            "min_value": 0,
            "max_value": 2,
        },
        {
            "ecosystem": "threat",
            "id": "urban",
            "filename": urban_filename,
            "min_value": 1,
            "max_value": 5,
        },
        {
            "ecosystem": "threat",
            "id": "slr",
            "filename": slr_filename,
            "min_value": 0,
            "max_value": 13,
        },
    ]
)


df = pd.concat(
    [
        core,
        indicators,
    ]
).set_index("id")
df["src"] = df.filename.apply(lambda x: rasterio.open(x))
df["nodata"] = df.src.apply(lambda src: int(src.nodata))

# any indicators that have listed 0 values need to be shifted up 1
df["value_shift"] = (df.min_value == 0).astype("uint8")
df["max_value"] += df.value_shift
df["bits"] = df.max_value.apply(lambda x: ceil(log2(max(x, 2) + EPS)))

# # export for manual review and assignment of groups
# tmp = df[["bits"]].copy()
# tmp["group"] = ""
# tmp.to_csv(out_dir / "layers.csv", index=True, index_label="id")

# read manually assigned groups that are up to 24 bits each
# Note: these are based loosely on overlapping spatial extent
grouped = pd.read_csv(out_dir / "layers.csv").set_index("id")
print("Groups:")
print(grouped.groupby("group", dropna=False).bits.sum())

if grouped.group.isnull().max():
    raise ValueError("All layers must be assigned to a group")

df = df.join(grouped.group)
df["orig_pos"] = np.arange(len(df))
df = df.sort_values(by=["group", "orig_pos"])

groups = sorted(df.group.unique())

# calculate position and bit offsets for each entity within each group
df["position"] = 0
df["offset"] = 0
for group in groups:
    ix = df.group == group
    df.loc[ix, "position"] = np.arange(ix.sum())
    df.loc[ix, "offset"] = np.cumsum(df.loc[ix].bits) - df.loc[ix].bits

for col in ["group", "position", "bits", "offset", "min_value", "max_value"]:
    df[col] = df[col].astype("uint8")

# NOTE: groups must be stored in encoding definition
# in exactly the same order they are encoded
df[["group", "position", "offset", "bits", "value_shift"]].reset_index().to_feather(
    out_dir / "encoding.feather"
)

# save encoding JSON for frontend
for group in groups:
    with open(out_dir / f"se_pixel_layers_{group}.json", "w") as out:
        _ = out.write(
            df.loc[df.group == group, ["offset", "bits", "value_shift"]]
            .rename(columns={"value_shift": "valueShift"})
            .reset_index()
            .to_json(orient="records")
        )


### determine the block windows that overlap bounds
# everything else will be filled with 0
print("Calculating overlapping windows")
bnd_df = gp.read_feather(bnd_filename)
bnd = bnd_df.loc[bnd_df.id == "base"].geometry.values[0]
blueprint = rasterio.open(blueprint_filename)
windows = np.array([w for _, w in blueprint.block_windows(1)])
bounds = np.array([blueprint.window_bounds(w) for w in windows]).T
bounds = shapely.box(*bounds)
tree = shapely.STRtree(bounds)
ix = tree.query(bnd, predicate="intersects")
ix.sort()
windows = windows[ix]

for group in groups:
    rows = df.loc[df.group == group]
    total_bits = rows.bits.sum()

    # tile creation pipeline expects uint32 for creating RGB PNGs
    out = np.zeros(shape=blueprint.shape, dtype="uint32")

    # process each stack of layers by window to avoid running out of memory
    for window in Bar(
        f"Processing group {group} ({total_bits} bits)", max=len(windows)
    ).iter(windows):
        window_shape = (window.height, window.width)
        ix = window.toslices()
        has_data = False
        layer_bits = []
        for id in rows.index:
            row = rows.loc[id]

            data = row.src.read(1, window=window)

            # shift values up if needed
            if row.value_shift:
                data[data != row.nodata] += 1

            # set nodata pixels to 0 (combined with existing 0 values that are below row.min_value)
            data[data == row.nodata] = 0

            if data.max() > 0:
                out[ix] = np.bitwise_or(
                    np.left_shift(data.astype("uint32"), row.offset), out[ix]
                )

    # determine the window where data are available, and write out a smaller output
    print("Calculating data window...")
    data_window = get_data_window(out, nodata=0)
    out = out[data_window.toslices()]
    transform = blueprint.window_transform(data_window)

    print(f"Data window: {data_window}")

    print("Writing GeoTIFF...")
    outfilename = out_dir / f"se_pixel_layers_{group}.tif"
    write_raster(outfilename, out, transform=transform, crs=blueprint.crs, nodata=0)

    # NOTE: we intentionally don't create overviews because this messes up the
    # data when converting to WGS84


#### Notes
# to verify that values are encoded correctly
# 1. cast encoded values to correct type (e.g., uint16): value = encoded[106,107].view('uint16')
# 2. use bit shifting and bit AND logic to extract value, based on offset and nbits:
# (value >> offset) & ((2**nbits)-1) # => original value
