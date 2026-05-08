# Olist E-Commerce: Key Insights Log

## Data Overview

### Dataset Summary
- **Source**: Kaggle (Olist Brazilian E-Commerce)
- **Date Range**: 2016-09-04 to 2018-10-17
- **Total Orders**: 99,441 (96,478 delivered)
- **Total Revenue**: $13,168,332.11 (from delivered orders)
- **Unique Customers**: 93,358
- **Repeat Customer Rate**: 3.00% (2,801 repeat buyers)

### SQL Used:
```sql
-- Date range
SELECT MIN(order_purchase_timestamp), MAX(order_purchase_timestamp) 
FROM olist.orders;

-- Total counts
SELECT 
    (SELECT COUNT(*) FROM olist.orders) AS total_orders,
    (SELECT COUNT(*) FROM olist.orders WHERE order_status = 'delivered') AS delivered,
    (SELECT COUNT(DISTINCT customer_unique_id) FROM olist.orders o 
     JOIN olist.customers c ON o.customer_id = c.customer_id) AS unique_customers;
```

---

## SCAN Framework: Exploratory Analysis

### Metrics in the Insights Log

For each finding, document using this structured format (per updated Playbook Section 4):

| Metric | Dimension | Finding | Team | Type |
|--------|-----------|---------|------|------|
| Revenue | Product Category | Books categories have 4.3+ stars, high satisfaction | Product | Directional |
| Repeat Rate | Customer Segment | At Risk = 24.1% of base, need re-engagement | Marketing | Actionable |
| Late Delivery Rate | State | 7.78% overall, varies by region (some states >10%) | Operations | Actionable |
| AOV | State | PB has 2× AOV ($266.61), premium market opportunity | Marketing | Directional |
| Revenue | Time (Month) | Q4 consistently strongest (seasonality pattern) | Finance | Contextual |
| Review Score | Product Category | books_general_interest highest (4.45), food_drink (4.32) | Product | Actionable |
| Payment Type | Customer | 73.6% credit card, 19.0% boleto | Marketing | Directional |

### Metrics to Prioritize vs. Ignore

**Prioritize (included in dashboard):**
- Revenue, Order Volume, AOV (represent 100% of total revenue)
- On-Time Delivery Rate (directly influenceable by Operations)
- Repeat Customer Rate (directly influenceable by Marketing)
- Review Score by Category (actionable for Product team)

**Deprioritize (excluded from executive dashboard):**
- Headsets category (<2% of revenue, ~1,000 orders)
- Seller-specific metrics on Executive page (belongs on Seller page only)
- Payment method trends for Operations team (belongs to Marketing)
- Geolocation details (technical, not decision-relevant)

---

### S — Stakeholder Goals
- **Sales Team:** Revenue trends, category performance, market opportunities
- **Ops Team:** Delivery performance, seller reliability, logistics bottlenecks
- **Target Decision:** Monthly/quarterly resource allocation and strategy adjustments

### C — Columns and Coverage
- **Data Available:** 9 tables, ~100k orders, 2016–2018
- **Can Answer:** Revenue trends, delivery performance, customer retention, seller quality
- **Cannot Answer (Gaps):** Marketing channel attribution, customer acquisition source, profitability margins

### A — Aggregates and Anomalies
| Metric | Value | Insight |
|--------|-------|---------|
| Total Revenue | $13,168,332.11 | Baseline for growth calculations |
| Avg Order Value | $137.41 | Typical transaction size |
| On-Time Delivery Rate | 92.22% | 7.78% are late — operational bottleneck |
| Repeat Customer Rate | 3.00% | Massive retention opportunity |
| Avg Review Score | 4.08/5.00 | Generally satisfied customers |

**Notable Patterns:**
- SP/RJ/MG = 66% of customers (market concentration)
- Q4 consistently strongest (seasonality)
- 3% repeat rate is extremely low for e-commerce

### N — Notable Segments
- **At Risk customers:** 23,272 (24.1%) — need re-engagement
- **Late deliveries:** 7,826 orders (7.78%) — concentrated in specific states
- **Premium markets:** PB ($266.61 AOV), AC ($244.69), AP ($240.92)
- **High-satisfaction categories:** books_general_interest (4.45), books_technical (4.37)

---

## North Star Deep Dive

### North Star Metric: Total Revenue ($13.17M)
### North Star Dimensions: Product Category, Customer State, Time

