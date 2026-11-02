-- =====================================================
-- Retail Sales Analytics System - Sample Data
-- Run AFTER schema.sql. Safe to re-run (clears tables first).
-- =====================================================
USE retail_sales;

DELETE FROM sale_items;
DELETE FROM sales;
DELETE FROM products;
DELETE FROM customers;

-- ---------- customers ----------
INSERT INTO customers (customer_id, full_name, email, city, state) VALUES
(1,  'Aarav Sharma',   'aarav.sharma@example.com',   'Hisar',      'Haryana'),
(2,  'Priya Verma',    'priya.verma@example.com',    'Delhi',      'Delhi'),
(3,  'Rohan Mehta',    'rohan.mehta@example.com',    'Mumbai',     'Maharashtra'),
(4,  'Sneha Reddy',    'sneha.reddy@example.com',    'Hyderabad',  'Telangana'),
(5,  'Vikram Singh',   'vikram.singh@example.com',   'Jaipur',     'Rajasthan'),
(6,  'Anjali Gupta',   'anjali.gupta@example.com',   'Lucknow',    'Uttar Pradesh'),
(7,  'Karan Malhotra', 'karan.malhotra@example.com', 'Chandigarh', 'Chandigarh'),
(8,  'Neha Kapoor',    'neha.kapoor@example.com',    'Gurugram',   'Haryana'),
(9,  'Rahul Nair',     'rahul.nair@example.com',     'Kochi',      'Kerala'),
(10, 'Pooja Iyer',     'pooja.iyer@example.com',     'Chennai',    'Tamil Nadu'),
(11, 'Amit Chauhan',   'amit.chauhan@example.com',   'Rohtak',     'Haryana'),
(12, 'Divya Joshi',    'divya.joshi@example.com',    'Pune',       'Maharashtra'),
(13, 'Sandeep Yadav',  'sandeep.yadav@example.com',  'Hisar',      'Haryana'),
(14, 'Meera Bansal',   'meera.bansal@example.com',   'Ludhiana',   'Punjab'),
(15, 'Arjun Das',      'arjun.das@example.com',      'Kolkata',    'West Bengal');

-- ---------- products ----------
INSERT INTO products (product_id, product_name, category, unit_price) VALUES
(1,  'Wireless Mouse',        'Electronics',    799.00),
(2,  'Bluetooth Headphones',  'Electronics',   2499.00),
(3,  'USB-C Charger',         'Electronics',   1299.00),
(4,  'Smartwatch',            'Electronics',   4999.00),
(5,  'Cotton T-Shirt',        'Clothing',       599.00),
(6,  'Denim Jeans',           'Clothing',      1799.00),
(7,  'Running Shoes',         'Clothing',      3499.00),
(8,  'Basmati Rice 5kg',      'Groceries',      650.00),
(9,  'Olive Oil 1L',          'Groceries',      899.00),
(10, 'Green Tea Box',         'Groceries',      349.00),
(11, 'Non-stick Pan',         'Home & Kitchen',1199.00),
(12, 'Mixer Grinder',         'Home & Kitchen',3299.00),
(13, 'Notebook Pack',         'Stationery',     299.00),
(14, 'Gel Pen Set',           'Stationery',     199.00),
(15, 'Steel Water Bottle',    'Home & Kitchen', 449.00);

-- ---------- sales (order headers) ----------
INSERT INTO sales (sale_id, customer_id, sale_date, payment_method) VALUES
(1,  1,  '2026-01-05', 'UPI'),
(2,  2,  '2026-01-12', 'Credit Card'),
(3,  3,  '2026-01-20', 'Cash'),
(4,  4,  '2026-01-28', 'Debit Card'),
(5,  5,  '2026-02-03', 'UPI'),
(6,  6,  '2026-02-10', 'Cash'),
(7,  7,  '2026-02-18', 'Credit Card'),
(8,  8,  '2026-02-25', 'UPI'),
(9,  9,  '2026-03-04', 'Cash'),
(10, 10, '2026-03-11', 'UPI'),
(11, 11, '2026-03-19', 'Debit Card'),
(12, 12, '2026-03-27', 'Credit Card'),
(13, 13, '2026-04-02', 'UPI'),
(14, 14, '2026-04-09', 'Cash'),
(15, 15, '2026-04-16', 'UPI'),
(16, 1,  '2026-04-24', 'Credit Card'),
(17, 2,  '2026-05-05', 'UPI'),
(18, 3,  '2026-05-13', 'Cash'),
(19, 4,  '2026-05-21', 'Debit Card'),
(20, 5,  '2026-05-29', 'UPI'),
(21, 6,  '2026-06-06', 'Credit Card'),
(22, 7,  '2026-06-14', 'UPI'),
(23, 8,  '2026-06-22', 'Cash'),
(24, 9,  '2026-07-03', 'UPI'),
(25, 10, '2026-07-11', 'Debit Card'),
(26, 11, '2026-07-19', 'Credit Card'),
(27, 12, '2026-07-30', 'UPI'),
(28, 13, '2026-08-07', 'Cash'),
(29, 14, '2026-08-15', 'UPI'),
(30, 15, '2026-08-23', 'Credit Card'),
(31, 1,  '2026-09-02', 'UPI'),
(32, 2,  '2026-09-10', 'Debit Card'),
(33, 3,  '2026-09-18', 'Cash'),
(34, 4,  '2026-09-26', 'UPI'),
(35, 5,  '2026-10-05', 'Credit Card'),
(36, 6,  '2026-10-14', 'UPI'),
(37, 7,  '2026-10-21', 'Cash');

