from pathlib import Path

import geopandas as gp
import pandas as pd
import pygeos as pg

from analysis.constants import CARIBBEAN_BOUNDS, M2_ACRES

from analysis.lib.bounds import bounds_overlap
from analysis.lib.pygeos_util import intersection


src_dir = Path("data/inputs/indicators/caribbean")
caribbean_filename = src_dir / "caribbean.feather"


def summarize_caribbean_aoi(df, bounds):
    """Calculate area of overlap with Caribbean dataset

    Parameters
    ----------
    df : GeoDataframe
        area of interest
    bounds : list-like of [xmin, ymin, xmax, ymax]
        bounds of area of interest

    Returns
    -------
    DataFrame
        aggregated
    """

    if not bounds_overlap(bounds, CARIBBEAN_BOUNDS):
        return None

    index_name = df.index.name

    car_df = gp.read_feather(caribbean_filename, columns=["geometry", "carrank"])

    df = intersection(df, car_df)
    df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES

    # aggregate totals by rank
    by_rank = (
        df[["carrank", "acres"]]
        .groupby(by=[df.index.get_level_values(0), "carrank"])
        .acres.sum()
        .astype("float32")
        .round()
        .reset_index()
        .set_index("level_0")
    )

    by_rank.index.name = index_name

    return by_rank


def summarize_caribbean_by_huc12(df, out_dir):
    """Calculate overlap of HUC12 summary units with HUC10 priority watersheds.

    This uses the HUC10 component of the HUC12 index to do a basic join, and
    returns those watersheds that are present in the Caribbean dataset.

    Parameters
    ----------
    df : GeoDataFrame
        summary units
    """

    print("Calculating overlap with Caribbean priority watersheds...")

    df = df.copy()
    car_df = pd.read_feather(
        caribbean_filename, columns=["HUC10", "carrank"]
    ).set_index("HUC10")

    # extract HUC10 codes from HUC12 index
    df["HUC10"] = df.index.str[:10]

    df = df.join(car_df, on="HUC10", how="inner")[["carrank"]].reset_index()

    df.to_feather(out_dir / "caribbean.feather")