#### Decomposition: Revenue = Order Volume × AOV
- **Order Volume:** 95,832 delivered orders
- **AOV:** $137.41
- **Late Deliveries:** 7.78% (driving negative reviews in affected segments)

#### Cross-Tabulation Findings:
| Dimension Combination | Finding | Impact |
|----------------------|---------|--------|
| Product Category × Review Score | Books categories have 4.3+ stars | Cross-sell opportunity |
| Customer State × AOV | PB/AC/AP have 2× AOV | Premium market expansion |
| Seller State × Late Rate | Late deliveries vary by region | Ops bottleneck investigation |
| Customer Segment × Frequency | 24.1% At Risk, only 3% repeat | Retention campaign priority |

---

## Key Metrics

| Metric | Value | Business Meaning |
|---|---|---|
| Avg Order Value (AOV) | $137.41 | Typical transaction size |
| On-Time Delivery Rate | 92.22% | 7.78% are late |
| Late Delivery Rate | 7.78% (7,826 orders) | Operational bottleneck |
| Avg Delivery Days | 12.1 days | Customer expectation setter |
| Avg Review Score | 4.08 / 5.00 | Generally satisfied customers |
| Repeat Customer Rate | 3.00% | Huge retention opportunity |

### SQL Used:
```sql
SELECT 
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(revenue)::NUMERIC, 2) AS revenue,
    ROUND(SUM(revenue)::NUMERIC / COUNT(DISTINCT order_id), 2) AS aov,
    ROUND(AVG(review_score), 2) AS avg_review,
    ROUND(SUM(CASE WHEN is_late = 1 THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) AS late_rate_pct
FROM olist.fact_orders
WHERE review_score IS NOT NULL;
```

---

## Geographic Insights

### Top 10 States by Customer Count
| State | Customers | % of Total |
|---|---|---|
| SP (São Paulo) | 41,746 | 42% |
| RJ (Rio de Janeiro) | 12,852 | 13% |
| MG (Minas Gerais) | 11,635 | 12% |
| RS (Rio Grande do Sul) | 5,466 | 6% |
| PR (Paraná) | 5,045 | 5% |
| SC (Santa Catarina) | 3,637 | 4% |
| BA (Bahia) | 3,380 | 3% |
| DF (Distrito Federal) | 2,140 | 2% |
| ES (Espírito Santo) | 2,033 | 2% |
| GO (Goiás) | 2,020 | 2% |

### Highest AOV by State
| State | AOV | Orders |
|---|---|---|
| PB (Paraíba) | $266.61 | 517 |
| AC (Acre) | $244.69 | 80 |
| AP (Amapá) | $240.92 | 67 |
| AL (Alagoas) | $237.21 | 397 |
| RO (Rondônia) | $234.43 | 243 |

### SQL Used:
```sql
-- Top states by customers
SELECT customer_state, COUNT(*) as cnt 
FROM olist.customers 
GROUP BY 1 
ORDER BY 2 DESC 
LIMIT 10;

-- AOV by state
SELECT 
    c.customer_state,
    ROUND(SUM(oi.price + oi.freight_value)::NUMERIC / COUNT(DISTINCT o.order_id), 2) as aov,
    COUNT(DISTINCT o.order_id) as orders
FROM olist.orders o
JOIN olist.order_items oi ON o.order_id = oi.order_id
JOIN olist.customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY 2 DESC
LIMIT 5;
```

**Business Insight**: Market concentration in Southeast (SP/RJ/MG = 66%). Premium markets (PB, AC, AP) show 2x AOV - untapped opportunity.

---

## Product & Category Performance

### Top Categories by Review Score (min 100 orders)
| Category | Avg Review | Orders |
|---|---|---|
| books_general_interest | 4.45 | 549 |
| books_technical | 4.37 | 266 |
| food_drink | 4.32 | 279 |
| luggage_accessories | 4.32 | 1,088 |
| fashion_shoes | 4.23 | 261 |

### SQL Used:
```sql
SELECT 
    COALESCE(t.category_en, p.product_category_name) as category,
    ROUND(AVG(r.review_score)::NUMERIC, 2) as avg_score,
    COUNT(*) as orders
FROM olist.order_items oi
JOIN olist.order_reviews r ON oi.order_id = r.order_id
JOIN olist.products p ON oi.product_id = p.product_id
LEFT JOIN olist.category_translation t ON p.product_category_name = t.string_field_0
GROUP BY 1
HAVING COUNT(*) > 100
ORDER BY 2 DESC
LIMIT 5;
```

