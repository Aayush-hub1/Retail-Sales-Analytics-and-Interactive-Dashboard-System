"""Download the (filtered) sales list as an Excel file."""
from datetime import date
from io import BytesIO

from flask import Blueprint, request, send_file
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from db import query_all

export_bp = Blueprint("export", __name__, url_prefix="/api")

REVENUE_SQL = "si.quantity * si.unit_price * (1 - si.discount_rate)"

HEADERS = ["Sale ID", "Date", "Customer", "Product", "Category",
           "Qty", "Unit Price", "Discount", "Revenue", "Payment"]


@export_bp.get("/export/excel")
def export_excel():
    q = request.args.get("q", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    # category may be one name or several separated by commas
    categories = [c.strip() for c in request.args.get("category", "").split(",") if c.strip()]

    # same filters as GET /api/sales
    conditions = []
    params = []
    if q:
        conditions.append("(c.full_name LIKE %s OR p.product_name LIKE %s)")
        params += ["%" + q + "%", "%" + q + "%"]
    if date_from:
        conditions.append("s.sale_date >= %s")
        params.append(date_from)
    if date_to:
        conditions.append("s.sale_date <= %s")
        params.append(date_to)
    if categories:
        placeholders = ", ".join(["%s"] * len(categories))
        conditions.append("p.category IN (" + placeholders + ")")
        params += categories
    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    rows = query_all(
        f"""
        SELECT s.sale_id, s.sale_date, c.full_name AS customer,
               p.product_name AS product, p.category AS category,
               si.quantity, si.unit_price, si.discount_rate,
               ROUND({REVENUE_SQL}, 2) AS revenue, s.payment_method
        FROM sale_items si
        INNER JOIN sales s     ON s.sale_id = si.sale_id
        INNER JOIN customers c ON c.customer_id = s.customer_id
        INNER JOIN products p  ON p.product_id = si.product_id
        {where}
        ORDER BY s.sale_date DESC, s.sale_id DESC
        """,
        params,
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Sales"
    ws.append(HEADERS)
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", start_color="2F6FED")

    for r in rows:
        d = r["sale_date"]
        ws.append([
            r["sale_id"],
            d if isinstance(d, date) else date.fromisoformat(str(d)),
            r["customer"], r["product"], r["category"],
            r["quantity"],
            float(r["unit_price"]),
            float(r["discount_rate"]),
            float(r["revenue"]),
            r["payment_method"],
        ])

    last = len(rows) + 1
    for row in ws.iter_rows(min_row=2, max_row=last):
        row[1].number_format = "yyyy-mm-dd"
        row[6].number_format = "#,##0.00"
        row[7].number_format = "0.0%"
        row[8].number_format = "#,##0.00"

    # totals row with live formulas
    ws.cell(row=last + 1, column=5, value="Total").font = Font(bold=True)
    ws.cell(row=last + 1, column=6, value=f"=SUM(F2:F{last})").font = Font(bold=True)
    total = ws.cell(row=last + 1, column=9, value=f"=SUM(I2:I{last})")
    total.font = Font(bold=True)
    total.number_format = "#,##0.00"

    for col, w in zip("ABCDEFGHIJ", [9, 12, 18, 24, 16, 6, 12, 10, 12, 14]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"
    if rows:
        ws.auto_filter.ref = f"A1:J{last}"

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name="sales_export.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )