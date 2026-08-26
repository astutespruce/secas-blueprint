import pandas as pd

from analysis.constants import SLR_DEPTH, SLR_DEPTH_VALUES, SLR_NODATA_VALUES, SLR_PROJ, SLR_PROJ_SCENARIOS, SLR_YEARS
from analysis.lib.xlsx.style import add_caption, set_cell_styles, set_column_widths

depth_value_columns = [f"Inundated at {v['label']} (acres)" for v in SLR_DEPTH_VALUES] + [
    f"{v['label']} (acres)" for v in SLR_NODATA_VALUES
]

proj_value_columns = ["Has projected SLR?", "SLR scenario"] + [f"{year}\n(feet)" for year in SLR_YEARS]


def add_slr_depth_sheet(
    xlsx: pd.ExcelWriter,
    df: pd.DataFrame,
    name_col_width: float,
    area_col_width: float,
    area_label: str,
    table_counter: int,
):
    """Add SLR inundation depth sheet.

    Parameters
    ----------
    xlsx : pd.ExcelWriter
    df : pd.DataFrame
    name_col_width : float
        width of name column
    area_col_width : float
        width of area column
    area_label : str
        name of analysis area acres column
    table_counter : int
    """
    dataset = SLR_DEPTH
    sheet_name = dataset["sheet_name"]
    caption = dataset["caption"] + "."

    # split values into columns
    slr = df[SLR_DEPTH["id"]].apply(pd.Series)

    # set NODATA into value 13
    outside = df.overlap - slr.sum(axis=1)
    outside.loc[outside < 0] = 0
    slr[13] += outside

    slr = df[["overlap"]].join(slr)
    slr.columns = ["overlap"] + depth_value_columns

    # reorder columns so that SLR not available (last column) comes first
    slr = (
        slr[["overlap", depth_value_columns[-1]] + depth_value_columns[:-1]]
        .rename(columns={"overlap": area_label})
        .reset_index()
    )

    # drop unnecessary nodata
    remove_cols = []
    for col in depth_value_columns[-3:]:
        if slr[col].sum() == 0:
            remove_cols.append(col)
    if remove_cols:
        slr = slr.drop(columns=remove_cols)

    num_value_cols = len(slr.columns) - 2

    slr.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width, area_col_width] + ([18] * (num_value_cols + 1)))
    set_cell_styles(ws, area_columns=[1] + list(range(2, num_value_cols + 3)))

    add_caption(ws, table_counter, caption)


def add_slr_projection_sheet(
    xlsx: pd.ExcelWriter,
    df: pd.DataFrame,
    name_col_width: float,
    area_col_width: float,
    area_label: str,
    table_counter: int,
):
    """Add sheet with decadal projections for each analysis unit, only if
    there is SLR at 10ft within the analysis unit.
    """
    dataset = SLR_PROJ
    sheet_name = dataset["sheet_name"]
    caption = dataset["caption"] + "."
    value_label = dataset["valueLabel"]
    caption += f"\nValues show {value_label[0].lower()}{value_label[1:]}."

    # transform data into one row per SLR scenario per analysis unit
    slr = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        # must also have depth to show projection data
        if row.overlap == 0 or row.get(SLR_DEPTH["id"], None) is None or not len(row.get(SLR_PROJ["id"], [])):
            slr.append([id, row.overlap, "no", ""] + [""] * len(SLR_YEARS))
            counter += 1
        else:
            for scenario in row[SLR_PROJ["id"]]:
                slr.append(
                    [id, row.overlap, "yes", SLR_PROJ_SCENARIOS[scenario["scenario"]]] + list(scenario["values"])
                )
                counter += 1

            breaks.append(counter)

    slr = pd.DataFrame(
        slr,
        columns=[df.index.name, area_label] + proj_value_columns,
    )

    slr.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width, area_col_width, 10, 18] + ([12] * len(SLR_YEARS)))
    # SLR values are not really areas but we want 2 decimal places
    set_cell_styles(ws, breaks=breaks, area_columns=[1] + list(range(4, len(SLR_YEARS) + 5)))

    add_caption(ws, table_counter, caption)
