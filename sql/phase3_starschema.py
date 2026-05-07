import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

def build_star_schema():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("=" * 50)
    print("PHASE 3: STAR SCHEMA DESIGN")
    print("=" * 50)
    
    # Drop existing views/tables
    print("\n1. Cleaning up existing objects...")
    cur.execute("DROP VIEW IF EXISTS olist.fact_orders CASCADE")
    cur.execute("DROP VIEW IF EXISTS olist.dim_date CASCADE")
    cur.execute("DROP VIEW IF EXISTS olist.dim_product CASCADE")
    cur.execute("DROP VIEW IF EXISTS olist.dim_customer CASCADE")
    cur.execute("DROP VIEW IF EXISTS olist.dim_seller CASCADE")
    conn.commit()
    print("   Done")
    
    # Create dim_date
    print("\n2. Creating dim_date...")
    cur.execute("""
        CREATE VIEW olist.dim_date AS
        SELECT
            d::DATE AS date_key,
            EXTRACT(YEAR FROM d)::INT AS year,
            EXTRACT(QUARTER FROM d)::INT AS quarter,
            TO_CHAR(d, 'YYYY-MM') AS year_month,
            EXTRACT(MONTH FROM d)::INT AS month,
            TO_CHAR(d, 'Month') AS month_name,
            EXTRACT(WEEK FROM d)::INT AS week_num,
            EXTRACT(DOW FROM d)::INT AS day_of_week,
            CASE WHEN EXTRACT(DOW FROM d) IN (0,6) THEN TRUE ELSE FALSE END AS is_weekend
        FROM GENERATE_SERIES('2016-01-01'::DATE, '2019-12-31'::DATE, '1 day') d
    """)
    conn.commit()
    print("   dim_date created")
    
    # Create dim_product
    print("\n3. Creating dim_product...")
    cur.execute("""
        CREATE VIEW olist.dim_product AS
        SELECT
            p.product_id,
            COALESCE(t.category_en, 'unknown') AS category_en,
            p.product_category_name AS category_pt,
            p.product_weight_g,
            p.product_length_cm,
            p.product_height_cm,
            p.product_width_cm
        FROM olist.products p
        LEFT JOIN olist.category_translation t ON p.product_category_name = t.category_pt
    """)
    conn.commit()
    print("   dim_product created")
    
    # Create dim_customer
    print("\n4. Creating dim_customer...")
    cur.execute("""
        CREATE VIEW olist.dim_customer AS
        SELECT
            c.customer_id,
            c.customer_unique_id,
            c.customer_zip_code_prefix,
            c.customer_city,
            c.customer_state,
            CASE 
                WHEN c.customer_state IN ('SP', 'RJ', 'MG') THEN 'Southeast'
                WHEN c.customer_state IN ('RS', 'SC', 'PR') THEN 'South'
                WHEN c.customer_state IN ('BA', 'SE', 'AL', 'PB', 'PE', 'RN', 'CE', 'PI', 'MA', 'PA') THEN 'Northeast'
                WHEN c.customer_state IN ('DF', 'GO', 'MT', 'MS') THEN 'Central-West'
                WHEN c.customer_state IN ('AC', 'AP', 'AM', 'RO', 'RR', 'TO') THEN 'North'
                ELSE 'Unknown'
            END AS region
        FROM olist.customers c
    """)
    conn.commit()
    print("   dim_customer created")
    
    # Create dim_seller
    print("\n5. Creating dim_seller...")
    cur.execute("""
        CREATE VIEW olist.dim_seller AS
        SELECT
            s.seller_id,
            s.seller_zip_code_prefix,
            s.seller_city,
            s.seller_state,
            CASE 
                WHEN s.seller_state IN ('SP', 'RJ', 'MG') THEN 'Southeast'
                WHEN s.seller_state IN ('RS', 'SC', 'PR') THEN 'South'
                WHEN s.seller_state IN ('BA', 'SE', 'AL', 'PB', 'PE', 'RN', 'CE', 'PI', 'MA', 'PA') THEN 'Northeast'
                WHEN s.seller_state IN ('DF', 'GO', 'MT', 'MS') THEN 'Central-West'
                WHEN s.seller_state IN ('AC', 'AP', 'AM', 'RO', 'RR', 'TO') THEN 'North'
                ELSE 'Unknown'
            END AS region
        FROM olist.sellers s
    """)
    conn.commit()
    print("   dim_seller created")
    
    # Create fact_orders
    print("\n6. Creating fact_orders...")
    cur.execute("""
        CREATE VIEW olist.fact_orders AS
        SELECT
            o.order_id,
            o.customer_id,
            oi.product_id,
            oi.seller_id,
            o.order_purchase_timestamp::DATE AS order_date,
            oi.price AS revenue,
            oi.freight_value,
            op.payment_type,
            op.payment_value AS payment_value,
            r.review_score,
            
            -- Delivery metrics
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
            
            -- Customer repeat flag
            CASE WHEN rc.order_count > 1 THEN 1 ELSE 0 END AS is_repeat_customer
            
        FROM olist.orders o
        JOIN olist.order_items oi ON o.order_id = oi.order_id
        LEFT JOIN olist.order_payments op ON o.order_id = op.order_id AND op.payment_sequential = 1
        LEFT JOIN olist.order_reviews r ON o.order_id = r.order_id
        LEFT JOIN (
            SELECT customer_id, COUNT(*) AS order_count
            FROM olist.orders
            WHERE order_status = 'delivered'
            GROUP BY customer_id
        ) rc ON o.customer_id = rc.customer_id
        WHERE o.is_valid_order = TRUE
          AND o.order_status = 'delivered'
    """)
    conn.commit()
    print("   fact_orders created")
    
    cur.close()
    conn.close()

def verify_schema():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("\n=== Star Schema Verification ===")
    
    tables = [
        ('dim_date', 'Date dimension'),
        ('dim_product', 'Product dimension'),
        ('dim_customer', 'Customer dimension'),
        ('dim_seller', 'Seller dimension'),
        ('fact_orders', 'Fact table')
    ]
    
    for name, desc in tables:
        if name == 'dim_date':
            cur.execute("SELECT COUNT(*) FROM olist.dim_date")
        elif name == 'fact_orders':
            cur.execute("SELECT COUNT(*) FROM olist.fact_orders")
        else:
            cur.execute(f"SELECT COUNT(*) FROM olist.{name}")
        count = cur.fetchone()[0]
        print(f"{name} ({desc}): {count:,} rows")
    
    # Sample query
    print("\nSample: Total Revenue")
    cur.execute("SELECT ROUND(SUM(revenue)::NUMERIC, 2) FROM olist.fact_orders")
    revenue = cur.fetchone()[0]
    print(f"  Total: ${revenue:,.2f}")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    build_star_schema()
    verify_schema()
    print("\n=== Phase 3 Complete ===")