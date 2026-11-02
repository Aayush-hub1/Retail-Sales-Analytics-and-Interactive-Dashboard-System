"""Generate the academic-style Retail Sales Analytics report in DOCX and PDF."""

from collections import defaultdict
from pathlib import Path
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image as PDFImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table as PDFTable,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ASSETS = DOCS / "report_assets"
ASSETS.mkdir(exist_ok=True)
DOCX_PATH = DOCS / "retail_sales_analytics_project_report.docx"
PDF_PATH = DOCS / "retail_sales_analytics_project_report.pdf"

NAVY = "#18324F"
BLUE = "#2F6FED"
TEAL = "#0F9F93"
GOLD = "#E5A33B"
INK = "#26374A"
MUTED = "#66778B"
PALE = "#F1F5FB"
LIGHT_BLUE = "#EAF1FF"
LINE = "#D7E0EB"

with (ROOT / "data" / "sales_dataset.csv").open(
    encoding="utf-8-sig", newline=""
) as source:
    rows = list(csv.DictReader(source))

category_revenue = defaultdict(float)
monthly_revenue = defaultdict(float)
payment_revenue = defaultdict(float)
for row in rows:
    value = float(row["revenue"])
    category_revenue[row["category"]] += value
    monthly_revenue[row["sale_date"][:7]] += value
    payment_revenue[row["payment_method"]] += value

revenue = sum(float(row["revenue"]) for row in rows)
order_count = len({row["sale_id"] for row in rows})
unit_count = sum(int(row["quantity"]) for row in rows)
average_order_value = revenue / order_count


