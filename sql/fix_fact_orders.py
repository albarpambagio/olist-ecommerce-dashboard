import psycopg2

DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

def fix_fact_orders():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("=== Fixing fact_orders view ===\n")
    
    # Drop dependent views first
    print("1. Dropping dependent views...")
    cur.execute("DROP VIEW IF EXISTS olist.cohort_retention CASCADE")
    cur.execute("DROP VIEW IF EXISTS olist.customer_rfm CASCADE")
    cur.execute("DROP VIEW IF EXISTS olist.kpi_customer_metrics CASCADE")
    conn.commit()
    
    # Rebuild fact_orders with customer_unique_id
    print("2. Rebuilding fact_orders with customer_unique_id...")
    cur.execute("DROP VIEW IF EXISTS olist.fact_orders CASCADE")
    cur.execute("""
        CREATE VIEW olist.fact_orders AS
        SELECT
            o.order_id,
            o.customer_id,
            c.customer_unique_id,
            oi.product_id,
            oi.seller_id,
            o.order_purchase_timestamp::DATE AS order_date,
            oi.price AS revenue,
            oi.freight_value,
            op.payment_type,
            op.payment_value AS payment_value,
            r.review_score,
            EXTRACT(DAY FROM (
                o.order_delivered_customer_date - o.order_purchase_timestamp
            ))::INT AS actual_delivery_days,
            EXTRACT(DAY FROM (
                o.order_estimated_delivery_date - o.order_purchase_timestamp
            ))::INT AS estimated_delivery_days,
            CASE
                WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1
                ELSE 0
            END AS is_late,
            CASE WHEN rc.order_count > 1 THEN 1 ELSE 0 END AS is_repeat_customer
        FROM olist.orders o
        JOIN olist.customers c ON o.customer_id = c.customer_id
        JOIN olist.order_items oi ON o.order_id = oi.order_id
        LEFT JOIN olist.order_payments op ON o.order_id = op.order_id AND op.payment_sequential = 1
        LEFT JOIN olist.order_reviews r ON o.order_id = r.order_id
        LEFT JOIN (
            SELECT customer_unique_id, COUNT(DISTINCT o2.order_id) AS order_count
            FROM olist.orders o2
            JOIN olist.customers c2 ON o2.customer_id = c2.customer_id
            WHERE o2.order_status = 'delivered'
            GROUP BY customer_unique_id
        ) rc ON c.customer_unique_id = rc.customer_unique_id
        WHERE o.is_valid_order = TRUE
          AND o.order_status = 'delivered'
    """)
    conn.commit()
    print("   fact_orders updated with customer_unique_id!")
    
    # Verify
    print("\n3. Verifying repeat customers in fact_orders...")
    cur.execute("""
        SELECT 
            COUNT(DISTINCT order_id) AS total_orders,
            COUNT(DISTINCT customer_unique_id) AS unique_customers,
            SUM(CASE WHEN is_repeat_customer = 1 THEN 1 ELSE 0 END) AS repeat_customers
        FROM olist.fact_orders
    """)
    row = cur.fetchone()
    print(f"   Total orders: {row[0]:,}")
    print(f"   Unique customers (by unique_id): {row[1]:,}")
    print(f"   Repeat customers: {row[2]:,}")
    
    # Rebuild cohort_retention with customer_unique_id
    print("\n4. Rebuilding cohort_retention view...")
    cur.execute("DROP VIEW IF EXISTS olist.cohort_retention CASCADE")
    cur.execute("""
        CREATE VIEW olist.cohort_retention AS
        WITH first_order AS (
            SELECT 
                customer_unique_id,
                MIN(DATE_TRUNC('month', order_date)) AS cohort_month
            FROM olist.fact_orders
            GROUP BY customer_unique_id
        ),
        all_orders AS (
            SELECT 
                fo.customer_unique_id,
                fo.cohort_month,
                DATE_TRUNC('month', f.order_date) AS order_month
            FROM first_order fo
            JOIN olist.fact_orders f ON fo.customer_unique_id = f.customer_unique_id
        ),
        month_diff AS (
            SELECT 
                customer_unique_id,
                cohort_month,
                order_month,
                (EXTRACT(YEAR FROM order_month) - EXTRACT(YEAR FROM cohort_month)) * 12 +
                (EXTRACT(MONTH FROM order_month) - EXTRACT(MONTH FROM cohort_month)) AS month_index
            FROM all_orders
        ),
        cohort_sizes AS (
            SELECT cohort_month, COUNT(DISTINCT customer_unique_id) AS cohort_size
            FROM first_order
            GROUP BY 1
        )
        SELECT
            cohort_month,
            month_index,
            COUNT(DISTINCT customer_unique_id) AS retained,
            MAX(cohort_size) AS cohort_size,
            ROUND(COUNT(DISTINCT customer_unique_id)::NUMERIC / MAX(cohort_size), 3) AS retention_rate
        FROM month_diff md
        JOIN cohort_sizes cs USING (cohort_month)
        WHERE month_index >= 0
        GROUP BY cohort_month, month_index
        ORDER BY cohort_month, month_index
    """)
    conn.commit()
    print("   cohort_retention rebuilt!")
    
    # Verify cohort data
    print("\n5. Verifying cohort data (M0-M2)...")
    cur.execute("""
        SELECT 
            TO_CHAR(cohort_month, 'YYYY-MM') AS cm,
            month_index,
            retained,
            cohort_size,
            ROUND(retention_rate * 100, 1) AS pct
        FROM olist.cohort_retention
        WHERE month_index <= 2
        ORDER BY cohort_month, month_index
        LIMIT 15
    """)
    rows = cur.fetchall()
    print("   Sample data (first 15 rows, M0-M2):")
    print("   Cohort | M | Retained | Size | Rate")
    print("   " + "-" * 50)
    for row in rows:
        print(f"   {row[0]} | M{row[1]} | {row[2]:,} | {row[3]:,} | {row[4]}%")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    fix_fact_orders()
    print("\n=== Done! ===")
