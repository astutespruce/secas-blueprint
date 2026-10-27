from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import shapely
from progress.bar import Bar
from pyogrio import read_dataframe

from analysis.constants import INDICATORS, M_MILES, STANDARD_RESOLUTION
from analysis.lib.io import read_unit_from_feather
from analysis.lib.pdf.format import format_number, format_percent, pluralize
from analysis.lib.raster import get_aligned_windows

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
    """Summarize cores in area of interest

    Parameters
    ----------
    subindicator : dict
        subindicator info
    df : GeoDataFrame
        area of interest data frame

    Returns
    -------
    dict
        {"footnote": <value>}
    """
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
    cores["label"] = (
        cores["count"].apply(format_number)
        + " "
        + cores["value"]
        + " cores ranging from "
        + cores.min_acres.apply(format_number)
        + " to "
        + cores.max_acres.apply(format_number)
        + " acres in size"
    )
    ix = cores.min_acres == cores.max_acres
    if ix.any():
        cores.loc[ix, "label"] = (
            cores["count"].apply(format_number)
            + " "
            + cores["value"]
            + cores["count"].apply(lambda x: pluralize(" core ", " cores ", x))
            + "that"
            + cores["count"].apply(lambda x: pluralize(" is ", " are ", x))
            + cores.loc[ix].min_acres.apply(format_number)
            + " acres in size"
        )

    return {"footnote": f"This area intersects {values_list_to_sentence(cores.label.tolist())}."}


def summarize_cores_in_summary_units(subindicator, df, out_dir):
    """Summarize cores by summary unit

    Outputs one row per size class per id in df where cores are present

    Parameters
    ----------
    subindicator : dict
        subindicator info
    df : GeoDataFrame
        units data frame
    out_dir : Path
    """
    index_name = df.index.name
    cores = read_dataframe(data_dir / subindicator["filename"], columns=["acres", "size", "geometry"], use_arrow=True)

    # find all cores that intersect any part of the AOI
    left, right = shapely.STRtree(cores.geometry.values).query(df.geometry.values, predicate="intersects")
    cores = pd.DataFrame(
        {index_name: df.index.take(left), "acres": cores.acres.take(right), "size": cores["size"].take(right)}
    )
    cores = cores.groupby(by=[index_name, "size"]).agg({"size": "count", "acres": ["min", "max"]})
    cores.columns = ["count", "min_acres", "max_acres"]
    cores.reset_index().to_feather(out_dir / f"{subindicator['id']}.feather")


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
        "footnote": f"These results are based on approximately {format_number(total_miles)} {pluralize('mile', 'miles', total_miles)} of coastal shoreline, {values_list_to_sentence(values)}."
    }


