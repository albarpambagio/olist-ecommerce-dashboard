import psycopg2
import os

# Connection parameters
DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

data_dir = r'D:\PROJECT\data_analyst_porto\olist complete\data'

def load_with_copy():
    """Load data using COPY command"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    # File mappings with columns
    files = [
        ('orders', 'olist_orders_dataset.csv', 
         'order_id,customer_id,order_status,order_purchase_timestamp,order_approved_at,order_delivered_carrier_date,order_delivered_customer_date,order_estimated_delivery_date'),
        ('order_items', 'olist_order_items_dataset.csv',
         'order_id,order_item_id,product_id,seller_id,shipping_limit_date,price,freight_value'),
        ('order_payments', 'olist_order_payments_dataset.csv',
         'order_id,payment_sequential,payment_type,payment_installments,payment_value'),
        ('order_reviews', 'olist_order_reviews_dataset.csv',
         'review_id,order_id,review_score,review_creation_date,review_answer_timestamp'),
        ('customers', 'olist_customers_dataset.csv',
         'customer_id,customer_unique_id,customer_zip_code_prefix,customer_city,customer_state'),
        ('sellers', 'olist_sellers_dataset.csv',
         'seller_id,seller_zip_code_prefix,seller_city,seller_state'),
        ('products', 'olist_products_dataset.csv',
         'product_id,product_category_name,product_name_lenght,product_description_lenght,product_photos_qty,product_weight_g,product_length_cm,product_height_cm,product_width_cm'),
        ('category_translation', 'product_category_name_translation.csv',
         'category_pt,category_en'),
        ('geolocation', 'olist_geolocation_dataset.csv',
         'zip_code_prefix,geolocation_lat,geolocation_lng,geolocation_city,geolocation_state'),
    ]
    
    for table, filename, columns in files:
        filepath = os.path.join(data_dir, filename)
        print(f"Loading {table}...")
        
        # Use COPY command
        sql = f"""COPY olist.{table} ({columns}) FROM '{filepath}' WITH (FORMAT csv, HEADER true, DELIMITER ',')"""
        try:
            cur.execute(sql)
            conn.commit()
            print(f"  {table} loaded")
        except Exception as e:
            print(f"  Error loading {table}: {e}")
            conn.rollback()
    
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
    print("Loading data with COPY command...")
    load_with_copy()
    
    print("\nVerifying counts...")
    verify_counts()
    
    print("\n=== Phase 1 Data Load Complete ===")