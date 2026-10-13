import pandas as pd

from analysis.lib.xlsx.writer import write_excel


def add_subindicator_sheet(xlsx: pd.ExcelWriter, df: pd.DataFrame, subindicator: dict, name_col_width: int):
    sheet_name = subindicator.get("sheet_name", None) or subindicator["label"]
    caption = subindicator["caption"] + "."
    values = subindicator["values"]

    if subindicator["type"] == "stacked_bits":
        tmp = df[[subindicator["id"]]].rename(columns={subindicator["id"]: "value"})
        tmp.loc[tmp.value.isnull(), "value"] = tmp.value.apply(lambda x: [])
        tmp["count"] = tmp.value.apply(len)
        tmp["value"] = tmp.value.apply(", ".join)

        # values are used as the lookup to column names
        tmp = tmp[["count", "value"]].rename(columns={value["value"]: value["label"] for value in values})

        write_excel(
            xlsx, tmp.reset_index(), sheet_name=sheet_name, caption=caption, column_widths=[name_col_width, 12, 100]
        )

    else:
        raise NotImplementedError(f"report not implemented for {subindicator['id']}")
