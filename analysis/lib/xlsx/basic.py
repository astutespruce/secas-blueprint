import pandas as pd

from analysis.constants import ANALYSIS_REGION_NAME
from analysis.lib.xlsx.style import CHAR_PER_WIDTH_UNIT, add_good_condition_row, set_cell_styles, set_column_widths


def add_basic_results_sheet(
    xlsx: pd.ExcelWriter, df: pd.DataFrame, dataset: dict, name_col_width: float, area_label: str
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
    """
    sheet_name = dataset.get("sheet_name", dataset["label"])
    values = dataset["values"]
    nodata_label = dataset.get(
        "nodata_label",
        f"Outside {sheet_name.lower()} data extent within {ANALYSIS_REGION_NAME} data extent (acres)",
    )
    # good threshold is only applicable to indicators
    good_threshold = dataset.get("goodThreshold", None)

    columns = [f"{v['label']} (acres)" for v in values]
    col_width = min(max([len(c) for c in columns]) * CHAR_PER_WIDTH_UNIT, 16)

    # split list into columns
    tmp = df[dataset["id"]].apply(pd.Series)
    tmp.columns = columns
    tmp = df[["overlap"]].join(tmp)

    # calculate area outside
    tmp["outside"] = tmp.overlap - tmp[columns].sum(axis=1)
    # remove small rounding-related errors
    tmp.loc[tmp.outside < 0, "outside"] = 0

    # reorder columns
    tmp = tmp[["overlap", "outside"] + columns]
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
        pos = [i for i, v in enumerate(values) if v["value"] == good_threshold][0]
        offset = 3 if has_area_outside else 2
        add_good_condition_row(ws, offset, offset + len(values), pos)
