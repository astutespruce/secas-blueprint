from pathlib import Path

import rasterio
from rasterio import windows

from analysis.lib.raster import write_raster, add_overviews
from pyogrio import read_dataframe


src_dir = Path("source_data/blueprint")
data_dir = Path("data")
out_dir = data_dir / "inputs"

# Window is determined in prepare_boundaries.py
data_window = windows.Window(col_off=855, row_off=294, width=144065, height=71409)

df = (
    read_dataframe(
        src_dir / "SE_Blueprint_2022.tif.vat.dbf",
        columns=[["Value", "Red", "Green", "Blue"]],
    )
    .set_index("Value")
    .astype("uint8")
)
df["Alpha"] = 255
df.loc[0, "Alpha"] = 0
colormap = df.apply(tuple, axis=1).to_dict()

with rasterio.open(src_dir / "blueprint/SE_Blueprint_2022.tif") as src:
    nodata = int(src.nodata)
    data = src.read(1)

    transform = windows.transform(data_window, src.transform)

    data = data[data_window.toslices()]
    outfilename = out_dir / "se_blueprint_2022.tif"
    write_raster(
        outfilename,
        data,
        transform,
        crs=src.crs,
        nodata=nodata,
    )

    with rasterio.open(outfilename, "r+") as out:
        out.write_colormap(1, colormap)

    add_overviews(outfilename)
