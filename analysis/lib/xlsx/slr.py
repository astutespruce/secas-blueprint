import pandas as pd

from analysis.constants import SLR_DEPTH, SLR_DEPTH_VALUES, SLR_NODATA_VALUES, SLR_PROJ, SLR_PROJ_SCENARIOS, SLR_YEARS
from analysis.lib.xlsx.style import add_caption, set_cell_styles, set_column_widths

depth_value_columns = [f"Inundated at {v['label']}\n(acres)" for v in SLR_DEPTH_VALUES] + [
    f"{v['label']}\n(acres)" for v in SLR_NODATA_VALUES
]

proj_value_columns = ["Has projected SLR?", "SLR scenario"] + [f"{year}\n(feet)" for year in SLR_YEARS]


def add_slr_depth_sheet(
    xlsx: pd.ExcelWriter,
    df: pd.DataFrame,
    name_col_width: float,
    area_col_width: float,
    area_label: str,
    outside_area_label: str,
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
    outside_area_label : str
        name of outside analysis area acres column
    table_counter : int
    """
    dataset = SLR_DEPTH
    sheet_name = dataset["sheet_name"]
    caption = dataset["caption"] + "."
    nodata_label = "Outside extent of this dataset\n(acres)"

    slr = df[["rasterized_acres", "overlap_acres", "outside_extent_acres", "outside_extent_percent"]].join(
        df[SLR_DEPTH["id"]].apply(pd.Series)
    )
    slr.columns = (
        [
            "rasterized_acres",
            "overlap_acres",
            "outside_extent_acres",
            "outside_extent_percent",
        ]
        + depth_value_columns
        + ["outside_dataset_acres"]
    )

    # calculate percents
    slr["outside_dataset_percent"] = slr.outside_dataset_acres / slr.rasterized_acres
    for col in depth_value_columns:
        slr[col.replace("(acres)", "(percent)")] = slr[col] / slr.rasterized_acres

    # reorder columns so that outside_dataset_col comes before other values
    slr = slr[
        ["overlap_acres", "outside_extent_acres", "outside_dataset_acres"]
        + depth_value_columns
        + ["outside_extent_percent", "outside_dataset_percent"]
        + [col.replace("(acres)", "(percent)") for col in depth_value_columns]
    ]

    # drop unnecessary nodata
    remove_cols = []
    num_value_cols = len(depth_value_columns)
    for col in depth_value_columns[-len(SLR_NODATA_VALUES) :]:
        if slr[col].sum() == 0:
            remove_cols.append(col)
            remove_cols.append(col.replace("(acres)", "(percent)"))
            num_value_cols -= 1
    if remove_cols:
        slr = slr.drop(columns=remove_cols)

    has_area_outside_extent = slr.outside_extent_acres.max() > 1e-2
    if not has_area_outside_extent:
        slr = slr.drop(columns=["outside_extent_acres", "outside_extent_percent"])

    has_area_outside_dataset = slr.outside_dataset_acres.max() > 1e-2
    if not has_area_outside_dataset:
        slr = slr.drop(columns=["outside_dataset_acres", "outside_dataset_percent"])

    slr = slr.rename(
        columns={
            "overlap_acres": area_label,
            "outside_extent_acres": outside_area_label,
            "outside_extent_percent": outside_area_label.replace("(acres)", "(percent)"),
            "outside_dataset_acres": nodata_label,
            "outside_dataset_percent": nodata_label.replace("(acres)", "(percent)"),
        }
    ).reset_index()

    slr.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]

    set_column_widths(ws, [name_col_width, area_col_width] + ([18] * (len(slr.columns) - 2)))

    area_col_offset = 1
    num_area_cols = num_value_cols + int(has_area_outside_extent) + int(has_area_outside_dataset) + 1

    set_cell_styles(
        ws,
        area_columns=range(area_col_offset, area_col_offset + num_area_cols),
        percent_columns=range(area_col_offset + num_area_cols, area_col_offset + num_area_cols + num_area_cols),
        add_percent_divider=True,
    )

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
        if row.overlap_acres == 0 or row.get(SLR_DEPTH["id"], None) is None or not len(row.get(SLR_PROJ["id"], [])):
            slr.append([id, row.overlap_acres, "no", ""] + [""] * len(SLR_YEARS))
            counter += 1
        else:
            for scenario in row[SLR_PROJ["id"]]:
                slr.append(
                    [id, row.overlap_acres, "yes", SLR_PROJ_SCENARIOS[scenario["scenario"]]] + list(scenario["values"])
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
