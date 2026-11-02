-- =====================================================
-- Retail Sales Analytics System - Schema
-- Target: MySQL 8.0 (CHECK constraints need 8.0.16+)
-- =====================================================

CREATE DATABASE IF NOT EXISTS retail_sales
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE retail_sales;

-- Drop in child-to-parent order so foreign keys don't block it.
-- WARNING: this deletes existing data. Fine for development only.
DROP TABLE IF EXISTS sale_items;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- ---------- customers ----------
CREATE TABLE customers (
  customer_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  full_name   VARCHAR(100) NOT NULL,
  email       VARCHAR(120) NOT NULL,
  city        VARCHAR(60)  NOT NULL,
  state       VARCHAR(60)  NOT NULL,
  created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (customer_id),
  UNIQUE KEY uq_customers_email (email)
) ENGINE=InnoDB;

-- ---------- products ----------
CREATE TABLE products (
  product_id   INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  product_name VARCHAR(100)  NOT NULL,
  category     VARCHAR(50)   NOT NULL,
  unit_price   DECIMAL(10,2) NOT NULL,
  created_at   TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (product_id),
  UNIQUE KEY uq_products_name (product_name),
  CONSTRAINT chk_products_price CHECK (unit_price > 0),
  INDEX idx_products_category (category)
) ENGINE=InnoDB;

-- ---------- sales (order header) ----------
CREATE TABLE sales (
  sale_id        INT UNSIGNED NOT NULL AUTO_INCREMENT,
  customer_id    INT UNSIGNED NOT NULL,
  sale_date      DATE         NOT NULL,
  payment_method VARCHAR(30)  NOT NULL DEFAULT 'Cash',
  created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (sale_id),
  CONSTRAINT fk_sales_customer FOREIGN KEY (customer_id)
    REFERENCES customers (customer_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  INDEX idx_sales_date (sale_date)
) ENGINE=InnoDB;

-- ---------- sale_items (order lines) ----------
CREATE TABLE sale_items (
  sale_item_id  INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  sale_id       INT UNSIGNED  NOT NULL,
  product_id    INT UNSIGNED  NOT NULL,
  quantity      INT UNSIGNED  NOT NULL,
  unit_price    DECIMAL(10,2) NOT NULL,           -- price at time of sale
  discount_rate DECIMAL(4,3)  NOT NULL DEFAULT 0, -- 0.000 to 1.000 (0.100 = 10%)
  PRIMARY KEY (sale_item_id),
  CONSTRAINT fk_items_sale FOREIGN KEY (sale_id)
    REFERENCES sales (sale_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_items_product FOREIGN KEY (product_id)
    REFERENCES products (product_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_items_qty      CHECK (quantity > 0),
  CONSTRAINT chk_items_price    CHECK (unit_price > 0),
  CONSTRAINT chk_items_discount CHECK (discount_rate >= 0 AND discount_rate <= 1)
) ENGINE=InnoDB;
