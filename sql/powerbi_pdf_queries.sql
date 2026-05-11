-- ============================================================================
-- Olist Sales Dashboard — Power BI PDF Report Queries
-- Run these against your PostgreSQL (localhost:5433, database: olist)
-- ============================================================================

-- ============================================================================
-- PAGE 1: THE HOOK — Headline Numbers
-- ============================================================================

-- Total Revenue, Orders, AOV
SELECT
    ROUND(SUM(revenue), 2) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(AVG(revenue), 2) AS aov
FROM olist.fact_orders;

-- Repeat Customer Stats (actual count of customers with >1 order)
SELECT
    COUNT(DISTINCT customer_unique_id) AS total_customers,
    COUNT(DISTINCT customer_unique_id) FILTER (
        WHERE customer_unique_id IN (
            SELECT customer_unique_id
            FROM olist.fact_orders
            GROUP BY customer_unique_id
            HAVING COUNT(DISTINCT order_id) > 1
        )
    ) AS repeat_customers,
    ROUND(
        COUNT(DISTINCT customer_unique_id) FILTER (
            WHERE customer_unique_id IN (
                SELECT customer_unique_id
                FROM olist.fact_orders
                GROUP BY customer_unique_id
                HAVING COUNT(DISTINCT order_id) > 1
            )
        )::numeric / NULLIF(COUNT(DISTINCT customer_unique_id), 0) * 100
    , 2) AS repeat_rate_pct
FROM olist.fact_orders;

-- At Risk Segment Count
SELECT
    COUNT(*) AS at_risk_customers,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM olist.customer_rfm) * 100, 1) AS pct_of_total
FROM olist.customer_rfm
WHERE segment = 'At Risk';

-- Revenue Opportunity Estimate (At Risk customers' first order value)
SELECT
    ROUND(SUM(fo.revenue), 2) AS at_risk_revenue_potential
FROM olist.fact_orders fo
JOIN olist.customer_rfm cr ON fo.customer_id = cr.customer_id
WHERE cr.segment = 'At Risk'
  AND fo.order_id IN (
      SELECT MIN(order_id)
      FROM olist.fact_orders
      WHERE customer_id IN (SELECT customer_id FROM olist.customer_rfm WHERE segment = 'At Risk')
      GROUP BY customer_id
  );


-- ============================================================================
-- PAGE 2: CONTEXT — Baseline Metrics
-- ============================================================================

-- Monthly Revenue Trend (last 6 months)
SELECT
    DATE_TRUNC('month', order_date) AS month,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(AVG(revenue), 2) AS aov
FROM olist.fact_orders
WHERE order_date >= '2018-04-01'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- Top 5 States by Customer Count
SELECT
    dc.customer_state AS state,
    COUNT(DISTINCT dc.customer_id) AS customers,
    ROUND(
        COUNT(DISTINCT dc.customer_id)::numeric /
        (SELECT COUNT(DISTINCT customer_id) FROM olist.dim_customer) * 100
    , 1) AS pct
FROM olist.fact_orders fo
JOIN olist.dim_customer dc ON fo.customer_id = dc.customer_id
GROUP BY dc.customer_state
ORDER BY customers DESC
LIMIT 5;

-- Revenue by State (top 10)
SELECT
    dc.customer_state AS state,
    ROUND(SUM(fo.revenue), 2) AS revenue,
    COUNT(DISTINCT fo.order_id) AS orders,
    ROUND(AVG(fo.revenue), 2) AS aov
FROM olist.fact_orders fo
JOIN olist.dim_customer dc ON fo.customer_id = dc.customer_id
GROUP BY dc.customer_state
ORDER BY revenue DESC
LIMIT 10;


-- ============================================================================
-- PAGE 3: RISING ACTION — RFM Segments
-- ============================================================================

-- RFM Segment Breakdown (with revenue)
SELECT
    segment,
    COUNT(*) AS customers,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM olist.customer_rfm) * 100, 1) AS pct_of_total,
    ROUND(SUM(monetary), 2) AS total_revenue,
    ROUND(AVG(monetary), 2) AS avg_revenue_per_customer,
    ROUND(AVG(recency_days), 0) AS avg_days_since_last_order
FROM olist.customer_rfm
GROUP BY segment
ORDER BY customers DESC;