def summarize_lines_in_summary_units(subindicator, df, out_dir):
    """Summarize a linear subindicator by value and length

    Outputs one row per value per id in df that had linear features present

    Parameters
    ----------
    subindicator : dict
        subindicator info
    df : GeoDataFrame
        units data frame
    out_dir : Path
    """
    index_name = df.index.name
    lines = read_dataframe(data_dir / subindicator["filename"], columns=["value", "miles", "geometry"], use_arrow=True)

    left, right = shapely.STRtree(lines.geometry.values).query(df.geometry.values, predicate="intersects")
    lines = pd.DataFrame(
        {
            index_name: df.index.take(left),
            "clip_geom": df.geometry.values.take(left),
            "value": lines.value.values.take(right),
            "miles": lines.miles.values.take(right),
            "geometry": lines.geometry.values.take(right),
        }
    )

    shapely.prepare(lines.clip_geom.values)
    contained = shapely.contains_properly(lines.clip_geom.values, lines.geometry.values)
    lines.loc[~contained, "geometry"] = shapely.intersection(
        lines.loc[~contained].clip_geom.values, lines.loc[~contained].geometry.values
    )
    lines.loc[~contained, "miles"] = (shapely.length(lines.loc[~contained].geometry.values) * M_MILES).astype("float32")
    lines = lines.groupby(by=[index_name, "value"]).miles.sum()
    lines.reset_index().to_feather(out_dir / f"{subindicator['id']}.feather")


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
            "clip_geom": df.geometry.values.take(left),
            "HUC12": huc12.HUC12.values.take(right),
            "species": huc12.species.values.take(right),
            "geometry": huc12.geometry.values.take(right),
        }
    )

    if len(huc12) == 0:
        return None

    # drop any that are less than a pixel of coverage
    shapely.prepare(huc12.clip_geom.values)
    huc12["contained"] = shapely.contains_properly(huc12.clip_geom.values, huc12.geometry.values)
    huc12.loc[huc12.contained, "overlap"] = shapely.area(huc12.loc[huc12.contained].geometry.values)
    huc12.loc[~huc12.contained, "overlap"] = shapely.area(
        shapely.intersection(huc12.clip_geom.values, huc12.loc[~huc12.contained].geometry.values)
    )
    huc12 = huc12.loc[huc12.overlap > STANDARD_RESOLUTION * STANDARD_RESOLUTION].drop(columns=["contained", "overlap"])

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
        data_dir / subindicator["filename"], columns=["HUC12", "species"], mask=read_mask, where="species IS NOT NULL"
    )

    if len(huc12) == 0:
        return None

    # find all HUC12 that intersect any part of the AOI
    geom = df.geometry.values[0]
    huc12 = huc12.take(shapely.STRtree(huc12.geometry.values).query(geom, predicate="intersects"))

    if len(huc12) == 0:
        return None

    # drop any that are less than a pixel of coverage
    shapely.prepare(geom)
    huc12["contained"] = shapely.contains_properly(geom, huc12.geometry.values)
    huc12.loc[huc12.contained, "overlap"] = shapely.area(huc12.loc[huc12.contained].geometry.values)
    huc12.loc[~huc12.contained, "overlap"] = shapely.area(
        shapely.intersection(geom, huc12.loc[~huc12.contained].geometry.values)
    )
    huc12 = huc12.loc[huc12.overlap > STANDARD_RESOLUTION * STANDARD_RESOLUTION].drop(columns=["contained", "overlap"])

    if len(huc12) == 0:
        return None

    # convert species_ids to list so we can add lists and then calculate unique set
    huc12["species"] = huc12.species.fillna("").str.split("|").apply(lambda x: [v for v in x if v != ""])

    huc12_count = len(huc12)
    spp_count = len(set(huc12.species.sum()))

    if "caribbean" in subindicator["id"]:
        return {
            "footnote": f"This area overlaps with {format_number(huc12_count)} {pluralize('subwatershed', 'subwatersheds', huc12_count)} where a total of {format_number(spp_count)} unique aquatic animal SGCN have been observed."
        }

    return {
        "footnote": f"This area overlaps with {format_number(huc12_count)} {pluralize('subwatershed', 'subwatersheds', huc12_count)} where a total of {format_number(spp_count)} unique aquatic animal RSGCN have been observed.",
        "note": "You may see minor differences between the indicator results and this total reported count of unique species across all overlapping subwatersheds. This occurs because the indicator uses a slightly older version of the source data, so where they differ, we recommend using the count reported here. Future updates will synchronize both applications.",
    }


def summarize_huc12_species_by_summary_units(subindicator, df, out_dir):
    """Summarize huc12 species counts by summary unit

    NOTE: only outputs records with >= 1 species in a summary unit

    Parameters
    ----------
    subindicator : dict
        subindicator info
    df : GeoDataFrame
        units data frame
    out_dir : Path
    """
    huc12_species = read_dataframe(
        data_dir / subindicator["filename"],
        columns=["HUC12", "species"],
        read_geometry=False,
        use_arrow=True,
        where="species IS NOT NULL",
    ).set_index("HUC12")

    huc12_species["count"] = (huc12_species.species.str.count(r"\|") + 1).astype("uint16")
    huc12_species = df[[]].join(huc12_species["count"], how="inner")

    if len(huc12_species):
        huc12_species.reset_index().to_feather(out_dir / f"{subindicator['id']}.feather")


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

    label = subindicator["label"].lower().split("species")[0].replace(" & ", " and ").strip()

    return {
        "footnote": f"This area includes predicted suitable habitat for {format_number(len(species))} {label} species."
    }


