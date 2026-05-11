import vizro
import vizro.plotly as vp
import vizro.dashboard as vd
import pandas as pd
import psycopg2
from datetime import datetime

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
    # Main metrics
    metrics = get_data("""
        SELECT
            ROUND(SUM(revenue), 2) AS total_revenue,
            COUNT(DISTINCT order_id) AS total_orders,
            ROUND(AVG(revenue), 2) AS aov
        FROM olist.fact_orders
    """)
    
    # Monthly trend
    monthly = get_data("""
        SELECT
            DATE_TRUNC('month', order_date) AS month,
            COUNT(DISTINCT order_id) AS orders,
            ROUND(SUM(revenue), 2) AS revenue
        FROM olist.fact_orders
        GROUP BY DATE_TRUNC('month', order_date)
        ORDER BY month
    """)
    
    # RFM segments
    rfm = get_data("""
        SELECT
            segment,
            COUNT(*) AS customers,
            ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER() * 100, 1) AS pct
        FROM olist.customer_rfm
        GROUP BY segment
        ORDER BY customers DESC
    """)
    
    # At Risk details
    at_risk = get_data("""
        SELECT
            CASE
                WHEN recency_days BETWEEN 0 AND 30 THEN '0-30 days'
                WHEN recency_days BETWEEN 31 AND 60 THEN '31-60 days'
                WHEN recency_days BETWEEN 61 AND 90 THEN '61-90 days'
                WHEN recency_days BETWEEN 91 AND 180 THEN '91-180 days'
                ELSE '180+ days'
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
                ELSE 5
            END
    """)
    
    # Cohort retention matrix
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
    
    # Top states
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

data = load_all_data()

# Dashboard definition
dashboard = vd.Dashboard(
    title="Olist Sales & Customer Analytics",
    pages=[
        vd.Page(
            name="Executive Overview",
            components=[
                vp.Card(
                    title="Key Metrics",
                    text=f"""
                    **Total Revenue:** R${data['metrics'].iloc[0]['total_revenue']:,.2f}
                    
                    **Total Orders:** {data['metrics'].iloc[0]['total_orders']:,}
                    
                    **Average Order Value:** R${data['metrics'].iloc[0]['aov']:,.2f}
                    
                    **At Risk Customers:** 23,272 (24.1%)
                    
                    **Repeat Rate:** ~3%
                    """
                ),
                vp.Graph(
                    figure=vp.bar(
                        data=data["monthly"],
                        x="month",
                        y="revenue",
                        title="Monthly Revenue Trend"
                    ).update_layout(template="plotly_white")
                ),
                vp.Graph(
                    figure=vp.bar(
                        data=data["states"].head(8),
                        x="state",
                        y="customers",
                        title="Top States by Customer Count"
                    ).update_layout(template="plotly_white")
                )
            ]
        ),
        vd.Page(
            name="RFM Segmentation",
            components=[
                vp.Graph(
                    figure=vp.bar(
                        data=data["rfm"],
                        x="segment",
                        y="customers",
                        color="segment",
                        title="Customer Segments by RFM Analysis"
                    ).update_layout(template="plotly_white", showlegend=False)
                ),
                vp.Card(
                    title="Segment Insights",
                    text="""
                    **At Risk (24.1%):** 23,272 customers who haven't returned. Priority for re-engagement campaigns.
                    
                    **Champions + Loyal (35.9%):** High-value customers who return. Protect and grow.
                    
                    **Lost (15.9%):** Haven't purchased in a long time. Low priority for reactivation.
                    """
                )
            ]
        ),
        vd.Page(
            name="Cohort Retention",
            components=[
                vp.Card(
                    title="The Problem",
                    text="""
                    **M1 Retention: ~0.5%**
                    
                    Only 0.5% of customers return for a second purchase after their first month.
                    This explains the 3% overall repeat rate.
                    
                    The cohort matrix shows this pattern is consistent across all monthly cohorts.
                    """
                ),
                vp.Graph(
                    figure=vp.scatter(
                        data=data["cohort"][data["cohort"]["month_index"] > 0],
                        x="cohort_month",
                        y="retention_pct",
                        size="cohort_size",
                        color="month_index",
                        title="Retention Rate by Cohort Month (bubble size = cohort size)"
                    ).update_layout(template="plotly_white")
                )
            ]
        ),
        vd.Page(
            name="At Risk Deep Dive",
            components=[
                vp.Graph(
                    figure=vp.bar(
                        data=data["at_risk"],
                        x="recency_bucket",
                        y="customers",
                        title="At Risk Customers: Days Since Last Order"
                    ).update_layout(template="plotly_white")
                ),
                vp.Card(
                    title="The Opportunity",
                    text="""
                    **23,272 At Risk customers** represent the biggest revenue opportunity.
                    
                    If just 20% (4,654 customers) return for a second order:
                    - At R$120 AOV = R$558,480 incremental revenue
                    
                    Recommended actions:
                    - Personalized email campaigns
                    - 15% discount for second purchase
                    - Loyalty program enrollment
                    """
                )
            ]
        )
    ]
)

if __name__ == "__main__":
    vizro.run(dashboard, port=8050)