import psycopg2

DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'olist'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'

def get_cohort_data():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("=== Cohort Retention Data (Months 0-6) ===\n")
    print("Cohort Month | M0 | M1 | M2 | M3 | M4 | M5 | M6")
    print("-" * 80)
    
    # Get all cohort data
    cur.execute("""
        SELECT
            cohort_month,
            month_index,
            ROUND(retention_rate * 100, 1) AS retention_pct,
            retained,
            cohort_size
        FROM olist.cohort_retention
        WHERE month_index <= 6
        ORDER BY cohort_month, month_index
    """)
    
    rows = cur.fetchall()
    
    # Organize by cohort
    cohorts = {}
    for row in rows:
        cohort = row[0].strftime('%Y-%m')
        idx = row[1]
        pct = row[2]
        if cohort not in cohorts:
            cohorts[cohort] = {}
        cohorts[cohort][idx] = pct
    
    # Print each cohort
    for cohort in sorted(cohorts.keys()):
        line = f"{cohort} |"
        for i in range(7):  # M0 to M6
            if i in cohorts[cohort]:
                line += f" {cohorts[cohort][i]:.1f}% |"
            else:
                line += " - |"
        print(line)
    
    print("\n=== Summary Statistics ===")
    cur.execute("""
        SELECT 
            month_index,
            ROUND(AVG(retention_rate) * 100, 1) AS avg_retention,
            COUNT(DISTINCT cohort_month) AS num_cohorts
        FROM olist.cohort_retention
        WHERE month_index <= 6
        GROUP BY 1
        ORDER BY 1
    """)
    
    print("\nMonth Index | Avg Retention | # Cohorts")
    print("-" * 40)
    for row in cur.fetchall():
        print(f"M{row[0]} | {row[1]:.1f}% | {row[2]}")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    get_cohort_data()