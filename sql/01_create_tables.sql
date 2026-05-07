-- Phase 1: Create Schema and Load Data
-- Olist Brazilian E-Commerce Dashboard Project

-- Create schema
CREATE SCHEMA IF NOT EXISTS olist;

-- ============================================
-- DROP existing tables (for clean reload)
-- ============================================

DROP TABLE IF EXISTS olist.orders CASCADE;
DROP TABLE IF EXISTS olist.order_items CASCADE;
DROP TABLE IF EXISTS olist.order_payments CASCADE;
DROP TABLE IF EXISTS olist.order_reviews CASCADE;
DROP TABLE IF EXISTS olist.customers CASCADE;
DROP TABLE IF EXISTS olist.sellers CASCADE;
DROP TABLE IF EXISTS olist.products CASCADE;
DROP TABLE IF EXISTS olist.category_translation CASCADE;
DROP TABLE IF EXISTS olist.geolocation CASCADE;

-- ============================================
-- Create tables with proper data types
-- ============================================

-- Orders table
CREATE TABLE olist.orders (
    order_id VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(32),
    order_status VARCHAR(20),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

-- Order Items table
CREATE TABLE olist.order_items (
    order_id VARCHAR(32),
    order_item_id INTEGER,
    product_id VARCHAR(32),
    seller_id VARCHAR(32),
    shipping_limit_date TIMESTAMP,
    price DECIMAL(10,2),
    freight_value DECIMAL(10,2),
    PRIMARY KEY (order_id, order_item_id)
);

-- Order Payments table
CREATE TABLE olist.order_payments (
    order_id VARCHAR(32),
    payment_sequential INTEGER,
    payment_type VARCHAR(20),
    payment_installments INTEGER,
    payment_value DECIMAL(10,2)
);

-- Order Reviews table
CREATE TABLE olist.order_reviews (
    review_id VARCHAR(32),
    order_id VARCHAR(32),
    review_score INTEGER,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);

-- Customers table
CREATE TABLE olist.customers (
    customer_id VARCHAR(32) PRIMARY KEY,
    customer_unique_id VARCHAR(32),
    customer_zip_code_prefix VARCHAR(10),
    customer_city VARCHAR(50),
    customer_state VARCHAR(2)
);

-- Sellers table
CREATE TABLE olist.sellers (
    seller_id VARCHAR(32) PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(10),
    seller_city VARCHAR(50),
    seller_state VARCHAR(2)
);

-- Products table
CREATE TABLE olist.products (
    product_id VARCHAR(32) PRIMARY KEY,
    product_category_name VARCHAR(50),
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER
);

-- Category Translation table
CREATE TABLE olist.category_translation (
    string_field_0 VARCHAR(100),  -- Portuguese
    string_field_1 VARCHAR(100)   -- English
);

-- Geolocation table
CREATE TABLE olist.geolocation (
    zip_code_prefix VARCHAR(10),
    geolocation_lat DECIMAL(10,8),
    geolocation_lng DECIMAL(10,8),
    geolocation_city VARCHAR(50),
    geolocation_state VARCHAR(2)
);

\echo 'Tables created successfully'