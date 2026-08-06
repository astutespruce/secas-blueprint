import pandas as pd

from analysis.constants import SLR_YEARS, SLR_DEPTH, SLR_DEPTH_VALUES, SLR_NODATA_VALUES, SLR_PROJ

from analysis.lib.xlsx.style import set_cell_styles, set_column_widths


def add_slr_depth_sheet(
    xlsx: pd.ExcelWriter, df: pd.DataFrame, name_col_width: float, area_col_width: float, area_label: str
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
    """
    dataset = SLR_DEPTH
    sheet_name = dataset["sheet_name"]

    # split values into columns
    depth_cols = [f"Inundated at {v['label']} (acres)" for v in SLR_DEPTH_VALUES]
    nodata_cols = [f"{v['label']} (acres)" for v in SLR_NODATA_VALUES]
    columns = depth_cols + nodata_cols

    # set NODATA into value 13
    slr = df[SLR_DEPTH["id"]].apply(pd.Series)
    outside = df.overlap - slr.sum(axis=1)
    outside.loc[outside < 0] = 0
    slr[13] += outside

    slr = df[["overlap"]].join(slr)
    slr.columns = ["overlap"] + columns

    # reorder columns
    slr = slr[["overlap", nodata_cols[2]] + depth_cols + nodata_cols[:2]].rename(columns={"overlap": area_label})

    # drop unnecessary nodata
    remove_cols = []
    for col in nodata_cols:
        if slr[col].sum() == 0:
            remove_cols.append(col)
    if remove_cols:
        slr = slr.drop(columns=remove_cols)

    num_value_cols = len(slr.columns) - 2

    slr.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width, area_col_width, 12] + ([12] * num_value_cols))
    set_cell_styles(ws, area_columns=[1] + list(range(2, num_value_cols + 3)))


def add_slr_projection_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    """Add sheet with decadal projections for each analysis unit, only if
    there is SLR at 10ft within the analysis unit.
    """
    dataset = SLR_PROJ
    sheet_name = dataset["sheet_name"]

    # transform data into one row per SLR scenario per analysis unit
    slr = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        # must also have depth to show projection data
        if row.overlap == 0 or row.get(SLR_DEPTH["id"], None) is None or row.get(SLR_PROJ["id"], None) is None:
            slr.append([id, row.overlap, "no", ""] + [""] * len(SLR_YEARS))
            counter += 1
        else:
            for scenario, values in row.slr_proj.items():
                slr.append([id, row.overlap, "yes", scenario] + list(values))
                counter += 1

            breaks.append(counter)

    slr = pd.DataFrame(
        slr,
        columns=[df.index.name, area_label, "Has projected SLR?", "SLR scenario"]
        + [f"{year} (ft)" for year in SLR_YEARS],
    )

    slr.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width, area_col_width, 10, 18] + ([8] * len(SLR_YEARS)))
    set_cell_styles(ws, breaks=breaks, area_columns=[1])
