from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import rasterize
from pyogrio import read_dataframe, write_dataframe

from analysis.pygeos_util import to_dict_all, explode

src_dir = Path("source_data/boundaries")
out_dir = Path("data/inputs")


blueprint_filename = out_dir / "blueprint_4.tif"

df = read_dataframe(
    src_dir / "SE_Blueprint_v4_0_Vectors.gdb",
    layer="HubsAndConnectors_v4_0_20191031",
    columns=["Type"],
)

df = explode(df)

# rasterize to match blueprint extent / transform

with rasterio.open(blueprint_filename) as src:
    hubs = rasterize(
        to_dict_all(df.loc[df.Type == "Hub"].geometry.values.data),
        src.shape,
        transform=src.transform,
        dtype="uint8",
        default_value=0,
        fill=255,
    )

    connectors = rasterize(
        to_dict_all(df.loc[df.Type == "Connector"].geometry.values.data),
        src.shape,
        transform=src.transform,
        dtype="uint8",
        default_value=1,
        fill=255,
    )

    # stack data with hubs on top
    data = connectors
    data[hubs == 0] = 0

    with rasterio.open(out_dir / "hubs_connectors.tif", "w", **src.profile) as out:
        out.write(data, 1)
