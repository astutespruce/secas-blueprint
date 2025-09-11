import json
from pathlib import Path
import re

from affine import Affine
import numpy as np
import pandas as pd
from pyogrio import read_dataframe
import rasterio
from rasterio.features import rasterize
from rasterio import windows
import shapely

from analysis.constants import MASK_RESOLUTION, CORRIDORS, BLUEPRINT
from analysis.lib.colors import hex_to_uint8
from analysis.lib.geometry import to_dict, dissolve
from analysis.lib.raster import (
    write_raster,
    add_overviews,
    create_lowres_mask,
    shift_window,
)


NODATA = 255  # standardize NODATA of all indicators
ECOSYSTEM_COLORS = {
    # terrestrial
    "t": {
        "color": "#f2f8ec",
        "borderColor": "#d8eac7",
    },
    # freshwater
    "f": {
        "color": "#eef7fc",
        "borderColor": "#c3e3f4",
    },
    # marine
    "m": {
        "color": "#f5f5ff",
        "borderColor": "#c2c2ff",
    },
}


src_dir = Path("source_data/blueprint")
indicators_dir = src_dir / "indicators"
data_dir = Path("data")
out_dir = data_dir / "inputs"
indicators_out_dir = out_dir / "indicators"
constants_dir = Path("constants")

indicators_out_dir.mkdir(exist_ok=True)

extent = rasterio.open(out_dir / "boundaries/blueprint_extent.tif")

################################################################################
### Extract blueprint to data extent
################################################################################
outfilename = out_dir / "blueprint.tif"

if not outfilename.exists():
    print("Extracting blueprint")
    colormap = {e["value"]: hex_to_uint8(e["color"]) for e in BLUEPRINT}
    colormap[0] = (255, 255, 255, 0)

    with rasterio.open(src_dir / "Blueprint2025.tif") as src:
        nodata = int(src.nodata)

        read_window = shift_window(
            windows.Window(
                col_off=0, row_off=0, width=extent.width, height=extent.height
            ),
            extent.transform,
            src.transform,
        )

        data = src.read(1, window=read_window)

        # Fill NODATA values within Blueprint extent with 0 values, per direction
        # from Amy K on 10/20/2023
        data = np.where(data == nodata, 0, data)

        extent_data = extent.read(1)
        data = np.where(extent_data == 1, data, NODATA)

        del extent_data

        write_raster(
            outfilename,
            data,
            transform=extent.transform,
            crs=src.crs,
            nodata=NODATA,
        )

        del data

        with rasterio.open(outfilename, "r+") as out:
            out.write_colormap(1, colormap)

        add_overviews(outfilename)


