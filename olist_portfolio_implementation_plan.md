# Olist Brazilian E-Commerce — Portfolio Implementation Plan
**Project 1: Executive Sales & Operations Dashboard**

---

## Plan Evaluation (Honest Assessment)

### ✅ What's Strong in Your Plan
- Business questions are well-framed and stakeholder-oriented — this is exactly what hiring managers want to see
- KPI selection is solid and covers multiple business dimensions (revenue, ops, logistics, customer)
- Multi-page dashboard structure mirrors real BI work
- Mentioning star schema and DAX signals genuine technical awareness
- "Advanced Touch" ideas (cohort retention, customer segmentation, drill-through) are the right differentiators

### ⚠️ Gaps & Improvements to Make
| Gap | Why It Matters | Fix |
|---|---|---|
| No defined star schema before building | You'll rebuild your data model mid-project, wasting time | Design schema first (see Section 3) |
| "Review score" KPI is vague | Low specificity — what question does it answer? | Be precise: "% orders with ≥4 stars" or "avg review score by category" |
| No data quality / cleaning phase | Olist data has nulls, missing geolocation rows, order inconsistencies | Add an explicit EDA & cleaning step |
| No mention of README/GitHub write-up | This is what hiring managers read first | Plan your narrative output from the start |
| "Dynamic date table" listed as a feature, not explained | If you can't explain why, a hiring manager will probe it in interviews | Understand it before building it (see Section 5) |
| No business narrative angle | The dashboard needs a "story" — are you the analyst for Olist's marketing team? sales team? ops team? | Pick a stakeholder persona |
| Advanced features listed without sequence | Cohort analysis requires clean customer data first — ordering matters | Follow the phased approach below |

### 🎯 Verdict
**Your plan is 75% of the way there.** It covers the right territory but needs structural sequencing, a data cleaning phase, and a storytelling framework before you start building. Follow the plan below and this will be a genuinely competitive portfolio piece.

---

## Project Overview

| Item | Detail |
|---|---|
| Dataset | Olist Brazilian E-Commerce (Kaggle) |
| Tool Stack | SQL (PostgreSQL or BigQuery) + Power BI (or Tableau) |
| Stakeholder Persona | Data Analyst supporting Olist's Sales & Operations leadership team |
| Output | Multi-page Power BI dashboard + GitHub README (stakeholder-style report) |
| Timeline | ~3–4 weeks (part-time) |
| Portfolio Signal | SQL joins + data modeling + KPI design + dashboard storytelling |

---

## Dataset Overview

The Olist dataset contains **9 interconnected tables** covering ~100,000 orders (2016–2018).

| Table | Key Columns | Role in Project |
|---|---|---|
| `olist_orders` | order_id, customer_id, status, purchase_timestamp, delivered dates | Fact table core |
| `olist_order_items` | order_id, product_id, seller_id, price, freight_value | Line-item facts |
| `olist_order_payments` | order_id, payment_type, payment_value | Payment dimension |
| `olist_order_reviews` | order_id, review_score, review_creation_date | Review dimension |
| `olist_customers` | customer_id, customer_zip, customer_city, customer_state | Customer dimension |
| `olist_sellers` | seller_id, seller_zip, seller_city, seller_state | Seller dimension |
| `olist_products` | product_id, product_category_name, dimensions/weight | Product dimension |
| `olist_product_category_name_translation` | category name (PT → EN) | Reference/lookup |
| `olist_geolocation` | zip_code_prefix, lat, lng, city, state | Geo dimension |

**Known data quality issues to handle:**
- ~3,000 rows in geolocation have no matching customer/seller zip — use LEFT JOIN, not INNER
- Some orders have `delivered_customer_date` = NULL (cancelled or in-transit orders)
- Product category names are in Portuguese — must JOIN to translation table
- A small number of orders have `order_status` = 'unavailable' or 'cancelled' — exclude from revenue KPIs but track in logistics

