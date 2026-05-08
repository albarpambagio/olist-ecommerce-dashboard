import psycopg2

DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

def fix_cohort_retention():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("Fixing cohort_retention view...")
    
    # Drop existing view
    cur.execute("DROP VIEW IF EXISTS olist.cohort_retention CASCADE")
    conn.commit()
    
    # Create corrected view
    # Logic: For each customer, find their cohort (first order month)
    # Then for each order, calculate months since first order
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
    print("  View recreated!")
    
    # Verify
    print("\nSample data (first 20 rows, month_index <= 2):")
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
        LIMIT 20
    """)
    for row in cur.fetchall():
        print(f"  {row[0]} M{row[1]}: {row[2]:,}/{row[3]:,} ({row[4]:.1f}%)")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    fix_cohort_retention()
    print("\nDone!")