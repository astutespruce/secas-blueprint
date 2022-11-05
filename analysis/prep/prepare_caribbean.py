from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from pyogrio import read_dataframe
from rasterio.features import rasterize

from analysis.constants import DATA_CRS, MASK_RESOLUTION
from analysis.lib.geometry import to_dict
from analysis.lib.input_areas import get_input_area_mask
from analysis.lib.raster import write_raster, create_lowres_mask, add_overviews

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

ID = "car"
NODATA = 255


bnd_dir = Path("data/boundaries")
src_dir = Path("source_data/caribbean")
out_dir = Path("data/inputs/indicators/caribbean")

out_dir.mkdir(exist_ok=True, parents=True)

df = (
    read_dataframe(src_dir / "Watershed_Ranking_PR.shp", columns=["Metric_Ran"])
    .rename(columns={"Metric_Ran": "carrank"})
    .to_crs(DATA_CRS)
)

### Create 30m version snapped to blueprint extent for tiles
mask, transform, window = get_input_area_mask(ID)

print("Rasterizing...")
df = pd.DataFrame(df)
df["geometry"] = df.geometry.values.data
shapes = df.apply(lambda row: (to_dict(row.geometry), row.carrank), axis=1)
data = rasterize(
    shapes,
    (window.height, window.width),
    transform=transform,
    dtype="uint8",
    fill=NODATA,
)

# apply input area mask
data = np.where(mask == 1, data, NODATA).astype("uint8")

outfilename = out_dir / "caribbean_lcd.tif"
write_raster(outfilename, data, transform=transform, crs=DATA_CRS, nodata=NODATA)

add_overviews(outfilename)

create_lowres_mask(
    outfilename,
    str(outfilename).replace(".tif", "_mask.tif"),
    resolution=MASK_RESOLUTION,
    ignore_zero=False,  # no 0 values present
)
