from pathlib import Path
import os
import warnings

from pyogrio import read_dataframe, write_dataframe

from analysis.constants import DATA_CRS


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


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
    df[["geometry", "carrank"]], tile_dir / "caribbean.geojson", driver="GeoJSONSeq"
)
