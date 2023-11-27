from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
import shapely

from analysis.lib.stats.summary_units import read_unit_from_feather


src_dir = Path("data/inputs/boundaries")
parca_filename = src_dir / "parca.feather"


def get_parcas_for_aoi(df):
    """Get ownership and protection levels and other statistics for the DataFrame

    Parameters
    ----------
    df : GeoDataFrame

    Returns
    -------
    list or None
        list of {"name": <name>, "description": <>}

    """
    parca_df = gp.read_feather(parca_filename).set_index("parca_id")
    tree = shapely.STRtree(parca_df.geometry.values)

    # PARCA dataset has multiple polygons per PARCA boundary, group them back together
    parcas = (
        parca_df[["name", "description"]]
        .take(tree.query(df.geometry.values, predicate="intersects")[1])
        .groupby(level=0)
        .first()
        .sort_values(by="name")
        .to_dict(orient="records")
    )

    return parcas if len(parcas) > 0 else None


def summarize_parcas_by_units(df, out_dir):
    """Calculate overlap with ownership and protection

    Parameters
    ----------
    df : GeoDataFrame
        contains unit boundaries, indexed by id
    out_dir : str
    """
    print("Calculating overlap with PARCAs")

    parca_df = gp.read_feather(parca_filename)  # .set_index("parca_id")

    # since PARCAs occur in just one area, use them as the left side of the query
    tree = shapely.STRtree(df.geometry.values)
    right, left = tree.query(parca_df.geometry.values, predicate="intersects")

    index_name = df.index.name
    results = (
        pd.DataFrame(
            {
                index_name: df.index.values.take(left),
                "parca_id": parca_df.parca_id.values.take(right),
                "name": parca_df.name.values.take(right),
                "description": parca_df.description.values.take(right),
            }
        )
        # PARCA dataset has multiple polygons per PARCA boundary, group them back together
        .groupby([index_name, "parca_id"])
        .first()
        .reset_index()
        .sort_values(by=[index_name, "name"])
    )

    results.reset_index().to_feather(out_dir / "parca.feather")


def get_parca_results(results_dir, unit):
    """Fetch PARCAs for the unit_id

    Parameters
    ----------
    results_dir : Path
        path containing results
    unit : pandas.Series
        row for this unit from the units dataset, indexed by unit ID (unit.name)

    Returns
    -------
    list
        [{"name": <name>, "description": <description>}]
    """

    results = read_unit_from_feather(results_dir / "parca.feather", unit.name)

    if len(results) == 0:
        return None

    return results.to_dict(orient="records")