def create_artwork():
    icon_path = ASSETS / "retail_analytics_logo.png"
    wordmark_path = ASSETS / "retail_analytics_wordmark.png"

    icon = Image.new("RGBA", (900, 900), (255, 255, 255, 0))
    draw = ImageDraw.Draw(icon)
    draw.rounded_rectangle((40, 40, 860, 860), radius=185, fill=NAVY)
    draw.line(
        [(250, 320), (315, 320), (370, 560), (665, 560), (730, 390), (340, 390)],
        fill="white",
        width=38,
        joint="curve",
    )
    for x, y, width, height, color in [
        (405, 480, 55, 65, "#72D8CB"),
        (490, 445, 55, 100, "#43C6B9"),
        (575, 405, 55, 140, GOLD),
    ]:
        draw.rounded_rectangle(
            (x, y, x + width, y + height), radius=8, fill=color
        )
    for x in (430, 665):
        draw.ellipse((x - 25, 575, x + 25, 625), fill=GOLD)
    icon.save(icon_path)

    wordmark = Image.new("RGBA", (1500, 340), (255, 255, 255, 0))
    wordmark.alpha_composite(icon.resize((285, 285), Image.Resampling.LANCZOS), (5, 25))
    font_dir = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    try:
        title_font = ImageFont.truetype(str(font_dir / "DejaVuSans-Bold.ttf"), 76)
        subtitle_font = ImageFont.truetype(str(font_dir / "DejaVuSans.ttf"), 46)
    except OSError:
        title_font = subtitle_font = ImageFont.load_default()
    word_draw = ImageDraw.Draw(wordmark)
    word_draw.text((330, 80), "RETAIL SALES", font=title_font, fill=NAVY)
    word_draw.text((335, 175), "ANALYTICS PROJECT REPORT", font=subtitle_font, fill=BLUE)
    wordmark.save(wordmark_path)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "text.color": NAVY,
            "axes.labelcolor": MUTED,
            "axes.edgecolor": LINE,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )

    fig, ax = plt.subplots(figsize=(11.2, 3.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")
    steps = [
        ("01", "RECORD", "Sales, customers\nand products", "#EAF1FF"),
        ("02", "STORE", "Normalized MySQL\nrecords", "#E8F7F4"),
        ("03", "ANALYZE", "Filter, aggregate\nand calculate KPIs", "#FFF5E7"),
        ("04", "EXPLORE", "Dashboard, charts\nand sales table", "#F1ECFF"),
        ("05", "SHARE", "Filtered Excel\nexport and analysis", "#EAF1FF"),
    ]
    for x, (number, title, detail, fill) in zip(
        (0.25, 2.65, 5.05, 7.45, 9.85), steps
    ):
        ax.add_patch(
            FancyBboxPatch(
                (x, 0.95),
                1.9,
                1.8,
                boxstyle="round,pad=.05,rounding_size=.12",
                facecolor=fill,
                edgecolor=LINE,
                linewidth=1.2,
            )
        )
        ax.text(x + 0.95, 2.39, number, ha="center", fontsize=8, color=TEAL)
        ax.text(
            x + 0.95,
            2.05,
            title,
            ha="center",
            fontsize=10,
            fontweight="bold",
            color=NAVY,
        )
        ax.text(
            x + 0.95,
            1.48,
            detail,
            ha="center",
            va="center",
            fontsize=8,
            color=MUTED,
            linespacing=1.4,
        )
        if x < 9:
            ax.add_patch(
                FancyArrowPatch(
                    (x + 1.92, 1.85),
                    (x + 2.35, 1.85),
                    arrowstyle="-|>",
                    mutation_scale=12,
                    color=BLUE,
                    linewidth=1.6,
                )
            )
    ax.text(
        6,
        3.55,
        "FROM RETAIL TRANSACTION TO DECISION-READY VIEW",
        ha="center",
        fontsize=11,
        fontweight="bold",
        color=NAVY,
    )
    ax.text(
        6,
        0.38,
        "Shared revenue definition: quantity x sale-time unit price x (1 - discount rate)",
        ha="center",
        fontsize=8,
        color=MUTED,
    )
    fig.tight_layout()
    fig.savefig(ASSETS / "graphical_abstract.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.8, 4.0))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4)
    ax.axis("off")
    layers = [
        (0.25, "PRESENTATION", "HTML / CSS / JS\nChart.js dashboard\nSearch, filters, forms", "#EAF1FF"),
        (3.0, "APPLICATION", "Flask REST API\nValidation / transactions\nSales / export routes", "#E8F7F4"),
        (5.75, "DATA", "MySQL 8\nCustomers / products\nSales / sale_items", "#FFF5E7"),
        (8.5, "REPORTING", "CSV dataset\nExcel workbook\nSQL analysis", "#F1ECFF"),
    ]
    for x, title, detail, fill in layers:
        ax.add_patch(
            FancyBboxPatch(
                (x, 1.15),
                2.25,
                1.75,
                boxstyle="round,pad=.05,rounding_size=.1",
                facecolor=fill,
                edgecolor=LINE,
                linewidth=1.2,
            )
        )
        ax.text(
            x + 1.125,
            2.48,
            title,
            ha="center",
            fontsize=9,
            fontweight="bold",
            color=NAVY,
        )
        ax.text(
            x + 1.125,
            1.83,
            detail,
            ha="center",
            va="center",
            fontsize=8,
            color=MUTED,
            linespacing=1.45,
        )
    for x in (2.5, 5.25, 8.0):
        ax.add_patch(
            FancyArrowPatch(
                (x, 2.03), (x + 0.46, 2.03), arrowstyle="-|>", color=BLUE, linewidth=1.6
            )
        )
    ax.text(
        5.5,
        3.55,
        "LAYERED APPLICATION ARCHITECTURE",
        ha="center",
        fontsize=11,
        fontweight="bold",
        color=NAVY,
    )
    ax.text(
        5.5,
        0.48,
        "JSON over HTTP  /  Parameterized SQL  /  Shared filters for table and export",
        ha="center",
        fontsize=8,
        color=MUTED,
    )
    fig.tight_layout()
    fig.savefig(ASSETS / "architecture.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.5, 4.4))
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.5)
    ax.axis("off")
    entities = [
        (0.2, 2.5, 2.15, 1.45, "CUSTOMERS", ["PK customer_id", "full_name / email", "city / state"]),
        (4.15, 2.5, 2.15, 1.45, "SALES", ["PK sale_id", "FK customer_id", "sale_date / payment"]),
        (
            4.15,
            0.35,
            2.15,
            1.55,
            "SALE_ITEMS",
            ["PK sale_item_id", "FK sale_id / product_id", "quantity / price / discount"],
        ),
        (8.1, 0.35, 2.15, 1.55, "PRODUCTS", ["PK product_id", "name / category", "unit_price"]),
    ]
    for x, y, width, height, title, fields in entities:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                width,
                height,
                boxstyle="round,pad=.04,rounding_size=.08",
                facecolor="#F5F8FD",
                edgecolor=BLUE,
                linewidth=1.2,
            )
        )
        ax.add_patch(
            FancyBboxPatch(
                (x, y + height - 0.36),
                width,
                0.36,
                boxstyle="round,pad=.04,rounding_size=.07",
                facecolor=BLUE,
                edgecolor=BLUE,
            )
        )
        ax.text(
            x + width / 2,
            y + height - 0.18,
            title,
            ha="center",
            va="center",
            color="white",
            fontsize=8.5,
            fontweight="bold",
        )
        ax.text(
            x + 0.13,
            y + height - 0.53,
            "\n".join(fields),
            ha="left",
            va="top",
            fontsize=7.6,
            color=NAVY,
            linespacing=1.5,
        )
    for start, end in [
        ((2.35, 3.18), (4.15, 3.18)),
        ((5.22, 2.5), (5.22, 1.9)),
        ((6.3, 1.12), (8.1, 1.12)),
    ]:
        ax.add_patch(
            FancyArrowPatch(
                start, end, arrowstyle="-|>", mutation_scale=12, color=TEAL, linewidth=1.5
            )
        )
    ax.text(3.25, 3.36, "1 : many", ha="center", fontsize=7, color=MUTED)
    ax.text(5.35, 2.16, "1 : many", fontsize=7, color=MUTED)
    ax.text(7.2, 1.3, "many : 1", ha="center", fontsize=7, color=MUTED)
    ax.text(
        5.25,
        4.28,
        "NORMALIZED ORDER AND LINE-ITEM MODEL",
        ha="center",
        fontsize=11,
        fontweight="bold",
        color=NAVY,
    )
    fig.tight_layout()
    fig.savefig(ASSETS / "data_model.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    cats = sorted(category_revenue.items(), key=lambda item: item[1])
    fig, ax = plt.subplots(figsize=(8.5, 3.45))
    bars = ax.barh(
        [item[0] for item in cats],
        [item[1] for item in cats],
        color=[TEAL if item[0] == "Electronics" else BLUE for item in cats],
        height=0.62,
    )
    ax.set_title("Net revenue by category", pad=11)
    ax.set_xlabel("Revenue (INR)")
    ax.xaxis.grid(True, color="#E8EDF4")
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value / 1000:.0f}k"))
    for bar, (_, value) in zip(bars, cats):
        ax.text(
            value + 500,
            bar.get_y() + bar.get_height() / 2,
            f"{value:,.0f}",
            va="center",
            fontsize=8,
            color=NAVY,
        )
    ax.set_xlim(0, max(value for _, value in cats) * 1.23)
    fig.tight_layout()
    fig.savefig(ASSETS / "category_revenue.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 3.45))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.text(
        5,
        3.55,
        "RETAIL SALES DASHBOARD  |  DATASET OVERVIEW",
        ha="center",
        fontsize=11,
        fontweight="bold",
        color=NAVY,
    )
    metrics = [
        ("TOTAL REVENUE", f"INR {revenue:,.0f}", "#EAF1FF"),
        ("ORDERS", f"{order_count}", "#E8F7F4"),
        ("UNITS SOLD", f"{unit_count}", "#FFF5E7"),
        ("AVG ORDER VALUE", f"INR {average_order_value:,.2f}", "#F1ECFF"),
    ]
    for x, (label, value, fill) in zip((0.2, 2.65, 5.1, 7.55), metrics):
        ax.add_patch(
            FancyBboxPatch(
                (x, 1.0),
                2.25,
                1.85,
                boxstyle="round,pad=.06,rounding_size=.14",
                facecolor=fill,
                edgecolor=LINE,
                linewidth=1.2,
            )
        )
        ax.text(
            x + 1.125,
            2.3,
            label,
            ha="center",
            fontsize=7.6,
            fontweight="bold",
            color=MUTED,
        )
        ax.text(
            x + 1.125,
            1.7,
            value,
            ha="center",
            fontsize=11 if x != 7.55 else 9.5,
            fontweight="bold",
            color=NAVY,
        )
    ax.text(
        5,
        0.5,
        f"{len(rows)} sale lines  |  {order_count} distinct orders  |  January-October 2026",
        ha="center",
        fontsize=8,
        color=MUTED,
    )
    fig.tight_layout()
    fig.savefig(ASSETS / "analysis_kpi_overview.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    months = sorted(monthly_revenue.items())
    values = [value for _, value in months]
    fig, ax = plt.subplots(figsize=(8.5, 3.45))
    peak = max(range(len(values)), key=values.__getitem__)
    ax.plot([month[5:] for month, _ in months], values, color=BLUE, linewidth=2.3, marker="o")
    ax.fill_between(range(len(values)), values, color=BLUE, alpha=0.09)
    ax.scatter([peak], [values[peak]], color=TEAL, s=55, zorder=3)
    ax.annotate(
        f"Peak INR {values[peak]:,.0f}",
        (peak, values[peak]),
        xytext=(-72, -25),
        textcoords="offset points",
        fontsize=7.5,
        color=TEAL,
        fontweight="bold",
        arrowprops={"arrowstyle": "->", "color": TEAL, "lw": 1},
    )
    ax.set_title("Monthly revenue - January to October 2026", pad=11)
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (INR)")
    ax.yaxis.grid(True, color="#E8EDF4")
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value / 1000:.0f}k"))
    fig.tight_layout()
    fig.savefig(ASSETS / "monthly_revenue.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    payment_rows = sorted(payment_revenue.items(), key=lambda item: item[1])
    fig, ax = plt.subplots(figsize=(8.5, 3.45))
    bars = ax.barh(
        [item[0] for item in payment_rows],
        [item[1] for item in payment_rows],
        color=[TEAL if item[0] == "UPI" else BLUE for item in payment_rows],
        height=0.58,
    )
    ax.set_title("Revenue by payment method", pad=10)
    ax.set_xlabel("Revenue (INR)")
    ax.xaxis.grid(True, color="#E8EDF4")
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda value, _: f"{value / 1000:.0f}k")
    )
    for bar, (_, value) in zip(bars, payment_rows):
        ax.text(
            value + 400,
            bar.get_y() + bar.get_height() / 2,
            f"{value:,.0f}",
            va="center",
            fontsize=7.7,
            color=NAVY,
        )
    ax.set_xlim(0, max(value for _, value in payment_rows) * 1.24)
    fig.tight_layout()
    fig.savefig(ASSETS / "payment_method_revenue.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    return icon_path, wordmark_path


def build_content():
    abstract = (
        "Retail businesses need a practical way to review transactions, identify category "
        "and time-based patterns, and share filtered data. This project implements an "
        "end-to-end retail sales analytics system that combines a normalized MySQL "
        "database, a Flask REST API, a browser dashboard, and Excel export. The dashboard "
        "presents revenue, order count, units sold, and average order value; visualizes "
        "monthly and category revenue; and supports text, date, and multi-category "
        "filtering. Forms support creation of sales, customers, and products. The API "
        "validates inputs, obtains product prices from the database, and records the "
        "order header and item within a transaction. The CSV snapshot contains 69 "
        "order-line records representing 37 orders, 201 units, and INR 159,188.00 in "
        "revenue. Electronics is the largest category in this snapshot, and October 2026 "
        "is the strongest observed month. The existing project report records 15 of 15 "
        "end-to-end checks passing on clean seed data; this report independently "
        "recomputes headline metrics from the CSV. The work demonstrates a coherent path "
        "from data entry to dashboard exploration and spreadsheet analysis, while "
        "identifying authentication, multi-item orders, and record maintenance as future "
        "improvements."
    )
    return [
        {
            "section": "FRONT MATTER",
            "title": "Bonafide Certificate",
            "blocks": [
                ("p", "Certified that this project report titled “Retail Sales Analytics System” is the bonafide work of the student named on the title page, completed as part of the stated academic programme. The work describes a MySQL-backed retail analytics application with a Flask API, browser dashboard, and Excel reporting workflow."),
                ("p", "The project was carried out under the guidance and supervision of the undersigned. The report presents the design, implementation, dataset analysis, and verification evidence available in the project repository."),
                ("space", 4),
                ("table", [["SUPERVISOR", "HEAD OF DEPARTMENT"], ["Signature: _____________________", "Signature: _____________________"], ["Name: ________________________", "Name: ________________________"], ["Date: _________________________", "Date: _________________________"]], [3.25, 3.25]),
                ("h", "Declaration"),
                ("p", "I declare that this report is prepared for academic submission and that project results are described with their evidence sources. Dataset metrics are calculated from the included CSV snapshot; test-suite outcomes are attributed to existing project documentation."),
                ("p", "Student signature: ______________________________      Date: __________________"),
                ("h", "Acknowledgements"),
                ("p", "The author acknowledges the maintainers of Python, Flask, MySQL, Chart.js, and openpyxl, whose software supports this project, and the instructors and reviewers who provide guidance during the project lifecycle."),
            ],
        },
        {
            "section": "FRONT MATTER",
            "title": "Abstract",
            "blocks": [
                ("p", abstract),
                ("small", "Keywords: Retail analytics; MySQL; Flask; REST API; dashboard; Excel; sales reporting."),
                ("h", "Graphical Abstract"),
                ("image", "graphical_abstract.png", 6.55, "Figure 0.1. Retail transaction-to-insight workflow; project artwork is original."),
                ("callout", "Revenue is calculated consistently as quantity x sale-time unit price x (1 - discount rate)."),
            ],
        },
        {
            "section": "FRONT MATTER",
            "title": "Contents & Abbreviations",
            "blocks": [
                ("table", [["Section", "Page"], ["Bonafide Certificate", "2"], ["Abstract & Graphical Abstract", "3"], ["Contents & Abbreviations", "4"], ["Chapter 1 - Introduction", "5"], ["Chapter 2 - Background & Requirements", "6"], ["Chapter 3 - Design & Methodology", "7"], ["Chapter 4 - Results & Validation", "8-9"], ["Chapter 5, References & Appendices", "9-10"]], [5.3, 1.1]),
                ("h", "Abbreviations"),
                ("table", [["Term", "Meaning"], ["API", "Application Programming Interface"], ["AOV", "Average Order Value"], ["CSV", "Comma-Separated Values"], ["DBMS", "Database Management System"], ["ERD", "Entity-Relationship Diagram"], ["JSON", "JavaScript Object Notation"], ["KPI", "Key Performance Indicator"], ["REST", "Representational State Transfer"], ["SQL", "Structured Query Language"], ["XLSX", "Excel Open XML Spreadsheet"]], [1.25, 5.15]),
                ("h", "Symbols & Measures"),
                ("small", "Revenue = quantity x unit price x (1 - discount rate).  |  AOV = total revenue / distinct orders.  |  INR = Indian Rupee."),
            ],
        },
        {
            "section": "CHAPTER 1",
            "title": "Introduction",
            "blocks": [
                ("h", "1.1 Background and motivation"),
                ("p", "Retail transaction data becomes useful when it can be summarized consistently and explored without manually reconciling spreadsheets. A small shop may need a quick view of revenue, orders, quantities, category performance, and recent trends, as well as a straightforward way to record transactions and share selected data."),
                ("p", "This project addresses that need with a compact, locally runnable application. MySQL stores customer, product, order, and order-line records; Flask exposes data and transaction endpoints; and a browser dashboard provides summary cards, charts, filters, and entry forms. Excel export connects the live dashboard workflow to offline analysis."),
                ("h", "1.2 Problem statement"),
                ("p", "The central problem is fragmented retail reporting: operational data, summary metrics, and spreadsheet analysis can diverge when they use different filters or revenue definitions. Manual reporting also makes it harder to search across customers and products or to investigate a particular date range and category selection."),
                ("h", "1.3 Objectives"),
                ("bullets", ["Design a relational database that preserves sales history and referential integrity.", "Provide API endpoints for sales, master data, summaries, charts, and Excel export.", "Build a filter-aware dashboard whose KPIs, charts, table, and export share the active selection.", "Validate sale inputs and derive prices server-side from the product catalogue.", "Verify the data path and document dataset findings, limitations, and setup."]),
                ("h", "1.4 Scope and users"),
                ("p", "The intended users are a small retail operator, analyst, or student demonstrating database-backed reporting. The included sample covers one store and a limited set of customers, products, and transactions. The system supports one product line per sale-form submission; it does not provide sign-in, role management, multi-store inventory, or edit/delete screens."),
                ("h", "1.5 Report organization"),
                ("p", "Chapter 2 outlines requirements and technology choices. Chapter 3 presents architecture, data design, and transaction logic. Chapter 4 reports dataset results and verification notes. Chapter 5 summarizes conclusions, limitations, and future work; the final page includes references and a concise user guide."),
            ],
        },
        {
            "section": "CHAPTER 2",
            "title": "Background & Requirements",
            "blocks": [
                ("h", "2.1 System requirements"),
                ("table", [["ID", "Requirement", "Evidence in project"], ["FR-01", "View sales KPIs and trends", "KPI cards; monthly and category charts"], ["FR-02", "Search and filter sales", "Text, date, multi-category filters"], ["FR-03", "Export selected records", "Excel endpoint shares sales filters"], ["FR-04", "Maintain basic records", "Forms for sales, customers, products"], ["NFR-01", "Preserve transactional integrity", "Foreign keys; sale transaction"], ["NFR-02", "Keep monetary history accurate", "Sale-time unit price and discount"]], [0.65, 2.45, 3.35]),
                ("h", "2.2 Technology selection"),
                ("table", [["Layer", "Technology", "Purpose"], ["Database", "MySQL 8", "Relational storage, constraints, joins, views"], ["Backend", "Python 3.14, Flask", "REST API and request validation"], ["Database access", "PyMySQL", "Parameterized SQL and transactions"], ["Frontend", "HTML, CSS, JavaScript", "Dashboard, filters, forms"], ["Charts / exports", "Chart.js, openpyxl", "Visual summaries and Excel workbooks"]], [1.15, 2.0, 3.3]),
                ("h", "2.3 Logical architecture"),
                ("image", "architecture.png", 6.45, "Figure 2.1. Application layers and the reporting path."),
                ("callout", "The sales listing and Excel export use matching search, date-range, and category filter parameters."),
            ],
        },
        {
            "section": "CHAPTER 3",
            "title": "Design & Methodology",
            "blocks": [
                ("h", "3.1 Relational data model"),
                ("p", "The schema separates customer and product master data from order headers and individual order lines. A sale may contain multiple sale_items in the database even though the current entry form submits one product line at a time. Foreign keys connect each order to a customer and each line to a sale and product."),
                ("image", "data_model.png", 6.4, "Figure 3.1. Core entity relationships and key fields."),
                ("h", "3.2 Integrity and revenue logic"),
                ("bullets", ["Customer email and product name are unique; item quantity and unit price must be positive.", "Discount rate is constrained between 0 and 1; customer deletion is restricted when sales exist.", "Deleting a sale cascades to its sale-item rows; products referenced by sales cannot be removed.", "Unit price and discount are stored on the order line to preserve the value agreed at purchase time."]),
                ("h", "3.3 Request and transaction workflow"),
                ("p", "For a new sale, the API validates customer, product, quantity, discount, payment method, and date. It looks up the current product price on the server, inserts the sale header and its line item in a database transaction, and returns the created sale identifier. The browser does not choose the authoritative price."),
                ("h", "3.4 Data processing"),
                ("p", "The report dataset is a CSV export from v_sales_detail with one row per order line. Aggregations group those rows by sale identifier, category, month, or payment method as required. The dashboard receives numeric API values, and the Excel workbook retains line-level detail for pivot tables and formulas."),
            ],
        },
        {
            "section": "CHAPTER 4",
            "title": "Results Analysis",
            "blocks": [
                ("h", "4.1 Dataset snapshot"),
                ("table", [["Measure", "Observed value"], ["Order-line rows", str(len(rows))], ["Distinct orders", str(order_count)], ["Units sold", str(unit_count)], ["Total revenue", f"INR {revenue:,.2f}"], ["Average order value", f"INR {average_order_value:,.2f}"], ["Distinct customer / product names", "15 / 15"], ["Dataset dates", "5 Jan-21 Oct 2026"]], [3.25, 3.15]),
                ("h", "4.2 Category performance"),
                (
                    "image_grid",
                    [
                        ("analysis_kpi_overview.png", "Figure 4.1. Dashboard KPI overview."),
                        ("category_revenue.png", "Figure 4.2. Revenue by category."),
                        ("monthly_revenue.png", "Figure 4.3. Monthly revenue trend."),
                        ("payment_method_revenue.png", "Figure 4.4. Revenue by payment method."),
                    ],
                ),
                ("small", "Electronics leads category revenue at INR 59,203.25. October is the strongest observed month at INR 28,278.10; UPI is the largest payment method at INR 58,612.95."),
                ("h", "4.3 Monthly performance"),
                ("small", "The four original visuals above summarize the dashboard KPIs, category comparison, monthly movement, and payment mix. February is the lowest month at INR 12,063.30. These findings describe this partial-year sample; they are not a forecast."),
            ],
        },
        {
            "section": "CHAPTER 4-5",
            "title": "Validation & Conclusion",
            "blocks": [
                ("h", "4.4 Payment mix and outlier context"),
                ("p", "Revenue by payment method is UPI INR 58,612.95; Credit Card INR 50,147.10; Cash INR 33,326.65; and Debit Card INR 17,101.30. Sale 37 is a documented deliberate bulk order with quantities of 20 and 30 units and about INR 10,157.50 in revenue. The mean order-line revenue (INR 2,307.07) exceeds the median (INR 1,799.00), consistent with a right-skewed distribution."),
                ("h", "4.5 Verification record"),
                ("table", [["Verification area", "Evidence / status"], ["Dataset totals", "Recomputed from CSV: 69 lines, 37 orders, 201 units, INR 159,188.00"], ["API / SQL agreement", "Existing docs/report.md records matching totals across layers"], ["End-to-end checks", "Existing project report records 15 of 15 checks passing on clean seed data"], ["Report scope", "CSV metrics recalculated here; database and browser checks not rerun for this report"]], [1.5, 4.9]),
                ("h", "5.1 Conclusion"),
                ("p", "The project delivers a complete small-retail reporting path from structured storage and validated API operations to interactive dashboard analysis and filtered Excel export. Its main strength is consistency: a shared revenue definition and shared filters align the displayed rows, metrics, and export workflow."),
                ("h", "5.2 Limitations and future work"),
                ("bullets", ["Add authentication, authorization, and audit history before deployment to multiple users.", "Support multi-item order entry and controlled edit/cancel workflows.", "Extend the single-store sample with inventory, cost/margin, and broader time coverage.", "Automate repeatable data checks and report generation from refreshed exports."]),
                ("callout", "Recommendation: treat the included figures as an illustrative sample until access control, operational workflows, and broader production data are in place."),
            ],
        },
        {
            "section": "REFERENCES & APPENDIX",
            "title": "References and User Guide",
            "blocks": [
                ("h", "References"),
                ("small", "[1] Retail Sales Analytics project repository. README.md: system scope, setup, endpoints, and expected seed-data totals."),
                ("small", "[2] Retail Sales Analytics project repository. database/schema.sql: MySQL tables, keys, indexes, and constraints."),
                ("small", "[3] Retail Sales Analytics project repository. backend/routes/sales.py and backend/routes/export.py: sales API and filtered Excel export."),
                ("small", "[4] Retail Sales Analytics project repository. data/sales_dataset.csv: 69-row report dataset used for this analysis."),
                ("small", "[5] Flask documentation. https://flask.palletsprojects.com/"),
                ("small", "[6] MySQL 8.0 Reference Manual. https://dev.mysql.com/doc/refman/8.0/en/"),
                ("small", "[7] Chart.js documentation. https://www.chartjs.org/docs/latest/"),
                ("small", "[8] openpyxl documentation. https://openpyxl.readthedocs.io/"),
                ("h", "Appendix A - Installation and launch"),
                ("small", "Requirements: Windows, Python 3.14, MySQL 8.0.31 or later, and PowerShell."),
                ("small", "1. Install dependencies: pip install flask flask-cors pymysql openpyxl"),
                ("small", "2. Load database scripts: Get-Content database\\schema.sql | mysql -u root -p; then load sample_data.sql into retail_sales."),
                ("small", "3. Put retail_app MySQL credentials in the .env file read by backend/config.py."),
                ("small", "4. Start from backend: python app.py; open http://127.0.0.1:5000/."),
                ("small", "5. Run checks: powershell -ExecutionPolicy Bypass -File docs\\e2e_check.ps1."),
                ("h", "Appendix B - Principal project files"),
                ("small", "backend/app.py and backend/routes/ | frontend/index.html and frontend/js/app.js | database/schema.sql and database/analysis.sql | data/sales_dataset.csv and data/make_excel.py | docs/excel_guide.md and docs/e2e_check.ps1."),
                ("h", "Appendix C - Project screenshots"),
                ("p", "These screenshots document the implemented user interface and export workflow. The first shows the full sample dashboard; the second shows the entry forms; the third confirms an Excel file was downloaded; and the fourth shows a filtered dashboard state. Values in the filtered screenshot describe that selected view, not the full-dataset totals reported in Chapter 4."),
                (
                    "image_grid",
                    [
                        (
                            "project_dashboard_overview.png",
                            "Figure C.1. Full dashboard: revenue, orders, units, average order value, charts, and sales table.",
                        ),
                        (
                            "project_data_entry_forms.png",
                            "Figure C.2. Entry forms for a sale, customer, and product; sale price is selected through the product record.",
                        ),
                        (
                            "project_excel_download.png",
                            "Figure C.3. Browser Downloads confirms the generated sales_export Excel workbook.",
                        ),
                        (
                            "project_filtered_dashboard.png",
                            "Figure C.4. Filtered example with Clothing and Groceries selected; its KPIs and 28 displayed lines are filter-specific.",
                        ),
                    ],
                ),
            ],
        },
    ]


def set_cell(cell, text, bold=False, color="26374A", size=8.2, alignment=None):
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(1)
    paragraph.paragraph_format.space_before = Pt(1)
    if alignment is not None:
        paragraph.alignment = alignment
    run = paragraph.add_run(str(text))
    run.bold = bold
    run.font.name = "Aptos"
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color.lstrip("#"))
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def shade(cell, fill):
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill.lstrip("#"))
    cell._tc.get_or_add_tcPr().append(shading)


