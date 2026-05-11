"""
Olist Sales Dashboard - Vizro Web Application
Run: python app.py
Open: http://localhost:8050
"""

import pandas as pd
import psycopg2
from vizro.models import Card, Graph, Page, Dashboard
from vizro.models.types import capture
from vizro import Vizro
import plotly.express as px
import plotly.graph_objects as go

DB_CONFIG = {
    "host": "localhost",
    "port": "5433",
    "dbname": "olist",
    "user": "postgres",
    "password": "admin"
}

def get_data(query):
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def load_all_data():
    """Load all data for the dashboard."""
    metrics = get_data("""
        SELECT
            ROUND(SUM(revenue), 2) AS total_revenue,
            COUNT(DISTINCT order_id) AS total_orders,
            ROUND(AVG(revenue), 2) AS aov
        FROM olist.fact_orders
    """)
    
    monthly = get_data("""
        SELECT
            DATE_TRUNC('month', order_date) AS month,
            COUNT(DISTINCT order_id) AS orders,
            ROUND(SUM(revenue), 2) AS revenue
        FROM olist.fact_orders
        GROUP BY DATE_TRUNC('month', order_date)
        ORDER BY month
    """)
    
    rfm = get_data("""
        SELECT
            segment,
            COUNT(*) AS customers,
            ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER() * 100, 1) AS pct
        FROM olist.customer_rfm
        GROUP BY segment
        ORDER BY customers DESC
    """)
    
    at_risk = get_data("""
        SELECT recency_bucket, customers FROM (
            SELECT
                CASE
                    WHEN recency_days BETWEEN 0 AND 30 THEN '0-30 days'
                    WHEN recency_days BETWEEN 31 AND 60 THEN '31-60 days'
                    WHEN recency_days BETWEEN 61 AND 90 THEN '61-90 days'
                    WHEN recency_days BETWEEN 91 AND 180 THEN '91-180 days'
                    ELSE '180+ days'
                END AS recency_bucket,
                CASE
                    WHEN recency_days BETWEEN 0 AND 30 THEN 1
                    WHEN recency_days BETWEEN 31 AND 60 THEN 2
                    WHEN recency_days BETWEEN 61 AND 90 THEN 3
                    WHEN recency_days BETWEEN 91 AND 180 THEN 4
                    ELSE 5
                END AS sort_order,
                COUNT(*) AS customers
            FROM olist.customer_rfm
            WHERE segment = 'At Risk'
            GROUP BY 1, 2
        ) t
        ORDER BY sort_order
    """)
    
    cohort = get_data("""
        SELECT
            TO_CHAR(cohort_month, 'YYYY-MM') AS cohort_month,
            month_index,
            cohort_size,
            ROUND(retention_rate * 100, 2) AS retention_pct
        FROM olist.cohort_retention
        WHERE cohort_size > 10
        ORDER BY cohort_month, month_index
    """)
    
    states = get_data("""
        SELECT
            dc.customer_state AS state,
            COUNT(DISTINCT dc.customer_id) AS customers,
            ROUND(SUM(fo.revenue), 2) AS revenue
        FROM olist.fact_orders fo
        JOIN olist.dim_customer dc ON fo.customer_id = dc.customer_id
        GROUP BY dc.customer_state
        ORDER BY customers DESC
        LIMIT 10
    """)
    
    return {
        "metrics": metrics,
        "monthly": monthly,
        "rfm": rfm,
        "at_risk": at_risk,
        "cohort": cohort,
        "states": states
    }

print("Loading data...")
DATA = load_all_data()
print("Data loaded successfully!")

SEGMENT_COLORS = {
    "At Risk": "#E85D04",
    "Loyal Customers": "#40916C",
    "Recent Customers": "#52B788",
    "Champions": "#2D6A4F",
    "Lost": "#9D4EDD",
    "Promising": "#74C69D"
}

monthly_data = DATA["monthly"].copy()
monthly_data["month_str"] = pd.to_datetime(monthly_data["month"]).dt.strftime("%Y-%m")

states_data = DATA["states"].head(8)
rfm_data = DATA["rfm"]
at_risk_data = DATA["at_risk"]
cohort_data = DATA["cohort"]
cohort_m1 = cohort_data[cohort_data["month_index"] > 0]
metrics_data = DATA["metrics"]

@capture("graph")
def revenue_chart(data_frame):
    return px.line(
        data_frame, 
        x="month_str", 
        y="revenue",
        title="Monthly Revenue Trend",
        markers=True
    ).update_layout(template="plotly_white", xaxis_title="Month", yaxis_title="Revenue (R$)")

@capture("graph")
def states_chart(data_frame):
    return px.bar(
        data_frame,
        x="state",
        y="customers",
        title="Top States by Customer Count"
    ).update_layout(template="plotly_white")

@capture("graph")
def rfm_chart(data_frame):
    return px.bar(
        data_frame,
        x="segment",
        y="customers",
        color="segment",
        title="Customer Segments by RFM Analysis",
        color_discrete_map=SEGMENT_COLORS
    ).update_layout(template="plotly_white", showlegend=False)

