# Phase 5: Power BI Dashboard Build Guide

## Connection Setup

1. Open Power BI Desktop
2. Get Data → PostgreSQL database
3. Server: `localhost:5433`
4. Database: `olist`
5. Use DirectQuery or Import mode

## Data Model Relationships

Set these relationships in Model view:
- `fact_orders[order_date]` → `dim_date[date_key]` (many-to-one)
- `fact_orders[product_id]` → `dim_product[product_id]` (many-to-one)
- `fact_orders[customer_id]` → `dim_customer[customer_id]` (many-to-one)
- `fact_orders[seller_id]` → `dim_seller[seller_id]` (many-to-one)

## DAX Measures

Copy these into Power BI → Table view → New Measure:

```dax
-- Revenue
Revenue = SUM(fact_orders[revenue])

-- Order Volume
Orders = DISTINCTCOUNT(fact_orders[order_id])

-- AOV (Average Order Value)
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
DIVIDE(
    SUM(fact_orders[freight_value]),
    SUM(fact_orders[revenue]) + SUM(fact_orders[freight_value])
)

-- Avg Delivery Days
Avg Delivery Days = AVERAGE(fact_orders[actual_delivery_days])

-- Repeat Customer Rate
Repeat Customer Rate =
VAR repeat_cust = COUNTROWS(FILTER(fact_orders, fact_orders[is_repeat_customer] = 1))
VAR total_cust = DISTINCTCOUNT(fact_orders[customer_id])
RETURN DIVIDE(repeat_cust, total_cust)

-- Avg Review Score
Avg Review Score = AVERAGE(fact_orders[review_score])

-- YTD Revenue
Revenue YTD = TOTALYTD([Revenue], dim_date[date_key])

-- 5-Star Review %
Five Star % =
VAR five_star = COUNTROWS(FILTER(fact_orders, fact_orders[review_score] = 5))
VAR total_reviews = COUNTROWS(FILTER(fact_orders, NOT(ISBLANK(fact_orders[review_score]))))
RETURN DIVIDE(five_star, total_reviews)
```

## Date Table (Already in PostgreSQL!)

**You already have `dim_date` in PostgreSQL** with all needed columns:
- `date_key`, `year`, `quarter`, `year_month`, `month`, `month_name`, `week_num`, `day_of_week`, `is_weekend`

### In Power BI:
1. **Use the existing `dim_date`** from PostgreSQL (already in your model)
2. **Mark it as a Date Table**: 
   - Go to **Table View** → select `dim_date` table
   - Click **Mark as Date Table** (ribbon) → select `date_key` column
3. **That's it!** No need to create a DAX DateTable.

### Why Skip the DAX DateTable?
- ✅ `dim_date` is already loaded and has all columns
- ✅ Relationship `fact_orders[order_date]` → `dim_date[date_key]` already set
- ✅ Power BI time intelligence works with `dim_date` once marked as Date Table
- ✅ Consistent with your star schema (single source of truth)

### If You Need DAX Time Intelligence Without Marking:
Some DAX functions (like `SAMEPERIODLASTYEAR`) require a marked date table. If you get errors, then create the DAX DateTable as a supplement (not replacement).

## Dashboard Pages Structure

### Page 1: Executive Overview
**KPI Cards (top row):**
- Revenue
- Orders
- AOV
- On-Time Rate
- Avg Review Score

**Visuals:**
- Revenue trend line (monthly, with MoM% annotation)
- Revenue by quarter (bar chart)
- Orders by status (donut)
- Slicer: Year, State

**Business narrative:** "Is the business growing and are we delivering on our promises?"

### Page 2: Customer Analysis
**Visuals:**
- Customer count by state (filled map)
- AOV distribution by state (bar chart, sorted desc)
- Repeat customer rate (KPI card + trend)
- Revenue by payment type (donut)
- New vs repeat customers over time (stacked bar)
- Customer segmentation table (see Advanced section)

**Business narrative:** "Who are our customers and where are they?"

### Page 3: Product & Category Analysis
**Visuals:**
- Revenue by product category (horizontal bar, top 15)
- Avg review score by category (bar, sorted)
- Revenue vs. freight cost % by category (scatter plot)
- Product weight vs. freight cost (scatter)
- Category performance matrix (revenue + review + order vol)

**Business narrative:** "Which categories drive revenue and which delight customers?"

### Page 4: Seller Performance
**Visuals:**
- Seller count by state (map)
- Top 20 sellers by revenue (bar with on-time rate overlay)
- Seller on-time rate vs. avg review score (scatter - quadrant analysis)
- Revenue per seller (KPI: avg, median, top decile)
- Sellers with <80% on-time rate flagged (conditional formatting)
- Drill-through: click seller → see their orders, products, review scores

**Business narrative:** "Which sellers are reliable and high-value?"

### Page 5: Logistics & Delivery
**Visuals:**
- On-time delivery rate by state (filled map)
- Avg delivery days trend (line chart over time)
- Estimated vs. actual delivery days (grouped bar by region)
- Late delivery rate by product category
- Freight cost % by state
- Delivery days by payment type

**Business narrative:** "Where are we slow, and is delivery getting better or worse over time?"

## Dashboard Design Checklist

- [ ] Consistent color palette across all pages (pick 2-3 colors max)
- [ ] All axis labels are readable (font size ≥ 11pt)
- [ ] No chart titles that just restate the chart type
- [ ] KPI cards show comparison context (vs. prior period or vs. target)
- [ ] Slicers are clearly labeled and visible
- [ ] No chart uses more than 6 colors at once
- [ ] Remove all gridlines except necessary reference lines
- [ ] Page navigation buttons between pages
- [ ] A text box on each page with a 1-sentence "so what"