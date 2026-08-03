import sqlite3
import pandas as pd
import os

def import_data():
    csv_path = r"C:\Users\shash\OneDrive\Desktop\guidelines_pdfs (1)\guidelines_sqft_valuation.csv"
    db_path = r"c:\Users\shash\PycharmProjects\PythonProject1\PythonProject1\guidelines.db"
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return
        
    print("Reading CSV data...")
    df = pd.read_csv(csv_path)
    print(f"Read {len(df)} rows.")
    
    print("Connecting to SQLite database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Creating table...")
    # Drop existing table if exists to overwrite
    cursor.execute("DROP TABLE IF EXISTS guidelines")
    cursor.execute("""
    CREATE TABLE guidelines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        district TEXT,
        taluk_office TEXT,
        village_area TEXT,
        property_classification TEXT,
        original_rate REAL,
        original_unit TEXT,
        rate_per_sqft REAL,
        unit TEXT
    )
    """)
    
    print("Writing data to table...")
    df.to_sql("guidelines", conn, if_exists="append", index=False)
    
    print("Creating indexes for fast search...")
    cursor.execute("CREATE INDEX idx_district ON guidelines(district)")
    cursor.execute("CREATE INDEX idx_taluk ON guidelines(taluk_office)")
    cursor.execute("CREATE INDEX idx_village ON guidelines(village_area)")
    cursor.execute("CREATE INDEX idx_class ON guidelines(property_classification)")
    
    conn.commit()
    conn.close()
    print("Import complete! guidelines.db is ready.")

if __name__ == "__main__":
    import_data()
