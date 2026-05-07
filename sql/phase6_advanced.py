import psycopg2

DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

def create_advanced_features():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("=" * 50)
    print("PHASE 6: ADVANCED FEATURES")
    print("=" * 50)
    
    # 6.1 Customer Segmentation (RFM)
    print("\n--- 6.1 RFM Customer Segmentation ---")
    
    # Drop existing view
    cur.execute("DROP VIEW IF EXISTS olist.customer_rfm CASCADE")
    conn.commit()
    
    # Create RFM view
    print("Creating RFM segmentation...")
    cur.execute("""
        CREATE VIEW olist.customer_rfm AS
        WITH rfm_base AS (
            SELECT
                customer_id,
                MAX(order_date) AS last_order_date,
                COUNT(DISTINCT order_id) AS frequency,
                SUM(revenue) AS monetary
            FROM olist.fact_orders
            GROUP BY customer_id
        ),
        rfm_scored AS (
            SELECT *,
                CURRENT_DATE - last_order_date AS recency_days,
                NTILE(5) OVER (ORDER BY CURRENT_DATE - last_order_date DESC) AS r_score,
                NTILE(5) OVER (ORDER BY frequency) AS f_score,
                NTILE(5) OVER (ORDER BY monetary) AS m_score
            FROM rfm_base
        )
        SELECT 
            customer_id,
            last_order_date,
            recency_days,
            frequency,
            monetary,
            r_score,
            f_score,
            m_score,
            CASE
                WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
                WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
                WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent Customers'
                WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
                WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
                ELSE 'Promising'
            END AS segment
        FROM rfm_scored
    """)
    conn.commit()
    print("   customer_rfm view created")
    
    # Show segment distribution
    print("\n   RFM Segment Distribution:")
    cur.execute("""
        SELECT 
            segment,
            COUNT(*) AS customers,
            ROUND(COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM olist.customer_rfm) * 100, 1) AS pct
        FROM olist.customer_rfm
        GROUP BY 1
        ORDER BY 2 DESC
    """)
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]:,} ({row[2]}%)")
    
    # 6.2 Cohort Retention Analysis
    print("\n--- 6.2 Cohort Retention Analysis ---")
    
    # Drop existing view
    cur.execute("DROP VIEW IF EXISTS olist.cohort_retention CASCADE")
    conn.commit()
    
    # Create cohort retention view
    print("Creating cohort retention analysis...")
    cur.execute("""
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
            FROM first_order 
            GROUP BY 1
        )
        SELECT
            om.cohort_month,
            EXTRACT(MONTH FROM AGE(om.order_month, om.cohort_month))::INT AS month_index,
            COUNT(DISTINCT om.customer_id) AS retained,
            cs.cohort_size,
            ROUND(COUNT(DISTINCT om.customer_id)::NUMERIC / cs.cohort_size, 3) AS retention_rate
        FROM order_months om
        JOIN cohort_sizes cs USING (cohort_month)
        GROUP BY 1, 2, cs.cohort_size
        ORDER BY 1, 2
    """)
    conn.commit()
    print("   cohort_retention view created")
    
    # Show sample retention data
    print("\n   Sample Retention Data (first 5 cohorts, first 3 months):")
    cur.execute("""
        SELECT cohort_month, month_index, retained, cohort_size, retention_rate
        FROM olist.cohort_retention
        WHERE month_index <= 2
        ORDER BY cohort_month, month_index
        LIMIT 15
    """)
    for row in cur.fetchall():
        print(f"   {row[0].strftime('%Y-%m')}: Month {row[1]}, Retained: {row[2]:,}/{row[3]:,} ({row[4]*100:.1f}%)")
    
    cur.close()
    conn.close()

def create_drillthrough_views():
    """Create views for drill-through pages"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("\n--- 6.3 Drill-Through Views ---")
    
    # Seller detail view
    print("Creating seller_detail view...")
    cur.execute("DROP VIEW IF EXISTS olist.seller_detail CASCADE")
    cur.execute("""
        CREATE VIEW olist.seller_detail AS
        SELECT 
            fo.seller_id,
            ds.seller_state,
            ds.region,
            COUNT(DISTINCT fo.order_id) AS total_orders,
            SUM(fo.revenue) AS total_revenue,
            ROUND(AVG(fo.review_score), 2) AS avg_review_score,
            ROUND(AVG(fo.actual_delivery_days), 1) AS avg_delivery_days,
            SUM(CASE WHEN fo.is_late = 1 THEN 1 ELSE 0 END) AS late_orders,
            ROUND(SUM(CASE WHEN fo.is_late = 1 THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 1) AS late_rate_pct,
            COUNT(DISTINCT fo.product_id) AS unique_products
        FROM olist.fact_orders fo
        JOIN olist.dim_seller ds ON fo.seller_id = ds.seller_id
        GROUP BY 1, 2, 3
    """)
    conn.commit()
    print("   seller_detail view created")
    
    # Product detail view (for potential product drill-through)
    print("Creating product_detail view...")
    cur.execute("DROP VIEW IF EXISTS olist.product_detail CASCADE")
    cur.execute("""
        CREATE VIEW olist.product_detail AS
        SELECT 
            fo.product_id,
            dp.category_en,
            dp.category_pt,
            COUNT(DISTINCT fo.order_id) AS total_orders,
            SUM(fo.revenue) AS total_revenue,
            ROUND(AVG(fo.review_score), 2) AS avg_review_score,
            ROUND(AVG(fo.freight_value), 2) AS avg_freight,
            COUNT(DISTINCT fo.seller_id) AS unique_sellers
        FROM olist.fact_orders fo
        JOIN olist.dim_product dp ON fo.product_id = dp.product_id
        GROUP BY 1, 2, 3
    """)
    conn.commit()
    print("   product_detail view created")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    create_advanced_features()
    create_drillthrough_views()
    print("\n=== Phase 6 Complete ===")