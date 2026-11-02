# Retail Sales Analytics System: Mini Project Report

## 1. Introduction
This project analyses the sales of a small retail business. Data is stored in a MySQL database, served through a Flask REST API, and shown on a web dashboard with KPIs, charts, a searchable and filterable sales table, and forms to record sales, customers and products. The filtered data can be downloaded as an Excel file, and an exported CSV is analysed further in Excel.

## 2. Objectives
- Design a normalised relational database for retail sales.
- Write SQL queries covering selection, joins, aggregation, subqueries, set operators, views, indexes and privileges.
- Build a Flask API and a web dashboard that uses it.
- Let the user filter the data (text, dates, one or more categories) and download the result as Excel.
- Analyse the exported data in Excel (cleaning, lookups, PivotTables, statistics, outliers).

## 3. Technology Stack
| Layer | Tool |
|---|---|
| Database | MySQL 8.0.43 |
| Backend | Python 3.14, Flask, PyMySQL, Flask-CORS, openpyxl |
| Frontend | HTML, CSS, vanilla JavaScript, Chart.js 4.4.1 |
| Analysis | SQL scripts, Excel |

## 4. Database Design
Four tables: `customers` (15 rows), `products` (15 rows, 5 categories), `sales` (37 rows) and `sale_items` (69 rows). `sales` links to `customers`. `sale_items` links to `sales` and `products` and stores the unit price and discount at the time of sale, so later price changes do not alter history. Deleting a sale cascades to its items. Customer email and product name are unique, and a CHECK constraint requires a product price above 0. A view, `v_sales_detail`, joins all four tables.

## 5. System Design
- `backend/app.py` creates the Flask app, enables CORS for `/api/*`, returns JSON errors, and serves the frontend from `frontend/`.
- Routes: `health`, `dashboard`, `sales`, `export` and `master`.
- Endpoints: `GET /api/health`, `/api/stats`, `/api/charts/monthly-revenue`, `/api/charts/category-sales`, `/api/products`, `/api/customers`, `/api/categories`, `/api/sales` (filters: q, date_from, date_to, category as a comma-separated list), `GET /api/export/excel` (same filters), and `POST` on `/api/sales`, `/api/customers` and `/api/products`.
- The server reads the sale price from the products table, so the browser cannot set it. Inputs are validated, and all SQL uses parameter placeholders.
- `frontend/js/app.js` loads all data from the API; no numbers are hardcoded. The KPI cards and both charts are built from the rows returned by `/api/sales`, so they follow the active filters. The earlier stats and chart endpoints remain available.
- Category checkboxes are built from the database, so a new product with a new category appears automatically.

## 6. Results (verified)
| Measure | Value |
|---|---|
| Orders | 37 |
| Units sold | 201 |
| Revenue | 159188.00 |
| Average order value | 4302.38 |

Revenue by category: Electronics 59203.25, Clothing 38519.55, Groceries 20893.00, Home & Kitchen 20512.05, Stationery 20060.15. Revenue by payment method: UPI 58612.95, Credit Card 50147.10, Cash 33326.65, Debit Card 17101.30. October 2026 is the strongest month (28278.10).

The API totals, the SQL totals and the chart values agree. An automated check (`docs/e2e_check.ps1`) passes 15 of 15 checks on the clean data. Multi-category filtering returned 35 rows for Clothing + Electronics and 49 rows with Groceries added, and the Excel export for Clothing + Electronics had 35 data rows. Test records created through the web forms and the API were removed afterwards so the verified numbers stand.

## 7. Outlier Analysis
Sale 37 is a deliberate bulk order (20 notebook packs and 30 gel pens at 15% discount, about 10157.50 in total). It raises October revenue and Karan Malhotra's total, and the mean line revenue (2307.07) sits above a typical line. The Excel guide describes quartile and fence checks to flag it.

## 8. Testing Notes
Verified with real output: database totals, all API endpoints, the SQL scripts, the CSV export, filtering, the Excel download, adding a customer, product and sale through the forms, and the end-to-end script.

Not tested: the Save Sale validation message when no customer is selected, browser Console errors, the Total row values inside a downloaded Excel file, the Summary sheet of `sales_report.xlsx`, and the Excel guide steps (its expected numbers come from the SQL results, not from Excel).

## 9. Limitations
- Single store, small sample data.
- No login: anyone who opens the page can add records.
- A sale holds one product per form submission.
- No edit or delete screens for sales, customers or products.

## 10. Conclusion
The system covers the full path from database to dashboard to Excel download and analysis, and its numbers agree at every layer.