@capture("graph")
def cohort_chart(data_frame):
    return px.scatter(
        data_frame,
        x="cohort_month",
        y="retention_pct",
        size="cohort_size",
        color="month_index",
        title="Retention Rate by Cohort (bubble size = cohort size)",
        labels={"cohort_month": "Cohort Month", "retention_pct": "Retention %"}
    ).update_layout(template="plotly_white")

@capture("graph")
def at_risk_chart(data_frame):
    return px.bar(
        data_frame,
        x="recency_bucket",
        y="customers",
        title="At Risk Customers: Days Since Last Order",
        color="customers",
        color_continuous_scale="Reds"
    ).update_layout(template="plotly_white")

def create_executive_page():
    """Executive Overview Page."""
    kpi_card = Card(text=f"""
## 📊 Olist Sales Performance

### Revenue
**R${metrics_data.iloc[0]['total_revenue']:,.2f}**

### Orders
**{metrics_data.iloc[0]['total_orders']:,}**

### Average Order Value
**R${metrics_data.iloc[0]['aov']:,.2f}**

---

### The Problem
- **At Risk Customers:** 23,272 (24.1%)
- **Repeat Rate:** ~3%
- **M1 Retention:** ~0.5%

*Retention is the biggest lever for revenue growth.*
""")
    
    return Page(
        title="Executive Overview",
        components=[kpi_card, Graph(figure=revenue_chart(data_frame=monthly_data)), Graph(figure=states_chart(data_frame=states_data))]
    )

def create_rfm_page():
    """RFM Segmentation Page."""
    insight_card = Card(text="""
## 🎯 What Each Segment Means

### 🔴 At Risk (24.1% - 23,272 customers)
Haven't returned in 90+ days. Priority target for re-engagement campaigns.

### 🟢 Champions (15.9% - 15,338 customers)
High-value repeat buyers. Protect and offer VIP benefits.

### 🟢 Loyal Customers (20.0% - 19,276 customers)
Consistent purchasers. Good candidates for loyalty programs.

### 🟡 Recent Customers (16.1% - 15,528 customers)
Just made first purchase. Nurture with welcome series.

### 🟣 Lost (15.9% - 15,320 customers)
Haven't purchased in a long time. Low priority for reactivation.

### 🟢 Promising (8.0% - 7,744 customers)
Show potential. Nurture to become loyal customers.

---

## The Opportunity
**24% of customers are At Risk** — targeting just 20% of them could generate R$500K+ in incremental revenue.
""")
    
    return Page(
        title="RFM Segmentation",
        components=[Graph(figure=rfm_chart(data_frame=rfm_data)), insight_card]
    )

def create_cohort_page():
    """Cohort Retention Page."""
    insight_card = Card(text="""
## 📉 The Churn Crisis

### M1 Retention: ~0.5%
Only 0.5% of customers return for a second purchase after their first month.

### What This Means
- **99.5% of customers never come back**
- This explains the overall ~3% repeat rate
- Pattern is consistent across ALL monthly cohorts

### The Business Impact
If Olist improves M1 retention from 0.5% to just 3%:
- ~4,700 additional repeat customers per year
- ~R$560,000 in incremental revenue (at R$120 AOV)

### Recommended Actions
1. **Welcome email sequence** within first 7 days
2. **Post-purchase upsell** at checkout
3. **Loyalty points** for second purchase
4. **Personalized product recommendations**
""")
    
    return Page(
        title="Cohort Retention",
        components=[Graph(figure=cohort_chart(data_frame=cohort_m1)), insight_card]
    )

def create_at_risk_page():
    """At Risk Deep Dive Page."""
    opportunity_card = Card(text="""
## 🎯 At Risk Customer Opportunity

### The Numbers
- **Total At Risk:** 23,272 customers
- **Avg days since last order:** 120+ days
- **Potential revenue:** R$2.8M (first order value)

### If Just 20% Return...
- **4,654 customers** make a second purchase
- **At R$120 AOV** = **R$558,480 incremental revenue**

### Recommended Actions

**1. Email Re-engagement Campaign**
- Send personalized "We miss you" email
- Include 15% discount code for second order

**2. Abandoned Cart Recovery**
- If they added items but didn't purchase
- Reminder sequence: 1hr, 24hr, 72hr

**3. Loyalty Program Enrollment**
- Offer points on first purchase
- Double points on second order

**4. Product Recommendations**
- Show items similar to their first purchase
- "Customers who bought X also bought Y"

---

### Priority
Focus on customers who last purchased 60-90 days ago — they're most likely to respond.
""")
    
    return Page(
        title="At Risk Deep Dive",
        components=[Graph(figure=at_risk_chart(data_frame=at_risk_data)), opportunity_card]
    )

dashboard = Dashboard(
    title="Olist Sales & Customer Analytics",
    pages=[
        create_executive_page(),
        create_rfm_page(),
        create_cohort_page(),
        create_at_risk_page()
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(port=8050)