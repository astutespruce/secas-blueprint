from pathlib import Path
import warnings

from pyogrio import read_dataframe

from analysis.constants import DATA_CRS


warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


src_dir = Path("source_data/caribbean")
out_dir = Path("data/inputs/indicators/caribbean")

out_dir.mkdir(exist_ok=True, parents=True)

df = (
    read_dataframe(
        src_dir / "Watershed_Ranking_PR.shp", columns=["Metric_Ran", "HUC_10"]
    )
    .rename(columns={"Metric_Ran": "carrank", "HUC_10": "HUC10"})
    .to_crs(DATA_CRS)
)

df.to_feather(out_dir / "caribbean.feather")
