import pandas as pd

from analysis.constants import SLR_DEPTH, SLR_DEPTH_VALUES, SLR_NODATA_VALUES, SLR_PROJ, SLR_PROJ_SCENARIOS, SLR_YEARS
from analysis.lib.xlsx.writer import write_excel

depth_value_columns = [f"Inundated at {v['label']}\n(acres)" for v in SLR_DEPTH_VALUES] + [
    f"{v['label']}\n(acres)" for v in SLR_NODATA_VALUES
]

proj_value_columns = ["Has projected SLR?", "SLR scenario"] + [f"{year}\n(feet)" for year in SLR_YEARS]


def add_slr_depth_sheet(xlsx: pd.ExcelWriter, df: pd.DataFrame, name_col_width: float, outside_area_label: str):
    """Add SLR inundation depth sheet.

    Parameters
    ----------
    xlsx : pd.ExcelWriter
    df : pd.DataFrame
    name_col_width : float
        width of name column
    outside_area_label : str
        name of outside analysis area acres column
    """
    dataset = SLR_DEPTH
    nodata_label = "Outside extent of this dataset\n(acres)"

    slr = df[["rasterized_acres", "outside_extent_acres", "outside_extent_percent"]].join(
        df[SLR_DEPTH["id"]].apply(pd.Series)
    )
    slr.columns = (
        [
            "rasterized_acres",
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
        ["outside_extent_acres", "outside_dataset_acres"]
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
            "outside_extent_acres": outside_area_label,
            "outside_extent_percent": outside_area_label.replace("(acres)", "(percent)"),
            "outside_dataset_acres": nodata_label,
            "outside_dataset_percent": nodata_label.replace("(acres)", "(percent)"),
        }
    ).reset_index()

    num_area_cols = num_value_cols + int(has_area_outside_extent) + int(has_area_outside_dataset) + 1
    column_widths = [name_col_width] + ([18] * (len(slr.columns) - 1))
    area_columns = list(range(num_area_cols))
    percent_columns = list(range(num_area_cols, num_area_cols + num_area_cols))
    write_excel(
        xlsx,
        slr,
        sheet_name=dataset["sheet_name"],
        caption=dataset["caption"] + ".",
        column_widths=column_widths,
        area_columns=area_columns,
        percent_columns=percent_columns,
        add_percent_divider=True,
    )


def add_slr_projection_sheet(xlsx: pd.ExcelWriter, df: pd.DataFrame, name_col_width: float):
    """Add sheet with decadal projections for each analysis unit, only if
    there is SLR at 10ft within the analysis unit.
    """
    dataset = SLR_PROJ
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
            slr.append([id, "no", ""] + [""] * len(SLR_YEARS))
            counter += 1
        else:
            for scenario in row[SLR_PROJ["id"]]:
                slr.append([id, "yes", SLR_PROJ_SCENARIOS[scenario["scenario"]]] + list(scenario["values"]))
                counter += 1

            breaks.append(counter)

    slr = pd.DataFrame(
        slr,
        columns=[df.index.name] + proj_value_columns,
    )

    column_widths = [name_col_width, 10, 18] + ([12] * len(SLR_YEARS))
    area_columns = [1] + list(range(4, len(SLR_YEARS) + 5))
    write_excel(
        xlsx,
        slr,
        sheet_name=dataset["sheet_name"],
        caption=caption,
        column_widths=column_widths,
        area_columns=area_columns,
        # only include breaks if they are not incremental
        breaks=None if breaks == list(range(len(df))) else breaks,
    )
