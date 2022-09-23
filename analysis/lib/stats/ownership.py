from pathlib import Path

import geopandas as gp
import pygeos as pg

from analysis.constants import M2_ACRES
from analysis.lib.geometry import intersection

src_dir = Path("data/inputs/boundaries")
ownership_filename = src_dir / "ownership.feather"


def summarize_by_unit(units_df, out_dir):
    print("Calculating overlap with land ownership and protection")

    ownership = gp.read_feather(
        ownership_filename, columns=["geometry", "Own_Type", "GAP_Sts"]
    )

    index_name = units_df.index.name

    df = intersection(units_df, ownership)

    if df is None:
        return

    df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES

    # drop areas that touch but have no overlap
    df = df.loc[df.acres > 0].copy()

    by_owner = (
        df[["Own_Type", "acres"]]
        .groupby([index_name, "Own_Type"])
        .acres.sum()
        .astype("float32")
        .round()
        .reset_index()
    )

    by_protection = (
        df[["GAP_Sts", "acres"]]
        .groupby([index_name, "GAP_Sts"])
        .acres.sum()
        .astype("float32")
        .round()
        .reset_index()
    )

    by_owner.to_feather(out_dir / "ownership.feather")
    by_protection.to_feather(out_dir / "protection.feather")
