import pandas as pd

from analysis.constants import ANALYSIS_REGION_NAME
from analysis.lib.xlsx.style import CHAR_PER_WIDTH_UNIT, add_good_condition_row, set_cell_styles, set_column_widths


def get_value_columns(values):
    return [f"{v['label'].replace(' (', '\n(')}\n(acres)" for v in values]


def add_basic_results_sheet(
    xlsx: pd.ExcelWriter, df: pd.DataFrame, dataset: dict, name_col_width: float, area_label: str, get_value_order=None
):
    """Add a sheet for one of the Blueprint datasets (Blueprint, corridors, indicators)
    or other simple raster results dataset.

    Parameters
    ----------
    xlsx : pd.ExcelWriter
    df : pd.DataFrame
    dataset : dict
        dataset object with info
    name_col_width : float
        width of name column
    area_label : str
        name of analysis area acres column
    get_value_order : function, optional (default: None)
        if defined, function that returns value columns in correct order
    """
    sheet_name = dataset.get("sheet_name", None) or dataset["label"]
    values = dataset["values"]
    nodata_label = dataset.get(
        "nodata_label",
        f"Outside extent of this dataset but within {ANALYSIS_REGION_NAME} data extent\n(acres)",
    )
    # good threshold is only applicable to indicators
    good_threshold = dataset.get("goodThreshold", None)

    value_columns = get_value_columns(values)
    col_width = min(max([len(c) for c in value_columns]) * CHAR_PER_WIDTH_UNIT, 18)

    # split list into columns
    tmp = df[dataset["id"]].apply(pd.Series)
    tmp.columns = value_columns
    tmp = df[["overlap"]].join(tmp)

    # calculate area outside
    tmp["outside"] = tmp.overlap - tmp[value_columns].sum(axis=1)
    # remove small rounding-related errors
    tmp.loc[tmp.outside < 0, "outside"] = 0

    # reorder columns
    if get_value_order is not None:
        value_columns = get_value_order(value_columns)
    tmp = tmp[["overlap", "outside"] + value_columns]

    # drop outside indicator col
    has_area_outside = tmp.outside.max() > 1e-2
    if not has_area_outside:
        tmp = tmp.drop(columns=["outside"])

    tmp.rename(columns={"overlap": area_label, "outside": nodata_label}).reset_index().to_excel(
        xlsx, sheet_name=sheet_name, index=False
    )

    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width] + ([col_width] * len(tmp.columns)))
    set_cell_styles(ws, area_columns=range(1, len(tmp.columns) + 3))

    if good_threshold:
        # NOTE: this only applies to indicators, which are always in greatest to least order
        offset = 3 if has_area_outside else 2
        # pos = [i for i, v in enumerate(values[::-1]) if v["value"] == good_threshold][0]
        pos = [v["value"] for v in values[::-1]].index(good_threshold) + 1
        add_good_condition_row(ws, offset, offset + len(values), break_col=pos)