################################################################################
### Extract hubs and corridors
################################################################################
outfilename = out_dir / "corridors.tif"
if not outfilename.exists():
    print("Extracting hubs and corridors")

    print("Reading hubs and making valid")
    continental_hubs = read_dataframe(
        src_dir / "hubs_corridors/ContinentalHubs2025.shp",
        columns=[],
        use_arrow=True,
    ).explode(ignore_index=True)
    continental_hubs["value"] = 1

    caribbean_hubs = read_dataframe(
        src_dir / "hubs_corridors/CaribbeanHubs2025.shp",
        columns=[],
        use_arrow=True,
    ).explode(ignore_index=True)
    caribbean_hubs["value"] = 1

    hubs = pd.concat([continental_hubs, caribbean_hubs], ignore_index=True)

    ix = ~shapely.is_valid(hubs.geometry.values)
    hubs.loc[ix, "geometry"] = shapely.buffer(hubs.loc[ix].geometry.values, 0)
    hubs = (
        dissolve(hubs, by="value")
        .explode(ignore_index=True)
        .sort_values(by="value", ascending=False)
    )

    with (
        rasterio.open(
            src_dir / "hubs_corridors/ContinentalCorridors2025.tif"
        ) as continental,
        rasterio.open(
            src_dir / "hubs_corridors/CaribbeanCorridors2025.tif"
        ) as caribbean,
    ):
        # consolidate all values into a single raster, writing hubs over corridors
        # see values in corridors.json

        data = np.zeros(shape=(extent.shape), dtype="uint8")

        print("Reading Caribbean corridors")
        # Caribbean data are limited to Caribbean extent, so use a larger read
        # window to read full extent
        caribbean_window = shift_window(
            windows.Window(
                col_off=0, row_off=0, width=extent.width, height=extent.height
            ),
            extent.transform,
            caribbean.transform,
        )
        caribbean_corridors_data = caribbean.read(
            1, window=caribbean_window, boundless=True
        )
        data[caribbean_corridors_data == np.uint8(1)] = np.uint8(2)
        del caribbean_corridors_data

        print("Reading continental corridors")
        # Inland corridors are at 30m snapped to blueprint extent
        inland_window = shift_window(
            windows.Window(
                col_off=0, row_off=0, width=extent.width, height=extent.height
            ),
            extent.transform,
            continental.transform,
        )
        continental_corridors_data = continental.read(
            1, window=inland_window, boundless=True
        )
        data[continental_corridors_data == np.uint8(1)] = np.uint8(2)
        del continental_corridors_data

        print("Rasterizing hubs")
        _ = rasterize(
            hubs.apply(lambda row: (to_dict(row.geometry), row.value), axis=1),
            transform=extent.transform,
            out=data,
        )

        # stamp back in nodata from Blueprint extent
        extent_data = extent.read(1)
        data[extent_data == np.uint8(extent.nodata)] = np.uint8(255)
        del extent_data

        print("Writing hubs & corridors...")
        write_raster(
            outfilename,
            data,
            extent.transform,
            crs=extent.crs,
            nodata=NODATA,
        )

        del data

        add_overviews(outfilename)

        colormap = {
            e["value"]: hex_to_uint8(e["color"])
            if e["color"] is not None
            else (255, 255, 255, 0)
            for e in CORRIDORS
        }

        with rasterio.open(outfilename, "r+") as src:
            src.write_colormap(1, colormap)


################################################################################
### Extract indicators info and create JSON file
################################################################################
# IMPORTANT: do not hand-edit the JSON file; it needs to be constructed from
# the XLSX file plus indicator attribute tables only
print("Extracting indicator info to indicators.json")

# Extract indicator names, descriptions, etc from XLSX
ecosystems = []
merged = None
for sheet_name in ["Terrestrial", "Freshwater", "Coastal & Marine"]:
    df = pd.read_excel(
        indicators_dir / "Blueprint 2025 Indicator Thresholds.xlsx",
        sheet_name=sheet_name,
        engine="calamine",
    ).rename(
        columns={
            "Indicator": "label",
            "Legend Subheader": "valueLabel",
            "Abbreviated indicator values": "valueLabels",
            'Blueprint Explorer "Good" threshold': "goodThreshold",
            "Indicator descriptions": "description",
            "Hub Link": "url",
        }
    )
    key = df.label.apply(
        lambda x: x.title()
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
        .replace("&", "and")
        .replace(" ", "")
        .replace(".", "")
    )

    ecosystem_id = sheet_name.lower().split(" ")[-1][:1]
    df["id"] = ecosystem_id + "_" + key.str.lower()

    ecosystems.append(
        {
            "id": ecosystem_id,
            "label": sheet_name.capitalize(),
            **ECOSYSTEM_COLORS[ecosystem_id],
            "indicators": df.id.sort_values().values.tolist(),
        }
    )

    df["filename"] = key + ".tif"
    ix = key.str.startswith("MississippiAlluvialValleyForestBirds")
    df.loc[ix, "filename"] = df.loc[ix].filename.str.replace(
        "MississippiAlluvialValleyForestBirds",
        "MississippiAlluvialValleyForestBirds_",
        regex=False,
    )
    missing = [f for f in df.filename.values if not (indicators_dir / f).exists()]

    if missing:
        raise ValueError(f"Unable to find files for {', '.join(missing)}")

    # extract first value as integer; this is the threshold, set the rest to None
    df.loc[df.goodThreshold.str.lower().str.contains("no"), "goodThreshold"] = None
    ix = df.goodThreshold.notnull()
    df.loc[ix, "goodThreshold"] = (
        df.loc[ix].goodThreshold.str.extract(r"(\d)").astype("uint8").values[:, 0]
    )

    df["url"] = df.url.fillna("")
    df["valueLabel"] = df.valueLabel.fillna("").str.strip().replace("N/A", "")

    # extract caption label; this is lowercase name except when includes placename
    places = [
        "Atlantic",
        "Caribbean",
        "East Coastal Plain",
        "Gulf",
        "Great Plains",
        "Interior Southeast",
        "Mississippi Alluvial Valley",
        "Puerto Rico",
        "South Atlantic",
        "U.S. Virgin Islands",
        "West Coastal Plain & Ouachitas",
        "West Gulf Coast",
        "West Virginia",
    ]
    df["captionLabel"] = df.label
    ix = ~df.label.apply(lambda x: any(x.startswith(p) for p in places))
    df.loc[ix, "captionLabel"] = df.loc[ix].label.str.lower()

    def parse_values(text):
        out = {}
        for part in (
            text.replace("\r", "")
            .replace("<=", "≤")
            .replace(">=", "≥")
            .replace("’", "'")
            .replace("–", "-")
            .strip()
            .split("\n")
        ):
            value, label = re.match(r"(\d+)\s*=\s*(.+)", part).groups()
            out[int(value)] = label.strip()

        return out

    df["valueLabels"] = df["valueLabels"].apply(parse_values)
    df["values"] = None  # filled below

    df = df[
        [
            "id",
            "filename",
            "label",
            "description",
            "valueLabels",
            "values",
            "valueLabel",
            "captionLabel",
            "goodThreshold",
            "url",
        ]
    ]

    df["description"] = (
        df["description"].str.replace("’", "'").str.replace("–", "-").str.strip()
    )

    if merged is None:
        merged = df
    else:
        merged = pd.concat([merged, df], ignore_index=True)

