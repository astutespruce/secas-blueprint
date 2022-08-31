import json
from pathlib import Path

import numpy as np
from pyogrio import read_dataframe
import rasterio
from rasterio import windows

from analysis.lib.io import write_raster
from analysis.lib.raster import add_overviews


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
data_window = window = windows.Window(
    col_off=855, row_off=806, width=106719, height=60170
)


outfilename = out_dir / "base_blueprint.tif"
if not outfilename.exists():
    print("Extracting Base Blueprint")
    with rasterio.open(src_dir / "Blueprint2022.tif") as src:
        nodata = int(src.nodata)
        data = src.read(1)

        write_raster(
            outfilename,
            data[data_window.toslices()],
            transform=windows.transform(data_window, src.transform),
            crs=src.crs,
            nodata=nodata,
        )

        add_overviews(outfilename)

### Extract indicators and associated json
print("Extracting indicators")

indicators = []
tifs = sorted(str(f) for f in (src_dir / "indicators").glob("*.tif"))
for tif in tifs:
    if tif.replace(".tif", "Binned.tif") in tifs:
        # print(f"Skipping {tif} because binned version available")
        continue

    # clip to new TIF, standardize nodata
    outfilename = out_dir / Path(tif).name
    if not outfilename.exists():
        print(f"Clipping {tif}")
        with rasterio.open(tif) as src:
            nodata = int(src.nodata)
            # manually checked value range to verify that all can be safely cast to uint8
            data = src.read(1).astype("uint8")
            data = np.where(data == nodata, NODATA, data)

            write_raster(
                outfilename,
                data[data_window.toslices()],
                transform=windows.transform(data_window, src.transform),
                crs=src.crs,
                nodata=NODATA,
            )

            add_overviews(outfilename)

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
        lambda x: x.split("=")[1].strip() if "=" in x else x
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


outfilename = json_dir / "base.json"
if not outfilename.exists():
    with open(outfilename, "w") as out:
        data = {"input": "base", "indicators": indicators}
        out.write(json.dumps(data, indent=2))
