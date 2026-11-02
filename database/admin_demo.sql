-- Retail Sales Analytics System: DML, DDL, views, indexes, metadata, privileges
-- Run as root: Get-Content admin_demo.sql | mysql -u root -p retail_sales
-- All changes use a scratch table (demo_discounts) and a throwaway user.
-- Safe to rerun.

USE retail_sales;

-- ===================== DDL =====================

DROP TABLE IF EXISTS demo_discounts;

-- 4.1 CREATE TABLE
CREATE TABLE demo_discounts (
  discount_id   INT AUTO_INCREMENT PRIMARY KEY,
  category      VARCHAR(50)  NOT NULL,
  discount_rate DECIMAL(4,3) NOT NULL,
  note          VARCHAR(100)
);

-- 4.2 ALTER TABLE
ALTER TABLE demo_discounts ADD COLUMN active TINYINT(1) NOT NULL DEFAULT 1;
DESCRIBE demo_discounts;

-- ===================== DML =====================

-- 4.3 INSERT
INSERT INTO demo_discounts (category, discount_rate, note) VALUES
  ('Electronics', 0.100, 'Festival offer'),
  ('Clothing',    0.050, 'Season sale'),
  ('Stationery',  0.150, 'Bulk order offer');
SELECT * FROM demo_discounts;

-- 4.4 UPDATE
UPDATE demo_discounts SET discount_rate = 0.120 WHERE category = 'Electronics';
SELECT category, discount_rate FROM demo_discounts WHERE category = 'Electronics';

-- 4.5 DELETE
DELETE FROM demo_discounts WHERE category = 'Clothing';
SELECT COUNT(*) AS rows_left FROM demo_discounts;

-- ===================== VIEW =====================

-- 4.6 View: one row per sale item with names and revenue
CREATE OR REPLACE VIEW v_sales_detail AS
SELECT
  s.sale_id,
  s.sale_date,
  c.full_name AS customer,
  p.product_name,
  p.category,
  si.quantity,
  ROUND(si.quantity * si.unit_price * (1 - si.discount_rate), 2) AS revenue,
  s.payment_method
FROM sales s
INNER JOIN customers c   ON c.customer_id = s.customer_id
INNER JOIN sale_items si ON si.sale_id = s.sale_id
INNER JOIN products p    ON p.product_id = si.product_id;

SELECT COUNT(*) AS view_rows, ROUND(SUM(revenue), 2) AS view_revenue FROM v_sales_detail;

-- ===================== INDEX =====================

-- 4.7 Index
CREATE INDEX idx_demo_category ON demo_discounts (category);
SHOW INDEX FROM demo_discounts;
EXPLAIN SELECT * FROM demo_discounts WHERE category = 'Electronics';

-- ===================== METADATA =====================

-- 4.8 information_schema and SHOW
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'retail_sales'
ORDER BY table_name;

SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'retail_sales' AND table_name = 'sale_items'
ORDER BY ordinal_position;

SHOW TABLES;

-- ===================== PRIVILEGES =====================

-- 4.9 Throwaway read-only user
CREATE USER IF NOT EXISTS 'demo_reader'@'localhost' IDENTIFIED BY 'Demo#12345';
GRANT SELECT ON retail_sales.products TO 'demo_reader'@'localhost';
SHOW GRANTS FOR 'demo_reader'@'localhost';
REVOKE SELECT ON retail_sales.products FROM 'demo_reader'@'localhost';
SHOW GRANTS FOR 'demo_reader'@'localhost';
DROP USER 'demo_reader'@'localhost';

-- ===================== CLEANUP =====================

DROP TABLE demo_discounts;
SELECT COUNT(*) AS sales_still_there FROM sales;
SELECT COUNT(*) AS items_still_there FROM sale_items;