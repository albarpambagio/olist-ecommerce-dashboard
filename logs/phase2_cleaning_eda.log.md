# Phase 2: Data Cleaning & EDA Log

## Date: 2026-05-07

## CLEAN Framework Applied

### C — Conceptualize the Data
- **Grain:** One row = one order item (112,650 rows in `olist_order_items`)
- **Key Metrics:** revenue (price), freight_value, review_score
- **Key Dimensions:** customer_state, product_category_en, seller_state, order_date
- **Example Record:** "Customer X placed an order on 2017-05-12 for a books_general_interest product at $45.99 via credit_card, delivered in 9 days."

### L — Locate Solvable Issues
| Issue | Resolution | % Affected | SQL Used |
|-------|-------------|-------------|----------|
| Geolocation duplicates (~3k rows with same zip prefix) | Created `olist.geo_deduped` view using AVG(lat/lng) | ~3% | `CREATE VIEW olist.geo_deduped AS SELECT zip_code_prefix, AVG(geolocation_lat) AS lat, AVG(geolocation_lng) AS lng, MAX(geolocation_city) AS city, MAX(geolocation_state) AS state FROM olist.geolocation GROUP BY zip_code_prefix;` |
| Null delivery dates (2,965 orders) | Excluded from delivery KPIs, tracked separately | 3% | `WHERE order_delivered_customer_date IS NOT NULL` |
| Portuguese category names | JOINed `category_translation` table, COALESCE for missing | ~15 categories | `LEFT JOIN olist.category_translation t ON p.product_category_name = t.string_field_0` |
| Initial repeat customer rate = 0% | Fixed by using `customer_unique_id` instead of `customer_id` | 100% of calculation | `JOIN olist.customers c ON o.customer_id = c.customer_id` |

### E — Evaluate Unsolvable Issues
| Issue | Impact | Decision |
|-------|--------|----------|
| Missing translations for some categories | Confusing labels | COALESCE to 'unknown', documented |
| 209-day delivery outlier | Skews avg delivery days | Flagged, not removed (<0.1% of orders) |
| Orders with `order_status` = 'cancelled' or 'unavailable' | Affects revenue KPIs | Excluded from revenue calculations, tracked in `is_valid_order` flag |

### A — Augment the Data
- Added date grains: `year`, `quarter`, `year_month`, `month`, `week_num` in `dim_date`
- Added flags: `is_late` (delivery > estimated), `is_repeat_customer` (frequency > 1)
- Added calculated metric: `actual_delivery_days` (delivered_customer_date - purchase_timestamp)
- Enriched dimensions: English category names via `dim_product`

### N — Note and Document
- Full issues log maintained in `logs/insights.md`
- All SQL scripts in `/sql/` folder with comments
- Data quality checklist completed before EDA

---

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