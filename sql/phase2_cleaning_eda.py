import psycopg2

DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

def data_cleaning():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("=" * 50)
    print("PHASE 2: DATA CLEANING & EDA")
    print("=" * 50)
    
    # 2.1 Data Quality Fixes
    print("\n--- DATA QUALITY FIXES ---")
    
    # Add is_valid_order column
    print("\n1. Adding is_valid_order flag...")
    cur.execute("""
        ALTER TABLE olist.orders 
        ADD COLUMN IF NOT EXISTS is_valid_order BOOLEAN
    """)
    cur.execute("""
        UPDATE olist.orders
        SET is_valid_order = (order_status NOT IN ('cancelled', 'unavailable'))
        WHERE is_valid_order IS NULL
    """)
    conn.commit()
    print("   Done")
    
    # Create geo_deduped view
    print("\n2. Creating geo_deduped view...")
    cur.execute("DROP VIEW IF EXISTS olist.geo_deduped")
    cur.execute("""
        CREATE VIEW olist.geo_deduped AS
        SELECT zip_code_prefix,
               AVG(geolocation_lat) AS lat,
               AVG(geolocation_lng) AS lng,
               MAX(geolocation_city) AS city,
               MAX(geolocation_state) AS state
        FROM olist.geolocation
        GROUP BY zip_code_prefix
    """)
    conn.commit()
    print("   Done")
    
    # 2.2 Key EDA Questions
    print("\n--- KEY EDA QUESTIONS ---")
    
    # 1. What % of orders are delivered on time vs. late?
    print("\n1. Delivery Performance:")
    cur.execute("""
        SELECT 
            COUNT(*) as total_orders,
            SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END) as late_deliveries,
            ROUND(SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) as late_pct
        FROM olist.orders
        WHERE order_status = 'delivered' 
          AND order_delivered_customer_date IS NOT NULL
          AND order_estimated_delivery_date IS NOT NULL
    """)
    row = cur.fetchone()
    print(f"   Total delivered: {row[0]:,}")
    print(f"   Late deliveries: {row[1]:,}")
    print(f"   Late delivery rate: {row[2]}%")
    
    # 2. Which product category has the highest average review score?
    print("\n2. Top Categories by Review Score:")
    cur.execute("""
        SELECT 
            COALESCE(t.category_en, p.product_category_name) as category,
            ROUND(AVG(r.review_score)::NUMERIC, 2) as avg_score,
            COUNT(*) as orders
        FROM olist.order_items oi
        JOIN olist.order_reviews r ON oi.order_id = r.order_id
        JOIN olist.products p ON oi.product_id = p.product_id
        LEFT JOIN olist.category_translation t ON p.product_category_name = t.category_pt
        GROUP BY 1
        HAVING COUNT(*) > 100
        ORDER BY 2 DESC
        LIMIT 5
    """)
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]} (n={row[2]:,})")
    
    # 3. Which state has the highest AOV?
    print("\n3. Top States by AOV:")
    cur.execute("""
        SELECT 
            c.customer_state,
            ROUND(SUM(oi.price + oi.freight_value)::NUMERIC / COUNT(DISTINCT o.order_id), 2) as aov,
            COUNT(DISTINCT o.order_id) as orders
        FROM olist.orders o
        JOIN olist.order_items oi ON o.order_id = oi.order_id
        JOIN olist.customers c ON o.customer_id = c.customer_id
        WHERE o.order_status = 'delivered'
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 5
    """)
    for row in cur.fetchall():
        print(f"   {row[0]}: ${row[1]} (n={row[2]:,})")
    
    # 4. What payment method is most common?
    print("\n4. Payment Method Distribution:")
    cur.execute("""
        SELECT 
            payment_type,
            COUNT(*) as cnt,
            ROUND(COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM olist.order_payments) * 100, 1) as pct
        FROM olist.order_payments
        WHERE payment_sequential = 1
        GROUP BY 1
        ORDER BY 2 DESC
    """)
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]:,} ({row[2]}%)")
    
    # 5. Repeat customer rate
    print("\n5. Repeat Customer Rate:")
    cur.execute("""
        SELECT 
            COUNT(*) as total_customers,
            SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) as repeat_customers,
            ROUND(SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) as repeat_rate
        FROM (
            SELECT customer_id, COUNT(*) as order_count
            FROM olist.orders
            WHERE order_status = 'delivered'
            GROUP BY customer_id
        ) t
    """)
    row = cur.fetchone()
    print(f"   Total customers: {row[0]:,}")
    print(f"   Repeat customers: {row[1]:,}")
    print(f"   Repeat rate: {row[2]}%")
    
    # Delivery time stats
    print("\n6. Delivery Time Stats:")
    cur.execute("""
        SELECT 
            AVG(EXTRACT(DAY FROM order_delivered_customer_date - order_purchase_timestamp)) as avg_days,
            MIN(EXTRACT(DAY FROM order_delivered_customer_date - order_purchase_timestamp)) as min_days,
            MAX(EXTRACT(DAY FROM order_delivered_customer_date - order_purchase_timestamp)) as max_days
        FROM olist.orders
        WHERE order_status = 'delivered'
          AND order_delivered_customer_date IS NOT NULL
    """)
    row = cur.fetchone()
    print(f"   Average: {row[0]:.1f} days")
    print(f"   Min: {row[1]:.0f} days")
    print(f"   Max: {row[2]:.0f} days")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    data_cleaning()