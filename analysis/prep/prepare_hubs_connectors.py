from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import rasterize
from pyogrio import read_dataframe, write_dataframe

from analysis.pygeos_util import to_dict_all, explode

src_dir = Path("source_data/blueprint")
out_dir = Path("data/inputs")


blueprint_filename = out_dir / "se_blueprint2020.tif"
extent_filename = src_dir / "EsimatedCorridorExtent.shp"


extent_df = read_dataframe(extent_filename)
extent_df = explode(extent_df)


df = read_dataframe(
    src_dir / "SE_Blueprint_v2020_Vectors.gdb",
    layer="HubsAndConnectors_v2020_20201005",
    columns=["Type"],
)

df = explode(df)

# rasterize to match blueprint extent / transform

with rasterio.open(blueprint_filename) as src:

    print("Rasterizing hubs / connectors extent...")
    data = rasterize(
        to_dict_all(extent_df.geometry.values.data),
        src.shape,
        transform=src.transform,
        dtype="uint8",
        default_value=0,
        fill=255,
    )

    print("Rasterizing hubs...")
    hubs = rasterize(
        to_dict_all(df.loc[df.Type == "Hub"].geometry.values.data),
        src.shape,
        transform=src.transform,
        dtype="uint8",
        default_value=1,
        fill=255,
    )

    print("Rasterizing connectors...")
    connectors = rasterize(
        to_dict_all(df.loc[df.Type == "Connector"].geometry.values.data),
        src.shape,
        transform=src.transform,
        dtype="uint8",
        default_value=2,
        fill=255,
    )

    print("Merging data...")
    # stack data with hubs on top
    data[connectors == 2] = 2
    data[hubs == 1] = 1

    print("Writing hubs & connectors...")
    with rasterio.open(out_dir / "hubs_connectors.tif", "w", **src.profile) as out:
        out.write(data, 1)
