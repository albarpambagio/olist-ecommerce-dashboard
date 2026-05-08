import psycopg2

DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

def create_kpi_views():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("=" * 50)
    print("PHASE 4: CORE KPI DESIGN")
    print("=" * 50)
    
    # Drop existing KPI views
    print("\n1. Cleaning up existing KPI views...")
    cur.execute("DROP VIEW IF EXISTS olist.kpi_revenue_overview CASCADE")
    cur.execute("DROP VIEW IF EXISTS olist.kpi_delivery_performance CASCADE")
    cur.execute("DROP VIEW IF EXISTS olist.kpi_customer_metrics CASCADE")
    cur.execute("DROP VIEW IF EXISTS olist.kpi_seller_performance CASCADE")
    conn.commit()
    print("   Done")
    
    # KPI View 1: Revenue Overview
    print("\n2. Creating KPI: Revenue Overview...")
    cur.execute("""
        CREATE VIEW olist.kpi_revenue_overview AS
        SELECT 
            DATE_TRUNC('month', order_date) AS month,
            COUNT(DISTINCT order_id) AS order_volume,
            SUM(revenue) AS revenue,
            ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS aov,
            SUM(freight_value) AS total_freight,
            ROUND(SUM(freight_value)::NUMERIC / SUM(revenue + freight_value) * 100, 2) AS freight_pct
        FROM olist.fact_orders
        GROUP BY 1
        ORDER BY 1
    """)
    conn.commit()
    print("   kpi_revenue_overview created")
    
    # KPI View 2: Delivery Performance
    print("\n3. Creating KPI: Delivery Performance...")
    cur.execute("""
        CREATE VIEW olist.kpi_delivery_performance AS
        SELECT 
            customer_state,
            COUNT(*) AS total_orders,
            SUM(CASE WHEN is_late = 1 THEN 1 ELSE 0 END) AS late_orders,
            ROUND(SUM(CASE WHEN is_late = 1 THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) AS late_rate_pct,
            ROUND(AVG(actual_delivery_days), 1) AS avg_delivery_days,
            ROUND(AVG(CASE WHEN is_late = 0 THEN actual_delivery_days END), 1) AS avg_on_time_days
        FROM olist.fact_orders fo
        JOIN olist.dim_customer dc ON fo.customer_id = dc.customer_id
        WHERE actual_delivery_days IS NOT NULL
        GROUP BY 1
        ORDER BY 2 DESC
    """)
    conn.commit()
    print("   kpi_delivery_performance created")
    
    # KPI View 3: Customer Metrics
    print("\n4. Creating KPI: Customer Metrics...")
    cur.execute("""
        CREATE VIEW olist.kpi_customer_metrics AS
        SELECT 
            dc.customer_state,
            dc.region,
            COUNT(DISTINCT fo.customer_id) AS unique_customers,
            COUNT(DISTINCT fo.order_id) AS total_orders,
            ROUND(SUM(fo.revenue)::NUMERIC / COUNT(DISTINCT fo.order_id), 2) AS aov,
            ROUND(AVG(fr.review_score), 2) AS avg_review_score,
            COUNT(DISTINCT CASE WHEN fo.is_repeat_customer = 1 THEN fo.customer_id END) AS repeat_customers,
            ROUND(COUNT(DISTINCT CASE WHEN fo.is_repeat_customer = 1 THEN fo.customer_id END)::NUMERIC / COUNT(DISTINCT fo.customer_id) * 100, 2) AS repeat_rate_pct
        FROM olist.fact_orders fo
        JOIN olist.dim_customer dc ON fo.customer_id = dc.customer_id
        LEFT JOIN olist.fact_orders fr ON fo.order_id = fr.order_id
        GROUP BY 1, 2
        ORDER BY 3 DESC
    """)
    conn.commit()
    print("   kpi_customer_metrics created")
    
    # KPI View 4: Seller Performance
    print("\n5. Creating KPI: Seller Performance...")
    cur.execute("""
        CREATE VIEW olist.kpi_seller_performance AS
        SELECT 
            ds.seller_state,
            ds.region,
            COUNT(DISTINCT fo.seller_id) AS unique_sellers,
            COUNT(DISTINCT fo.order_id) AS total_orders,
            ROUND(SUM(fo.revenue)::NUMERIC / COUNT(DISTINCT fo.seller_id), 2) AS revenue_per_seller,
            ROUND(AVG(fo.review_score), 2) AS avg_review_score,
            SUM(CASE WHEN fo.is_late = 1 THEN 1 ELSE 0 END) AS late_orders,
            ROUND(SUM(CASE WHEN fo.is_late = 1 THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) AS seller_late_rate_pct
        FROM olist.fact_orders fo
        JOIN olist.dim_seller ds ON fo.seller_id = ds.seller_id
        GROUP BY 1, 2
        ORDER BY 3 DESC
    """)
    conn.commit()
    print("   kpi_seller_performance created")
    
    # KPI View 5: Sales Mix (Absolute + % of Total by Category)
    print("\n6. Creating KPI: Sales Mix...")
    cur.execute("""
        CREATE VIEW olist.kpi_sales_mix AS
        WITH category_revenue AS (
            SELECT 
                DATE_TRUNC('month', fo.order_date) AS month,
                dp.category_en,
                SUM(fo.revenue) AS category_revenue
            FROM olist.fact_orders fo
            JOIN olist.dim_product dp USING (product_id)
            GROUP BY 1, 2
        ),
        total_revenue AS (
            SELECT 
                month,
                SUM(category_revenue) AS total_revenue
            FROM category_revenue
            GROUP BY 1
        )
        SELECT 
            cr.month,
            cr.category_en,
            cr.category_revenue,
            tr.total_revenue,
            ROUND(cr.category_revenue::NUMERIC / tr.total_revenue * 100, 2) AS pct_of_total
        FROM category_revenue cr
        JOIN total_revenue tr USING (month)
        ORDER BY cr.month, cr.category_revenue DESC
    """)
    conn.commit()
    print("   kpi_sales_mix created")
    
    cur.close()
    conn.close()
 