---

## Phase 1: Environment Setup & Data Loading (Days 1–2)

### 1.1 Tools to Set Up
- [ ] **PostgreSQL** (local) or **BigQuery** (free tier, 10GB/month) — for SQL layer
- [ ] **Power BI Desktop** (free) — for dashboard layer
- [ ] **GitHub** — create a repo: `olist-ecommerce-dashboard`
- [ ] **DBeaver or pgAdmin** — SQL client (if using PostgreSQL)

### 1.2 Load Data into SQL
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

### 1.3 Initial Exploration Queries
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

---

## Phase 2: Data Cleaning & EDA (Days 3–5)

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

### 2.2 Key EDA Questions to Answer Before Building
Run these queries and note findings — they become your **README insights** later.

1. What % of orders are delivered on time vs. late?
2. Which product category has the highest average review score?
3. Which state has the highest AOV?
4. What payment method is most common? Does it vary by order value?
5. What % of customers made more than one purchase? (Repeat rate)

---

## Phase 3: Star Schema Design & SQL Data Model (Days 5–8)

### 3.1 Star Schema

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

### 3.2 Build the Fact Table in SQL
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

### 3.3 Dimension Tables to Create

```sql
-- dim_date: generate a date spine
CREATE VIEW olist.dim_date AS
SELECT
  d::DATE                                AS date_key,
  EXTRACT(YEAR FROM d)::INT              AS year,
  EXTRACT(QUARTER FROM d)::INT           AS quarter,
  TO_CHAR(d, 'YYYY-MM')                  AS year_month,
  EXTRACT(MONTH FROM d)::INT             AS month,
  TO_CHAR(d, 'Month')                    AS month_name,
  EXTRACT(WEEK FROM d)::INT              AS week_num,
  EXTRACT(DOW FROM d)::INT               AS day_of_week,
  CASE WHEN EXTRACT(DOW FROM d) IN (0,6)
       THEN TRUE ELSE FALSE END          AS is_weekend
FROM GENERATE_SERIES('2016-01-01'::DATE, '2019-12-31'::DATE, '1 day') d;

-- dim_product: with English category names
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

---

## Phase 4: Core KPI Design (Days 8–10)

Define each KPI precisely before building in Power BI. Know the formula, the denominator, and the business question it answers.

| KPI | Formula | Denominator | Business Question |
|---|---|---|---|
| **Revenue** | SUM(price) | All delivered orders | How much did we earn? |
| **Order Volume** | COUNT(DISTINCT order_id) | All delivered orders | How busy were we? |
| **AOV** | Revenue / Order Volume | Delivered orders | How much per transaction? |
| **Freight Cost %** | SUM(freight_value) / SUM(price + freight_value) | Delivered orders | What share of total goes to shipping? |
| **On-Time Delivery Rate** | COUNT(is_late=0) / COUNT(total) | Delivered orders with estimated date | Are we meeting promises? |
| **Avg Delivery Days** | AVG(actual_delivery_days) | Delivered orders | How fast are we? |
| **Review Score (avg)** | AVG(review_score) | Orders with a review | How satisfied are customers? |
| **% 5-Star Reviews** | COUNT(review=5) / COUNT(reviews) | Reviewed orders | Are customers delighted? |
| **Repeat Customer Rate** | COUNT(is_repeat=1) / COUNT(customers) | All customers | Do customers come back? |
| **Seller On-Time Rate** | COUNT(on-time by seller) / total | Per seller | Which sellers are reliable? |

---

## Phase 5: Dashboard Build in Power BI (Days 10–18)

### 5.1 Connection & Data Model Setup
1. Connect Power BI to your SQL database (DirectQuery for BigQuery, Import for PostgreSQL)
2. Import: `fact_orders`, `dim_date`, `dim_product`, `dim_customer`, `dim_seller`
3. Set relationships:
   - `fact_orders[order_date]` → `dim_date[date_key]` (many-to-one)
   - `fact_orders[product_id]` → `dim_product[product_id]` (many-to-one)
   - `fact_orders[customer_id]` → `dim_customer[customer_id]` (many-to-one)
   - `fact_orders[seller_id]` → `dim_seller[seller_id]` (many-to-one)

### 5.2 DAX Measures to Create

```dax
-- Revenue
Revenue = SUM(fact_orders[revenue])

