import pandas as pd

from analysis.constants import PROTECTED_AREAS_POLY

from analysis.lib.xlsx.style import set_cell_styles, set_column_widths


def add_protected_areas_poly_sheet(
    xlsx: pd.ExcelWriter, df: pd.DataFrame, name_col_width: float, area_col_width: float
):
    dataset = PROTECTED_AREAS_POLY
    sheet_name = dataset.get("sheet_name", dataset["label"])

    # transform data into one row per per protected area per analysis unit
    protected_areas = []
    breaks = []
    counter = 0
    col = dataset["id"]
    for id, row in df.iterrows():
        if hasattr(row, col) and row[col]:
            for pa in row[col]:
                protected_areas.append([id, f"{row.acres:.2f}", pa["name"], pa["owner"], f"{pa['acres']:.2f}"])
        else:
            protected_areas.append([id, f"{row.acres:.2f}", "no protected areas at this location", "", ""])
            counter += 1

        breaks.append(counter)

    protected_areas = pd.DataFrame(
        protected_areas,
        columns=[df.index.name, "GIS Acres", "Protected area name", "Owner", "Overlap acres"],
    )
    protected_areas.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]

    set_column_widths(ws, [name_col_width, area_col_width, 40, 30, area_col_width])
    set_cell_styles(ws)
