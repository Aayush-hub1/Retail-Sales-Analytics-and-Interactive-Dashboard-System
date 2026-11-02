# Excel Analysis Guide

Dataset: `data/sales_dataset.csv` (69 rows, one per sale item, exported from the MySQL view `v_sales_detail`).
Columns: A sale_id, B sale_date, C customer, D product_name, E category, F quantity, G revenue, H payment_method.
Known totals to check against: revenue 159188.00, 201 units, 37 orders.

## 1. Open and clean the data
1. Open the CSV, then **Save As** `sales_dataset.xlsx` (keep the CSV untouched).
2. Select column G, then Home > Number > Number with 2 decimals. If values are left-aligned, they are text: Data > Text to Columns > Finish.
3. Remove stray spaces: in a helper column use `=TRIM(C2)` and fill down.
4. Check duplicates: Data > Remove Duplicates is NOT appropriate here, because sales repeat a sale_id for each item. Use `=COUNTIFS($A$2:$A$70,A2,$D$2:$D$70,D2)` instead; every result should be 1.
5. Check blanks: Home > Find & Select > Go To Special > Blanks (expect none).
6. Sanity check: `=SUM(G2:G70)` should give 159188 and `=SUM(F2:F70)` should give 201.

## 2. CONCAT and text functions
- Label: `=CONCAT(C2," - ",D2)` or `=C2&" - "&D2` in column I.
- First name: `=LEFT(C2,FIND(" ",C2)-1)`.
- Upper case: `=UPPER(E2)`.

## 3. Sorting and filtering
- Select the header, Data > Filter. Filter category = Electronics.
- Sort revenue largest to smallest: Data > Sort > revenue > Largest to Smallest. The top row should be 8998.20 (Smartwatch, sale 35).
- Filtered total: `=SUBTOTAL(109,G2:G70)` changes with the filter; `SUM` does not.

## 4. Lookups
Create a small price table on a new sheet "Prices" (product_name in A, unit_price in B), then in the data sheet:
- `=XLOOKUP(D2,Prices!A:A,Prices!B:B)` (Excel 365/2021), or
- `=VLOOKUP(D2,Prices!A:B,2,FALSE)` (all versions).
Use `=IFERROR(...,"Not found")` to catch typos.

## 5. Conditional formatting
- Home > Conditional Formatting > Top/Bottom Rules > Top 10 Items on column G to highlight the biggest lines.
- Highlight Cells Rules > Greater Than > 5000 for large orders.
- Data Bars on column F (quantity) makes the bulk rows (20 and 30 units) stand out.

## 6. PivotTables
Insert > PivotTable from the data range, new sheet.
1. Rows = category, Values = Sum of revenue. Expected: Electronics 59203.25, Clothing 38519.55, Groceries 20893.00, Home & Kitchen 20512.05, Stationery 20060.15.
2. Rows = sale_date grouped by Months, Values = Sum of revenue. Expected 10 months, October 28278.10.
3. Rows = payment_method, Values = Sum of revenue. Expected UPI 58612.95.
4. Add a Slicer on category (PivotTable Analyze > Insert Slicer).
5. Insert > PivotChart for a visual.
These totals match the SQL queries in `database/analysis.sql` (sections 2.2, 2.3 and 2.5).

## 7. Mean, median, mode
Using revenue in G2:G70:
- Mean: `=AVERAGE(G2:G70)` (expected about 2307.07)
- Median: `=MEDIAN(G2:G70)`
- Mode of quantity: `=MODE.SNGL(F2:F70)`
- Standard deviation: `=STDEV.S(G2:G70)`
The mean is higher than the median because a few large lines pull it up.

## 8. Outliers
Sale 37 is a deliberate bulk outlier (20 and 30 units, about 10157.50 in total).
1. `=QUARTILE.INC(G2:G70,1)` in K1 and `=QUARTILE.INC(G2:G70,3)` in K2.
2. IQR: `=K2-K1`.
3. Upper fence: `=K2+1.5*(K2-K1)`.
4. Flag: `=IF(G2>$K$3,"Outlier","")`.
5. Do the same for quantity (column F). Rows 20 and 30 units should be flagged.
6. Compare the mean with and without sale 37 to show its effect.