-- Order Volume
Orders = DISTINCTCOUNT(fact_orders[order_id])

-- AOV
AOV = DIVIDE([Revenue], [Orders])

-- MoM Revenue Growth
Revenue MoM% =
VAR current = [Revenue]
VAR prior = CALCULATE([Revenue], DATEADD(dim_date[date_key], -1, MONTH))
RETURN DIVIDE(current - prior, prior)

-- On-Time Delivery Rate
On-Time Rate =
DIVIDE(
    COUNTROWS(FILTER(fact_orders, fact_orders[is_late] = 0)),
    COUNTROWS(fact_orders)
)

-- Freight Cost %
Freight % =
DIVIDE(SUM(fact_orders[freight_value]),
       SUM(fact_orders[revenue]) + SUM(fact_orders[freight_value]))

-- Avg Delivery Days
Avg Delivery Days = AVERAGE(fact_orders[actual_delivery_days])

-- Repeat Customer Rate
Repeat Customer Rate =
DIVIDE(
    COUNTROWS(FILTER(fact_orders, fact_orders[is_repeat_customer] = 1)),
    DISTINCTCOUNT(fact_orders[customer_id])
)

-- Avg Review Score
Avg Review Score = AVERAGE(fact_orders[review_score])

-- YTD Revenue
Revenue YTD = TOTALYTD([Revenue], dim_date[date_key])
```

### 5.3 Dynamic Date Table (DAX)

Create this as a calculated table in Power BI — don't import from SQL:

```dax
DateTable =
VAR StartDate = DATE(2016, 1, 1)
VAR EndDate = DATE(2019, 12, 31)
RETURN
ADDCOLUMNS(
    CALENDAR(StartDate, EndDate),
    "Year",           YEAR([Date]),
    "Quarter",        "Q" & QUARTER([Date]),
    "Month Number",   MONTH([Date]),
    "Month Name",     FORMAT([Date], "MMMM"),
    "Month Short",    FORMAT([Date], "MMM"),
    "Year-Month",     FORMAT([Date], "YYYY-MM"),
    "Week Number",    WEEKNUM([Date]),
    "Day of Week",    FORMAT([Date], "dddd"),
    "Is Weekend",     IF(WEEKDAY([Date], 2) >= 6, TRUE, FALSE)
)
```

Mark it as a Date Table (right-click → Mark as Date Table → select `[Date]` column).

### 5.4 Dashboard Pages

#### Page 1: Executive Overview
- KPI cards (top row): Revenue, Orders, AOV, On-Time Rate, Avg Review Score
- Revenue trend line (monthly, with MoM% annotation)
- Revenue by quarter (bar chart)
- Orders by status (donut)
- Slicer: Year, State
- **Business narrative:** "Is the business growing and are we delivering on our promises?"

#### Page 2: Customer Analysis
- Customer count by state (filled map)
- AOV distribution by state (bar chart, sorted desc)
- Repeat customer rate (KPI card + trend)
- Revenue by payment type (donut)
- New vs repeat customers over time (stacked bar)
- Customer segmentation table (see Advanced section)
- **Business narrative:** "Who are our customers and where are they?"

#### Page 3: Product & Category Analysis
- Revenue by product category (horizontal bar, top 15)
- Avg review score by category (bar, sorted)
- Revenue vs. freight cost % by category (scatter plot)
- Product weight vs. freight cost (scatter, to show cost drivers)
- Category performance matrix (revenue + review + order vol)
- **Business narrative:** "Which categories drive revenue and which delight customers?"

#### Page 4: Seller Performance
- Seller count by state (map)
- Top 20 sellers by revenue (bar with on-time rate overlay)
- Seller on-time rate vs. avg review score (scatter — quadrant analysis)
- Revenue per seller (KPI: avg, median, top decile)
- Sellers with <80% on-time rate flagged (conditional formatting)
- Drill-through: click seller → see their orders, products, review scores
- **Business narrative:** "Which sellers are reliable and high-value?"

#### Page 5: Logistics & Delivery
- On-time delivery rate by state (filled map)
- Avg delivery days trend (line chart over time)
- Estimated vs. actual delivery days (grouped bar by region)
- Late delivery rate by product category (reveals which categories cause delays)
- Freight cost % by state (are some regions more expensive to serve?)
- Delivery days by payment type (does payment method correlate with speed?)
- **Business narrative:** "Where are we slow, and is delivery getting better or worse over time?"

---

## Phase 6: Advanced Features (Days 18–22)

### 6.1 Customer Segmentation (RFM)
Build in SQL before bringing to Power BI:

```sql
CREATE VIEW olist.customer_rfm AS
WITH rfm_base AS (
  SELECT
    customer_id,
    MAX(order_date)                    AS last_order_date,
    COUNT(DISTINCT order_id)           AS frequency,
    SUM(revenue)                       AS monetary
  FROM olist.fact_orders
  GROUP BY customer_id
),
rfm_scored AS (
  SELECT *,
    CURRENT_DATE - last_order_date::DATE    AS recency_days,
    NTILE(5) OVER (ORDER BY CURRENT_DATE - last_order_date::DATE DESC) AS r_score,
    NTILE(5) OVER (ORDER BY frequency)                                  AS f_score,
    NTILE(5) OVER (ORDER BY monetary)                                   AS m_score
  FROM rfm_base
)
SELECT *,
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

