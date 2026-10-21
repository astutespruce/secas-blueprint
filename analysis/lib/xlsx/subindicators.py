import pandas as pd

from analysis.constants import INDICATORS_INDEX
from analysis.lib.xlsx.style import CHAR_PER_WIDTH_UNIT
from analysis.lib.xlsx.writer import write_excel

cores_value_columns = [
    "Intact habitat core size",
    "Number of overlapping cores",
    "Area of smallest overlapping core\n(acres)",
    "Area of largest overlapping core\n(acres)",
]


def add_subindicator_sheet(
    xlsx: pd.ExcelWriter, df: pd.DataFrame, subindicator: dict, name_col_width: int, outside_area_label: str
):
    """Add a sheet for one of the Blueprint subindicators.

    Parameters
    ----------
    xlsx : pd.ExcelWriter
    df : pd.DataFrame
    dataset : dict
        dataset object with info
    name_col_width : float
        width of name column
    outside_area_label : str
        name of outside analysis area acres column
    """
    sheet_name = subindicator.get("sheet_name", None) or subindicator["label"]
    caption = subindicator["caption"] + "."
    values = subindicator["values"]
    nodata_label = "Outside extent of this dataset\n(acres)"

    if subindicator["type"] == "stacked_bit_species":
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

                    cores.append([id, entry["label"], core["count"], core["min_acres"], core["max_acres"]])
                    counter += 1
            else:
                cores.append([id, "", "", "", ""])
                counter += 1

            breaks.append(counter)

        cores = pd.DataFrame(cores, columns=[df.index.name] + cores_value_columns)
        column_widths = [name_col_width, 30, 12, 16, 16]

        write_excel(
            xlsx,
            cores,
            sheet_name=sheet_name,
            caption=caption,
            column_widths=column_widths,
            area_columns=[3, 4],
            # only include breaks if they are not incremental
            breaks=None if breaks == list(range(len(df))) else breaks,
        )

    elif subindicator["type"] == "lines":
        good_threshold = INDICATORS_INDEX[subindicator["indicator_id"]].get("goodThreshold", None)
        if good_threshold is not None:
            caption += "  Good condition thresholds reflect the range of indicator values that occur in healthy, functioning ecosystems."

        value_columns = [f"{v['label'].replace(' (', '\n(')}\n(miles)" for v in values]
        col_width = min(max([len(c) for c in value_columns]) * CHAR_PER_WIDTH_UNIT, 18)
        tmp = df[subindicator["id"]].apply(pd.Series).fillna(0)
        tmp.columns = value_columns

        # sort greatest to least
        value_columns = value_columns[::-1]

        percent_columns = [col.replace("(miles)", "(percent)") for col in value_columns]
        tmp["total_miles"] = tmp[value_columns].sum(axis=1)
        for value_col, percent_col in zip(value_columns, percent_columns):
            tmp[percent_col] = (tmp[value_col] / tmp.total_miles).fillna(0)

        tmp = tmp[value_columns + percent_columns]

        good_condition_info = None
        if good_threshold is not None:
            # NOTE: this only applies to indicators, which are always in greatest to least order

            num_good_values = len([v for v in values if v["value"] >= good_threshold])
            num_not_good_values = len(values) - num_good_values

            good_condition_info = {
                "num_good_values": num_good_values,
                "num_not_good_values": num_not_good_values,
                "num_extra_columns": 0,
            }

        column_widths = [name_col_width] + ([col_width] * len(tmp.columns))

        num_area_cols = len(value_columns) + 1
        area_columns = list(range(num_area_cols))
        percent_columns = list(range(num_area_cols, num_area_cols * 2))

        write_excel(
            xlsx,
            tmp.reset_index(),
            sheet_name=sheet_name,
            caption=caption,
            column_widths=column_widths,
            area_columns=area_columns,
            percent_columns=percent_columns,
            add_percent_divider=True,
            good_condition_info=good_condition_info,
            area_header="MILES",
            percent_header=subindicator.get("percent_header", "PERCENT"),
        )

    elif subindicator["type"] == "huc12_species":
        tmp = df[subindicator["id"]].apply(pd.Series)[[v["value"] for v in values]]
        columns = {v["value"]: v["label"] for v in values}
        tmp = tmp.rename(columns=columns).reset_index()
        column_widths = [name_col_width, 16, 16]
        if "species" in columns:
            column_widths += [100]

        write_excel(xlsx, tmp, sheet_name=sheet_name, caption=caption, column_widths=column_widths)

    else:
        raise NotImplementedError(f"report not implemented for {subindicator['id']}")
