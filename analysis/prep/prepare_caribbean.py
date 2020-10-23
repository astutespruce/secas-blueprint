from pathlib import Path
import os

from pyogrio import read_dataframe, write_dataframe
import pygeos as pg
import geopandas as gp

from analysis.constants import DATA_CRS


src_dir = Path("source_data/caribbean")
out_dir = Path("data/inputs/indicators/caribbean")
tile_dir = Path("data/for_tiles")

if not out_dir.exists():
    os.makedirs(out_dir)

df = (
    read_dataframe(
        src_dir / "Watershed_Ranking_PR.shp", columns=["Metric_Ran", "HUC_10"]
    )
    .rename(columns={"Metric_Ran": "carrank", "HUC_10": "HUC10"})
    .to_crs(DATA_CRS)
)

df.to_feather(out_dir / "caribbean.feather")

# for tiles
write_dataframe(
    df[["geometry", "carrank"]], tile_dir / f"caribbean.geojson", driver="GeoJSONSeq"
)