-- RFM Segment Revenue Contribution
SELECT
    segment,
    ROUND(SUM(monetary), 2) AS segment_revenue,
    ROUND(
        SUM(monetary)::numeric /
        (SELECT SUM(revenue) FROM olist.fact_orders) * 100
    , 1) AS pct_of_total_revenue
FROM olist.customer_rfm
GROUP BY segment
ORDER BY segment_revenue DESC;


-- ============================================================================
-- PAGE 4: AT RISK DEEP DIVE
-- ============================================================================

-- At Risk Customer Details
SELECT
    segment,
    COUNT(*) AS customers,
    ROUND(AVG(recency_days), 0) AS avg_recency_days,
    MIN(recency_days) AS min_recency_days,
    MAX(recency_days) AS max_recency_days,
    ROUND(AVG(monetary), 2) AS avg_first_order_value,
    ROUND(SUM(monetary), 2) AS total_revenue_from_segment
FROM olist.customer_rfm
WHERE segment = 'At Risk'
GROUP BY segment;

-- At Risk: Distribution of Days Since Last Order (for histogram)
SELECT
    CASE
        WHEN recency_days BETWEEN 0 AND 30 THEN '0-30 days'
        WHEN recency_days BETWEEN 31 AND 60 THEN '31-60 days'
        WHEN recency_days BETWEEN 61 AND 90 THEN '61-90 days'
        WHEN recency_days BETWEEN 91 AND 180 THEN '91-180 days'
        WHEN recency_days BETWEEN 181 AND 365 THEN '181-365 days'
        ELSE '365+ days'
    END AS recency_bucket,
    COUNT(*) AS customers
FROM olist.customer_rfm
WHERE segment = 'At Risk'
GROUP BY 1
ORDER BY
    CASE recency_bucket
        WHEN '0-30 days' THEN 1
        WHEN '31-60 days' THEN 2
        WHEN '61-90 days' THEN 3
        WHEN '91-180 days' THEN 4
        WHEN '181-365 days' THEN 5
        ELSE 6
    END;

-- At Risk: First Order Value Distribution (for histogram)
SELECT
    CASE
        WHEN monetary < 50 THEN 'R$0-50'
        WHEN monetary BETWEEN 50 AND 100 THEN 'R$50-100'
        WHEN monetary BETWEEN 100 AND 200 THEN 'R$100-200'
        WHEN monetary BETWEEN 200 AND 500 THEN 'R$200-500'
        WHEN monetary > 500 THEN 'R$500+'
    END AS order_value_bucket,
    COUNT(*) AS customers
FROM olist.customer_rfm
WHERE segment = 'At Risk'
GROUP BY 1
ORDER BY
    CASE order_value_bucket
        WHEN 'R$0-50' THEN 1
        WHEN 'R$50-100' THEN 2
        WHEN 'R$100-200' THEN 3
        WHEN 'R$200-500' THEN 4
        WHEN 'R$500+' THEN 5
    END;


-- ============================================================================
-- PAGE 5: COHORT RETENTION MATRIX
-- ============================================================================

-- Cohort Retention: Full Matrix (M0-M6)
-- Pivoted: rows = cohort month, columns = month index
SELECT
    cohort_month,
    cohort_size,
    ROUND(M0 * 100, 1) AS M0,
    ROUND(M1 * 100, 1) AS M1,
    ROUND(M2 * 100, 1) AS M2,
    ROUND(M3 * 100, 1) AS M3,
    ROUND(M4 * 100, 1) AS M4,
    ROUND(M5 * 100, 1) AS M5,
    ROUND(M6 * 100, 1) AS M6
FROM (
    SELECT
        cohort_month,
        MAX(cohort_size) AS cohort_size,
        MAX(CASE WHEN month_index = 0 THEN retention_rate END) AS M0,
        MAX(CASE WHEN month_index = 1 THEN retention_rate END) AS M1,
        MAX(CASE WHEN month_index = 2 THEN retention_rate END) AS M2,
        MAX(CASE WHEN month_index = 3 THEN retention_rate END) AS M3,
        MAX(CASE WHEN month_index = 4 THEN retention_rate END) AS M4,
        MAX(CASE WHEN month_index = 5 THEN retention_rate END) AS M5,
        MAX(CASE WHEN month_index = 6 THEN retention_rate END) AS M6
    FROM olist.cohort_retention
    WHERE cohort_size > 10
    GROUP BY cohort_month
) sub
ORDER BY cohort_month;

