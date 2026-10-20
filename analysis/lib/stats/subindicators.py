from pathlib import Path

import numpy as np
import pandas as pd
import shapely
from pyogrio import read_dataframe

from analysis.constants import M_MILES

data_dir = Path("data")
src_dir = data_dir / "inputs"


def extract_cores_in_analysis_areas(subindicator, df):
    index_name = df.index.name or "index"
    out_name = subindicator["id"]

    tmp = df.explode(ignore_index=False, index_parts=False)
    # use union of individual area bounding boxes to read features
    read_mask = shapely.union_all(shapely.envelope(tmp.geometry.values))
    # NOTE: pyogrio does not currently work properly for use_arrow=True if the
    # mask does not overlap and returns no features, so we can't use it here.
    cores = read_dataframe(src_dir / subindicator["filename"], columns=["acres", "size", "geometry"], mask=read_mask)

    if len(cores) == 0:
        return None

    # find all cores that intersect any part of the AOI
    left, right = shapely.STRtree(cores.geometry.values).query(tmp.geometry.values, predicate="intersects")
    cores = pd.DataFrame(
        {
            "size": cores["size"].values.take(right),
            "acres": cores.acres.values.take(right),
            index_name: tmp.index.take(left),
        }
    )

    if len(cores) == 0:
        return None

    cores = cores.groupby(by=[index_name, "size"]).agg({"acres": ["count", "min", "max"]})
    cores.columns = ["count", "min_acres", "max_acres"]
    return (
        cores.reset_index(level=-1)
        .groupby(level=0)
        .apply(lambda row: row.set_index("size").to_dict(orient="index"))
        .rename(out_name)
    )


def extract_lines_in_analysis_areas(subindicator, df):
    index_name = df.index.name or "index"
    out_name = subindicator["id"]

    tmp = df.explode(ignore_index=False, index_parts=False)
    # use union of individual area bounding boxes to read features
    read_mask = shapely.union_all(shapely.envelope(tmp.geometry.values))
    # NOTE: pyogrio does not currently work properly for use_arrow=True if the
    # mask does not overlap and returns no features, so we can't use it here.
    lines = read_dataframe(src_dir / subindicator["filename"], columns=["value", "miles", "geometry"], mask=read_mask)

    if len(lines) == 0:
        return None

    # find all cores that intersect any part of the AOI
    left, right = shapely.STRtree(lines.geometry.values).query(tmp.geometry.values, predicate="intersects")
    lines = pd.DataFrame(
        {
            index_name: tmp.index.take(left),
            "clip_geometry": tmp.geometry.values.take(left),
            "geometry": lines.geometry.values.take(right),
            "value": lines["value"].values.take(right),
            "miles": lines.miles.values.take(right),
        }
    )

    if len(lines) == 0:
        return None

    shapely.prepare(lines.clip_geometry.values)
    contained = shapely.contains_properly(lines.clip_geometry.values, lines.geometry.values)
    # clip and recalculate the parts not fully contained
    lines.loc[~contained, "miles"] = (
        shapely.length(
            shapely.intersection(lines.loc[~contained].geometry.values, lines.loc[~contained].clip_geometry.values)
        )
        * M_MILES
    ).astype("float32")

    lines = (
        lines.groupby(by=[index_name, "value"])
        .miles.sum()
        .reset_index()
        .pivot(index=index_name, columns="value", values="miles")
    )

    # convert to list of values ordered same as subindicator
    out_cols = range(0, subindicator["values"][-1]["value"] + 1)
    for col in out_cols:
        if col not in lines.columns:
            lines[col] = np.float32(0)

    return lines[out_cols].apply(lambda x: x.values, axis=1).rename(out_name)


def extract_huc12_species_counts_in_analysis_areas(subindicator, df):
    index_name = df.index.name or "index"
    out_name = subindicator["id"]

    tmp = df.explode(ignore_index=False, index_parts=False)
    # use union of individual area bounding boxes to read features
    read_mask = shapely.union_all(shapely.envelope(tmp.geometry.values))
    # NOTE: pyogrio does not currently work properly for use_arrow=True if the
    # mask does not overlap and returns no features, so we can't use it here.
    huc12 = read_dataframe(
        src_dir / subindicator["filename"], columns=["HUC12", "species_ids", "geometry"], mask=read_mask
    )

    if len(huc12) == 0:
        return None

    # find all cores that intersect any part of the AOI
    left, right = shapely.STRtree(huc12.geometry.values).query(tmp.geometry.values, predicate="intersects")
    huc12 = pd.DataFrame(
        {
            index_name: tmp.index.take(left),
            "HUC12": huc12.HUC12.values.take(right),
            "species_ids": huc12.species_ids.take(right),
        }
    )

    if len(huc12) == 0:
        return None

    # convert species_ids to list
    huc12["species_ids"] = huc12.species_ids.str.split(",").apply(lambda x: [int(v) for v in x if v != ""])

    huc12 = (
        huc12.groupby(by=[index_name])
        .agg({"HUC12": "nunique", "species_ids": "sum"})
        .rename(columns={"HUC12": "huc12_count", "species_ids": "count"})
    )
    huc12["huc12_count"] = huc12.huc12_count.astype("uint16")
    huc12["count"] = huc12["count"].apply(set).apply(len).astype("uint8")
    huc12[out_name] = huc12[["huc12_count", "count"]].to_dict(orient="records")

    return huc12[out_name]
