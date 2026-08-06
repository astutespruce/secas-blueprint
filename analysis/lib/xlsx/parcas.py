import pandas as pd

from analysis.constants import PARCAS_POLY

from analysis.lib.xlsx.style import set_cell_styles, set_column_widths


def add_parcas_poly_sheet(xlsx: pd.ExcelWriter, df: pd.DataFrame, name_col_width: float, area_col_width: float):
    dataset = PARCAS_POLY
    sheet_name = dataset.get("sheet_name", dataset["label"])

    # transform data into one row per per protected area per analysis unit
    parcas = []
    breaks = []
    counter = 0
    col = dataset["id"]
    for id, row in df.iterrows():
        if hasattr(row, col) and row[col]:
            for parca in row[col]:
                parcas.append([id, f"{row.acres:.2f}", parca["name"], parca["description"], f"{parca['acres']:.2f}"])
        else:
            parcas.append([id, f"{row.acres:.2f}", "no PARCAs at this location", "", ""])
            counter += 1

        breaks.append(counter)

    protected_areas = pd.DataFrame(
        parcas,
        columns=[df.index.name, "GIS Acres", "Name", "Description", "Overlap acres"],
    )
    protected_areas.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]

    set_column_widths(ws, [name_col_width, area_col_width, 40, 64, area_col_width])
    set_cell_styles(ws)
