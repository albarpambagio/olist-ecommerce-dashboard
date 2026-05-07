# Phase 3: Star Schema Design & SQL Data Model Log

## Date: 2026-05-07

### 3.1 Star Schema Design

```
                    ┌─────────────────┐
                    │  dim_date       │
                    │  date_key PK    │
                    │  year           │
                    │  quarter        │
                    │  month          │
                    │  week           │
                    │  day_of_week    │
                    │  is_weekend     │
                    └────────┬────────┘
                             │
┌──────────────┐    ┌────────▼────────┐    ┌──────────────┐
│ dim_customer │    │  fact_orders    │    │ dim_product  │
│ customer_id  ◄────┤  order_id PK   ├────► product_id   │
│ city         │    │  customer_id FK │    │ category_en  │
│ state        │    │  product_id FK  │    │ weight_g     │
│ region       │    │  seller_id FK   │    └──────────────┘
└──────────────┘    │  date_key FK    │
                    │  payment_type FK│    ┌──────────────┐
┌──────────────┐    │  revenue        │    │ dim_seller   │
│ dim_seller   ◄────┤  freight_value  ├────► seller_id    │
│ seller_id    │    │  review_score   │    │ city         │
│ city         │    │  delivery_days  │    │ state        │
│ state        │    │  is_late        │    └──────────────┘
└──────────────┘    │  is_repeat_cust │
                    └─────────────────┘
```

### 3.2 Fact Table SQL (olist.fact_orders)

```sql
CREATE VIEW olist.fact_orders AS
SELECT
  o.order_id,
  o.customer_id,
  oi.product_id,
  oi.seller_id,
  o.order_purchase_timestamp::DATE                          AS order_date,
  oi.price                                                  AS revenue,
  oi.freight_value,
  op.payment_type,
  op.payment_value,
  COALESCE(r.review_score, NULL)                           AS review_score,

  -- Delivery metrics
  EXTRACT(DAY FROM (
    o.order_delivered_customer_date - o.order_purchase_timestamp
  ))::INT                                                   AS actual_delivery_days,
  EXTRACT(DAY FROM (
    o.order_estimated_delivery_date - o.order_purchase_timestamp
  ))::INT                                                   AS estimated_delivery_days,
  CASE
    WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1
    ELSE 0
  END                                                       AS is_late,

  -- Customer repeat flag (join to subquery)
  CASE WHEN rc.order_count > 1 THEN 1 ELSE 0 END           AS is_repeat_customer

FROM olist.orders o
JOIN olist.order_items oi USING (order_id)
LEFT JOIN olist.order_payments op USING (order_id)
LEFT JOIN olist.order_reviews r USING (order_id)
LEFT JOIN (
  SELECT customer_id, COUNT(*) AS order_count
  FROM olist.orders
  WHERE order_status = 'delivered'
  GROUP BY customer_id
) rc USING (customer_id)
WHERE o.is_valid_order = TRUE
  AND o.order_status = 'delivered';
```

### 3.3 Dimension Tables

#### dim_date
```sql
CREATE VIEW olist.dim_date AS
SELECT
  d::DATE                                AS date_key,
  EXTRACT(YEAR FROM d)::INT              AS year,
  EXTRACT(QUARTER FROM d)::INT           AS quarter,
  TO_CHAR(d, 'YYYY-MM')                  AS year_month,
  EXTRACT(MONTH FROM d)::INT             AS month,
  TO_CHAR(d, 'Month')                    AS month_name,
  EXTRACT(WEEK FROM d)::INT             AS week_num,
  EXTRACT(DOW FROM d)::INT              AS day_of_week,
  CASE WHEN EXTRACT(DOW FROM d) IN (0,6)
       THEN TRUE ELSE FALSE END          AS is_weekend
FROM GENERATE_SERIES('2016-01-01'::DATE, '2019-12-31'::DATE, '1 day') d;
```

#### dim_product
```sql
CREATE VIEW olist.dim_product AS
SELECT
  p.product_id,
  COALESCE(t.string_field_1, 'unknown')  AS category_en,
  p.product_weight_g,
  p.product_length_cm,
  p.product_height_cm,
  p.product_width_cm
FROM olist.products p
LEFT JOIN olist.category_translation t
  ON p.product_category_name = t.string_field_0;
```

### Implementation Status

| Component | Status | Notes |
|---|---|---|
| Schema created | ✅ Complete | |
| fact_orders view | ✅ Complete | 110,840 rows |
| dim_date view | ✅ Complete | 1,461 rows |
| dim_product view | ✅ Complete | 32,951 rows |
| dim_customer view | ✅ Complete | 99,441 rows |
| dim_seller view | ✅ Complete | 3,095 rows |

### Summary
- Total revenue: $13,279,836.59
- Star schema ready for Power BI