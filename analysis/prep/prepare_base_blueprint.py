import json
from pathlib import Path

import numpy as np
from pyogrio import read_dataframe
import rasterio
from rasterio.features import rasterize
from rasterio import windows
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from analysis.constants import MASK_RESOLUTION
from analysis.lib.colors import hex_to_uint8
from analysis.lib.geometry import to_dict_all
from analysis.lib.raster import add_overviews, create_lowres_mask, write_raster


src_dir = Path("source_data/base_blueprint")
data_dir = Path("data")
bnd_dir = data_dir / "boundaries"  # used for processing but not as inputs
out_dir = data_dir / "inputs/indicators/base"
json_dir = Path("constants/indicators")

bnd_dir.mkdir(exist_ok=True, parents=True)
out_dir.mkdir(exist_ok=True, parents=True)

NODATA = 255  # standardize NODATA of all indicators

# data window is used to extract the data extent in the blueprint and indicators;
# all have the same original extent
# this value is calculated in prepare_boundaries.py
data_window = window = windows.Window(
    col_off=855, row_off=806, width=106719, height=60170
)

with rasterio.open(src_dir / "BaseBlueprintExtent2022.tif") as src:
    orig_transform = src.transform
    dst_transform = windows.transform(data_window, src.transform)


outfilename = out_dir / "base_blueprint.tif"
if not outfilename.exists():
    print("Extracting Base Blueprint")
    with rasterio.open(src_dir / "Blueprint2022.tif") as src:
        nodata = int(src.nodata)
        data = src.read(1, window=data_window)

        df = (
            read_dataframe(src_dir / "Blueprint2022.tif.vat.dbf")
            .set_index("Value")[["Red", "Green", "Blue"]]
            .astype("uint8")
        )
        df["Alpha"] = 255
        df.loc[0, "Alpha"] = 0

        # uncomment to print blueprint colors
        # print(df[['Red','Green', 'Blue']].apply(lambda row: f"#{row.Red:02X}{row.Green:02X}{row.Blue:02X}", axis=1))

        colormap = df.apply(tuple, axis=1).to_dict()

        write_raster(
            outfilename,
            data,
            transform=windows.transform(data_window, src.transform),
            crs=src.crs,
            nodata=nodata,
        )

        with rasterio.open(outfilename, "r+") as out:
            out.write_colormap(1, colormap)

        add_overviews(outfilename)

        create_lowres_mask(
            outfilename,
            str(outfilename).replace(".tif", "_mask.tif"),
            resolution=MASK_RESOLUTION,
            ignore_zero=False,
        )


### Extract indicators and associated json
print("Extracting indicators")

indicators = []
tifs = sorted(str(f) for f in (src_dir / "indicators").glob("*.tif"))
for tif in tifs:
    if tif.replace(".tif", "Binned.tif") in tifs:
        # print(f"Skipping {tif} because binned version available")
        continue

    print(f"Processing {tif}")

    # read data tables and extract indicator values
    df = read_dataframe(f"{tif}.vat.dbf")
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
    df["red"] = df.red.astype("uint8")
    df["green"] = df.green.astype("uint8")
    df["blue"] = df.blue.astype("uint8")

    df["label"] = df["label"].apply(
        lambda x: x.split("=", 1)[1].strip() if "=" in x else x
    )
    df["color"] = df[["red", "green", "blue"]].apply(
        lambda row: f"#{row[0]:02X}{row[1]:02X}{row[2]:02X}", axis=1
    )

    # All white is intended to be transparent
    df.loc[df.color == "#FFFFFF", "color"] = None

    indicator = {
        "id": f"base:ECO_{outfilename.stem.lower()}",
        "filename": outfilename.name,
        "label": outfilename.stem,
        "values": df[["value", "label", "color"]].to_dict(orient="records"),
        "description": "TODO:",
        "url": "",
    }
    indicators.append(indicator)

    colors = df.set_index("value")[["red", "green", "blue"]]
    colors["Alpha"] = 255
    colors.loc[
        (colors.red == 255) & (colors.green == 255) & (colors.blue == 255), "Alpha"
    ] = 0
    colormap = colors.apply(tuple, axis=1).to_dict()

    has_zero = df.value.min() == 0

    # clip to new TIF, standardize nodata
    # Note: manually checked value range to verify that all can be safely cast to uint8
    outfilename = out_dir / Path(tif).name
    if not outfilename.exists():
        with rasterio.open(tif) as src:
            nodata = int(src.nodata)

            if src.transform == orig_transform:
                # if exactly aligned with blueprint extent, we can safely read a window out of the data
                print("Reading data via window")
                data = src.read(1, window=data_window).astype("uint8")
            else:
                # use a WarpedVRT to read data, which may differ in terms of
                # resolution or offset
                print("Reading data via warped VRT")
                with WarpedVRT(
                    src,
                    width=data_window.width,
                    height=data_window.height,
                    nodata=nodata,
                    transform=dst_transform,
                    resampling=Resampling.nearest,
                ) as vrt:
                    data = vrt.read()[0]

            data = np.where(data == nodata, NODATA, data)

            write_raster(
                outfilename,
                data,
                transform=dst_transform,
                crs=src.crs,
                nodata=NODATA,
            )

            add_overviews(outfilename)

        with rasterio.open(outfilename, "r+") as src:
            src.write_colormap(1, colormap)

        print("Creating mask...")

        create_lowres_mask(
            outfilename,
            str(outfilename).replace(".tif", "_mask.tif"),
            resolution=MASK_RESOLUTION,
            ignore_zero=not has_zero,
        )


