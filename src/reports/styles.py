from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

TITLE_FONT = Font(bold=True, size=14)
GROUP_FONT = Font(bold=True, size=12)
HEADER_FONT = Font(bold=True, size=12)
NORMAL_FONT = Font()

CENTER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT_ALIGN = Alignment(horizontal="left", vertical="center", wrap_text=True)
TOP_LEFT_ALIGN = Alignment(horizontal="left", vertical="top", wrap_text=True)

THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

HEADER_FILL = PatternFill(start_color="D6BCFA", end_color="D6BCFA", fill_type="solid")