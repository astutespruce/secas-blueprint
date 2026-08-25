import pandas as pd

from analysis.constants import ANALYSIS_REGION_NAME, URBAN_BY_DECADE, URBAN_YEARS
from analysis.lib.xlsx.style import set_cell_styles, set_column_widths

value_columns = (
    ["Urban in 2021\n(acres)"]
    + [f"{year} projected extent\n(acres)" for year in URBAN_YEARS]
    + ["Not projected to urbanize by 2100\n(acres)"]
)


def add_urbanization_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    """Add urbanization sheet.

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
    dataset = URBAN_BY_DECADE
    sheet_name = dataset.get("sheet_name", dataset["label"])
    nodata_label = dataset.get(
        "nodata_label",
        f"Outside extent of this dataset but within {ANALYSIS_REGION_NAME} data extent\n(acres)",
    )

    # transform data into one row for high and low urbanization per analysis unit
    columns = value_columns + ["outside"]

    # convert values to columns
    urban = df[["overlap"]].join(df[URBAN_BY_DECADE["id"]].apply(pd.Series))
    urban.columns = ["overlap"] + columns
    # move nodata to left
    urban = urban[["overlap", "outside"] + value_columns]
    if urban.outside.max() < 1e-2:
        urban = urban.drop(columns=["outside"])

    urban.rename(columns={"overlap": area_label, "outside": nodata_label}).reset_index().to_excel(
        xlsx, sheet_name=sheet_name, index=False
    )

    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width, area_col_width] + ([18] * (len(urban.columns) - 1)))
    set_cell_styles(ws, area_columns=range(1, len(urban.columns) + 3))
