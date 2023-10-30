import json
from pathlib import Path

from affine import Affine
import numpy as np
import pandas as pd
from pyogrio import read_dataframe
import rasterio
from rasterio.features import rasterize
from rasterio import windows
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
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
    colormap = {
        e["value"]: hex_to_uint8(e["color"])
        for e in BLUEPRINT
    }
    colormap[0] = (255, 255, 255, 0)

    with rasterio.open(src_dir / "Blueprint2023.tif") as src:
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
    inland_hubs = read_dataframe(
        src_dir / "hubs_corridors/ContinentalInlandHubs2023.shp",
        columns=[],
        use_arrow=True,
    ).explode(ignore_index=True)
    inland_hubs["value"] = 1
    marine_hubs = read_dataframe(
        src_dir / "hubs_corridors/ContinentalEstuarineAndMarineHubs2023.shp",
        columns=[],
        use_arrow=True,
    ).explode(ignore_index=True)
    marine_hubs["value"] = 3
    caribbean_hubs = read_dataframe(
        src_dir / "hubs_corridors/CaribbeanHubs2023.shp",
        columns=[],
        use_arrow=True,
    ).explode(ignore_index=True)
    caribbean_hubs["value"] = 5

    # sort so that inland hubs get rasterized last (on top)
    hubs = pd.concat([inland_hubs, marine_hubs, caribbean_hubs], ignore_index=True)

    ix = ~shapely.is_valid(hubs.geometry.values)
    hubs.loc[ix, "geometry"] = shapely.buffer(hubs.loc[ix].geometry.values, 0)
    hubs = (
        dissolve(hubs, by="value")
        .explode(ignore_index=True)
        .sort_values(by="value", ascending=False)
    )

    with rasterio.open(
        src_dir / "hubs_corridors/ContinentalInlandCorridors2023.tif"
    ) as inland, rasterio.open(
        src_dir / "hubs_corridors/ContinentalMarineCorridors2023.tif"
    ) as marine, rasterio.open(
        src_dir / "hubs_corridors/CaribbeanCorridors2023.tif"
    ) as caribbean:
        # consolidate all values into a single raster, writing hubs over corridors
        # see values in corridors.json
        # NOTE: per guidance from Amy K., always stack inland on top of marine

        data = np.zeros(shape=(extent.shape), dtype="uint8")

        print("Reading Caribbean corridors")
        # Caribbean data are limited to Caribbean extent, so use a larger read
        # window to read full extent
        carribean_window = shift_window(
            windows.Window(
                col_off=0, row_off=0, width=extent.width, height=extent.height
            ),
            extent.transform,
            caribbean.transform,
        )
        caribbean_corridors_data = caribbean.read(
            1, window=carribean_window, boundless=True
        )
        data[caribbean_corridors_data == np.uint8(1)] = np.uint8(6)
        del caribbean_corridors_data

        print("Reading marine corridors")
        # Marine corridors are at 90m; resample them to 30m
        with WarpedVRT(
            marine,
            width=extent.width,
            height=extent.height,
            nodata=marine.nodata,
            transform=extent.transform,
            resampling=Resampling.nearest,
        ) as vrt:
            marine_corridors_data = vrt.read()[0]

        data[marine_corridors_data == np.uint8(1)] = np.uint8(4)
        del marine_corridors_data

        print("Reading inland corridors")
        # Inland corridors are at 30m snapped to blueprint extent
        inland_window = shift_window(
            windows.Window(
                col_off=0, row_off=0, width=extent.width, height=extent.height
            ),
            extent.transform,
            inland.transform,
        )
        inland_corridors_data = inland.read(1, window=inland_window)
        data[inland_corridors_data == np.uint8(1)] = np.uint8(2)
        del inland_corridors_data

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

        print("Writing corridors...")
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
        indicators_dir / "Blueprint 2023 Indicator Thresholds.xlsx",
        sheet_name=sheet_name,
    ).rename(
        columns={
            "Indicator": "label",
            "2023 Indicator values": "values",
            '2023 Blueprint Explorer "Good" threshold': "goodThreshold",
            "2023 Indicator descriptions": "description",
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
    )

    ecosystem_id = sheet_name.lower().split(" ")[-1][:1]
    df["id"] = ecosystem_id + "_" + key.str.lower()

    ecosystems.append(
        {
            "id": ecosystem_id,
            "label": sheet_name.capitalize(),
            **ECOSYSTEM_COLORS[ecosystem_id],
            "indicators": df.id.values.tolist(),
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
        df.loc[ix].goodThreshold.str.extract("(\d)").astype("uint8").values[:, 0]
    )

    # extract caption label; this is lowercase name except when includes placename
    places = [
        "Atlantic",
        "Caribbean",
        "Gulf",
        "Great Plains",
        "Interior Southeast",
        "Mississippi Alluvial Valley",
        "South Atlantic",
        "West Coastal Plain & Ouachitas",
        "West Gulf Coast" "West Virginia",
    ]
    df["captionLabel"] = df.label
    ix = ~df.label.apply(lambda x: any(x.startswith(p) for p in places))
    df.loc[ix, "captionLabel"] = df.label.str.lower()

    df["values"] = None
    df["valueLabel"] = ""

    df = df[
        [
            "id",
            "filename",
            "label",
            "description",
            "values",
            "valueLabel",
            "captionLabel",
            "goodThreshold",
            "url",
        ]
    ]

    df["description"] = (
        df["description"]
        .str.replace("’", "'")
        .str.replace("–", "-")
        .str.strip()
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
    df = read_dataframe(indicators_dir / f"{filename}.vat.dbf")

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

    df["label"] = (
        df["label"]
        .apply(lambda x: x.split("=", 1)[1].strip() if "=" in x else x)
        .str.replace("<=", "≤")
        .str.replace(">=", "≥")
        .str.replace("’", "'")
        .str.replace("–", "-")
        .str.strip()
    )

    # shorten labels for some indicators
    if filename == "MississippiAlluvialValleyForestBirds_Protection.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Priority of forest breeding bird habitat patch for future protection"

        df["label"] = (
            df["label"]
            .str.replace(
                "Not a priority (score =0)", "Score 0 (not a priority)", regex=False
            )
            .str.replace(
                "Low priority (score >0-10)", "Score >0-10 (low priority)", regex=False
            )
            .str.replace(
                "Highest priority forest breeding bird habitat patch for future protection (score >90-100)",
                "Score >90-100 (highest priority)",
                regex=False,
            )
        )
        ix = df["label"].str.startswith("(") & df["label"].str.endswith(")")
        df.loc[ix, "label"] = df.loc[ix, "label"].str.strip("()").str.title()

    elif filename == "MississippiAlluvialValleyForestBirds_Reforestation.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Likelihood that reforestation will contribute to forest breeding bird habitat needs"

        df["label"] = (
            df["label"]
            .str.replace(
                "Reforestation least likely to contribute to forest breeding bird habitat needs",
                "Least likely",
            )
            .str.replace(
                "Reforestation less likely to contribute to forest breeding bird habitat needs",
                "Less likely",
            )
            .str.replace(
                "Reforestation more likely to contribute to forest breeding bird habitat needs",
                "More likely",
            )
            .str.replace(
                "Reforestation most likely to contribute to forest breeding bird habitat needs",
                "Most likely",
            )
        )
    elif filename == "EastCoastalPlainOpenPineBirds.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Priority for open pine conservation for focal bird species"
        df["label"] = df["label"].str.replace(
            "High priority for open pine conservation for focal bird species (Bachman's sparrow, red-cockaded woodpecker, Henslow's sparrow, red-headed woodpecker, Northern bobwhite, and brown-headed nuthatch)",
            "High priority",
        )
    elif filename == "EquitableAccessToPotentialParks.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Priority for a new park that would create nearby equitable access"
        df["label"] = df["label"].str.replace(
            " for a new park that would create nearby equitable access", ""
        )
    elif filename == "WestCoastalPlainandOuachitasForestedWetlandBirds.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Habitat suitability for forested wetland bird umbrella species"
        df["label"] = (
            df["label"]
            .str.replace(
                "High habitat suitability for forested wetland bird umbrella species (Acadian flycatcher, Kentucky warbler, yellow-throated warbler, prothonotary warbler, red-shouldered hawk)",
                "High habitat suitability",
            )
            .str.replace(" for forested wetland bird umbrella species", "")
        )

    elif filename == "WestCoastalPlainandOuachitasOpenPineBirds.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Ability of pine patch to support a population of umbrella bird species if managed in open condition"
        df["label"] = (
            df["label"]
            .str.replace(" if managed in open condition", "")
            .str.replace("umbrella bird ", "")
            .str.replace(" (brown-headed nuthatch, Bachman's sparrow, red-cockaded woodpecker)", "")
            .str.replace("Pine patch ", "")
            .str.capitalize()
        )

    elif filename == "WestGulfCoastMottledDuckNesting.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Percentile of suitable mottled duck nesting habitat"
        df["label"] = (
            df["label"]
            .str.replace(" of suitable mottled duck nesting habitat", "")
            .str.replace(" mottled duck nesting", "")
        )

    elif filename in (
        "NaturalLandcoverInFloodplains.tif",
        "CaribbeanNaturalLandcoverInFloodplains.tif",
    ):
        indicator_df.at[
            index, "valueLabel"
        ] = "Percent natural landcover within the estimated floodplain, by catchment"
        df["label"] = (
            df["label"]
            .str.replace(
                " natural habitat within the estimated floodplain, by catchment", ""
            )
            .str.replace(
                " natural landcover within the estimated floodplain, by catchment", ""
            )
        )
        df.loc[df['value']!=0, 'label'] += " natural landcover"

    elif filename == "ImperiledAquaticSpecies.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Number of aquatic animal Species of Greatest Conservation Need (SGCN) observed"
        df["label"] = (
            df["label"]
            .str.replace(
                "aquatic animal Species of Greatest Conservation Need (SGCN) observed",
                "species",
            )
            .str.replace("aquatic animal SGCN observed", "species")
        )

    elif filename == "WestVirginiaImperiledAquaticSpecies.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Number of aquatic imperiled (G1/G2) or threatened/endangered animal species observed"
        df["label"] = df["label"].str.replace(
            "aquatic imperiled (G1/G2) or threatened/endangered animal species observed",
            "species",
        )

    elif filename == "AtlanticMarineBirds.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Percentile of importance for marine bird index species (across the full East Coast study area)"
        df["label"] = (
            df["label"]
            .str.replace(
                " of importance for marine bird index species (across the full East Coast study area)",
                "",
            )
            .str.replace(" of importance", "")
        )

    elif filename == "AtlanticMarineMammals.tif":
            indicator_df.at[
                index, "valueLabel"
            ] = "Percentile of importance for marine mammal index species (across the full East Coast study area)"
            df["label"] = df["label"].str.replace(" of importance for marine mammal index species (across the full East Coast study area)", "").str.replace(" of importance", "")


    elif filename == "GulfMarineMammals.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Percentile of importance for marine mammal index species (across larger analysis area)"
        df["label"] = df["label"].str.replace(" of importance for marine mammal index species (across larger analysis area)", "").str.replace(" of importance", "")

    elif filename == "GulfSeaTurtles.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Percentile of importance for sea turtle index species (across larger analysis area)"
        df["label"] = df["label"].str.replace(" of importance for sea turtle index species (across larger analysis area)", "").str.replace(" of importance", "")

    elif filename == "MarineHighlyMigratoryFish.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Percentile of importance for bluefin and skipjack tuna or blue shark"
        df["label"] = df["label"].str.replace(" of importance for bluefin tuna and skipjack tuna or blue shark", "").str.replace(" of importance", "")


    elif filename == "SouthAtlanticBeachBirds.tif":
        indicator_df.at[
            index, "valueLabel"
        ] = "Percentile of importance for beach bird index species (American oystercatcher, Wilson's plover, least tern, piping plover)"
        df["label"] = (
            df["label"]
            .str.replace(
                "Open water or not identified as important for bird index species",
                "Open water or not identified as a priority",
            )
            .str.replace(
                " of importance for bird index species (American oystercatcher, Wilson's plover, least tern, piping plover)",
                "",
            )
            .str.replace(" of importance for bird index species", "")
            .str.replace(" of importance", "")
        )

    elif filename in ("PermeableSurface.tif", "CaribbeanPermeableSurface.tif"):
        df["label"] = (
            df["label"]
            .str.replace(" of catchment or small island", "")
            .str.replace(" of catchment", "")
        )

        if filename == "PermeableSurface.tif":
            indicator_df.at[index, "valueLabel"] = "Percent of catchment permeable "
        elif filename == "CaribbeanPermeableSurface.tif":
            indicator_df.at[
                index, "valueLabel"
            ] = "Percent of catchment or small island permeable"

    elif filename == "NetworkComplexity.tif":
        indicator_df.at[index, "valueLabel"] = "Number of connected stream size classes"
        df["label"] = (
            df["label"]
            .str.replace("connected stream classes", "size classes")
            .str.replace("connected stream class", "size class")
        )

    elif filename == "CaribbeanNetworkComplexity.tif":
        indicator_df.at[index, "valueLabel"] = "Number of connected stream size classes"
        df["label"] = (
            df["label"]
            .str.replace("connected stream classes", "size classes")
            .str.replace("connected stream class", "size class")
        )

    #######################

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

indicator_df = indicator_df.sort_values(by="id")


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

            # read data, standardize NODATA, and clip to data extent
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
