# Phase 2: Data Cleaning & EDA Log

## Date: 2026-05-07

### 2.1 Data Quality Fixes

```sql
-- Flag cancelled and unavailable orders
ALTER TABLE olist.orders ADD COLUMN is_valid_order BOOLEAN;
UPDATE olist.orders
SET is_valid_order = (order_status NOT IN ('cancelled', 'unavailable'));

-- Standardise category names (Portuguese → English)
-- Always join via category_translation to get English names

-- Handle delivery date nulls
-- For delay calculation: only use orders where both estimated and actual delivery exist
-- For order count KPIs: include all delivered orders regardless of review

-- Geolocation: deduplicate by zip prefix (multiple lat/lng per zip)
CREATE VIEW olist.geo_deduped AS
SELECT zip_code_prefix,
       AVG(geolocation_lat) AS lat,
       AVG(geolocation_lng) AS lng,
       MAX(geolocation_city) AS city,
       MAX(geolocation_state) AS state
FROM olist.geolocation
GROUP BY zip_code_prefix;
```

### 2.2 Key EDA Questions to Answer

Before building, run these queries and note findings:

1. **What % of orders are delivered on time vs. late?**
2. **Which product category has the highest average review score?**
3. **Which state has the highest AOV?**
4. **What payment method is most common? Does it vary by order value?**
5. **What % of customers made more than one purchase? (Repeat rate)**

### Known Data Quality Issues

| Issue | Description | Handling |
|---|---|---|
| ~3,000 geolocation rows | No matching customer/seller zip | Use LEFT JOIN |
| NULL delivery dates | Cancelled or in-transit orders | Exclude from delivery KPIs |
| Portuguese categories | Category names in PT | JOIN to translation table |
| Invalid order statuses | 'unavailable' or 'cancelled' | Exclude from revenue KPIs |

### EDA Findings

| Question | Finding | Date |
|---|---|---|
| Date range | 2016-09-04 to 2018-10-17 | 2026-05-07 |
| Order status (delivered) | 96,478 (97%) | 2026-05-07 |
| % delivered late | 8.11% | 2026-05-07 |
| Top category by review | books_general_interest: 4.45 | 2026-05-07 |
| Top state by AOV | PB: $266.61 | 2026-05-07 |
| Most common payment | credit_card: 73.6% | 2026-05-07 |
| Repeat customer rate | 3.00% | 2026-05-07 |
| Avg delivery days | 12.1 days | 2026-05-07 |