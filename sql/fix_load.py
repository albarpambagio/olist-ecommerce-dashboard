import psycopg2

# Connection parameters
DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

data_dir = r'D:\PROJECT\data_analyst_porto\olist complete\data'

def fix_and_load():
    """Fix tables and load data"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    # Fix order_reviews - add extra columns
    print("Recreating order_reviews table...")
    cur.execute("DROP TABLE IF EXISTS olist.order_reviews CASCADE")
    cur.execute("""
        CREATE TABLE olist.order_reviews (
            review_id VARCHAR(32),
            order_id VARCHAR(32),
            review_score INTEGER,
            review_comment_title VARCHAR(100),
            review_comment_message TEXT,
            review_creation_date TIMESTAMP,
            review_answer_timestamp TIMESTAMP
        )
    """)
    
    # Fix geolocation - change precision
    print("Recreating geolocation table...")
    cur.execute("DROP TABLE IF EXISTS olist.geolocation CASCADE")
    cur.execute("""
        CREATE TABLE olist.geolocation (
            zip_code_prefix VARCHAR(10),
            geolocation_lat NUMERIC(12,8),
            geolocation_lng NUMERIC(12,8),
            geolocation_city VARCHAR(100),
            geolocation_state VARCHAR(2)
        )
    """)
    
    conn.commit()
    
    # Load order_reviews
    print("Loading order_reviews...")
    sql = f"""COPY olist.order_reviews FROM '{data_dir}\\olist_order_reviews_dataset.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',')"""
    cur.execute(sql)
    conn.commit()
    print("  order_reviews loaded")
    
    # Load geolocation  
    print("Loading geolocation...")
    sql = f"""COPY olist.geolocation FROM '{data_dir}\\olist_geolocation_dataset.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',')"""
    cur.execute(sql)
    conn.commit()
    print("  geolocation loaded")
    
    cur.close()
    conn.close()

def verify_counts():
    """Verify row counts"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    tables = ['orders', 'order_items', 'order_payments', 'order_reviews', 
             'customers', 'sellers', 'products', 'category_translation', 'geolocation']
    
    print("\n=== Final Row Counts ===")
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM olist.{t}")
        count = cur.fetchone()[0]
        print(f"{t}: {count:,}")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    fix_and_load()
    verify_counts()
    print("\n=== Data Load Fixed ===")