def summarize_stacked_bit_species_by_summary_units(
    subindicator, df, units_dataset, out_dir, progress_label="Summarizing data..."
):
    """Summarize unique counts and species lists for stacked-bit rasters

    Parameters
    ----------
    subindicator : dict
        subindicator info
    df : GeoDataFrame
        units data frame
    units_dataset : open rasterio dataset
    out_dir : Path
    progress_label : str, optional

    """

    table = pd.read_feather(data_dir / subindicator["table_filename"], columns=["group"])
    groups = sorted(table.group.unique().tolist())
    files = {}
    try:
        files.update(
            {group: rasterio.open(data_dir / subindicator["filename"].format(group=group)) for group in groups}
        )

        totals = np.zeros((len(df), len(groups)), dtype="uint64")
        for i, (_, row) in Bar(progress_label, max=len(df)).iter(enumerate(df.iterrows())):
            for group in table.group.unique():
                value_dataset = files[group]
                unit_window, value_window = get_aligned_windows(
                    units_dataset, value_dataset, bounds=(row.minx, row.miny, row.maxx, row.maxy)
                )
                if (
                    unit_window.width == 0
                    or unit_window.height == 0
                    or value_window.width == 0
                    or value_window.height == 0
                ):
                    continue

                unit_mask = units_dataset.read(1, window=unit_window) == row.value
                data = value_dataset.read(1, window=value_window)
                data = np.where(unit_mask == True, data, np.uint64(0))
                # extract all bits that are set (bitwise OR)
                totals[i, group] = np.bitwise_or.reduce(data.flat)

                # ruff: disable[ERA001]
                # DEBUG
                # write_raster(
                #     "/tmp/unit.tif",
                #     unit_mask.astype("uint8"),
                #     units_dataset.window_transform(unit_window),
                #     crs=units_dataset.crs,
                #     nodata=255,
                # )

                # write_raster(
                #     "/tmp/values.tif",
                #     data,
                #     value_dataset.window_transform(value_window),
                #     crs=value_dataset.crs,
                #     nodata=255,
                # )
                # ruff: enable[ERA001]

        # index here is same as value in df
        bits = pd.DataFrame(totals, columns=groups, index=df.index).melt(
            var_name="group", value_name="value", ignore_index=False
        )
        # drop any that didn't have any species present
        bits = bits.loc[bits.value != 0].copy()
        # NOTE: have to flip bit order
        bits["bit"] = bits["value"].apply(
            lambda v: set(np.arange(64)[[bool(int(x)) for x in np.binary_repr(v, width=64)[::-1]]].tolist())
        )
        bits = bits.explode("bit").groupby(level=0).size().astype("uint8").rename("count")
        bits.reset_index().to_feather(out_dir / f"{subindicator['id']}.feather")

    finally:
        for raster in files.values():
            raster.close()


def summarize_subindicators_by_summary_units(df, units_dataset, out_dir):
    """Summarize subindicators by summary units

    Each subindicator writes its own file to out_dir, named based on its ID.

    Parameters
    ----------
    df : GeoDataFrame
        units data frame
    units_dataset : open rasterio reader
        units raster
    out_dir : Path
    """
    subindicators = [i["subindicator"] for i in INDICATORS if "subindicator" in i]

    for subindicator in subindicators:
        if subindicator["type"] == "stacked_bit_species":
            summarize_stacked_bit_species_by_summary_units(
                subindicator, df, units_dataset, out_dir, progress_label=f"Summarizing {subindicator['label']}..."
            )

        elif subindicator["type"] == "cores":
            summarize_cores_in_summary_units(subindicator, df, out_dir)

        elif subindicator["type"] == "lines":
            summarize_lines_in_summary_units(subindicator, df, out_dir)

        elif subindicator["type"] == "huc12_species":
            summarize_huc12_species_by_summary_units(subindicator, df, out_dir)