def add_doc_table(doc, data, widths=None):
    table = doc.add_table(rows=len(data), cols=len(data[0]))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    if widths:
        for row in table.rows:
            for index, width in enumerate(widths):
                row.cells[index].width = Inches(width)
    for i, row in enumerate(data):
        for j, value in enumerate(row):
            cell = table.cell(i, j)
            set_cell(
                cell,
                value,
                bold=i == 0,
                color="FFFFFF" if i == 0 else INK,
                size=8.1,
            )
            if i == 0:
                shade(cell, NAVY)
            elif i % 2 == 0:
                shade(cell, PALE)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_doc_paragraph(doc, text, size=9.0, style=None):
    paragraph = doc.add_paragraph(style=style)
    paragraph.paragraph_format.space_after = Pt(4)
    paragraph.paragraph_format.line_spacing = 1.04
    run = paragraph.add_run(text)
    run.font.name = "Aptos"
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(INK.lstrip("#"))
    return paragraph


def add_doc_heading(doc, text, level=2):
    paragraph = doc.add_paragraph(style=f"Heading {level}")
    paragraph.paragraph_format.keep_with_next = True
    paragraph.add_run(text)


def add_doc_image(doc, filename, width, caption):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(1)
    paragraph.add_run().add_picture(str(ASSETS / filename), width=Inches(width))
    caption_paragraph = doc.add_paragraph()
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_paragraph.paragraph_format.space_after = Pt(3)
    run = caption_paragraph.add_run(caption)
    run.italic = True
    run.font.name = "Aptos"
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor.from_string(MUTED.lstrip("#"))


