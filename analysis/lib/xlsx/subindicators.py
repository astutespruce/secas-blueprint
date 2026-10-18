import pandas as pd

from analysis.lib.xlsx.writer import write_excel

cores_value_columns = [
    "Intact habitat core size",
    "Number of overlapping cores",
    "Area of smallest overlapping core\n(acres)",
    "Mean area of overlapping cores\n(acre)",
    "Area of largest overlapping core\n(acres)",
]


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

    elif subindicator["type"] == "cores":
        cores = []
        breaks = []
        counter = 0
        col = subindicator["id"]
        for id, row in df.iterrows():
            if not pd.isnull(row.get(col)):
                # sort so largest cores first
                for entry in values[::-1]:
                    core = row[col].get(entry["value"])
                    if not core:
                        continue

                    cores.append(
                        [id, entry["label"], core["count"], core["min_acres"], core["mean_acres"], core["max_acres"]]
                    )
                    counter += 1
            else:
                cores.append([id, "", "", "", "", ""])
                counter += 1

            breaks.append(counter)

        cores = pd.DataFrame(cores, columns=[df.index.name] + cores_value_columns)
        column_widths = [name_col_width, 30, 12] + [16] * 3

        write_excel(
            xlsx,
            cores,
            sheet_name=sheet_name,
            caption=caption,
            column_widths=column_widths,
            area_columns=[3, 4, 5],
            # only include breaks if they are not incremental
            breaks=None if breaks == list(range(len(df))) else breaks,
        )

    else:
        raise NotImplementedError(f"report not implemented for {subindicator['id']}")
