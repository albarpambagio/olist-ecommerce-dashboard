# Olist Sales Dashboard — Power BI PDF Report Guide

## Executive-Ready Paginated Report with Data Storytelling

---

## Overview

This guide builds a polished, paginated PDF report (6-8 pages) designed for executive presentation. The report follows data storytelling principles: **Setup → Conflict → Resolution**.

**Key difference from dashboard:**
- No interactivity — static, linear narrative
- Designed for printing/PDF export
- Every page tells one complete story
- Executive-ready — no drill-through required

---

## Report Structure (Data Storytelling Framework)

| Page | Type | Content | Est. Length |
|------|------|---------|-------------|
| 1 | **Hook** | Headline finding + one-sentence impact | 1 page |
| 2 | **Context** | Revenue baseline, order volume, market scope | 1 page |
| 3 | **Rising Action** | RFM segment breakdown, the retention problem | 2 pages |
| 4 | **Climax** | Cohort analysis + At Risk opportunity sizing | 1-2 pages |
| 5 | **Resolution** | Recommendations with quantified impact | 1 page |
| 6 | **Call to Action** | Next steps, investment ask | 1 page |

**Total: 6-8 pages**

---

## Page-by-Page Design Specifications

### Page 1: The Hook (Headline)

**Goal:** Capture attention in 30 seconds. Lead with the problem, not the metrics.

**Layout:**
- Title: Large, bold. "3% Repeat Rate is Costing Olist R$X in Missed Revenue"
- Subtitle: One-sentence context — "Analysis of 96,000 orders reveals a structural retention problem"
- Key number callout: Large R$ figure for the opportunity
- Source note: Small text — "Based on analysis of 96,478 delivered orders, Sep 2016 – Oct 2018"

**Visuals:**
- Single KPI card with the opportunity number (highlighted in accent color)
- No charts on this page — just the headline and the number

**Data source:**
- Revenue total from fact_orders
- Repeat customer count (is_repeat_customer = true)
- At Risk segment count from customer_rfm view
- Estimated opportunity calculation (see SQL below)

---

### Page 2: Context (The Baseline)

**Goal:** Establish the scale. Show what we're working with.

**Layout:**
- Three KPI cards in a row: Total Revenue | Total Orders | AOV
- Monthly trend sparkline (6-month view)
- Geographic heatmap thumbnail (Brazil map with top states)

**KPI Cards:**
| KPI | Value | YoY/Trend |
|-----|-------|-----------|
| Total Revenue | R$13,279,837 | Stable |
| Delivered Orders | 96,478 | +4% |
| AOV | R$119.81 | +8% |

**Visuals:**
- Small multiple: Monthly revenue line (last 6 months)
- Small multiple: Top 5 states by customer count (horizontal bar)

**Data source:**
- fact_orders aggregated by month
- dim_customer joined for state breakdown

---

### Page 3: Rising Action — RFM Segments

**Goal:** Introduce the segmentation framework and show the problem distribution.

**Layout:**
- Left: Segment breakdown table (segment name, count, %, revenue)
- Right: Segment distribution visual (horizontal stacked bar or treemap)
- Bottom: Segment definitions callout box

**Table:**
| Segment | Customers | % of Base | Revenue | Action |
|---------|-----------|-----------|---------|--------|
| At Risk | 23,272 | 24.1% | R$X | Re-engagement campaign |
| Loyal Customers | 19,276 | 20.0% | R$X | Loyalty rewards |
| Recent Customers | 15,528 | 16.1% | R$X | Welcome series |
| Champions | 15,338 | 15.9% | R$X | VIP program |
| Lost | 15,320 | 15.9% | R$X | Win-back (low priority) |
| Promising | 7,744 | 8.0% | R$X | Nurture to loyal |

**Visuals:**
- Horizontal bar chart: Customers per segment (color-coded by action priority)
- Annotation: Circle/highlight the "At Risk" segment (24.1%)

**Data source:**
- customer_rfm view aggregated by segment

---

### Page 4: Rising Action — At Risk Deep Dive

**Goal:** Prove the problem is real. Show who these customers are.

**Layout:**
- At Risk segment summary (the headline number)
- Two column layout:
  - Left: Recency distribution (how long since last order)
  - Right: Monetary distribution (how much they spent)
- Bottom: "These customers bought once and never returned" callout

**Visuals:**
- Histogram: Days since last order for At Risk segment (range: 30-365+ days)
- Histogram: First order value distribution for At Risk segment

**Key insight text:**
> "At Risk customers last purchased 90+ days ago on average. They represent R$X in potential revenue if just 20% return for a second order."

**Data source:**
- customer_rfm filtered by segment = 'At Risk'
- fact_orders joined for order values

---

### Page 5: Climax — Cohort Retention Matrix

**Goal:** Show the retention problem visually. The heatmap tells the story.

**Layout:**
- Full-page cohort retention heatmap
- Row: Cohort month (YYYY-MM)
- Column: Month index (M0, M1, M2, ... M12)
- Cell: Retention % (color-coded: green > 1%, yellow 0.5-1%, red < 0.5%)

**Key callout:**
> "M1 retention averages just 0.5% — 99.5% of customers never come back after their first purchase."

**Visuals:**
- Heatmap matrix with conditional formatting
- Highlight the diagonal pattern (or lack thereof)

**Data source:**
- cohort_retention view (pivot to show months as columns)

---

### Page 6: Resolution — Recommendations