outfilename = json_dir / "base.json"
if not outfilename.exists():
    with open(outfilename, "w") as out:
        data = {"input": "base", "indicators": indicators}
        out.write(json.dumps(data, indent=2))


### Prepare hubs and corridors
print("Processing hubs and corridors")

inland_hubs = read_dataframe(src_dir / "InlandHubs2022.shp", columns=[])
marine_hubs = read_dataframe(src_dir / "EstuarineAndMarineHubs2022.shp", columns=[])

with rasterio.open(bnd_dir / "base_blueprint_extent.tif") as src, rasterio.open(
    src_dir / "InlandCorridors2022.tif"
) as inland, rasterio.open(src_dir / "MarineCorridors2022.tif") as marine:
    print("Rasterizing hubs...")
    # rasterize hubs to match inland
    inland_hubs_data = rasterize(
        to_dict_all(inland_hubs.geometry.values.data),
        src.shape,
        transform=src.transform,
        dtype="uint8",
    )
    marine_hubs_data = rasterize(
        to_dict_all(marine_hubs.geometry.values.data),
        src.shape,
        transform=src.transform,
        dtype="uint8",
    )

    # Inland corridors are at 30m snapped to blueprint extent
    inland_data = inland.read(1, window=data_window)

    # Marine corridors are at 90m
    print("Reading and warping marine corridors...")
    vrt = WarpedVRT(
        marine,
        width=src.width,
        height=src.height,
        nodata=marine.nodata,
        transform=src.transform,
        resampling=Resampling.nearest,
    )
    marine_data = vrt.read()[0]

    # consolidate all values into a single raster, writing hubs over corridors
    # 4 = not a hub or corridor, but within data extent
    data = np.ones(shape=src.shape, dtype="uint8") * 4
    data[inland_data == 1] = 1
    data[marine_data == 1] = 3
    data[inland_hubs_data == 1] = 0
    data[marine_hubs_data == 1] = 2

    # stamp back in nodata from Blueprint extent
    extent_data = src.read(1)
    data[extent_data == int(src.nodata)] = 255

    outfilename = out_dir / "corridors.tif"
    write_raster(
        outfilename,
        data,
        src.transform,
        crs=src.crs,
        nodata=NODATA,
    )

    add_overviews(outfilename)

    create_lowres_mask(
        outfilename,
        str(outfilename).replace(".tif", "_mask.tif"),
        resolution=MASK_RESOLUTION,
        ignore_zero=False,
    )

    colormap = {
        e["value"]: hex_to_uint8(e["color"])
        if e["color"] is not None
        else (255, 255, 255, 0)
        for e in json.loads(open(json_dir / "../corridors.json").read())
    }

    with rasterio.open(outfilename, "r+") as src:
        src.write_colormap(1, colormap)