indicator_df = merged

with open(constants_dir / "ecosystems.json", "w") as out:
    res = out.write(json.dumps(ecosystems, indent=2))


# read indicator attribute tables
for index, indicator_row in indicator_df.iterrows():
    filename = indicator_row.filename

    # read data tables and extract indicator values
    df = read_dataframe(indicators_dir / f"{filename}.vat.dbf", use_arrow=True)

    # columns not named consistently; standardize them
    desc_col = [c for c in df.columns if c.lower().startswith("desc")][0]
    red_col = [c for c in df.columns if c.lower() == "red"][0]
    green_col = [c for c in df.columns if c.lower() == "green"][0]
    blue_col = [c for c in df.columns if c.lower() == "blue"][0]
    df = df.rename(
        columns={
            "Value": "value",
            desc_col: "label",
            red_col: "red",
            green_col: "green",
            blue_col: "blue",
        }
    )
    df[["red", "green", "blue"]] = df[["red", "green", "blue"]].astype("uint8")

    # by default, use the value labels from the GeoTIFF files, but override where
    # necessary from indicators_df
    if indicator_row.valueLabel:
        df["label"] = df["value"].map(indicator_row.valueLabels)

    else:
        df["label"] = (
            df["label"]
            .apply(lambda x: x.split("=", 1)[1].strip() if "=" in x else x)
            .str.replace("<=", "≤")
            .str.replace(">=", "≥")
            .str.replace("’", "'")
            .str.replace("–", "-")
            .str.replace("10ac", "10 acres")
            .str.strip()
        )

    df["color"] = (
        df[["red", "green", "blue"]]
        .apply(lambda row: f"#{row.red:02X}{row.green:02X}{row.blue:02X}", axis=1)
        .values
    )

    # All white is intended to be transparent
    df.loc[df.color == "#FFFFFF", "color"] = None

    indicator_df.at[index, "values"] = df[["value", "label", "color"]].to_dict(
        orient="records"
    )

indicator_df = indicator_df.sort_values(by="id").drop(columns=["valueLabels"])


