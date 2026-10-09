import pandas as pd

from analysis.constants import PARCAS_POLY
from analysis.lib.xlsx.writer import write_excel


def add_parcas_poly_sheet(xlsx: pd.ExcelWriter, df: pd.DataFrame, name_col_width: float, area_col_width: float):
    dataset = PARCAS_POLY

    # transform data into one row per per protected area per analysis unit
    parcas = []
    breaks = []
    counter = 0
    col = dataset["id"]
    for id, row in df.iterrows():
        if len(row.get(col, [])):
            for parca in row[col]:
                parcas.append(
                    [id, row.acres, parca["acres"], parca["acres"] / row.acres, parca["name"], parca["description"]]
                )
                counter += 1
        else:
            parcas.append([id, row.acres, "0", "0", "no PARCAs at this location", ""])
            counter += 1

        breaks.append(counter)

    parcas = pd.DataFrame(
        parcas,
        columns=[df.index.name, "GIS acres", "Overlap acres", "Overlap percent", "Name", "Description"],
    )

    column_widths = [name_col_width, area_col_width, area_col_width, area_col_width, 40, 64]
    write_excel(
        xlsx,
        parcas,
        sheet_name=dataset["sheet_name"],
        caption=dataset["caption"] + ".",
        column_widths=column_widths,
        area_columns=range(1, 3),
        percent_columns=[3],
        # only include breaks if they are not incremental
        breaks=None if breaks == list(range(len(df))) else breaks,
    )