-- ---------- sale_items (order lines) ----------
-- (sale_id, product_id, quantity, unit_price, discount_rate)
INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, discount_rate) VALUES
(1,  2,  1, 2499.00, 0.000), (1,  10, 2,  349.00, 0.000),
(2,  4,  1, 4999.00, 0.100), (2,  3,  1, 1299.00, 0.000),
(3,  8,  2,  650.00, 0.000), (3,  9,  1,  899.00, 0.050),
(4,  5,  3,  599.00, 0.100), (4,  6,  1, 1799.00, 0.000),
(5,  13, 4,  299.00, 0.000), (5,  14, 6,  199.00, 0.000),
(6,  7,  1, 3499.00, 0.150),
(7,  12, 1, 3299.00, 0.100), (7,  15, 2,  449.00, 0.000),
(8,  1,  2,  799.00, 0.000), (8,  3,  1, 1299.00, 0.050),
(9,  8,  3,  650.00, 0.050), (9,  10, 2,  349.00, 0.000),
(10, 2,  1, 2499.00, 0.100), (10, 1,  1,  799.00, 0.000),
(11, 11, 2, 1199.00, 0.000), (11, 15, 3,  449.00, 0.050),
(12, 4,  1, 4999.00, 0.000), (12, 2,  1, 2499.00, 0.050),
(13, 6,  2, 1799.00, 0.100), (13, 5,  2,  599.00, 0.000),
(14, 9,  2,  899.00, 0.000), (14, 10, 3,  349.00, 0.050),
(15, 13, 5,  299.00, 0.050), (15, 14, 10, 199.00, 0.100),
(16, 7,  1, 3499.00, 0.000), (16, 5,  1,  599.00, 0.000),
(17, 12, 1, 3299.00, 0.050),
(18, 8,  4,  650.00, 0.100), (18, 9,  2,  899.00, 0.000),
(19, 3,  2, 1299.00, 0.000), (19, 1,  1,  799.00, 0.100),
(20, 11, 1, 1199.00, 0.050), (20, 15, 2,  449.00, 0.000),
(21, 4,  1, 4999.00, 0.150), (21, 2,  1, 2499.00, 0.000),
(22, 6,  1, 1799.00, 0.000), (22, 7,  1, 3499.00, 0.100),
(23, 10, 4,  349.00, 0.000), (23, 8,  2,  650.00, 0.000),
(24, 12, 1, 3299.00, 0.000), (24, 11, 1, 1199.00, 0.100),
(25, 1,  3,  799.00, 0.050), (25, 14, 5,  199.00, 0.000),
(26, 2,  2, 2499.00, 0.100),
(27, 5,  4,  599.00, 0.050), (27, 6,  2, 1799.00, 0.050),
(28, 9,  3,  899.00, 0.100), (28, 10, 1,  349.00, 0.000),
(29, 4,  1, 4999.00, 0.050), (29, 3,  1, 1299.00, 0.000),
(30, 7,  2, 3499.00, 0.100),
(31, 13, 6,  299.00, 0.000), (31, 14, 8,  199.00, 0.050),
(32, 12, 1, 3299.00, 0.100), (32, 15, 1,  449.00, 0.000),
(33, 8,  5,  650.00, 0.050),
(34, 2,  1, 2499.00, 0.000), (34, 1,  1,  799.00, 0.000),
(35, 4,  2, 4999.00, 0.100), (35, 3,  2, 1299.00, 0.050),
(36, 6,  3, 1799.00, 0.100), (36, 5,  3,  599.00, 0.000),
-- Sale 37: deliberate bulk order (outlier for the Excel analysis)
(37, 14, 30, 199.00, 0.150), (37, 13, 20, 299.00, 0.150);