def add_doc_image_grid(doc, images):
    table = doc.add_table(rows=2, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for cell in (cell for row in table.rows for cell in row.cells):
        cell.width = Inches(3.2)
    for index, (filename, caption) in enumerate(images):
        cell = table.cell(index // 2, index % 2)
        cell.text = ""
        image_paragraph = cell.paragraphs[0]
        image_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        image_paragraph.paragraph_format.space_after = Pt(0)
        image_paragraph.add_run().add_picture(
            str(ASSETS / filename), width=Inches(3.0)
        )
        caption_paragraph = cell.add_paragraph()
        caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption_paragraph.paragraph_format.space_after = Pt(1)
        run = caption_paragraph.add_run(caption)
        run.italic = True
        run.font.name = "Aptos"
        run.font.size = Pt(7.5)
        run.font.color.rgb = RGBColor.from_string(MUTED.lstrip("#"))
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def build_docx(pages, icon_path, wordmark_path):
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.62)
    section.left_margin = Inches(0.82)
    section.right_margin = Inches(0.82)
    section.header_distance = Inches(0.28)
    section.footer_distance = Inches(0.28)
    section.different_first_page_header_footer = True

    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(9.1)
    normal.font.color.rgb = RGBColor.from_string(INK.lstrip("#"))
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.04
    for name, size, color in [
        ("Heading 1", 18, NAVY),
        ("Heading 2", 11, BLUE),
        ("Heading 3", 9.5, NAVY),
    ]:
        style = doc.styles[name]
        style.font.name = "Aptos Display"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color.lstrip("#"))
        style.paragraph_format.space_before = Pt(7)
        style.paragraph_format.space_after = Pt(4)

    header = section.header
    table = header.add_table(rows=1, cols=2, width=Inches(6.6))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.cell(0, 0).width = Inches(0.38)
    table.cell(0, 1).width = Inches(6.2)
    table.cell(0, 0).paragraphs[0].add_run().add_picture(str(icon_path), width=Inches(0.26))
    set_cell(
        table.cell(0, 1),
        "RETAIL SALES ANALYTICS  |  PROJECT REPORT",
        bold=True,
        color=NAVY,
        size=7.6,
        alignment=WD_ALIGN_PARAGRAPH.RIGHT,
    )
    header.paragraphs[0].paragraph_format.space_after = Pt(0)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = footer.add_run("RETAIL SALES ANALYTICS  |  ")
    run.font.size = Pt(7.5)
    run.font.color.rgb = RGBColor.from_string(MUTED.lstrip("#"))
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)
    section.first_page_footer.paragraphs[0].text = ""

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(48)
    paragraph.paragraph_format.space_after = Pt(16)
    paragraph.add_run().add_picture(str(wordmark_path), width=Inches(5.0))
    for text, size, color, before, after in [
        ("RETAIL SALES ANALYTICS SYSTEM", 23, NAVY, 18, 6),
        ("A PROJECT REPORT", 12, BLUE, 0, 28),
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.space_after = Pt(after)
        r = p.add_run(text)
        r.bold = True
        r.font.name = "Aptos Display"
        r.font.size = Pt(size)
        r.font.color.rgb = RGBColor.from_string(color.lstrip("#"))
    for text in [
        "Submitted by",
        "____________________________________________",
        "Student / Registration ID: __________________________",
        "in partial fulfillment of the requirements for",
        "Programme / Department: __________________________",
        "Institution: _______________________________________",
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(5)
        r = p.add_run(text)
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor.from_string(INK.lstrip("#"))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(22)
    r = p.add_run("OCTOBER 2026")
    r.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor.from_string(NAVY.lstrip("#"))
    doc.add_page_break()

    for page_index, page in enumerate(pages):
        if page_index:
            doc.add_page_break()
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(page["section"].upper())
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor.from_string(BLUE.lstrip("#"))
        add_doc_heading(doc, page["title"], 1)
        for block in page["blocks"]:
            kind = block[0]
            if kind == "p":
                add_doc_paragraph(doc, block[1])
            elif kind == "small":
                add_doc_paragraph(doc, block[1], size=7.9)
            elif kind == "h":
                add_doc_heading(doc, block[1])
            elif kind == "bullets":
                for text in block[1]:
                    p = doc.add_paragraph(style="List Bullet")
                    p.paragraph_format.left_indent = Inches(0.22)
                    p.paragraph_format.first_line_indent = Inches(-0.12)
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.02
                    r = p.add_run(text)
                    r.font.size = Pt(8.6)
            elif kind == "table":
                add_doc_table(doc, block[1], block[2])
            elif kind == "image":
                add_doc_image(doc, block[1], block[2], block[3])
            elif kind == "image_grid":
                add_doc_image_grid(doc, block[1])
            elif kind == "callout":
                table = doc.add_table(rows=1, cols=1)
                shade(table.cell(0, 0), LIGHT_BLUE)
                set_cell(table.cell(0, 0), block[1], color=NAVY, size=8.2)
                doc.add_paragraph().paragraph_format.space_after = Pt(0)
            elif kind == "space":
                doc.add_paragraph().paragraph_format.space_after = Pt(block[1])
    doc.save(DOCX_PATH)


def escape_markup(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("·", " | ")
        .replace("×", "x")
        .replace("–", "-")
        .replace("’", "'")
        .replace("“", "&quot;")
        .replace("”", "&quot;")
        .replace("\n", "<br/>")
    )


def build_pdf(pages, icon_path, wordmark_path):
    font_dir = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    for name, filename in [
        ("ReportSans", "DejaVuSans.ttf"),
        ("ReportBold", "DejaVuSans-Bold.ttf"),
        ("ReportItalic", "DejaVuSans-Oblique.ttf"),
    ]:
        pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            fontName="ReportBold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor(NAVY),
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportChapter",
            fontName="ReportBold",
            fontSize=8.5,
            leading=10,
            textColor=colors.HexColor(BLUE),
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportSubhead",
            fontName="ReportBold",
            fontSize=10.2,
            leading=12.5,
            textColor=colors.HexColor(BLUE),
            spaceBefore=4,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportBody",
            fontName="ReportSans",
            fontSize=7.9,
            leading=9.9,
            textColor=colors.HexColor(INK),
            spaceAfter=3.5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportSmall",
            fontName="ReportSans",
            fontSize=7.3,
            leading=8.8,
            textColor=colors.HexColor(INK),
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportBullet",
            fontName="ReportSans",
            fontSize=7.7,
            leading=9.4,
            leftIndent=12,
            firstLineIndent=-7,
            textColor=colors.HexColor(INK),
            spaceAfter=1.5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportTable",
            fontName="ReportSans",
            fontSize=7.0,
            leading=8.3,
            textColor=colors.HexColor(INK),
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportTableHeader",
            fontName="ReportBold",
            fontSize=7.0,
            leading=8.3,
            textColor=colors.white,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportCaption",
            fontName="ReportItalic",
            fontSize=7.0,
            leading=8.2,
            textColor=colors.HexColor(MUTED),
            alignment=1,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportCallout",
            fontName="ReportSans",
            fontSize=7.6,
            leading=9.3,
            textColor=colors.HexColor(NAVY),
        )
    )

    def paragraph(text, style="ReportBody"):
        return Paragraph(escape_markup(text), styles[style])

    def table(data, widths):
        cell_data = []
        for row_index, row in enumerate(data):
            style = "ReportTableHeader" if row_index == 0 else "ReportTable"
            cell_data.append([paragraph(item, style) for item in row])
        result = PDFTable(
            cell_data,
            colWidths=[width * 72 for width in widths],
            repeatRows=1,
            hAlign="LEFT",
        )
        result.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(PALE)]),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor(LINE)),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        return result

    def callout(text):
        box = PDFTable([[paragraph(text, "ReportCallout")]], colWidths=[6.65 * 72])
        box.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(LIGHT_BLUE)),
                    ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor(LINE)),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        return box

    def figure(filename, width, caption):
        image_path = ASSETS / filename
        with Image.open(image_path) as image:
            height = width * image.height / image.width
        result = PDFImage(str(image_path), width=width * 72, height=height * 72)
        result.hAlign = "CENTER"
        return [result, paragraph(caption, "ReportCaption")]

    def figure_grid(items, width=3.12):
        cells = []
        for filename, caption in items:
            image_path = ASSETS / filename
            with Image.open(image_path) as image:
                height = width * image.height / image.width
            picture = PDFImage(
                str(image_path), width=width * 72, height=height * 72
            )
            picture.hAlign = "CENTER"
            cells.append([picture, paragraph(caption, "ReportCaption")])
        grid = PDFTable(
            [[cells[0], cells[1]], [cells[2], cells[3]]],
            colWidths=[3.22 * 72, 3.22 * 72],
            hAlign="CENTER",
        )
        grid.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        return grid

    story = [
        Spacer(1, 28 * mm),
        PDFImage(str(wordmark_path), width=4.9 * 72, height=4.9 * 72 * 340 / 1500),
        Spacer(1, 9 * mm),
        Paragraph(
            "RETAIL SALES ANALYTICS SYSTEM",
            ParagraphStyle(
                "CoverTitle",
                fontName="ReportBold",
                fontSize=22,
                leading=27,
                textColor=colors.HexColor(NAVY),
                alignment=1,
                spaceAfter=7,
            ),
        ),
        Paragraph(
            "A PROJECT REPORT",
            ParagraphStyle(
                "CoverSubtitle",
                fontName="ReportBold",
                fontSize=11,
                leading=14,
                textColor=colors.HexColor(BLUE),
                alignment=1,
                spaceAfter=20,
            ),
        ),
    ]
    for text in [
        "Submitted by",
        "____________________________________________",
        "Student / Registration ID: __________________________",
        "in partial fulfillment of the requirements for",
        "Programme / Department: __________________________",
        "Institution: _______________________________________",
    ]:
        story.append(
            Paragraph(
                escape_markup(text),
                ParagraphStyle(
                    f"CoverField{len(story)}",
                    fontName="ReportSans",
                    fontSize=9,
                    leading=13,
                    textColor=colors.HexColor(INK),
                    alignment=1,
                    spaceAfter=3,
                ),
            )
        )
    story += [
        Spacer(1, 10 * mm),
        Paragraph(
            "OCTOBER 2026",
            ParagraphStyle(
                "CoverDate",
                fontName="ReportBold",
                fontSize=9,
                textColor=colors.HexColor(NAVY),
                alignment=1,
            ),
        ),
        PageBreak(),
    ]

    for page_index, page in enumerate(pages):
        story.append(paragraph(page["section"].upper(), "ReportChapter"))
        story.append(paragraph(page["title"], "ReportTitle"))
        for block in page["blocks"]:
            kind = block[0]
            if kind == "p":
                story.append(paragraph(block[1]))
            elif kind == "small":
                story.append(paragraph(block[1], "ReportSmall"))
            elif kind == "h":
                story.append(paragraph(block[1], "ReportSubhead"))
            elif kind == "bullets":
                story.extend(paragraph("- " + item, "ReportBullet") for item in block[1])
            elif kind == "table":
                story.extend([table(block[1], block[2]), Spacer(1, 3)])
            elif kind == "image":
                story.extend(figure(block[1], block[2], block[3]))
            elif kind == "image_grid":
                story.append(figure_grid(block[1]))
            elif kind == "callout":
                story.extend([Spacer(1, 2), callout(block[1])])
            elif kind == "space":
                story.append(Spacer(1, block[1] * mm))
        if page_index < len(pages) - 1:
            story.append(PageBreak())

    def page_furniture(canvas, document, cover=False):
        canvas.saveState()
        page_width, page_height = A4
        if not cover:
            canvas.drawImage(
                str(icon_path),
                18 * mm,
                page_height - 15 * mm,
                width=6 * mm,
                height=6 * mm,
                mask="auto",
            )
            canvas.setFont("ReportBold", 7)
            canvas.setFillColor(colors.HexColor(NAVY))
            canvas.drawString(
                26 * mm, page_height - 11 * mm, "RETAIL SALES ANALYTICS  |  PROJECT REPORT"
            )
            canvas.setStrokeColor(colors.HexColor(LINE))
            canvas.setLineWidth(0.5)
            canvas.line(
                18 * mm,
                page_height - 17 * mm,
                page_width - 18 * mm,
                page_height - 17 * mm,
            )
            canvas.line(18 * mm, 13 * mm, page_width - 18 * mm, 13 * mm)
            canvas.setFont("ReportSans", 7)
            canvas.setFillColor(colors.HexColor(MUTED))
            canvas.drawString(18 * mm, 8 * mm, "RETAIL SALES ANALYTICS  |  OCTOBER 2026")
            canvas.drawRightString(page_width - 18 * mm, 8 * mm, str(document.page))
        canvas.restoreState()

    pdf = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=19 * mm,
        title="Retail Sales Analytics System - Project Report",
        author="Retail Sales Analytics Project",
    )
    pdf.build(
        story,
        onFirstPage=lambda canvas, document: page_furniture(canvas, document, cover=True),
        onLaterPages=page_furniture,
    )


def main():
    icon_path, wordmark_path = create_artwork()
    pages = build_content()
    build_docx(pages, icon_path, wordmark_path)
    build_pdf(pages, icon_path, wordmark_path)
    print(f"Created {DOCX_PATH}")
    print(f"Created {PDF_PATH}")
    print(f"Report pages (including cover): {len(pages) + 1}")


if __name__ == "__main__":
    main()
