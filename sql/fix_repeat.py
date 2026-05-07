import psycopg2

DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

def fix_repeat_analysis():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    # Fix repeat customer analysis - use customer_unique_id instead
    print("Repeat Customer Analysis (corrected):")
    cur.execute("""
        WITH customer_orders AS (
            SELECT c.customer_unique_id, COUNT(*) as order_count
            FROM olist.orders o
            JOIN olist.customers c ON o.customer_id = c.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        )
        SELECT 
            COUNT(*) as total_unique_customers,
            SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) as repeat_customers,
            ROUND(SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) as repeat_rate,
            SUM(order_count) as total_orders
        FROM customer_orders
    """)
    row = cur.fetchone()
    print(f"   Unique customers: {row[0]:,}")
    print(f"   Repeat customers: {row[1]:,}")
    print(f"   Repeat rate: {row[2]}%")
    print(f"   Total orders: {row[3]:,}")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    fix_repeat_analysis()