def verify_kpis():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("\n=== KPI Verification ===")
    
    # Overall KPIs
    print("\n1. Overall KPIs:")
    cur.execute("""
        SELECT 
            COUNT(DISTINCT order_id) AS orders,
            ROUND(SUM(revenue)::NUMERIC, 2) AS revenue,
            ROUND(SUM(revenue)::NUMERIC / COUNT(DISTINCT order_id), 2) AS aov,
            ROUND(AVG(review_score), 2) AS avg_review,
            ROUND(SUM(CASE WHEN is_late = 1 THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) AS late_rate_pct
        FROM olist.fact_orders
        WHERE review_score IS NOT NULL
    """)
    row = cur.fetchone()
    print(f"   Orders: {row[0]:,}")
    print(f"   Revenue: ${row[1]:,.2f}")
    print(f"   AOV: ${row[2]:.2f}")
    print(f"   Avg Review: {row[3]}")
    print(f"   Late Rate: {row[4]}%")
    
    # Monthly trend
    print("\n2. Monthly Revenue (last 6 months):")
    cur.execute("""
        SELECT 
            TO_CHAR(month, 'YYYY-MM') AS ym,
            order_volume,
            revenue,
            aov
        FROM olist.kpi_revenue_overview
        ORDER BY month DESC
        LIMIT 6
    """)
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]:,} orders, ${row[2]:,.2f} revenue, AOV: ${row[3]:.2f}")
    
    # Sales Mix verification
    print("\n3. Sales Mix (sample - top categories in recent month):")
    cur.execute("""
        SELECT 
            category_en,
            ROUND(category_revenue::NUMERIC, 2) AS revenue,
            pct_of_total
        FROM olist.kpi_sales_mix
        WHERE month = (SELECT MAX(month) FROM olist.kpi_sales_mix)
        ORDER BY category_revenue DESC
        LIMIT 5
    """)
    for row in cur.fetchall():
        print(f"   {row[0]}: ${row[1]:,.2f} ({row[2]}% of total)")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    create_kpi_views()
    verify_kpis()
    print("\n=== Phase 4 Complete ===")