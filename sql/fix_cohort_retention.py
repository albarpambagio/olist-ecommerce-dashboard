import psycopg2

DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

def create_proper_cohort_retention():
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cur = conn.cursor()

    print("Rebuilding cohort retention analysis...")

    cur.execute("DROP VIEW IF EXISTS olist.cohort_retention CASCADE")
    conn.commit()

    cur.execute("""
        CREATE VIEW olist.cohort_retention AS
        WITH first_orders AS (
            SELECT
                customer_unique_id,
                MIN(order_date) AS first_order_date,
                DATE_TRUNC('month', MIN(order_date)) AS cohort_month
            FROM olist.fact_orders
            GROUP BY customer_unique_id
        ),
        cohort_with_orders AS (
            SELECT
                f.customer_unique_id,
                fo.cohort_month,
                DATE_TRUNC('month', f.order_date) AS order_month
            FROM olist.fact_orders f
            JOIN first_orders fo ON f.customer_unique_id = fo.customer_unique_id
        ),
        cohort_summary AS (
            SELECT
                cohort_month,
                COUNT(DISTINCT customer_unique_id) AS cohort_size,
                COUNT(DISTINCT customer_unique_id) FILTER (WHERE DATE_PART('month', AGE(order_month, cohort_month)) = 1) AS m1_retained,
                COUNT(DISTINCT customer_unique_id) FILTER (WHERE DATE_PART('month', AGE(order_month, cohort_month)) = 2) AS m2_retained,
                COUNT(DISTINCT customer_unique_id) FILTER (WHERE DATE_PART('month', AGE(order_month, cohort_month)) = 3) AS m3_retained,
                COUNT(DISTINCT customer_unique_id) FILTER (WHERE DATE_PART('month', AGE(order_month, cohort_month)) = 4) AS m4_retained,
                COUNT(DISTINCT customer_unique_id) FILTER (WHERE DATE_PART('month', AGE(order_month, cohort_month)) = 5) AS m5_retained,
                COUNT(DISTINCT customer_unique_id) FILTER (WHERE DATE_PART('month', AGE(order_month, cohort_month)) = 6) AS m6_retained
            FROM cohort_with_orders
            GROUP BY cohort_month
        )
        SELECT cohort_month, cohort_size, 0 AS month_index, cohort_size AS retained, 1.0 AS retention_rate
        FROM cohort_summary
        UNION ALL
        SELECT cohort_month, cohort_size, 1 AS month_index, m1_retained, CASE WHEN cohort_size > 0 THEN m1_retained::numeric / cohort_size ELSE 0 END FROM cohort_summary WHERE m1_retained IS NOT NULL
        UNION ALL
        SELECT cohort_month, cohort_size, 2 AS month_index, m2_retained, CASE WHEN cohort_size > 0 THEN m2_retained::numeric / cohort_size ELSE 0 END FROM cohort_summary WHERE m2_retained IS NOT NULL
        UNION ALL
        SELECT cohort_month, cohort_size, 3 AS month_index, m3_retained, CASE WHEN cohort_size > 0 THEN m3_retained::numeric / cohort_size ELSE 0 END FROM cohort_summary WHERE m3_retained IS NOT NULL
        UNION ALL
        SELECT cohort_month, cohort_size, 4 AS month_index, m4_retained, CASE WHEN cohort_size > 0 THEN m4_retained::numeric / cohort_size ELSE 0 END FROM cohort_summary WHERE m4_retained IS NOT NULL
        UNION ALL
        SELECT cohort_month, cohort_size, 5 AS month_index, m5_retained, CASE WHEN cohort_size > 0 THEN m5_retained::numeric / cohort_size ELSE 0 END FROM cohort_summary WHERE m5_retained IS NOT NULL
        UNION ALL
        SELECT cohort_month, cohort_size, 6 AS month_index, m6_retained, CASE WHEN cohort_size > 0 THEN m6_retained::numeric / cohort_size ELSE 0 END FROM cohort_summary WHERE m6_retained IS NOT NULL
        ORDER BY cohort_month, month_index
    """)

    conn.commit()
    print("   cohort_retention view created")

    print("\n   Sample retention data:")
    cur.execute("""
        SELECT cohort_month, month_index, cohort_size, retained, ROUND(retention_rate * 100, 2) AS retention_pct
        FROM olist.cohort_retention
        WHERE cohort_month >= '2017-01-01' AND cohort_month < '2017-04-01'
        ORDER BY cohort_month, month_index
    """)
    for row in cur.fetchall():
        print(f"   {row[0].strftime('%Y-%m')}: M{row[1]}, cohort={row[2]}, retained={row[3]}, rate={row[4]}%")

    cur.execute("""
        SELECT ROUND(AVG(retention_rate) * 100, 2)
        FROM olist.cohort_retention
        WHERE month_index = 1 AND cohort_size > 10
    """)
    m1 = cur.fetchone()[0]
    print(f"\n   Average M1 Retention: {m1}%")

    conn.close()
    print("\n=== Cohort retention complete ===")

if __name__ == "__main__":
    create_proper_cohort_retention()