-- Cohort: Average Retention by Month Index
SELECT
    month_index,
    ROUND(AVG(retention_rate) * 100, 2) AS avg_retention_pct,
    COUNT(*) AS cohorts_included
FROM olist.cohort_retention
WHERE cohort_size > 10
GROUP BY month_index
ORDER BY month_index;

-- M1 Retention Key Stat (filtered for meaningful cohorts)
SELECT
    ROUND(AVG(retention_rate) * 100, 2) AS m1_avg_retention
FROM olist.cohort_retention
WHERE month_index = 1 AND cohort_size > 10;


-- ============================================================================
-- PAGE 6: RECOMMENDATIONS — Quantified Impact
-- ============================================================================

-- Recommendation 1: Retention Program Impact Calculation
WITH repeat_stats AS (
    SELECT
        COUNT(DISTINCT customer_unique_id) AS total_customers,
        COUNT(DISTINCT customer_unique_id) FILTER (
            WHERE customer_unique_id IN (
                SELECT customer_unique_id
                FROM olist.fact_orders
                GROUP BY customer_unique_id
                HAVING COUNT(DISTINCT order_id) > 1
            )
        ) AS repeat_customers
    FROM olist.fact_orders
)
SELECT
    total_customers,
    repeat_customers,
    ROUND(repeat_customers::numeric / total_customers * 100, 2) AS current_repeat_rate,
    ROUND(total_customers * 0.08 - repeat_customers, 0) AS incremental_repeat_customers_target,
    ROUND((total_customers * 0.08 - repeat_customers) * 119.81, 0) AS incremental_revenue_estimate
FROM repeat_stats;

-- Recommendation 2: Delivery Improvement — Late Rate by State
SELECT
    dc.customer_state AS state,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (WHERE is_late = true) AS late_orders,
    ROUND(COUNT(*) FILTER (WHERE is_late = true)::numeric / COUNT(*) * 100, 2) AS late_rate_pct
FROM olist.fact_orders fo
JOIN olist.dim_customer dc ON fo.customer_id = dc.customer_id
GROUP BY dc.customer_state
HAVING COUNT(*) > 100
ORDER BY late_rate_pct DESC
LIMIT 10;

-- Recommendation 3: Premium Markets — High AOV States
SELECT
    dc.customer_state AS state,
    ROUND(AVG(fo.revenue), 2) AS aov,
    COUNT(*) AS orders,
    ROUND(SUM(fo.revenue), 2) AS total_revenue
FROM olist.fact_orders fo
JOIN olist.dim_customer dc ON fo.customer_id = dc.customer_id
GROUP BY dc.customer_state
HAVING COUNT(*) > 50
ORDER BY aov DESC
LIMIT 5;

-- Calculate expansion opportunity for Paraíba (from 517 to 1000 orders)
-- Current PB orders from previous query
SELECT
    1000 - 517 AS incremental_orders,
    ROUND((1000 - 517) * 266.61, 0) AS incremental_revenue;

-- Combined Impact Summary
SELECT 'Retention Program (3% → 8%)' AS initiative, 'R$645,000' AS estimated_impact
UNION ALL
SELECT 'Delivery Improvement (7.78% → 5%)', 'R$200,000'
UNION ALL
SELECT 'Premium Market Expansion (PB)', 'R$129,000';


-- ============================================================================
-- ADDITIONAL: Category & Product Insights (optional for Appendix)
-- ============================================================================

-- Top Categories by Revenue
SELECT
    dp.category_en AS category,
    COUNT(DISTINCT fo.order_id) AS orders,
    ROUND(SUM(fo.revenue), 2) AS revenue,
    ROUND(AVG(fo.review_score), 2) AS avg_review_score
FROM olist.fact_orders fo
JOIN olist.dim_product dp ON fo.product_id = dp.product_id
GROUP BY dp.category_en
ORDER BY revenue DESC
LIMIT 10;

-- Categories with Highest Review Scores (min 100 orders)
SELECT
    dp.category_en AS category,
    ROUND(AVG(fo.review_score), 2) AS avg_review_score,
    COUNT(*) AS orders
FROM olist.fact_orders fo
JOIN olist.dim_product dp ON fo.product_id = dp.product_id
GROUP BY dp.category_en
HAVING COUNT(*) >= 100
ORDER BY avg_review_score DESC
LIMIT 10;