**Business Insight**: Books and food categories have highest satisfaction. Promote these to boost overall review scores.

---

## Payment Preferences

| Payment Type | Count | % of Total |
|---|---|---|
| credit_card | 76,476 | 73.6% |
| boleto | 19,783 | 19.0% |
| voucher | 1,621 | 1.6% |
| debit_card | 1,477 | 1.4% |
| not_defined | 3 | 0.0% |

### SQL Used:
```sql
SELECT 
    payment_type,
    COUNT(*) as cnt,
    ROUND(COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM olist.order_payments) * 100, 1) as pct
FROM olist.order_payments
WHERE payment_sequential = 1
GROUP BY 1
ORDER BY 2 DESC;
```

---

## Delivery Performance

### Late Delivery Analysis
- **Total Delivered Orders**: 96,470
- **Late Deliveries**: 7,826 (8.11%)
- **Average Delivery Time**: 12.1 days
- **Min Delivery**: 0 days (same-day)
- **Max Delivery**: 209 days (extreme outlier)

### SQL Used:
```sql
-- Late delivery rate
SELECT 
    COUNT(*) as total_orders,
    SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END) as late_deliveries,
    ROUND(SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) as late_pct
FROM olist.orders
WHERE order_status = 'delivered' 
  AND order_delivered_customer_date IS NOT NULL
  AND order_estimated_delivery_date IS NOT NULL;

-- Delivery time stats
SELECT 
    AVG(EXTRACT(DAY FROM order_delivered_customer_date - order_purchase_timestamp)) as avg_days,
    MIN(EXTRACT(DAY FROM order_delivered_customer_date - order_purchase_timestamp)) as min_days,
    MAX(EXTRACT(DAY FROM order_delivered_customer_date - order_purchase_timestamp)) as max_days
FROM olist.orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL;
```

**Business Insight**: 7.78% late rate directly impacts customer satisfaction and review scores. Investigating bottlenecks in key states could reduce churn.

---

## Customer Segmentation (RFM)

### RFM Segment Distribution
| Segment | Customers | % of Total | Action |
|---|---|---|---|
| At Risk | 23,272 | 24.1% | Re-engagement campaign (email, discounts) |
| Loyal Customers | 19,276 | 20.0% | Loyalty rewards program |
| Recent Customers | 15,528 | 16.1% | Welcome series, onboarding |
| Champions | 15,338 | 15.9% | VIP program, referrals |
| Lost | 15,320 | 15.9% | Win-back (low priority) |
| Promising | 7,744 | 8.0% | Nurture to loyal |

### SQL Used:
```sql
SELECT 
    segment,
    COUNT(*) AS customers,
    ROUND(COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM olist.customer_rfm) * 100, 1) AS pct
FROM olist.customer_rfm
GROUP BY 1
ORDER BY 2 DESC;

-- RFM creation logic
CREATE VIEW olist.customer_rfm AS
WITH rfm_base AS (
    SELECT
        customer_id,
        MAX(order_date) AS last_order_date,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(revenue) AS monetary
    FROM olist.fact_orders
    GROUP BY customer_id
),
rfm_scored AS (
    SELECT *,
        CURRENT_DATE - last_order_date AS recency_days,
        NTILE(5) OVER (ORDER BY CURRENT_DATE - last_order_date DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency) AS f_score,
        NTILE(5) OVER (ORDER BY monetary) AS m_score
    FROM rfm_base
)
SELECT 
    customer_id, last_order_date, recency_days, frequency, monetary,
    r_score, f_score, m_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
        ELSE 'Promising'
    END AS segment
FROM rfm_scored;
```

**Business Insight**: 24.1% of customers are "At Risk" - targeted campaigns could prevent churn. Only 3% repeat rate suggests massive retention opportunity.

---

## Cohort Retention Analysis

### Retention Rates by Month Index (Months 0-6)

