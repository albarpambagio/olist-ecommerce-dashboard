import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import glob

# Connection parameters
DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

def create_database():
    """Create olist database if not exists"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname='postgres',
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Check if database exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'olist'")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE olist")
        print("Database 'olist' created")
    else:
        print("Database 'olist' already exists")
    
    cur.close()
    conn.close()

def create_tables():
    """Create tables in PostgreSQL"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    # Create schema
    cur.execute("CREATE SCHEMA IF NOT EXISTS olist")
    
    # Drop existing tables
    tables = ['orders', 'order_items', 'order_payments', 'order_reviews', 
             'customers', 'sellers', 'products', 'category_translation', 'geolocation']
    for t in tables:
        cur.execute(f"DROP TABLE IF EXISTS olist.{t} CASCADE")
    
    # Create tables
    cur.execute("""
        CREATE TABLE olist.orders (
            order_id VARCHAR(32) PRIMARY KEY,
            customer_id VARCHAR(32),
            order_status VARCHAR(20),
            order_purchase_timestamp TIMESTAMP,
            order_approved_at TIMESTAMP,
            order_delivered_carrier_date TIMESTAMP,
            order_delivered_customer_date TIMESTAMP,
            order_estimated_delivery_date TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE olist.order_items (
            order_id VARCHAR(32),
            order_item_id INTEGER,
            product_id VARCHAR(32),
            seller_id VARCHAR(32),
            shipping_limit_date TIMESTAMP,
            price NUMERIC(10,2),
            freight_value NUMERIC(10,2),
            PRIMARY KEY (order_id, order_item_id)
        )
    """)
    
    cur.execute("""
        CREATE TABLE olist.order_payments (
            order_id VARCHAR(32),
            payment_sequential INTEGER,
            payment_type VARCHAR(20),
            payment_installments INTEGER,
            payment_value NUMERIC(10,2)
        )
    """)
    
    cur.execute("""
        CREATE TABLE olist.order_reviews (
            review_id VARCHAR(32),
            order_id VARCHAR(32),
            review_score INTEGER,
            review_creation_date TIMESTAMP,
            review_answer_timestamp TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE olist.customers (
            customer_id VARCHAR(32) PRIMARY KEY,
            customer_unique_id VARCHAR(32),
            customer_zip_code_prefix VARCHAR(10),
            customer_city VARCHAR(100),
            customer_state VARCHAR(2)
        )
    """)
    
    cur.execute("""
        CREATE TABLE olist.sellers (
            seller_id VARCHAR(32) PRIMARY KEY,
            seller_zip_code_prefix VARCHAR(10),
            seller_city VARCHAR(100),
            seller_state VARCHAR(2)
        )
    """)
    
    cur.execute("""
        CREATE TABLE olist.products (
            product_id VARCHAR(32) PRIMARY KEY,
            product_category_name VARCHAR(100),
            product_name_lenght INTEGER,
            product_description_lenght INTEGER,
            product_photos_qty INTEGER,
            product_weight_g INTEGER,
            product_length_cm INTEGER,
            product_height_cm INTEGER,
            product_width_cm INTEGER
        )
    """)
    
    cur.execute("""
        CREATE TABLE olist.category_translation (
            category_pt VARCHAR(100),
            category_en VARCHAR(100)
        )
    """)
    
    cur.execute("""
        CREATE TABLE olist.geolocation (
            zip_code_prefix VARCHAR(10),
            geolocation_lat NUMERIC(10,8),
            geolocation_lng NUMERIC(10,8),
            geolocation_city VARCHAR(100),
            geolocation_state VARCHAR(2)
        )
    """)
    
    conn.commit()
    print("Tables created successfully")
    cur.close()
    conn.close()

def load_data():
    """Load CSV data into tables"""
    data_dir = r'D:\PROJECT\data_analyst_porto\olist complete\data'
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    # File mapping
    files = {
        'orders': 'olist_orders_dataset.csv',
        'order_items': 'olist_order_items_dataset.csv',
        'order_payments': 'olist_order_payments_dataset.csv',
        'order_reviews': 'olist_order_reviews_dataset.csv',
        'customers': 'olist_customers_dataset.csv',
        'sellers': 'olist_sellers_dataset.csv',
        'products': 'olist_products_dataset.csv',
        'category_translation': 'product_category_name_translation.csv',
        'geolocation': 'olist_geolocation_dataset.csv'
    }
    
    for table, filename in files.items():
        filepath = os.path.join(data_dir, filename)
        print(f"Loading {table}...")
        
        # Use COPY command
        with open(filepath, 'r', encoding='utf-8') as f:
            # Skip header
            header = f.readline().strip()
            
            if table == 'orders':
                cols = 'order_id,customer_id,order_status,order_purchase_timestamp,order_approved_at,order_delivered_carrier_date,order_delivered_customer_date,order_estimated_delivery_date'
            elif table == 'order_items':
                cols = 'order_id,order_item_id,product_id,seller_id,shipping_limit_date,price,freight_value'
            elif table == 'order_payments':
                cols = 'order_id,payment_sequential,payment_type,payment_installments,payment_value'
            elif table == 'order_reviews':
                cols = 'review_id,order_id,review_score,review_creation_date,review_answer_timestamp'
            elif table == 'customers':
                cols = 'customer_id,customer_unique_id,customer_zip_code_prefix,customer_city,customer_state'
            elif table == 'sellers':
                cols = 'seller_id,seller_zip_code_prefix,seller_city,seller_state'
            elif table == 'products':
                cols = 'product_id,product_category_name,product_name_lenght,product_description_lenght,product_photos_qty,product_weight_g,product_length_cm,product_height_cm,product_width_cm'
            elif table == 'category_translation':
                cols = 'category_pt,category_en'
            elif table == 'geolocation':
                cols = 'zip_code_prefix,geolocation_lat,geolocation_lng,geolocation_city,geolocation_state'
            
            # Reset file pointer
            f.seek(0)
            
            # Use COPY FROM
            cur.copy_from(f, f'olist.{table}', sep=',', columns=cols, null='')
            
        conn.commit()
        print(f"  {table} loaded")
    
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
    
    print("\n=== Row Counts ===")
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM olist.{t}")
        count = cur.fetchone()[0]
        print(f"{t}: {count:,}")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    print("Creating database...")
    create_database()
    
    print("\nCreating tables...")
    create_tables()
    
    print("\nLoading data...")
    load_data()
    
    print("\nVerifying counts...")
    verify_counts()
    
    print("\n=== Phase 1 Complete ===")