from openpyxl.styles import (
    Alignment,
    Border,
    Font,
    NamedStyle,
    PatternFill,
    Side,
)
from openpyxl.utils.cell import get_column_letter

# Guess at how many characters fit into a column width measurement
CHAR_PER_WIDTH_UNIT = 1.7

### Create named styles for formatting cells
font_bold = Font(bold=True)


alignment_left_wrap = Alignment(horizontal="left", wrap_text=True)
alignment_center_wrap = Alignment(horizontal="center", wrap_text=True)

default_header_border = Border(
    bottom=Side(border_style="medium", color="000000"),
)
default_cell_border = Border(
    bottom=Side(border_style="thin", color="AAAAAA"),
    left=Side(border_style="thin", color="DDDDDD"),
    right=Side(border_style="thin", color="DDDDDD"),
)

# Note: all cells are setup to wrap text
left_header_style = NamedStyle(
    name="Left Header Style",
    font=font_bold,
    alignment=alignment_left_wrap,
    border=default_header_border,
)

center_header_style = NamedStyle(
    name="Center Header Style",
    font=font_bold,
    alignment=alignment_center_wrap,
    border=default_header_border,
)

good_condition_header_style = NamedStyle(
    name="Good Condition Header Style",
    alignment=alignment_center_wrap,
    border=Border(
        bottom=Side(border_style="thin", color="000000"),
    ),
    fill=PatternFill("solid", "EEEEEE"),
)


value_style = NamedStyle(
    name="Value Style",
    alignment=alignment_left_wrap,
    border=default_cell_border,
)

even_row_bg = PatternFill("solid", fgColor="00F6F6F6")

analysis_unit_divider = Border(
    bottom=Side(border_style="medium", color="AAAAAA"),
    left=Side(border_style="thin", color="DDDDDD"),
    right=Side(border_style="thin", color="DDDDDD"),
)

description_font = Font(color="999999")


def set_cell_styles(ws, breaks=None, area_columns=None, percent_columns=None):
    area_columns = area_columns or []
    percent_columns = percent_columns or []

    for col_idx, col in enumerate(ws.columns):
        col[0].style = center_header_style

        for i, cell in enumerate(col[1:]):
            cell.style = value_style
            value = cell.value
            is_int = isinstance(value, (float, int)) and int(value) == value

            if col_idx in area_columns:
                if is_int:
                    cell.number_format = "#,##0"
                else:
                    cell.number_format = "#,##0.00"
            elif col_idx in percent_columns:
                if is_int:
                    cell.number_format = "0%"
                else:
                    cell.number_format = "0.00%"

            if i % 2 == 1:
                cell.fill = even_row_bg

    ws["A1"].style = left_header_style

    if breaks is not None:
        # add a stronger line between analysis units
        for col in ws.columns:
            for line in breaks:
                col[line].border = analysis_unit_divider


def set_column_widths(ws, widths):
    for i, width in enumerate(widths):
        letter = get_column_letter(i + 1)
        ws.column_dimensions[letter].width = width


def add_good_condition_row(ws, values_start_col, values_end_col, good_condition_col):
    """Add header row with merged cells for not in good condition / in good condition

    Parameters
    ----------
    ws : Worksheet
    values_start_col : int
        values start column index, 0-based
    values_end_col : int
        values end column index, 0-based
    good_condition_col : int
        good condition column index, 0-based
    """
    ws.insert_rows(idx=1)

    start_col = get_column_letter(values_start_col + 1)
    end_col = get_column_letter(values_start_col + good_condition_col)
    cell = ws[f"{start_col}1"]
    cell.value = "Not in good condition"
    cell.style = good_condition_header_style
    ws.merge_cells(f"{start_col}1:{end_col}1")

    start_col = get_column_letter(values_start_col + good_condition_col + 1)
    end_col = get_column_letter(values_end_col)
    cell = ws[f"{start_col}1"]
    cell.value = "In good condition"
    cell.style = good_condition_header_style
    ws.merge_cells(f"{start_col}1:{end_col}1")

    for i in range(1, ws.max_row + 1):
        cell = ws[f"{start_col}{i}"]
        cell.border = Border(
            left=Side(border_style="medium", color="666666"), bottom=cell.border.bottom, right=cell.border.right
        )
