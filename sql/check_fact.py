import psycopg2

DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

def check_fact_orders():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("=== Checking fact_orders for repeat customers ===\n")
    
    # Check if any customer_id has multiple order_ids
    print("1. Checking for repeat customer_id in fact_orders...")
    cur.execute("""
        SELECT customer_id, COUNT(DISTINCT order_id) as order_count
        FROM olist.fact_orders
        GROUP BY customer_id
        HAVING COUNT(DISTINCT order_id) > 1
        LIMIT 5
    """)
    rows = cur.fetchall()
    print(f"   Found {len(rows)} customers with multiple orders (showing 5):")
    for row in rows:
        print(f"   Customer: {row[0]}, Orders: {row[1]}")
    
    # Check raw orders table
    print("\n2. Checking raw olist.orders for repeat customers...")
    cur.execute("""
        SELECT customer_id, COUNT(DISTINCT order_id) as order_count
        FROM olist.orders
        WHERE order_status = 'delivered'
        GROUP BY customer_id
        HAVING COUNT(DISTINCT order_id) > 1
        LIMIT 5
    """)
    rows = cur.fetchall()
    print(f"   Found {len(rows)} customers with multiple orders (showing 5):")
    for row in rows:
        print(f"   Customer: {row[0]}, Orders: {row[1]}")
    
    # Check using customer_unique_id (correct way)
    print("\n3. Checking by customer_unique_id (correct method)...")
    cur.execute("""
        SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) as order_count
        FROM olist.orders o
        JOIN olist.customers c ON o.customer_id = c.customer_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_unique_id
        HAVING COUNT(DISTINCT o.order_id) > 1
        LIMIT 5
    """)
    rows = cur.fetchall()
    print(f"   Found {len(rows)} unique customers with multiple orders (showing 5):")
    for row in rows:
        print(f"   Unique ID: {row[0]}, Orders: {row[1]}")
    
    # Show one customer's orders
    if len(rows) > 0:
        uid = rows[0][0]
        print(f"\n4. Orders for unique_id {uid}...")
        cur.execute("""
            SELECT o.order_id, o.order_purchase_timestamp
            FROM olist.orders o
            JOIN olist.customers c ON o.customer_id = c.customer_id
            WHERE c.customer_unique_id = %s
            ORDER BY o.order_purchase_timestamp
        """, (uid,))
        for row in cur.fetchall():
            print(f"   Order: {row[0]}, Date: {row[1]}")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    check_fact_orders()