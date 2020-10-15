from pathlib import Path

import geopandas as gp
import pygeos as pg

from analysis.constants import M2_ACRES
from analysis.lib.pygeos_util import intersection

src_dir = Path("data/inputs/boundaries")
ownership_filename = src_dir / "ownership.feather"


def summarize_ownership(df):
    """Calculates area of overlap and returns data frames of total area per summary
    unit in each category of ownership and protection present in each.

    Parameters
    ----------
    df : GeoDataFrame
        areas of interest

    Returns
    -------
    (DataFrame, DataFrame)
        by_owner, by_protection
    """
    ownership = gp.read_feather(
        ownership_filename, columns=["geometry", "Own_Type", "GAP_Sts"]
    )

    index_name = df.index.name

    df = intersection(df, ownership)
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

    return by_owner, by_protection
