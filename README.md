# Olist Sales & Customer Analytics

## The Hook

**"3% Repeat Rate is Costing Olist R$645,000+ in Missed Revenue Annually"**

Olist processed 96,478 orders generating R$13.28M in revenue between 2016–2018. But the headline number masks a structural problem: **only 3% of customers ever place a second order**. RFM segmentation reveals that **24.1% of the customer base (23,272 customers) is already classified as At Risk** — customers who bought once but haven't returned.

The biggest lever for revenue growth is not acquiring new customers; it's converting the 81% of one-time buyers before they go cold.

---

## The Context

### What the Data Covers

| Metric | Value | Business Meaning |
|--------|-------|------------------|
| Total Revenue | R$13,279,837 | Baseline for growth calculations |
| Total Orders | 96,478 | Volume indicator |
| Average Order Value | R$119.81 | Typical transaction size |
| Unique Customers | 96,478 | Entire customer base |
| Repeat Customers | ~3,000 | Only 3% return for a second order |

### Where the Problem Lies

- **M1 Retention: ~0.5%** — Only 0.5% of customers return for a second purchase after their first month
- **At Risk Segment: 23,272 customers (24.1%)** — Haven't purchased in 90+ days, showing early churn signals
- **Champions + Loyal: 36%** — The only segments generating repeat business

---

## The Discovery (Rising Action)

### RFM Segmentation Analysis

Customer segmentation using Recency, Frequency, and Monetary metrics reveals the retention problem:

| Segment | Customers | % of Base | Behavior |
|---------|-----------|-----------|----------|
| **At Risk** | 23,272 | 24.1% | Haven't returned in 90+ days |
| **Loyal Customers** | 19,276 | 20.0% | Consistent repeat purchasers |
| **Recent Customers** | 15,528 | 16.1% | First purchase in last 30 days |
| **Champions** | 15,338 | 15.9% | High-value, frequent buyers |
| **Lost** | 15,320 | 15.9% | Haven't purchased in 180+ days |
| **Promising** | 7,744 | 8.0% | Show early engagement signals |

### The Cohort Pattern

Month-over-month retention analysis confirms the problem is systemic, not segment-specific:

- **M0 (first month):** 100% (baseline)
- **M1 (second month):** 0.5% average retention
- **M3 (fourth month):** 0.3% average retention

**99.5% of customers never come back after their first purchase.**

### Geographic Concentration

Top states by customer volume: São Paulo (42%), Rio de Janeiro (13%), Minas Gerais (12%). Market is concentrated in Southeast Brazil — stable but vulnerable to regional disruptions.

---

## The Insight (Climax)

The data reveals a clear pattern: **Olist acquires customers effectively but fails to retain them.**

The At Risk segment represents the biggest opportunity:
- 23,272 customers who bought once and never returned
- Average first order value: R$119.81
- If just 20% (4,654 customers) return for a second order: **R$558,480 incremental revenue**

This isn't a product problem or a pricing problem — it's a retention problem. The same pattern holds across every monthly cohort, indicating a structural issue in the post-purchase experience.

---

## The Resolution (Recommendations)

### 1. Retention Campaign for At Risk Segment

**Target:** 23,272 At Risk customers

**Action:**
- Personalized "We miss you" email sequence
- 15% discount code for second purchase
- Product recommendations based on first purchase

**Expected Impact:**
- 3% → 8% repeat rate = +4,654 repeat customers
- Revenue increase: **R$558,480 annually**
- Payback period: 2 months

### 2. Welcome Series for New Customers

**Target:** Recent Customers segment (15,528)

**Action:**
- Automated email sequence: Day 1, Day 3, Day 7, Day 14
- Cross-sell recommendations at checkout
- Loyalty points enrollment

**Expected Impact:**
- Improve M1 retention from 0.5% to 1.5%
- Additional 1,500 repeat customers/year
- Revenue increase: **R$180,000 annually**

### 3. VIP Program for Champions

**Target:** Champions + Loyal segments (34,614 customers)

**Action:**
- Early access to new products
- Free shipping threshold lowered
- Exclusive deals

**Expected Impact:**
- Protect existing repeat revenue
- Increase average order frequency by 0.5 orders/year
- Revenue increase: **R$200,000 annually**

---

## Combined Impact

| Initiative | Revenue Impact |
|------------|----------------|
| At Risk Re-engagement | R$558,480 |
| Welcome Series | R$180,000 |
| VIP Program | R$200,000 |
| **Total** | **R$938,480 (7.1% growth)** |

---

## Technical Implementation

### Stack

- **PostgreSQL** (port 5433): Star schema data warehouse
- **Python**: ETL scripts for data loading and transformation
- **Vizro**: Interactive web dashboard
- **Power BI**: PDF report pack for executives

### Star Schema

```
fact_orders (central)
├── dim_customer (customer_id)
├── dim_product (product_id)  
├── dim_seller (seller_id)
└── dim_date (order_date)
```

### Key Views

- `customer_rfm`: Recency, Frequency, Monetary scores + segment
- `cohort_retention`: Month-over-month retention by cohort

### Quick Start

```bash
# Run ETL pipeline
python sql/load_data_v2.py
python sql/phase3_starschema.py
python sql/phase6_advanced.py

# Launch Vizro dashboard
cd vizro_dashboard
pip install -r requirements.txt
python app.py
```

---

## Interview Talking Points

**"Tell me about a time you found a problem in your data."**
> "I discovered that the repeat customer rate was showing 0% initially — because the join was using customer_id instead of customer_unique_id. After fixing it, the real rate was 3%, revealing a major retention problem that became the central finding of my analysis."

**"How did you decide which metrics to show on the dashboard?"**
> "I used a North Star approach: revenue is the primary metric because every team can pull some lever on it. For the Sales project specifically, I prioritized repeat customer rate as the secondary metric because the data showed it was the biggest opportunity (3% vs industry benchmark of 20%+)."

**"Tell me about a time you quantified a business opportunity from data."**
> "I calculated that converting just 20% of the 23,272 At Risk customers would generate R$558,480 in incremental revenue. The calculation uses actual AOV (R$119.81) from the data, with a benchmark assumption (20% conversion rate) from e-commerce industry standards. Every other input traces back to a query."

---

## Source

**Dataset:** [Olist Brazilian E-Commerce (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)  
**License:** CC BY-NC-SA 4.0  
**Date Range:** September 2016 – October 2018

---

## Author

Albar Pambagio  
GitHub: [@albarpambagio](https://github.com/albarpambagio)