################################################################################
### Extract indicator GeoTIFFs
################################################################################
for index, indicator_row in indicator_df.iterrows():
    filename = indicator_row.filename

    # clip to new TIF, standardize nodata
    # Note: manually checked value range to verify that all can be safely cast to uint8
    outfilename = indicators_out_dir / filename
    if not outfilename.exists():
        with rasterio.open(indicators_dir / filename) as src:
            print(f"\n-------------------------\nProcessing {indicator_row.label}")

            nodata = int(src.nodata)

            # read data, standardize NODATA, and clip to data extent (not necessarily Blueprint extent)
            data = src.read(1)
            data = np.where(data == nodata, NODATA, data)
            data_window = windows.get_data_window(data, nodata=NODATA)
            data = data[data_window.toslices()]
            transform = windows.transform(data_window, src.transform)

            # all inputs are very closely aligned to Blueprint extent except for
            # floating point precision issues, so we create a new output transform
            # to set those exactly based on an integer offset into the blueprint extent
            col_off = round((extent.transform.c - transform.c) / extent.transform.a)
            row_off = round((extent.transform.f - transform.f) / extent.transform.e)
            out_transform = Affine(
                a=extent.transform.a,
                b=0.0,
                c=extent.transform.c - (col_off * extent.transform.a),
                d=0.0,
                e=extent.transform.e,
                f=extent.transform.f - (row_off * extent.transform.e),
            )

            write_raster(
                outfilename,
                data,
                transform=out_transform,
                crs=src.crs,
                nodata=NODATA,
            )

            del data

            add_overviews(outfilename)

        values = pd.DataFrame(indicator_row["values"])
        has_zero = values.value.min() == 0

        colormap = (
            values.set_index("value")
            .color.apply(
                lambda x: hex_to_uint8(x) + (255,) if x else (255, 255, 255, 0)
            )
            .to_dict()
        )
        with rasterio.open(outfilename, "r+") as src:
            src.write_colormap(1, colormap)

        print("Creating mask...")
        # create a transform for the mask that is an integer number of rows/cols
        # offset from the origin; this makes sure that we can always do an
        # origin point offset then read from the mask
        col_off = int(round((out_transform.c - extent.transform.c) / MASK_RESOLUTION))
        row_off = int(round((out_transform.f - extent.transform.f) / -MASK_RESOLUTION))

        mask_transform = Affine(
            a=MASK_RESOLUTION,
            b=0.0,
            c=extent.transform.c + col_off * MASK_RESOLUTION,
            d=0.0,
            e=-MASK_RESOLUTION,
            f=extent.transform.f - row_off * MASK_RESOLUTION,
        )
        create_lowres_mask(
            outfilename,
            str(outfilename).replace(".tif", "_mask.tif"),
            resolution=MASK_RESOLUTION,
            transform=mask_transform,
            ignore_zero=not has_zero,
        )


################################################################################
### Extract subregions associated with indicator
################################################################################
print("Extracting subregions associated with each indicator")
indicator_df["subregions"] = None
subregion_df = pd.read_feather(
    data_dir / "inputs/boundaries/subregions.feather", columns=["value", "subregion"]
)
subregion_lut = subregion_df.set_index("value").subregion.to_dict()
bins = np.arange(subregion_df.value.max() + 1)
with rasterio.open(data_dir / "boundaries/subregion_mask.tif") as subregions:
    subregion_values = subregions.read(1)
    for index, indicator_row in indicator_df.iterrows():
        print(f"Finding subregions for {indicator_row.label}")
        mask_filename = indicators_out_dir / str(indicator_row.filename).replace(
            ".tif", "_mask.tif"
        )

        with rasterio.open(mask_filename) as src:
            read_window = shift_window(
                windows.Window(
                    col_off=0,
                    row_off=0,
                    width=subregions.width,
                    height=subregions.height,
                ),
                subregions.transform,
                src.transform,
            )
            mask = src.read(1, window=read_window, boundless=True)
            indicator_subregions = np.where(mask == 1, subregion_values, NODATA)

            values = subregion_values[(subregion_values != NODATA) & (mask == 1)]
            counts = np.bincount(values, minlength=len(bins))
            # drop any where the area is < 0.1% of the total area of the indicator
            # these are usually at the edges of subregions where the indicator
            # has 0 values and was clipped to subregion boundaries
            ix = counts / counts.sum() >= 0.001
            indicator_subregions = sorted([subregion_lut[v] for v in bins[ix]])
            indicator_df.at[index, "subregions"] = indicator_subregions


extent.close()


with open(constants_dir / "indicators.json", "w") as out:
    res = out.write(
        json.dumps(indicator_df.to_dict(orient="records"), indent=2, ensure_ascii=False)
    )