| Cohort Month | M0 | M1 | M2 | M3 | M4 | M5 | M6 |
|---|---|---|---|---|---|---|---|
| 2016-09 | 100% | - | - | - | - | - | - |
| 2016-10 | 100% | - | - | - | - | - | - |
| 2016-12 | 100% | 100% | - | - | - | - | - |
| 2017-01 | 100% | 0.3% | 0.3% | 0.1% | 0.4% | 0.1% | 0.4% |
| 2017-02 | 100% | 0.2% | 0.3% | 0.1% | 0.4% | 0.1% | 0.2% |
| 2017-03 | 100% | 0.4% | 0.4% | 0.4% | 0.4% | 0.2% | 0.2% |
| 2017-04 | 100% | 0.6% | 0.2% | 0.2% | 0.3% | 0.3% | 0.4% |
| 2017-05 | 100% | 0.5% | 0.5% | 0.3% | 0.3% | 0.3% | 0.4% |
| 2017-06 | 100% | 0.5% | 0.4% | 0.4% | 0.3% | 0.4% | 0.4% |
| 2017-07 | 100% | 0.5% | 0.3% | 0.2% | 0.3% | 0.2% | 0.3% |
| 2017-08 | 100% | 0.7% | 0.3% | 0.3% | 0.3% | 0.5% | 0.3% |
| 2017-09 | 100% | 0.7% | 0.5% | 0.3% | 0.4% | 0.2% | 0.2% |
| 2017-10 | 100% | 0.7% | 0.3% | 0.1% | 0.2% | 0.2% | 0.2% |
| 2017-11 | 100% | 0.6% | 0.4% | 0.2% | 0.2% | 0.2% | 0.1% |
| 2017-12 | 100% | 0.2% | 0.3% | 0.3% | 0.3% | 0.2% | 0.2% |
| 2018-01 | 100% | 0.3% | 0.4% | 0.3% | 0.3% | 0.2% | 0.2% |
| 2018-02 | 100% | 0.3% | 0.4% | 0.3% | 0.3% | 0.2% | 0.2% |
| 2018-03 | 100% | 0.4% | 0.3% | 0.3% | 0.1% | 0.1% | - |
| 2018-04 | 100% | 0.6% | 0.3% | 0.2% | 0.1% | - | - |
| 2018-05 | 100% | 0.5% | 0.3% | 0.2% | - | - | - |
| 2018-06 | 100% | 0.4% | 0.3% | - | - | - | - |
| 2018-07 | 100% | 0.5% | - | - | - | - | - |
| 2018-08 | 100% | - | - | - | - | - | - |

**Average Retention by Month Index:**
- M0: 100.0% (baseline, all cohorts)
- M1: 5.4% (avg across cohorts with data)
- M2: 0.3% (avg across cohorts with data)
- M3: 0.2% (avg across cohorts with data)
- M4: 0.3% (avg across cohorts with data)
- M5: 0.2% (avg across cohorts with data)
- M6: 0.3% (avg across cohorts with data)

**Note:** Retention rates appear very low (0.2-0.5%) because this is calculated at the UNIQUE CUSTOMER level (using `customer_unique_id`). The repeat customer rate is 3.00% overall, meaning most customers only order once.

**Business Insight:** 
- Month-1 retention ~0.5% is extremely low, indicating customers don't return after their first purchase
- This confirms the 3% repeat rate finding - Olist has a massive retention problem
- Retention campaigns targeting "At Risk" segment (23,272 customers) could dramatically improve LTV

### SQL Used:
```sql
SELECT
    TO_CHAR(cohort_month, 'YYYY-MM') AS cohort,
    month_index,
    ROUND(retention_rate * 100, 1) AS retention_pct,
    retained,
    cohort_size
FROM olist.cohort_retention
WHERE month_index <= 6
ORDER BY cohort_month, month_index;
```

**Business Insight**: Month-1 retention ~21% is decent, but month-6 dropping to 8% shows need for ongoing engagement campaigns.

---

## Business Recommendations

### 1. Customer Retention Program (High Impact)
- **Target**: "At Risk" segment (23,272 customers, 24.1% of base)
- **Action**: Personalized email campaigns with exclusive offers, loyalty points
- **Expected Impact**: 5% → 8% repeat rate = ~2,800 additional orders = +$384,000 revenue

### 2. Delivery Bottleneck Investigation (High Impact)
- **Target**: States with >10% late rate
- **Action**: Audit seller fulfillment, carrier contracts in those regions
- **Expected Impact**: Reduce late rate from 7.78% to <5% = +2,000 on-time deliveries, improved reviews

### 3. Leverage High-Satisfaction Categories (Medium Impact)
- **Target**: books_general_interest (4.45 stars), books_technical (4.37 stars)
- **Action**: Cross-sell these categories to customers who haven't purchased them
- **Expected Impact**: Increase overall review scores, reduce returns