Show on Customer Analysis page: segment distribution donut + revenue per segment bar.

### 6.2 Cohort Retention Analysis
```sql
CREATE VIEW olist.cohort_retention AS
WITH first_order AS (
  SELECT customer_id,
         DATE_TRUNC('month', MIN(order_date)) AS cohort_month
  FROM olist.fact_orders
  GROUP BY customer_id
),
order_months AS (
  SELECT f.customer_id,
         fo.cohort_month,
         DATE_TRUNC('month', f.order_date) AS order_month
  FROM olist.fact_orders f
  JOIN first_order fo USING (customer_id)
),
cohort_sizes AS (
  SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_size
  FROM first_order GROUP BY 1
)
SELECT
  om.cohort_month,
  EXTRACT(MONTH FROM AGE(om.order_month, om.cohort_month))::INT AS month_index,
  COUNT(DISTINCT om.customer_id)                                AS retained,
  cs.cohort_size,
  ROUND(COUNT(DISTINCT om.customer_id)::NUMERIC / cs.cohort_size, 3) AS retention_rate
FROM order_months om
JOIN cohort_sizes cs USING (cohort_month)
GROUP BY 1, 2, cs.cohort_size
ORDER BY 1, 2;
```

Display as a **heat table** in Power BI (matrix visual with conditional color formatting: dark = high retention, light = low).

### 6.3 Drill-Through Pages
On the Seller Performance page:
1. Right-click → Add Page → mark as Drill-through page
2. Add `seller_id` as the drill-through field
3. Show: seller's top products, monthly revenue trend, review score distribution, on-time rate over time
4. Hiring managers love this — it shows you understand Power BI's navigation model

---

## Phase 7: GitHub README (Days 22–25)

Write this as if you're an Olist data analyst presenting to leadership. Structure it exactly like you would present in a meeting.