**Goal:** Translate insights into action. Quantify the opportunity.

**Layout:**
- Three recommendation cards (vertical stack)
- Each card: Target → Action → Expected Impact

**Recommendation 1: Retention Program**
| Field | Value |
|-------|-------|
| Target | At Risk segment (23,272 customers) |
| Action | Personalized email + 15% discount for second purchase |
| Expected Impact | 3% → 8% repeat rate = +R$645,000/year |

**Recommendation 2: Delivery Improvement**
| Field | Value |
|-------|-------|
| Target | Northern states (PB, AC, AP) |
| Action | Carrier coverage audit, regional fulfillment center |
| Expected Impact | Reduce late rate 7.78% → 5% = +R$200,000 (reduced churn) |

**Recommendation 3: Premium Market Expansion**
| Field | Value |
|-------|-------|
| Target | Paraíba (R$266.61 AOV) |
| Action | Targeted marketing, local seller recruitment |
| Expected Impact | +R$129,000 if orders grow from 517 → 1,000 |

**Total impact callout:**
> **Combined opportunity: R$800,000+ annually (6% growth on R$13.28M baseline)**

---

### Page 7: Call to Action

**Goal:** Clear next steps. What do we need to decide?

**Layout:**
- Summary of the problem (one paragraph)
- Summary of the opportunity (one paragraph)
- Three action items with owners
- Investment ask (if applicable)

**Text:**
> "The data is clear: Olist acquires customers effectively but fails to retain them. A targeted retention program targeting the 24% At Risk segment could add R$645,000 in annual revenue with minimal investment. The next step is a pilot campaign targeting 5,000 At Risk customers with personalized offers."

**Action items:**
1. [Marketing] Design re-engagement email sequence for At Risk segment — 2 weeks
2. [Operations] Investigate northern state delivery bottlenecks — 3 weeks
3. [Product] Build cross-sell recommendation engine for high-review categories — 4 weeks

---

## Visual Design Standards

### Color Palette
- **Primary:** #1E3A5F (Deep Navy — authority, trust)
- **Accent:** #E85D04 (Burnt Orange — action, urgency)
- **Background:** #FFFFFF (White)
- **Text:** #2D3436 (Dark Gray)
- **Success:** #2D6A4F (Forest Green)
- **Warning:** #F4A261 (Sandy Orange)
- **Danger:** #E63946 (Crimson Red)

### Chart Colors (segment-specific)
- Champions: #2D6A4F (green)
- Loyal Customers: #40916C (light green)
- Recent Customers: #52B788 (mint)
- Promising: #74C69D (pale green)
- At Risk: #E85D04 (orange — draw attention)
- Lost: #9D4EDD (purple)

### Typography
- **Headings:** Segoe UI Semibold, 24pt (page title), 16pt (section)
- **Body:** Segoe UI, 12pt
- **KPI numbers:** Segoe UI Bold, 28pt
- **Captions:** Segoe UI Italic, 10pt

### Layout Rules
- Margins: 0.5 inches all sides
- Page numbers: Bottom center, "Page X of Y"
- Header: Project title left, date right
- No gridlines on charts (cleaner for print)
- Data labels inside bars where possible, outside only if needed

---

## Export Settings

### PDF Export Configuration
- **File → Export → PDF**
- **Settings:**
  - Page size: A4 (210 × 297 mm) or Letter (8.5 × 11 in)
  - Orientation: Portrait
  - Quality: High (300 dpi)
  - Include all pages: Yes
  - Visualize data: Checked

### Page Setup in Power BI
- Turn off **view mode** visual elements (tooltips, hover states)
- Ensure all text is readable at 100% zoom (no 8pt font)
- Add page titles to every canvas page
- Use **Ctrl+Shift+P** to preview before export

### Alternative: Paginated Report Service
If Power BI Pro/Premium available:
- Use **Publish to Web** for embed
- Or export each page as PNG and compile in PDF manually

---

## Recommended Visuals Per Page

| Page | Primary Visual | Secondary Visual | Callout Style |
|------|---------------|------------------|---------------|
| 1 Hook | KPI Card (large number) | — | Text box, accent color |
| 2 Context | 3 KPI cards in row | Sparkline | — |
| 3 RFM | Horizontal bar (segments) | Table | Annotation box |
| 4 At Risk | Two histograms (recency, monetary) | — | Insight callout |
| 5 Cohort | Heatmap matrix | — | Arrow pointing to M1 |
| 6 Recs | 3 vertical cards | — | Number highlighted |
| 7 CTA | Summary text box | Checklist | — |

---

## Final Polish Checklist

- [ ] No chart titles inside visual (use page section titles instead)
- [ ] All numbers formatted: R$ with thousand separators, percentages with 1 decimal
- [ ] No "Power BI" watermark or default visuals showing
- [ ] Consistent color scheme across all pages
- [ ] Page numbers present and sequential
- [ ] Source note on Page 1 ("Data: Olist Brazilian E-Commerce, Sep 2016 – Oct 2018")
- [ ] Tested print preview — nothing cuts off at margins
- [ ] Executive summary readable in <60 seconds

---

## Source Files

- **Data warehouse:** PostgreSQL (localhost:5433, database: olist)
- **Schema:** Star schema with fact_orders, dim_customer, dim_product, dim_seller, dim_date
- **Analysis views:** customer_rfm, cohort_retention
- **SQL queries:** sql/powerbi_pdf_queries.sql
- **This guide:** docs/powerbi_pdf_guide.md