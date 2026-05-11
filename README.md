# Olist Sales & Customer Analytics

## The Hook

**"3% Repeat Rate is Costing Olist R$558,000+ in Missed Revenue Annually"**

Olist processed 96,478 orders generating R$13.28M in revenue between 2016–2018. But the headline number masks a structural problem: **only 3% of customers ever place a second order**. RFM segmentation reveals that **24.1% of the customer base (23,272 customers) is already classified as At Risk** — customers who bought once but haven't returned.

The biggest lever for revenue growth is not acquiring new customers; it's converting the 81% of one-time buyers before they go cold.

---

## Background & Overview

This project analyzes ~100,000 orders from Olist, a Brazilian e-commerce platform, across 2016–2018. The analysis surfaces trends in revenue growth, delivery performance, and customer behavior to help Olist's Sales & Operations leadership team make data-driven decisions.

### Dataset

| Attribute | Detail |
|-----------|--------|
| Source | [Olist Brazilian E-Commerce (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) |
| License | CC BY-NC-SA 4.0 |
| Tables | 9 interconnected tables |
| Orders | 99,441 total (96,478 delivered) |
| Customers | 93,358 unique |
| Date Range | September 2016 – October 2018 |
| Repeat Customer Rate | 3.00% (2,801 repeat buyers) |

### Technical Stack

**PostgreSQL → Python ETL → Vizro Dashboard**

- **PostgreSQL** (port 5433): Star schema data warehouse with fact/dimension tables
- **Python**: ETL scripts for data loading, cleaning, and KPI generation
- **Vizro**: Interactive web dashboard with 4 pages

### Stakeholder Audience

This dashboard supports three key stakeholder groups:

| Audience | Needs | Dashboard Implication |
|----------|-------|----------------------|
| Sales & Ops Leadership | High-level trends, big picture | KPI callouts, trend lines, minimal detail |
| Category Managers | Product performance, customer satisfaction | Category breakdowns, review scores, AOV by segment |
| Analysts & Data Teams | Ability to explore and validate | Filters, dimension drill-through, detailed tables |

### Metrics by Stakeholder Team

Different teams care about different metrics and can pull different levers:

| Team | Metrics They Care About | Levers They Can Pull |
|------|------------------------|---------------------|
| **Finance** | Total revenue, revenue by state, AOV | Budget allocation, cost management, forecasting |
| **Marketing** | Repeat customer rate, payment preferences, customer acquisition | Retention campaigns, channel strategy, messaging |
| **Product** | Category revenue, review scores, freight cost % | Inventory decisions, seller recruitment, promotions |
| **Operations** | On-time delivery rate, avg delivery days, late orders | Carrier contracts, fulfillment processes, SLA management |

### Business Questions Answered

1. How is revenue trending, and which categories drive it?
2. Which Brazilian states represent the biggest market opportunity?
3. Are we meeting delivery promises, and where are the bottlenecks?
4. Which sellers are high-value and reliable vs. high-risk?
5. How loyal are our customers, and which segments are most valuable?

---

## Data Structure Overview

### Star Schema Data Model

The data is modeled in a star schema, separating measurable facts from descriptive dimensions. This enables fast slice-and-dice analysis across any combination of time, geography, product, and customer attributes.

```
                 ┌─────────────────┐
                 │  dim_date       │
                 │  date_key PK    │
                 │  year, quarter  │
                 │  month, week    │
                 └────────┬────────┘
                          │
┌──────────────┐    ┌────────▼────────┐    ┌──────────────┐
│ dim_customer │    │  fact_orders    │    │ dim_product  │
│ customer_id  ◄────┤  order_id PK   ├────► product_id   │
│ state, region│    │  customer_id FK │    │ category_en  │
└──────────────┘    │  product_id FK  │    └──────────────┘
                    │  seller_id FK   │    ┌──────────────┐
┌──────────────┐    │  date_key FK    │    │ dim_seller   │
│ dim_seller   ◄────┤  revenue        ├────► seller_id    │
│ seller_id    │    │  freight_value  │    │ state, region│
└──────────────┘    │  review_score   │    └──────────────┘
                    │  is_late        │
                    │  is_repeat_cust │
                    └─────────────────┘
```

### Tables

| Table | Role | Key Columns |
|-------|------|-------------|
| `fact_orders` | Central fact table | order_id, revenue, freight_value, review_score, is_late, is_repeat_customer |
| `dim_date` | Time dimension | date_key, year, quarter, year_month, month, week_num, is_weekend |
| `dim_customer` | Customer dimension | customer_id, customer_unique_id, customer_state, customer_city |
| `dim_product` | Product dimension | product_id, category_en, weight_g, dimensions |
| `dim_seller` | Seller dimension | seller_id, seller_state, seller_city |

### Data Pipeline

```
CSV Files → load_data_v2.py → Raw Tables
                   ↓
        phase2_cleaning_eda.py → Cleaned Data + Issues Log
                   ↓
        phase3_starschema.py → Star Schema Views (fact + dimensions)
                   ↓
        phase4_kpis.py → KPI Views (revenue, delivery, customer metrics)
                   ↓
        phase6_advanced.py → RFM Segmentation + Cohort Analysis
                   ↓
        Vizro → Dashboard (4 pages, interactive)
```

### Data Quality & Cleaning

Real-world data requires cleaning. Key issues identified and resolved:

| Issue | Impact | Resolution |
|-------|--------|-------------|
| ~3,000 geolocation rows with duplicate zip prefixes | Inaccurate city/state mapping | Created `geo_deduped` view with AVG(lat/lng) by zip prefix |
| 2,965 orders with NULL delivery dates | Underestimated delivery metrics | Excluded from delivery KPIs, tracked separately |
| Portuguese product category names | Confusing for non-Brazilian stakeholders | JOINed to `category_translation` table, COALESCE for missing |
| Initial repeat customer rate = 0% | Incorrect business insight | Fixed by using `customer_unique_id` instead of `customer_id` |
| Payment table has multiple rows per order | Inflated payment method counts | Used `payment_sequential = 1` to get primary method |

**Data quality logs:** `logs/phase2_cleaning_eda.log.md` | **Full issues log:** `logs/insights.md`

---

## Executive Summary

### Key Metrics

| Metric | Value | Business Meaning |
|--------|-------|------------------|
| **Total Revenue** | R$13,279,837 | Baseline for growth calculations |
| **Total Orders** | 96,478 (delivered) | Volume indicator |
| **Average Order Value (AOV)** | R$119.81 | Typical transaction size |
| **On-Time Delivery Rate** | 92.22% | 7.78% are late — operational bottleneck |
| **Average Delivery Days** | 12.1 days | Customer expectation setter |
| **Average Review Score** | 4.08 / 5.00 | Generally satisfied customers |
| **Repeat Customer Rate** | 3.00% | Massive retention opportunity |

### Monthly Revenue Trend (Last 6 Months)

| Month | Orders | Revenue | AOV |
|-------|--------|---------|-----|
| 2018-08 | 6,351 | R$838,651 | R$132.05 |
| 2018-07 | 6,159 | R$869,842 | R$141.23 |
| 2018-06 | 6,099 | R$856,910 | R$140.50 |
| 2018-05 | 6,749 | R$978,066 | R$144.92 |
| 2018-04 | 6,798 | R$975,779 | R$143.54 |
| 2018-03 | 7,003 | R$956,924 | R$136.64 |

**Trend:** Revenue stable around R$950k/month, AOV ranging R$132–R$145. Seasonal patterns visible (Q4 typically stronger).

---

## North Star Metrics

Every analysis needs a North Star to prevent analysis paralysis. These are the primary metrics, dimensions, and team goals guiding this project.

| North Star | Value | Stakeholder Team | Levers They Can Pull |
|------------|-------|------------------|---------------------|
| **Total Revenue** (R$13.28M) | Primary KPI | Finance | Budget allocation, cost management, forecasting |
| **Order Volume** (96,478) | Demand indicator | Marketing | Campaign strategy, customer acquisition |
| **AOV** (R$119.81) | Price health per transaction | Product | Pricing strategy, promotions |

### Key Dimensions for Slicing

| Dimension | Why It Matters | Team Responsible |
|-----------|----------------|----------|
| **Product Category** | Revenue driver, satisfaction indicator | Product Team |
| **Customer State** | Market opportunity, geographic trends | Marketing + Ops |
| **Time** (Month/Quarter) | Trend analysis, seasonality | All teams |

### Decomposing Revenue: Going One Level Deeper

Revenue is a composite metric: **Revenue = Order Volume × AOV**

When revenue dips, ask:
- **Did customers buy *less often*?** → Order volume declined (Marketing issue)
- **Did customers pay *less per purchase*?** → AOV declined (Pricing/Product issue)
- **Was it *both*?** → Combined effect (competitive pressure)

**Finding:** In this dataset, the 3% repeat customer rate is the primary driver of stagnant order volume — a Marketing team lever, not Product.

### Metrics to Prioritize vs. Ignore

**Prioritize (included in dashboard):**
- Revenue, Order Volume, AOV (represent 100% of total)
- On-Time Delivery Rate (directly influenceable by Ops)
- Repeat Customer Rate (directly influenceable by Marketing)

**Deprioritize (excluded from dashboard):**
- Headsets category (<2% of revenue, ~1,000 orders)
- Seller-specific metrics on Executive page (belongs on Seller page only)
- Payment method trends for Ops team (belongs to Marketing)

---

## Insights Deep Dive

### Geographic Performance

#### Top 10 States by Customer Count

| State | Customers | % of Total |
|-------|-----------|-------------|
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

**Finding:** Market concentration in Southeast (SP/RJ/MG = 66%). This represents both stability and vulnerability.

#### Highest AOV by State (Premium Market Opportunity)

| State | AOV | Orders |
|-------|-----|---------|
| PB (Paraíba) | R$266.61 | 517 |
| AC (Acre) | R$244.69 | 80 |
| AP (Amapá) | R$240.92 | 67 |
| AL (Alagoas) | R$237.21 | 397 |
| RO (Rondônia) | R$234.43 | 243 |

**Finding:** Premium markets (PB, AC, AP) show 2× AOV — untapped opportunity for targeted marketing and seller recruitment.

---

### Product & Category Performance

#### Top Categories by Review Score (min 100 orders)

| Category | Avg Review | Orders |
|----------|-----------|---------|
| books_general_interest | 4.45 | 549 |
| books_technical | 4.37 | 266 |
| food_drink | 4.32 | 279 |
| luggage_accessories | 4.32 | 1,088 |
| fashion_shoes | 4.23 | 261 |

**Finding:** Books and food categories have highest satisfaction. Cross-selling these to existing customers could boost overall review scores.

#### Payment Preferences

| Payment Type | Count | % of Total |
|--------------|-------|-------------|
| credit_card | 76,476 | 73.6% |
| boleto | 19,783 | 19.0% |
| voucher | 1,621 | 1.6% |
| debit_card | 1,477 | 1.4% |

**Finding:** Credit card dominance (73.6%) suggests customers are comfortable with digital payments — opportunity for installment-based promotions.

---

### Customer Segmentation (RFM Analysis)

Customers segmented by Recency (days since last order), Frequency (number of orders), and Monetary (total revenue).

| Segment | Customers | % of Total | Recommended Action |
|---------|-----------|-------------|---------------------|
| At Risk | 23,272 | 24.1% | Re-engagement campaign (email, discounts) |
| Loyal Customers | 19,276 | 20.0% | Loyalty rewards program |
| Recent Customers | 15,528 | 16.1% | Welcome series, onboarding |
| Champions | 15,338 | 15.9% | VIP program, referrals |
| Lost | 15,320 | 15.9% | Win-back (low priority) |
| Promising | 7,744 | 8.0% | Nurture to loyal |

**Finding:** 24.1% of customers are "At Risk" — targeted campaigns could prevent churn. Only 3% repeat rate suggests massive retention opportunity.

---

### Cohort Retention Analysis

Retention rates by month index (months since first purchase):

| Cohort Month | M0 | M1 | M2 | M3 | M4 | M5 | M6 |
|--------------|----|----|----|----|----|----|-----|
| 2017-01 | 100% | 0.3% | 0.3% | 0.1% | 0.4% | 0.1% | 0.4% |
| 2017-06 | 100% | 0.5% | 0.4% | 0.4% | 0.3% | 0.4% | 0.4% |
| 2018-01 | 100% | 0.3% | 0.4% | 0.3% | 0.3% | 0.2% | 0.2% |

**Average Retention:**
- M0: 100.0% (baseline)
- M1: 0.5% (avg across cohorts)
- M6: 0.3% (avg across cohorts)

**Finding:** Month-1 retention ~0.5% is extremely low, confirming the 3% repeat rate. Olist has a massive retention problem — customers acquire but don't return.

---

### Sales Mix: Revenue Distribution Over Time

**Absolute View (Line Chart):** Total revenue by category over time — shows magnitude and trends.

**Mix View (Area Chart as % of Total):** Each category's share of total revenue — shows whether a dip was concentrated in one category or spread evenly.

**Finding:** Combining both views reveals that revenue dips are often category-specific (e.g., a single product line underperforming) rather than macro trends — which determines whether you're looking at a product issue or company-wide problem.

**SQL:** Available in `olist.kpi_sales_mix` view (created in `sql/phase4_kpis.py`).

---

### Seller Performance

- **Total Sellers**: 3,095
- **Avg Review Score by Seller**: 4.08 (same as overall)
- **Seller Late Rate**: Varies by seller (0% to 100%)

**Action:** Flag sellers with <80% on-time rate for performance review and potential contract renegotiation.

---

## Recommendations

### Market Context & Background
*Insights that explain the "why" but can't be directly acted on:*

- Seasonal patterns: Q4 consistently shows revenue spikes (2017, 2018 data)
- Market concentration: SP/RJ/MG = 66% of customers (stable but vulnerable)
- Payment preference: 73.6% credit card, 19.0% boleto (customers comfortable with digital payments)
- All regions show similar delivery dips → macro events (e.g., holidays, carrier delays)

### Areas for Further Investigation
*Observations that point to something worth exploring but need more data:*

- **Paraíba (PB)** has 2× AOV (R$266.61 vs. R$119.81 avg) with only 517 orders — needs market research
- **Payment preferences** vary by region — could inform checkout optimization strategies
- **Seller reliability** varies from 0% to 100% on-time rate — need performance benchmarking
- **Books categories** have 4.3+ star ratings but represent small revenue share — cross-sell potential unclear

### Actionable Recommendations
*Findings with clear, concrete next steps:*

#### 1. Customer Retention Program (High Impact)

**Target:** "At Risk" segment (23,272 customers, 24.1% of base)

**Actions:**
- Personalized email campaigns with exclusive offers
- Loyalty points program for repeat purchases
- VIP tier for "Champions" (15.9%) with early access to new products

**Expected Impact:**
- 3% → 8% repeat rate = ~4,700 additional orders/year
- Revenue Impact: ~R$558,480 additional revenue (at R$119.81 AOV)

---

#### 2. Leverage High-Satisfaction Categories (Medium Impact)

**Target:** `books_general_interest` (4.45 stars), `books_technical` (4.37 stars), `food_drink` (4.32 stars)

**Actions:**
- Cross-sell these categories to customers who haven't purchased them
- Promote high-review products in marketing campaigns
- Prioritize seller recruitment in these categories

**Expected Impact:**
- Increase overall review scores from 4.08 to 4.15+
- Reduce return rates (satisfied customers return less)

---

#### 3. Expand in High-AOV Markets (Medium Impact)

**Target:** Paraíba (PB, R$266.61 AOV), Acre (AC, R$244.69 AOV), Amapá (AP, R$240.92 AOV)

**Actions:**
- Targeted marketing campaigns in these states
- Recruit local sellers to expand product selection
- Offer free shipping thresholds tailored to premium AOV

**Expected Impact:**
- Grow orders in premium markets
- If PB grows from 517 to 1,000 orders: +R$129,000 revenue from one state

---

### Combined 1-Year Business Impact

| Initiative | Estimated Revenue Impact |
|------------|--------------------------|
| Customer Retention (3% → 8%) | ~R$558,480 |
| Premium Market Expansion (PB, AC, AP) | ~R$129,000+ |
| **Total Conservative Estimate** | **R$687,000+ (~5% growth on R$13.28M baseline)** |

---

## Technical Implementation

### SQL Scripts (`/sql/` folder)

| Script | Description |
|--------|-------------|
| `01_create_tables.sql` | Schema creation for all 9 tables |
| `02_load_data.sql` | Data loading queries |
| `load_data_v2.py` | Python ETL: creates tables and loads CSV data |
| `phase2_cleaning_eda.py` | Data quality fixes + EDA queries |
| `phase3_starschema.py` | Creates star schema views (fact + dimensions) |
| `phase4_kpis.py` | Creates KPI views for dashboard |
| `phase6_advanced.py` | RFM segmentation + cohort retention analysis |

### Quick Start

```bash
# Set up database and star schema
python sql/load_data_v2.py
python sql/phase3_starschema.py
python sql/phase4_kpis.py
python sql/phase6_advanced.py

# Launch Vizro dashboard
cd vizro_dashboard
uv sync
uv run python app.py
# Open http://localhost:8050
```

---

## Interview Reference

### One-Sentence Project Summary
> "I built a sales & customer analytics dashboard for Olist (Brazilian e-commerce) using PostgreSQL, Python, and Vizro, finding that only 3% of customers return and 24% are At Risk — representing R$558K+ annual improvement opportunity."

### 5 Numbers to Memorize
1. **Revenue:** R$13.28M across 96,478 orders
2. **Problem:** Only 3% repeat customers, 24% At Risk segment
3. **Solution:** Retention campaigns for At Risk segment, welcome series for new customers
4. **Tech Stack:** PostgreSQL → Python ETL → Vizro (Star Schema)
5. **Differentiator:** RFM segmentation + Cohort analysis (not just basic charts)

---

## Source

**Dataset:** [Olist Brazilian E-Commerce (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)  
**License:** CC BY-NC-SA 4.0  
**Date Range:** September 2016 – October 2018

---

## Author

Albar Pambagio  
GitHub: [@albarpambagio](https://github.com/albarpambagio)