def get_subindicator_unit_results(results_dir, unit):
    """Get results for each subindicator present in unit

    NOTE: only valid for subwatersheds

    Parameters
    ----------
    results_dir : Path
    unit : Series
    """

    results = {}
    subindicators = [i["subindicator"] for i in INDICATORS if "subindicator" in i]

    for subindicator in subindicators:
        results_filename = results_dir / f"{subindicator['id']}.feather"
        if not results_filename.exists():
            continue

        unit_results = read_unit_from_feather(results_filename, unit.name)
        if len(unit_results) == 0:
            continue

        if subindicator["type"] == "stacked_bit_species":
            unit_results = unit_results.iloc[0]
            label = subindicator["label"].lower().split("species")[0].replace(" & ", " and ").strip()
            results[subindicator["id"]] = {
                "footnote": f"This area includes predicted suitable habitat for {format_number(unit_results['count'])} {label} species."
            }

        elif subindicator["type"] == "cores":
            # we join back to original values to put in correct
            cores = pd.DataFrame(subindicator["values"][::-1]).join(
                unit_results.set_index("size"), on="value", how="inner"
            )
            cores["label"] = (
                cores["count"].apply(format_number)
                + " "
                + cores["value"]
                + " cores ranging from "
                + cores.min_acres.apply(format_number)
                + " to "
                + cores.max_acres.apply(format_number)
                + " acres in size"
            )
            ix = cores.min_acres == cores.max_acres
            if ix.any():
                cores.loc[ix, "label"] = (
                    cores["count"].apply(format_number)
                    + " "
                    + cores["value"]
                    + cores["count"].apply(lambda x: pluralize(" core ", " cores ", x))
                    + "that"
                    + cores["count"].apply(lambda x: pluralize(" is ", " are ", x))
                    + cores.loc[ix].min_acres.apply(format_number)
                    + " acres in size"
                )

            results[subindicator["id"]] = {
                "footnote": f"This area intersects {values_list_to_sentence(cores.label.tolist())}."
            }

        elif subindicator["type"] == "lines":
            total_miles = unit_results.miles.sum()
            lines = pd.DataFrame(subindicator["values"][::-1]).join(
                unit_results.set_index("value"), on="value", how="inner"
            )
            lines["percent"] = 100 * lines["miles"] / total_miles
            values = (lines.percent.apply(format_percent) + "% of which are " + lines.label.str.lower()).tolist()
            results[subindicator["id"]] = {
                "footnote": f"These results are based on approximately {format_number(total_miles)} {pluralize('mile', 'miles', total_miles)} of coastal shoreline, {values_list_to_sentence(values)}."
            }

        elif subindicator["type"] == "huc12_species":
            unit_results = unit_results.iloc[0]

            if "caribbean" in subindicator["id"]:
                results[subindicator["id"]] = {
                    "footnote": f"A total of {format_number(unit_results['count'])} unique aquatic animal SGCN have been observed in this subwatershed."
                }

            results[subindicator["id"]] = {
                "footnote": f"A total of {format_number(unit_results['count'])} unique aquatic animal RSGCN have been observed in this subwatershed.",
                "note": "You may see minor differences between the indicator results and this total reported count of unique species across all overlapping subwatersheds. This occurs because the indicator uses a slightly older version of the source data, so where they differ, we recommend using the count reported here. Future updates will synchronize both applications.",
            }

    return results