```markdown
# Olist E-Commerce: Sales & Operations Dashboard

## Executive Summary
Analysis of ~100,000 orders from Olist's Brazilian e-commerce platform (2016–2018).
This project surfaces trends in revenue growth, delivery performance, and customer
behaviour to help the Sales & Operations team make data-driven decisions.

## Business Questions Answered
1. How is revenue trending, and which categories drive it?
2. Which Brazilian states represent the biggest market opportunity?
3. Are we meeting delivery promises, and where are the bottlenecks?
4. Which sellers are high-value and reliable vs. high-risk?
5. How loyal are our customers, and which segments are most valuable?

## Key Findings
- Revenue grew X% from [year] to [year], with Q4 consistently strongest (seasonality)
- São Paulo and Rio de Janeiro account for X% of total orders
- Late delivery rate is X%, concentrated in [state/category]
- X% of revenue comes from customers who ordered only once — retention opportunity
- The [category] category has the best review scores; [category] the worst
- Top 10% of sellers generate X% of total revenue

## Recommendations
- Investigate late delivery root causes in [state] — freight cost AND review score both suffer
- Consider targeted re-engagement campaign for "At Risk" and "Lost" customer segments
- Audit low-performing sellers in [category] — their review scores drag platform average

## Data Model
[Star schema diagram — embed as image]

## Technical Stack
SQL (PostgreSQL) → Power BI Desktop
Data: 9 tables, ~100k orders, 2016–2018
[Link to SQL files] | [Link to Power BI .pbix file]
```

---

## Phase 8: Polish & Packaging (Days 25–28)

### Dashboard Design Checklist
- [ ] Consistent color palette across all pages (pick 2–3 colors max)
- [ ] All axis labels are readable (font size ≥ 11pt)
- [ ] No chart titles that just restate the chart type ("Bar Chart") — use business question ("Which categories drive revenue?")
- [ ] KPI cards show comparison context (vs. prior period or vs. target)
- [ ] Slicers are clearly labeled and visible
- [ ] No chart uses more than 6 colors at once
- [ ] Remove all gridlines except necessary reference lines
- [ ] Page navigation buttons between pages
- [ ] A text box on each page with a 1-sentence "so what" of that page

### GitHub Repo Checklist
- [ ] README.md structured as stakeholder report (see Phase 7)
- [ ] `/sql/` folder with all SQL scripts (fact table, dimensions, RFM, cohort)
- [ ] `/screenshots/` folder with dashboard page images
- [ ] `.pbix` file uploaded (or note that it's available on request)
- [ ] Data source clearly credited (Olist via Kaggle)
- [ ] Insights visible within 1 click of landing on the repo

---

## Interview Talking Points to Prepare

You will likely be asked these questions about this project:

| Question | Key Points to Hit |
|---|---|
| "Walk me through this project" | Business question first → data model → KPIs defined → insights found → recommendations made |
| "Why did you use a star schema?" | Optimized for slice-and-dice queries; separates facts from dimensions; faster aggregation in Power BI; mirrors how BI teams actually work |
| "What was the hardest data challenge?" | Geolocation deduplication, null delivery dates, Portuguese category names, repeat customer identification across tables |
| "What did you find?" | Have 3 specific insights memorized with actual numbers |
| "What would you do differently?" | Show you can think critically — maybe you'd add real-time data, or build a forecasting model, or segment sellers instead of customers |
| "What do the recommendations mean for the business?" | Tie each insight to revenue impact or cost savings — even estimated |

---

## Timeline Summary

| Week | Phase | Deliverable |
|---|---|---|
| Week 1 | Setup + EDA + Cleaning | Clean fact table in SQL; EDA findings documented |
| Week 2 | Star schema + DAX measures | Relationships set in Power BI; all KPIs calculating correctly |
| Week 3 | Dashboard build (Pages 1–5) | Full dashboard draft complete |
| Week 4 | Advanced features + README | RFM, cohort, drill-through; GitHub repo published |

---

*Source dataset: [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — licensed CC BY-NC-SA 4.0*
