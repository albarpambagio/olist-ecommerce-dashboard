import psycopg2

DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

def initial_eda():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("=" * 50)
    print("PHASE 1: INITIAL EXPLORATION")
    print("=" * 50)
    
    # 1. Date range
    print("\n1. Date Range:")
    cur.execute("SELECT MIN(order_purchase_timestamp), MAX(order_purchase_timestamp) FROM olist.orders")
    row = cur.fetchone()
    print(f"   From: {row[0]} to {row[1]}")
    
    # 2. Order status distribution
    print("\n2. Order Status Distribution:")
    cur.execute("SELECT order_status, COUNT(*) AS cnt FROM olist.orders GROUP BY 1 ORDER BY 2 DESC")
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]:,}")
    
    # 3. Null check on delivery dates
    print("\n3. Delivery Date Null Check:")
    cur.execute("""
        SELECT 
            COUNT(*) AS total,
            COUNT(order_delivered_customer_date) AS has_delivery_date,
            COUNT(*) - COUNT(order_delivered_customer_date) AS missing_delivery_date
        FROM olist.orders
    """)
    row = cur.fetchone()
    print(f"   Total orders: {row[0]:,}")
    print(f"   With delivery date: {row[1]:,}")
    print(f"   Missing delivery date: {row[2]:,}")
    
    # 4. Payment types
    print("\n4. Payment Types:")
    cur.execute("SELECT payment_type, COUNT(*) FROM olist.order_payments GROUP BY 1 ORDER BY 2 DESC")
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]:,}")
    
    # 5. Reviews
    print("\n5. Review Scores:")
    cur.execute("SELECT review_score, COUNT(*) FROM olist.order_reviews GROUP BY 1 ORDER BY 1")
    for row in cur.fetchall():
        print(f"   Score {row[0]}: {row[1]:,}")
    
    # 6. Top states
    print("\n6. Top 10 States by Customers:")
    cur.execute("""
        SELECT customer_state, COUNT(*) as cnt 
        FROM olist.customers 
        GROUP BY 1 
        ORDER BY 2 DESC 
        LIMIT 10
    """)
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]:,}")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    initial_eda()