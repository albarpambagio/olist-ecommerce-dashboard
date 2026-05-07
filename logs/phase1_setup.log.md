# Phase 1: Environment Setup & Data Loading Log

## Date: 2026-05-07

### 1.1 Tools Setup
- [ ] PostgreSQL (local) — pending installation
- [ ] Power BI Desktop (free) — for dashboard layer
- [ ] GitHub repository — to be created

### 1.2 Data Loading

#### Dataset Download
- Source: Kaggle (https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- License: CC-BY-NC-SA 4.0
- Files downloaded: 9 CSV files
- Total size: ~42.6 MB

#### Files Available
| File | Status |
|---|---|
| olist_orders_dataset.csv | ✅ Downloaded |
| olist_order_items_dataset.csv | ✅ Downloaded |
| olist_order_payments_dataset.csv | ✅ Downloaded |
| olist_order_reviews_dataset.csv | ✅ Downloaded |
| olist_customers_dataset.csv | ✅ Downloaded |
| olist_sellers_dataset.csv | ✅ Downloaded |
| olist_products_dataset.csv | ✅ Downloaded |
| product_category_name_translation.csv | ✅ Downloaded |
| olist_geolocation_dataset.csv | ✅ Downloaded |

### 1.3 Initial SQL Queries (to execute after PostgreSQL setup)

```sql
-- Create schema
CREATE SCHEMA olist;

-- Load each CSV as a table:
-- olist.orders, olist.order_items, olist.order_payments,
-- olist.order_reviews, olist.customers, olist.sellers,
-- olist.products, olist.category_translation, olist.geolocation

-- Verify row counts after load:
SELECT 'orders' AS tbl, COUNT(*) FROM olist.orders
UNION ALL SELECT 'order_items', COUNT(*) FROM olist.order_items
UNION ALL SELECT 'customers', COUNT(*) FROM olist.customers;
-- Expected: orders ~99,441 | items ~112,650 | customers ~99,441
```

### 1.4 Initial Exploration Queries

```sql
-- Date range of data
SELECT MIN(order_purchase_timestamp), MAX(order_purchase_timestamp)
FROM olist.orders;

-- Order status distribution
SELECT order_status, COUNT(*) AS cnt
FROM olist.orders
GROUP BY 1 ORDER BY 2 DESC;

-- Null check on key fields
SELECT
  COUNT(*) AS total,
  COUNT(order_delivered_customer_date) AS has_delivery_date,
  COUNT(*) - COUNT(order_delivered_customer_date) AS missing_delivery_date
FROM olist.orders;
```

### Notes
- PostgreSQL installation: COMPLETED by user
- Database connection: localhost:5433, password: admin
- Data loading: COMPLETED