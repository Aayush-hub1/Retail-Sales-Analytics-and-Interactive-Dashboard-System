"""Build data/sales_report.xlsx from data/sales_dataset.csv."""
import csv
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

DATA_DIR = Path(__file__).resolve().parent
CSV_PATH = DATA_DIR / "sales_dataset.csv"
XLSX_PATH = DATA_DIR / "sales_report.xlsx"

HEADER_FILL = PatternFill("solid", start_color="2F6FED")
HEADER_FONT = Font(bold=True, color="FFFFFF")

# utf-8-sig removes the BOM that PowerShell's Export-Csv may have added
with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

wb = Workbook()

# ---------- Sheet 1: Sales ----------
ws = wb.active
ws.title = "Sales"
headers = ["sale_id", "sale_date", "customer", "product_name",
           "category", "quantity", "revenue", "payment_method"]
ws.append(headers)

for r in rows:
    ws.append([
        int(r["sale_id"]),
        date.fromisoformat(r["sale_date"]),
        r["customer"],
        r["product_name"],
        r["category"],
        int(r["quantity"]),
        float(r["revenue"]),
        r["payment_method"],
    ])

last = len(rows) + 1  # last data row
for cell in ws[1]:
    cell.fill = HEADER_FILL
    cell.font = HEADER_FONT
for row in ws.iter_rows(min_row=2, max_row=last):
    row[1].number_format = "yyyy-mm-dd"
    row[6].number_format = "#,##0.00"

widths = [9, 12, 18, 24, 16, 10, 12, 16]
for i, w in enumerate(widths):
    ws.column_dimensions[chr(65 + i)].width = w
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:H{last}"

# ---------- Sheet 2: Summary (live formulas) ----------
sm = wb.create_sheet("Summary")
sm["A1"], sm["B1"] = "Measure", "Value"
sm["A2"], sm["B2"] = "Total revenue", f"=SUM(Sales!G2:G{last})"
sm["A3"], sm["B3"] = "Units sold", f"=SUM(Sales!F2:F{last})"
sm["A4"], sm["B4"] = "Orders", f"=SUMPRODUCT(1/COUNTIF(Sales!A2:A{last},Sales!A2:A{last}))"
sm["A5"], sm["B5"] = "Average order value", "=B2/B4"
sm["B2"].number_format = sm["B5"].number_format = "#,##0.00"

sm["A7"], sm["B7"] = "Category", "Revenue"
categories = sorted({r["category"] for r in rows})
for i, cat in enumerate(categories, start=8):
    sm[f"A{i}"] = cat
    sm[f"B{i}"] = f"=SUMIF(Sales!E2:E{last},A{i},Sales!G2:G{last})"
    sm[f"B{i}"].number_format = "#,##0.00"

for cell in (sm["A1"], sm["B1"], sm["A7"], sm["B7"]):
    cell.fill = HEADER_FILL
    cell.font = HEADER_FONT
sm.column_dimensions["A"].width = 24
sm.column_dimensions["B"].width = 16

wb.save(XLSX_PATH)
print("Saved", XLSX_PATH, "with", len(rows), "data rows")