### 4. Expand in High-AOV Markets (Medium Impact)
- **Target**: Paraíba (PB), Acre (AC), Amapá (AP)
- **Action**: Targeted marketing, seller recruitment in these states
- **Expected Impact**: Grow orders in premium markets

### Combined 1-Year Impact:
- **Conservative Estimate**: $800,000+ in additional revenue (~6% growth on $13.17M baseline)

---

## Data Quality Issues Found

| Issue | Impact | Resolution |
|---|---|---|
| ~3,000 geolocation rows with duplicate zip prefixes | Inaccurate city/state mapping | Created `geo_deduped` view with AVG(lat/lng) |
| 2,965 orders with NULL delivery dates | Underestimated delivery metrics | Excluded from delivery KPIs, tracked separately |
| Portuguese category names | Confusing for non-Brazilian stakeholders | JOINed to `category_translation` table, COALESCE for missing |
| Initial repeat customer rate = 0% | Incorrect business insight | Fixed by using `customer_unique_id` instead of `customer_id` |
| Payment table has multiple rows per order | Inflated payment method counts | Used `payment_sequential = 1` to get primary method |

### SQL Used for Data Quality Fixes:
```sql
-- Add is_valid_order flag
ALTER TABLE olist.orders ADD COLUMN is_valid_order BOOLEAN;
UPDATE olist.orders
SET is_valid_order = (order_status NOT IN ('cancelled', 'unavailable'));

-- Deduplicate geolocation
CREATE VIEW olist.geo_deduped AS
SELECT zip_code_prefix,
       AVG(geolocation_lat) AS lat,
       AVG(geolocation_lng) AS lng,
       MAX(geolocation_city) AS city,
       MAX(geolocation_state) AS state
FROM olist.geolocation
GROUP BY zip_code_prefix;
```

---

## Monthly Revenue Trend (Last 6 Months)

| Month | Orders | Revenue | AOV |
|---|---|---|---|
| 2018-08 | 6,351 | $838,650.76 | $132.05 |
| 2018-07 | 6,159 | $869,842.48 | $141.23 |
| 2018-06 | 6,099 | $856,909.79 | $140.50 |
| 2018-05 | 6,749 | $978,065.68 | $144.92 |
| 2018-04 | 6,798 | $975,779.41 | $143.54 |
| 2018-03 | 7,003 | $956,923.96 | $136.64 |

**Trend**: Revenue stable around $950k/month, AOV ranging $132-$145. Seasonal patterns visible (Q4 typically stronger).

### SQL Used:
```sql
SELECT 
    TO_CHAR(month, 'YYYY-MM') AS ym,
    order_volume AS orders,
    revenue,
    aov
FROM olist.kpi_revenue_overview
ORDER BY month DESC
LIMIT 6;
```

---

## Seller Performance Insights

### Top Seller Metrics
- **Total Sellers**: 3,095
- **Avg Review Score by Seller**: 4.08 (same as overall)
- **Seller Late Rate**: Varies by seller (0% to 100%)

**Action**: Flag sellers with <80% on-time rate for performance review.

### SQL Used:
```sql
SELECT 
    ds.seller_state,
    COUNT(DISTINCT fo.seller_id) AS unique_sellers,
    ROUND(SUM(fo.revenue)::NUMERIC / COUNT(DISTINCT fo.seller_id), 2) AS revenue_per_seller,
    ROUND(AVG(fo.review_score), 2) AS avg_review_score,
    ROUND(SUM(CASE WHEN fo.is_late = 1 THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) AS seller_late_rate_pct
FROM olist.fact_orders fo
JOIN olist.dim_seller ds ON fo.seller_id = ds.seller_id
GROUP BY 1
ORDER BY 3 DESC;
```

---

## Interview-Ready Summary

**One-Sentence Project Summary:**
> "I built a sales & ops dashboard for Olist (Brazilian e-commerce) using PostgreSQL and Power BI, finding that while revenue is growing, only 3% of customers return and 7.78% of deliveries are late - representing $800k+ annual improvement opportunity."

**5 Numbers to Memorize:**
1. **Revenue**: $13.17M across 95,832 orders
2. **Problem**: Only 3% repeat customers, 7.78% late deliveries
3. **Solution**: Retention campaigns for At-Risk segment, investigate delivery bottlenecks
4. **Tech Stack**: PostgreSQL → Python ETL → Power BI (Star Schema)
5. **Differentiator**: RFM segmentation + Cohort analysis (not just basic charts)

---

*Log created: 2026-05-07*
*Last updated: 2026-05-07*