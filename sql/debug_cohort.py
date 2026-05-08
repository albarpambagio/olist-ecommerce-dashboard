import psycopg2

DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

def debug_cohort():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("=== Debugging Cohort Retention ===\n")
    
    # Check if there are repeat orders
    print("1. Checking repeat orders...")
    cur.execute("""
        SELECT 
            customer_id,
            COUNT(DISTINCT order_date) as order_count,
            MIN(order_date) as first_order,
            MAX(order_date) as last_order
        FROM olist.fact_orders
        GROUP BY customer_id
        HAVING COUNT(DISTINCT order_date) > 1
        LIMIT 5
    """)
    rows = cur.fetchall()
    print(f"   Found {len(rows)} repeat customers (showing 5):")
    for row in rows:
        print(f"   Customer: {row[0]}, Orders: {row[1]}, First: {row[2]}, Last: {row[3]}")
    
    # Check month difference calculation
    print("\n2. Testing month_diff calculation...")
    cur.execute("""
        WITH test AS (
            SELECT 
                DATE('2017-01-15') as cohort_month,
                DATE('2017-03-20') as order_month
        )
        SELECT 
            cohort_month,
            order_month,
            (EXTRACT(YEAR FROM order_month) - EXTRACT(YEAR FROM cohort_month)) * 12 +
            (EXTRACT(MONTH FROM order_month) - EXTRACT(MONTH FROM cohort_month)) AS month_index
        FROM test
    """)
    row = cur.fetchone()
    print(f"   Cohort: {row[0]}, Order: {row[1]}, Month Index: {row[2]} (should be 2)")
    
    # Check actual cohort data
    print("\n3. Checking first_order CTE...")
    cur.execute("""
        WITH first_order AS (
            SELECT 
                customer_id,
                MIN(DATE_TRUNC('month', order_date)) AS cohort_month
            FROM olist.fact_orders
            GROUP BY customer_id
        )
        SELECT COUNT(*) FROM first_order
    """)
    print(f"   Total cohorts: {cur.fetchone()[0]:,}")
    
    # Check if all_orders join works
    print("\n4. Checking all_orders with month_index...")
    cur.execute("""
        WITH first_order AS (
            SELECT 
                customer_id,
                MIN(DATE_TRUNC('month', order_date)) AS cohort_month
            FROM olist.fact_orders
            GROUP BY customer_id
        ),
        all_orders AS (
            SELECT 
                fo.customer_id,
                fo.cohort_month,
                DATE_TRUNC('month', fo2.order_date) AS order_month
            FROM first_order fo
            JOIN olist.fact_orders fo2 ON fo.customer_id = fo2.customer_id
        )
        SELECT 
            customer_id,
            cohort_month,
            order_month,
            (EXTRACT(YEAR FROM order_month) - EXTRACT(YEAR FROM cohort_month)) * 12 +
            (EXTRACT(MONTH FROM order_month) - EXTRACT(MONTH FROM cohort_month)) AS month_index
        FROM all_orders
        WHERE customer_id IN (
            SELECT customer_id FROM all_orders GROUP BY 1 HAVING COUNT(*) > 1 LIMIT 1
        )
        LIMIT 10
    """)
    rows = cur.fetchall()
    print(f"   Sample data for one repeat customer:")
    for row in rows:
        print(f"   Cohort: {row[1]}, Order: {row[2]}, M{row[3]}")
    
    # Now create a simple, working cohort view
    print("\n5. Creating simple cohort_retention view...")
    cur.execute("DROP VIEW IF EXISTS olist.cohort_retention CASCADE")
    conn.commit()
    
    cur.execute("""
        CREATE VIEW olist.cohort_retention AS
        WITH first_order AS (
            SELECT 
                customer_id,
                MIN(DATE_TRUNC('month', order_date)) AS cohort_month
            FROM olist.fact_orders
            GROUP BY customer_id
        ),
        all_orders AS (
            SELECT 
                fo.customer_id,
                fo.cohort_month,
                DATE_TRUNC('month', fo2.order_date) AS order_month
            FROM first_order fo
            JOIN olist.fact_orders fo2 ON fo.customer_id = fo2.customer_id
        ),
        month_diff AS (
            SELECT 
                customer_id,
                cohort_month,
                order_month,
                (EXTRACT(YEAR FROM order_month) - EXTRACT(YEAR FROM cohort_month)) * 12 +
                (EXTRACT(MONTH FROM order_month) - EXTRACT(MONTH FROM cohort_month)) AS month_index
            FROM all_orders
        ),
        cohort_sizes AS (
            SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_size
            FROM first_order
            GROUP BY 1
        )
        SELECT
            cohort_month,
            month_index,
            COUNT(DISTINCT customer_id) AS retained,
            MAX(cohort_size) AS cohort_size,
            ROUND(COUNT(DISTINCT customer_id)::NUMERIC / MAX(cohort_size), 3) AS retention_rate
        FROM month_diff md
        JOIN cohort_sizes cs USING (cohort_month)
        WHERE month_index >= 0
        GROUP BY cohort_month, month_index
        ORDER BY cohort_month, month_index
    """)
    conn.commit()
    print("   View created!")
    
    # Verify
    print("\n6. Verification - checking for month_index > 0...")
    cur.execute("""
        SELECT COUNT(*) FROM olist.cohort_retention WHERE month_index > 0
    """)
    non_zero = cur.fetchone()[0]
    print(f"   Rows with month_index > 0: {non_zero:,}")
    
    if non_zero > 0:
        print("\n   Sample data (month_index <= 2):")
        cur.execute("""
            SELECT 
                TO_CHAR(cohort_month, 'YYYY-MM'), month_index,
                retained, cohort_size,
                ROUND(retention_rate * 100, 1) AS pct
            FROM olist.cohort_retention
            WHERE month_index <= 2
            ORDER BY cohort_month, month_index
            LIMIT 15
        """)
        for row in cur.fetchall():
            print(f"   {row[0]} M{row[1]}: {row[2]:,}/{row[3]:,} ({row[4]}%)")
    else:
        print("\n   ⚠️  Still no data for month_index > 0!")
        print("   This means customers either don't return, or the join isn't working.")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    debug_cohort()
    print("\n=== Done ===")