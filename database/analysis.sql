-- Retail Sales Analytics System: analysis queries
-- Run with: Get-Content analysis.sql | mysql -u root -p retail_sales
-- Section 1: SELECT, WHERE, ORDER BY, string / date / numeric functions
-- Section 2: aggregates, GROUP BY, HAVING, INNER JOIN, LEFT JOIN
-- Section 3: subqueries, UNION, INTERSECT, EXCEPT (INTERSECT/EXCEPT need MySQL 8.0.31+)

USE retail_sales;

-- ===================== SECTION 1 =====================

-- 1.1 Basic SELECT with ORDER BY and LIMIT
SELECT product_name, category, unit_price
FROM products
ORDER BY unit_price DESC
LIMIT 5;

-- 1.2 WHERE with AND, IN, BETWEEN, LIKE
SELECT product_name, category, unit_price
FROM products
WHERE category IN ('Electronics', 'Clothing')
  AND unit_price BETWEEN 1000 AND 5000
  AND product_name LIKE '%a%'
ORDER BY unit_price;

-- 1.3 Distinct states
SELECT DISTINCT state FROM customers ORDER BY state;

-- 1.4 String functions
SELECT
  full_name,
  UPPER(full_name)              AS name_upper,
  LENGTH(full_name)             AS name_length,
  SUBSTRING_INDEX(full_name, ' ', 1) AS first_name,
  CONCAT(city, ', ', state)     AS location
FROM customers
ORDER BY full_name
LIMIT 5;

-- 1.5 Date functions
SELECT
  sale_id,
  sale_date,
  YEAR(sale_date)       AS sale_year,
  MONTH(sale_date)      AS sale_month,
  MONTHNAME(sale_date)  AS month_name,
  DAYNAME(sale_date)    AS weekday,
  DATE_FORMAT(sale_date, '%d-%m-%Y') AS indian_format
FROM sales
ORDER BY sale_date DESC
LIMIT 5;

-- 1.6 Numeric functions (line revenue per item)
SELECT
  sale_item_id,
  quantity,
  unit_price,
  discount_rate,
  ROUND(quantity * unit_price * (1 - discount_rate), 2) AS revenue,
  CEIL(quantity * unit_price * discount_rate)           AS discount_ceil,
  FLOOR(quantity * unit_price * discount_rate)          AS discount_floor
FROM sale_items
ORDER BY revenue DESC
LIMIT 5;

-- ===================== SECTION 2 =====================

-- 2.1 Aggregate functions over all sales (should match /api/stats)
SELECT
  COUNT(DISTINCT s.sale_id)                                   AS total_orders,
  SUM(si.quantity)                                            AS total_units,
  ROUND(SUM(si.quantity * si.unit_price * (1 - si.discount_rate)), 2) AS total_revenue,
  ROUND(AVG(si.quantity * si.unit_price * (1 - si.discount_rate)), 2) AS avg_item_revenue,
  MIN(si.unit_price)                                          AS min_price,
  MAX(si.unit_price)                                          AS max_price
FROM sales s
INNER JOIN sale_items si ON si.sale_id = s.sale_id;

-- 2.2 Revenue by category (GROUP BY + INNER JOIN, should match the category chart)
SELECT
  p.category,
  SUM(si.quantity)                                            AS units,
  ROUND(SUM(si.quantity * si.unit_price * (1 - si.discount_rate)), 2) AS revenue
FROM sale_items si
INNER JOIN products p ON p.product_id = si.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- 2.3 Revenue by month (should match the monthly chart)
SELECT
  DATE_FORMAT(s.sale_date, '%Y-%m')                           AS month,
  ROUND(SUM(si.quantity * si.unit_price * (1 - si.discount_rate)), 2) AS revenue
FROM sales s
INNER JOIN sale_items si ON si.sale_id = s.sale_id
GROUP BY DATE_FORMAT(s.sale_date, '%Y-%m')
ORDER BY month;

-- 2.4 GROUP BY with HAVING: customers who spent more than 10000
SELECT
  c.full_name,
  COUNT(DISTINCT s.sale_id)                                   AS orders,
  ROUND(SUM(si.quantity * si.unit_price * (1 - si.discount_rate)), 2) AS total_spent
