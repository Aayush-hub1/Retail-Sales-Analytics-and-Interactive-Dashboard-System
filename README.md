# Retail Sales Analytics System

A mini project: MySQL database, Flask REST API, a web dashboard (HTML/CSS/JS + Chart.js) and Excel analysis of an exported CSV.

## Features
- KPI cards (revenue, orders, units, average order value) and two charts (monthly revenue, sales by category).
- Searchable, filterable sales table: text search, date range, and one or more categories (tick any number of category boxes; none ticked = all).
- KPIs, charts and table all follow the active filters.
- **Download Excel** button: exports the currently filtered rows to `sales_export.xlsx` with a Total row.
- Forms to record a new sale, add a customer and add a product. A new product with a new category appears in the category filter automatically.
- SQL scripts and an Excel guide for further analysis.

## Project structure
- `backend/` Flask app: `app.py`, `config.py`, `db.py`, `routes/` (`health`, `dashboard`, `sales`, `export`, `master`)
- `frontend/` `index.html`, `css/style.css`, `js/app.js`
- `database/` `schema.sql`, `sample_data.sql`, `analysis.sql`, `admin_demo.sql`
- `data/` `sales_dataset.csv` (69 rows from the view `v_sales_detail`), `make_excel.py` (builds `sales_report.xlsx`)
- `docs/` `excel_guide.md`, `report.md`, `viva_questions.md`, `e2e_check.ps1`, and the ten-page academic-style `retail_sales_analytics_project_report.docx` / `.pdf` (original logo, analysis figures, and project UI screenshots in `docs/report_assets/`; regenerate with `python docs\generate_project_report.py`)

## Requirements
Windows, Python 3.14, MySQL 8.0.31 or later (INTERSECT/EXCEPT are used), PowerShell.

## Setup
1. Create and activate a virtual environment, then install the packages:
   `pip install flask flask-cors pymysql openpyxl`
2. Load the database as an admin user (`schema.sql` creates the `retail_sales` database):
   `Get-Content database\schema.sql | mysql -u root -p`
   `Get-Content database\sample_data.sql | mysql -u root -p retail_sales`
3. Put the MySQL credentials of the `retail_app` user in the `.env` file read by `config.py`. Never share or commit this file.

## Run
    cd backend
    python app.py
Open http://127.0.0.1:5000/

## API
- `GET /api/health`, `/api/stats`, `/api/charts/monthly-revenue`, `/api/charts/category-sales`
- `GET /api/products`, `/api/customers`, `/api/categories`
- `GET /api/sales?q=&date_from=&date_to=&category=Clothing,Electronics`
- `GET /api/export/excel` (same filters as `/api/sales`)
- `POST /api/sales`, `POST /api/customers`, `POST /api/products`

## Test
With the server running, in a second PowerShell window:

    powershell -ExecutionPolicy Bypass -File docs\e2e_check.ps1

Expected data: 37 orders, 201 units, revenue 159188.00, 15 customers, 15 products, 5 categories, 69 sale items. The check fails if test data is left in the database.

Test records made through the web forms must be removed before re-running the check. Delete in this order (sale first, then product, then customer), using the real IDs:

    DELETE FROM sales WHERE sale_id = <id>;
    DELETE FROM products WHERE product_id = <id>;
    DELETE FROM customers WHERE customer_id = <id>;

## SQL scripts
- `Get-Content database\analysis.sql | mysql -u root -p retail_sales` (read-only queries)
- `Get-Content database\admin_demo.sql | mysql -u root -p retail_sales` (DDL/DML on a scratch table and a throwaway user; safe to rerun)

## Excel
- `data/sales_dataset.csv` is the exported dataset; see `docs/excel_guide.md`.
- `python data\make_excel.py` builds `data/sales_report.xlsx` with a Sales sheet and a Summary sheet.

## Known limitations
No login, single store, one product per sale form submission, no edit or delete screens for sales, customers or products.