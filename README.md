# Olist Brazilian E-Commerce: Sales & Operations Dashboard

## Executive Summary

Analysis of ~100,000 orders from Olist's Brazilian e-commerce platform (2016–2018). This project surfaces trends in revenue growth, delivery performance, and customer behaviour to help the Sales & Operations team make data-driven decisions.

**Technical Stack:** SQL (PostgreSQL) → Power BI Desktop  
**Data:** 9 tables, ~100k orders, 2016–2018  
**License:** Dataset licensed CC BY-NC-SA 4.0

---

## Business Questions Answered

1. **How is revenue trending, and which categories drive it?**
2. **Which Brazilian states represent the biggest market opportunity?**
3. **Are we meeting delivery promises, and where are the bottlenecks?**
4. **Which sellers are high-value and reliable vs. high-risk?**
5. **How loyal are our customers, and which segments are most valuable?**

---

## Key Findings

| Metric | Value |
|---|---|
| Total Revenue | $13,168,332.11 |
| Total Orders | 95,832 |
| Average Order Value (AOV) | $137.41 |
| Average Review Score | 4.08 / 5.00 |
| On-Time Delivery Rate | 92.22% |
| Late Delivery Rate | 7.78% |
| Average Delivery Days | 12.1 days |
| Repeat Customer Rate | 3.00% |

### Geographic Insights
- **São Paulo (SP)** leads with 41,746 customers (42% of total)
- **Rio de Janeiro (RJ)** follows with 12,852 customers
- **Minas Gerais (MG)** has 11,635 customers
- Top AOV by state: **Paraíba (PB)** at $266.61, **Acre (AC)** at $244.69

### Category Performance
- Highest review scores: **books_general_interest** (4.45), **books_technical** (4.37)
- Most common payment: **credit_card** (73.6%), followed by **boleto** (19.0%)

### Customer Segmentation (RFM)
| Segment | Customers | % of Total |
|---|---|---|
| At Risk | 23,272 | 24.1% |
| Loyal Customers | 19,276 | 20.0% |
| Recent Customers | 15,528 | 16.1% |
| Champions | 15,338 | 15.9% |
| Lost | 15,320 | 15.9% |
| Promising | 7,744 | 8.0% |

---

## Recommendations

1. **Investigate late deliveries in key states** — 7.78% late rate (7,826 orders) impacts customer satisfaction and review scores
2. **Re-engagement campaign for "At Risk" segment** — 23,272 customers (24.1%) need targeted offers to prevent churn
3. **Leverage high-review categories** — Promote books and technical products that consistently earn 4.3+ star ratings
4. **Investigate Paraíba (PB) market** — Highest AOV at $266.61 suggests premium market opportunity
5. **Improve repeat customer rate** — Only 3% of customers order more than once; loyalty programs could drive LTV

---

## Data Model

### Star Schema

```
                ┌─────────────────┐
                │  dim_date       │
                │  date_key PK    │
                │  year, quarter  │
                │  month, week   │
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

---

## Project Structure

```
olist-ecommerce-dashboard/
├── data/                    # CSV files (download from Kaggle)
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_load_data.sql
│   ├── phase2_cleaning_eda.py
│   ├── phase3_starschema.py
│   ├── phase4_kpis.py
│   └── phase6_advanced.py
├── logs/
│   ├── phase1_setup.log.md
│   ├── phase2_cleaning_eda.log.md
│   └── phase3_starschema.log.md
├── docs/
│   └── dashboard_guide.md    # Power BI build guide + DAX measures
└── README.md
```

---

## Quick Start

### 1. Prerequisites
- PostgreSQL (running on port 5433)
- Python 3.x with psycopg2-binary
- Power BI Desktop (free)

### 2. Download Dataset
```bash
kaggle datasets download -d olistbr/brazilian-ecommerce -p ./data --unzip
```

### 3. Set Up Database
```bash
python sql/load_data_v2.py
python sql/phase3_starschema.py
python sql/phase4_kpis.py
python sql/phase6_advanced.py
```

### 4. Connect Power BI
- Server: `localhost:5433`
- Database: `olist`
- Import: `fact_orders`, `dim_date`, `dim_product`, `dim_customer`, `dim_seller`

### 5. DAX Measures
See [docs/dashboard_guide.md](docs/dashboard_guide.md) for all DAX measures and dashboard build instructions.

---

## SQL Scripts

| Script | Description |
|---|---|
| `load_data_v2.py` | Creates tables and loads CSV data |
| `phase2_cleaning_eda.py` | Data quality fixes + EDA queries |
| `phase3_starschema.py` | Creates star schema views |
| `phase4_kpis.py` | Creates KPI views for dashboard |
| `phase6_advanced.py` | RFM segmentation + cohort analysis |

---

## Dataset Source

**Olist Brazilian E-Commerce Dataset**  
[Download from Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)  
Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

---

## Author

**Albar Pambagio**  
GitHub: [@albarpambagio](https://github.com/albarpambagio)  
Project: [olist-ecommerce-dashboard](https://github.com/albarpambagio/olist-ecommerce-dashboard)