FROM customers c
INNER JOIN sales s       ON s.customer_id = c.customer_id
INNER JOIN sale_items si ON si.sale_id = s.sale_id
GROUP BY c.customer_id, c.full_name
HAVING total_spent > 10000
ORDER BY total_spent DESC;

-- 2.5 Revenue by payment method
SELECT
  s.payment_method,
  COUNT(DISTINCT s.sale_id)                                   AS orders,
  ROUND(SUM(si.quantity * si.unit_price * (1 - si.discount_rate)), 2) AS revenue
FROM sales s
INNER JOIN sale_items si ON si.sale_id = s.sale_id
GROUP BY s.payment_method
ORDER BY revenue DESC;

-- 2.6 LEFT JOIN: every product, including any that never sold
SELECT
  p.product_name,
  p.category,
  COALESCE(SUM(si.quantity), 0)                               AS units_sold
FROM products p
LEFT JOIN sale_items si ON si.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY units_sold ASC, p.product_name
LIMIT 5;

-- 2.7 LEFT JOIN: customers with no sales (empty result is expected if all 15 bought)
SELECT c.customer_id, c.full_name
FROM customers c
LEFT JOIN sales s ON s.customer_id = c.customer_id
WHERE s.sale_id IS NULL;

-- ===================== SECTION 3 =====================

-- 3.1 Scalar subquery: items priced above the average product price
SELECT product_name, category, unit_price
FROM products
WHERE unit_price > (SELECT AVG(unit_price) FROM products)
ORDER BY unit_price DESC;

-- 3.2 IN subquery: customers who bought anything in Electronics
SELECT full_name
FROM customers
WHERE customer_id IN (
  SELECT s.customer_id
  FROM sales s
  INNER JOIN sale_items si ON si.sale_id = s.sale_id
  INNER JOIN products p    ON p.product_id = si.product_id
  WHERE p.category = 'Electronics'
)
ORDER BY full_name;

-- 3.3 Correlated subquery: each customer's largest single order line
SELECT
  c.full_name,
  (SELECT MAX(si.quantity * si.unit_price * (1 - si.discount_rate))
   FROM sales s
   INNER JOIN sale_items si ON si.sale_id = s.sale_id
   WHERE s.customer_id = c.customer_id) AS biggest_line
FROM customers c
ORDER BY biggest_line DESC
LIMIT 5;

-- 3.4 Subquery in FROM (derived table): order totals above the average order total
SELECT order_totals.sale_id, ROUND(order_totals.total, 2) AS order_total
FROM (
  SELECT sale_id, SUM(quantity * unit_price * (1 - discount_rate)) AS total
  FROM sale_items
  GROUP BY sale_id
) AS order_totals
WHERE order_totals.total > (
  SELECT AVG(t.total)
  FROM (
    SELECT SUM(quantity * unit_price * (1 - discount_rate)) AS total
    FROM sale_items
    GROUP BY sale_id
  ) AS t
)
ORDER BY order_total DESC;

-- 3.5 EXISTS: products that have been sold at least once
SELECT p.product_name
FROM products p
WHERE EXISTS (SELECT 1 FROM sale_items si WHERE si.product_id = p.product_id)
ORDER BY p.product_name
LIMIT 5;

-- 3.6 UNION: customer cities and product categories in one list
SELECT city AS label, 'city' AS kind FROM customers
UNION
SELECT category, 'category' FROM products
ORDER BY kind, label;

-- 3.7 INTERSECT: customers who bought both Electronics and Clothing
SELECT s.customer_id
FROM sales s
INNER JOIN sale_items si ON si.sale_id = s.sale_id
INNER JOIN products p    ON p.product_id = si.product_id
WHERE p.category = 'Electronics'
INTERSECT
SELECT s.customer_id
FROM sales s
INNER JOIN sale_items si ON si.sale_id = s.sale_id
INNER JOIN products p    ON p.product_id = si.product_id
WHERE p.category = 'Clothing';

-- 3.8 EXCEPT: customers who bought Electronics but never Stationery
SELECT s.customer_id
FROM sales s
INNER JOIN sale_items si ON si.sale_id = s.sale_id
INNER JOIN products p    ON p.product_id = si.product_id
WHERE p.category = 'Electronics'
EXCEPT
SELECT s.customer_id
FROM sales s
INNER JOIN sale_items si ON si.sale_id = s.sale_id
INNER JOIN products p    ON p.product_id = si.product_id
WHERE p.category = 'Stationery';