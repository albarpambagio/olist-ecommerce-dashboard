-- Phase 1: Load Data from CSV files
-- Run this after 01_create_tables.sql
-- Adjust the path to your data directory

-- Load orders
COPY olist.orders (order_id, customer_id, order_status, order_purchase_timestamp, 
                  order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, 
                  order_estimated_delivery_date)
FROM 'D:\PROJECT\data_analyst_porto\olist complete\data\olist_orders_dataset.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'utf8');

-- Load order items
COPY olist.order_items (order_id, order_item_id, product_id, seller_id, shipping_limit_date, 
                     price, freight_value)
FROM 'D:\PROJECT\data_analyst_porto\olist complete\data\olist_order_items_dataset.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'utf8');

-- Load order payments
COPY olist.order_payments (order_id, payment_sequential, payment_type, payment_installments, payment_value)
FROM 'D:\PROJECT\data_analyst_porto\olist complete\data\olist_order_payments_dataset.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'utf8');

-- Load order reviews
COPY olist.order_reviews (review_id, order_id, review_score, review_creation_date, review_answer_timestamp)
FROM 'D:\PROJECT\data_analyst_porto\olist complete\data\olist_order_reviews_dataset.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'utf8');

-- Load customers
COPY olist.customers (customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)
FROM 'D:\PROJECT\data_analyst_porto\olist complete\data\olist_customers_dataset.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'utf8');

-- Load sellers
COPY olist.sellers (seller_id, seller_zip_code_prefix, seller_city, seller_state)
FROM 'D:\PROJECT\data_analyst_porto\olist complete\data\olist_sellers_dataset.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'utf8');

-- Load products
COPY olist.products (product_id, product_category_name, product_name_lenght, product_description_lenght, 
                    product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm)
FROM 'D:\PROJECT\data_analyst_porto\olist complete\data\olist_products_dataset.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'utf8');

-- Load category translation
COPY olist.category_translation (string_field_0, string_field_1)
FROM 'D:\PROJECT\data_analyst_porto\olist complete\data\product_category_name_translation.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'utf8');

-- Load geolocation
COPY olist.geolocation (zip_code_prefix, geolocation_lat, geolocation_lng, geolocation_city, geolocation_state)
FROM 'D:\PROJECT\data_analyst_porto\olist complete\data\olist_geolocation_dataset.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'utf8');

\echo 'Data loaded successfully'

-- Verify row counts
SELECT 'orders' AS tbl, COUNT(*) AS cnt FROM olist.orders
UNION ALL SELECT 'order_items', COUNT(*) FROM olist.order_items
UNION ALL SELECT 'order_payments', COUNT(*) FROM olist.order_payments
UNION ALL SELECT 'order_reviews', COUNT(*) FROM olist.order_reviews
UNION ALL SELECT 'customers', COUNT(*) FROM olist.customers
UNION ALL SELECT 'sellers', COUNT(*) FROM olist.sellers
UNION ALL SELECT 'products', COUNT(*) FROM olist.products
UNION ALL SELECT 'category_translation', COUNT(*) FROM olist.category_translation
UNION ALL SELECT 'geolocation', COUNT(*) FROM olist.geolocation;