from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import shapely
from pyogrio import read_dataframe

from analysis.constants import M_MILES
from analysis.lib.pdf.format import format_number, format_percent, pluralize

data_dir = Path("data/inputs")


def values_list_to_sentence(values):
    """Convert a values list of >= 1 values into sentence form.

    Parameters
    ----------
    values : list-like of str

    Returns
    -------
    str
    """
    if len(values) == 1:
        return values[0]
    elif len(values) == 2:
        return " and ".join(values)

    return f"{', '.join(values[:-1])}, and {values[-1]}"


def extract_cores_in_analysis_areas(subindicator, df):
    """Find all overlapping intact habitat cores and summarize their count, min,
    and max area by size class.

    Size class matches the values of the associated indicator.

    Parameters
    ----------
    subindicator : dict
        subindicator info
    df : GeoDataFrame
        analysis units

    Returns
    -------
    Series
        Series indexed on index of df containing dict of dict of stats: {<size>: {"count": <count>, "min_acres": <min_acres>, "max_acres": <max_acres>}, ... }
    """
    index_name = df.index.name or "index"
    out_name = subindicator["id"]

    tmp = df.explode(ignore_index=False, index_parts=False)
    # use union of individual area bounding boxes to read features
    read_mask = shapely.union_all(shapely.envelope(tmp.geometry.values))
    # NOTE: pyogrio does not currently work properly for use_arrow=True if the
    # mask does not overlap and returns no features, so we can't use it here.
    cores = read_dataframe(data_dir / subindicator["filename"], columns=["acres", "size", "geometry"], mask=read_mask)

    if len(cores) == 0:
        return None

    # find all cores that intersect any part of the AOI
    left, right = shapely.STRtree(cores.geometry.values).query(df.geometry.values, predicate="intersects")
    cores = pd.DataFrame(
        {
            "size": cores["size"].values.take(right),
            "acres": cores.acres.values.take(right),
            index_name: df.index.take(left),
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


def summarize_cores_in_aoi(subindicator, df):
    tmp = df.explode(ignore_index=False, index_parts=False)
    # use union of individual area bounding boxes to read features
    read_mask = shapely.union_all(shapely.envelope(tmp.geometry.values))
    # NOTE: pyogrio does not currently work properly for use_arrow=True if the
    # mask does not overlap and returns no features, so we can't use it here.
    cores = read_dataframe(data_dir / subindicator["filename"], columns=["acres", "size", "geometry"], mask=read_mask)

    if len(cores) == 0:
        return None

    # find all cores that intersect any part of the AOI
    cores = cores.take(shapely.STRtree(cores.geometry.values).query(df.geometry.values[0], predicate="intersects"))
    if len(cores) == 0:
        return None

    cores = cores.groupby("size").agg({"size": "count", "acres": ["min", "max"]})
    cores.columns = ["count", "min_acres", "max_acres"]
    cores = pd.DataFrame(subindicator["values"][::-1]).join(cores, on="value", how="inner")
    cores["range"] = (
        "(" + cores.min_acres.apply(format_number) + " to " + cores.max_acres.apply(format_number) + " acres)"
    )
    ix = cores.min_acres == cores.max_acres
    if ix.any():
        cores.loc[ix, "range"] = (
            "("
            + cores.loc[ix].min_acres.apply(format_number)
            + " "
            + cores.loc[ix].min_acres.apply(lambda x: pluralize("acre", "acres", x))
            + ")"
        )

    values = (
        cores["count"].apply(format_number)
        + " "
        + cores["value"]
        + " "
        + cores["count"].apply(lambda x: pluralize("core", "cores", x))
        + " "
        + cores["range"]
    ).tolist()

    return {"footnote": f"This area includes {values_list_to_sentence(values)}."}


def extract_lines_in_analysis_areas(subindicator, df):
    """Extract length of linear features by value

    Parameters
    ----------
    subindicator : dict
        subindicator info
    df : GeoDataFrame
        analysis units

    Returns
    -------
    Series
        Series indexed on index of df containing array of miles with same length
        and order as associated indicator values.
    """
    index_name = df.index.name or "index"
    out_name = subindicator["id"]

    # use union of individual area bounding boxes to read features
    read_mask = shapely.union_all(shapely.envelope(df.explode(ignore_index=False, index_parts=False).geometry.values))
    # NOTE: pyogrio does not currently work properly for use_arrow=True if the
    # mask does not overlap and returns no features, so we can't use it here.
    lines = read_dataframe(data_dir / subindicator["filename"], columns=["value", "miles", "geometry"], mask=read_mask)

    if len(lines) == 0:
        return None

    # find all lines that intersect any part of the AOI
    left, right = shapely.STRtree(lines.geometry.values).query(df.geometry.values, predicate="intersects")
    lines = pd.DataFrame(
        {
            index_name: df.index.take(left),
            "clip_geometry": df.geometry.values.take(left),
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


def summarize_lines_in_aoi(subindicator, df):
    """Summarize length of linear features by value in area of interest

    Parameters
    ----------
    subindicator : dict
        subindicator info
    df : GeoDataFrame
        area of interest

    Returns
    -------
    dict | None
        {"footnote": <footnote text>} or None
    """
    tmp = df.explode(ignore_index=False, index_parts=False)
    # use union of individual area bounding boxes to read features
    read_mask = shapely.union_all(shapely.envelope(tmp.geometry.values))
    # NOTE: pyogrio does not currently work properly for use_arrow=True if the
    # mask does not overlap and returns no features, so we can't use it here.
    lines = read_dataframe(data_dir / subindicator["filename"], columns=["value", "miles", "geometry"], mask=read_mask)

    if len(lines) == 0:
        return None

    # find all lines that intersect any part of the AOI
    bnd = df.geometry.values[0]
    shapely.prepare(bnd)
    lines = lines.take(shapely.STRtree(lines.geometry.values).query(bnd, predicate="intersects"))

    if len(lines) == 0:
        return None

    contained = shapely.contains_properly(bnd, lines.geometry.values)
    # clip and recalculate the parts not fully contained
    lines.loc[~contained, "miles"] = (
        shapely.length(shapely.intersection(lines.loc[~contained].geometry.values, bnd)) * M_MILES
    ).astype("float32")

    total_miles = lines.miles.sum()

    if total_miles < 0.001:
        return None

    lines = lines.groupby("value").miles.sum()
    # reverse order to match display in table
    lines = pd.DataFrame(subindicator["values"][::-1]).join(lines, on="value", how="inner")
    lines["percent"] = 100 * lines["miles"] / total_miles
    values = (lines.percent.apply(format_percent) + "% of which are " + lines.label.str.lower()).tolist()

    return {
        "footnote": f"These results are based on approximately {format_number(total_miles)} {pluralize('mile', 'miles', total_miles)} of coastline, {values_list_to_sentence(values)}."
    }


def extract_huc12_species_in_analysis_areas(subindicator, df):
    """Extract count of subwatersheds and count and possibly list of unique species
    across all watersheds per analysis unit.

    Species list is only included if listed as a value of the subindicator; it
    can only be used where the list of species names can be publicly disclosed.

    Parameters
    ----------
    subindicator : dict
        subindicator info
    df : GeoDataFrame
        analysis units

    Returns
    -------
    Series
        Series indexed on index of df with dict of values: {"huc12_count": <count of subwatersheds>, "count": <count of unique species>, "species": <comma-delimited list of unique species names>}
    """
    index_name = df.index.name or "index"
    out_name = subindicator["id"]

    tmp = df.explode(ignore_index=False, index_parts=False)
    # use union of individual area bounding boxes to read features
    read_mask = shapely.union_all(shapely.envelope(tmp.geometry.values))
    # NOTE: pyogrio does not currently work properly for use_arrow=True if the
    # mask does not overlap and returns no features, so we can't use it here.
    huc12 = read_dataframe(
        data_dir / subindicator["filename"], columns=["HUC12", "species", "geometry"], mask=read_mask
    )

    if len(huc12) == 0:
        return None

    # find all HUC12 that intersect any part of the AOI
    left, right = shapely.STRtree(huc12.geometry.values).query(df.geometry.values, predicate="intersects")
    huc12 = pd.DataFrame(
        {
            index_name: df.index.take(left),
            "HUC12": huc12.HUC12.values.take(right),
            "species": huc12.species.take(right),
        }
    )

    if len(huc12) == 0:
        return None

    # convert species_ids to list
    huc12["species"] = huc12.species.fillna("").str.split("|").apply(lambda x: [v for v in x if v != ""])

    huc12 = (
        huc12.groupby(by=[index_name])
        .agg({"HUC12": "nunique", "species": "sum"})
        .rename(columns={"HUC12": "huc12_count"})
    )
    huc12["huc12_count"] = huc12.huc12_count.astype("uint16")
    huc12["species"] = huc12.species.apply(set).apply(sorted)
    huc12["count"] = huc12.species.apply(len).astype("uint8")

    cols = [v["value"] for v in subindicator["values"]]
    if "species" in cols:
        huc12["species"] = huc12.species.apply(", ".join)

    huc12[out_name] = huc12[cols].to_dict(orient="records")

    return huc12[out_name]


def summarize_huc12_species_in_aoi(subindicator, df):
    """Count subwatersheds and unique species for an area of interest.  Does not
    return list of species.

    Parameters
    ----------
    subindicator : dict
        subindicator info
    df : GeoDataFrame
        area of interest

    Returns
    -------
    dict | None
        {"footnote": <footnote text>} or None
    """
    tmp = df.explode(ignore_index=False, index_parts=False)
    # use union of individual area bounding boxes to read features
    read_mask = shapely.union_all(shapely.envelope(tmp.geometry.values))
    # NOTE: pyogrio does not currently work properly for use_arrow=True if the
    # mask does not overlap and returns no features, so we can't use it here.
    huc12 = read_dataframe(
        data_dir / subindicator["filename"], columns=["HUC12", "species", "geometry"], mask=read_mask
    )

    if len(huc12) == 0:
        return None

    # find all HUC12 that intersect any part of the AOI
    huc12 = huc12.take(shapely.STRtree(huc12.geometry.values).query(df.geometry.values[0], predicate="intersects"))

    if len(huc12) == 0:
        return None

    # convert species_ids to list so we can add lists and then calculate unique set
    huc12["species"] = huc12.species.fillna("").str.split("|").apply(lambda x: [v for v in x if v != ""])

    huc12_count = len(huc12)
    spp_count = len(set(huc12.species.sum()))

    label = subindicator["label"].lower().replace("caribbean", "").split("species")[0]

    return {
        "footnote": f"This area overlaps with {format_number(huc12_count)} {pluralize('subwatershed', 'subwatersheds', huc12_count)} with a total of {format_number(spp_count)} {label} species."
    }


def summarize_stacked_bit_species_in_aoi(subindicator, rasterized_geometry):
    """Summarize count of unique species from stacked bit rasters

    Parameters
    ----------
    subindicator : dict
            subindicator info
    rasterized_geometry : RasterizedGeometry
        rasterized geometry for area of interest

    Returns
    -------
    dict | None
        {"footnote": <value>} or None
    """

    species = set()

    table = pd.read_feather(data_dir / subindicator["table_filename"], columns=subindicator["table_columns"])
    for group in table.group.unique():
        with rasterio.open(data_dir / subindicator["filename"].format(group=group)) as src:
            bits = rasterized_geometry.get_set_bits(src)
            species.update(table.loc[(table.group == group) & table.bit.isin(bits)].value.tolist())

    if not species:
        return None

    label = subindicator["label"].lower().replace("caribbean", "").split("species")[0]

    return {"footnote": f"This area includes {format_number(len(species))} {label} species."}
