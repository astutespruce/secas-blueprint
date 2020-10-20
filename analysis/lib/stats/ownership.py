from pathlib import Path

import geopandas as gp
import pygeos as pg

from analysis.constants import M2_ACRES
from analysis.lib.pygeos_util import intersection

src_dir = Path("data/inputs/boundaries")
ownership_filename = src_dir / "ownership.feather"


def summarize_by_unit(units_df, out_dir):
    print("Calculating overlap with land ownership and protection")

    ownership = gp.read_feather(
        ownership_filename, columns=["geometry", "Own_Type", "GAP_Sts"]
    )

    index_name = units_df.index.name

    df = intersection(units_df, ownership)

    if not len(df):
        return

    df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES

    # drop areas that touch but have no overlap
    df = df.loc[df.acres > 0].copy()

    by_owner = (
        df[["Own_Type", "acres"]]
        .groupby(by=[df.index.get_level_values(0), "Own_Type"])
        .acres.sum()
        .astype("float32")
        .round()
        .reset_index()
        .set_index("level_0")
    )
    by_owner.index.name = index_name

    by_protection = (
        df[["GAP_Sts", "acres"]]
        .groupby(by=[df.index.get_level_values(0), "GAP_Sts"])
        .acres.sum()
        .astype("float32")
        .round()
        .reset_index()
        .set_index("level_0")
    )
    by_protection.index.name = index_name

    by_owner.to_feather(out_dir / "ownership.feather")
    by_protection.to_feather(out_dir / "protection.feather")

