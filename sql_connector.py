import urllib.parse
from langchain_community.utilities import SQLDatabase

DB_USER = "root"
DB_PASS = "forwhat@123"  # If you have a password, put it here
DB_HOST = "127.0.0.1"
DB_NAME = "forwhat"

# Encode the password to handle special characters
encoded_pass = urllib.parse.quote_plus(DB_PASS)

# Construct URI - Note: If no password, the colon stays but the middle part is empty
mysql_uri = f"mysql+pymysql://{DB_USER}:{encoded_pass}@{DB_HOST}/{DB_NAME}"

try:
    db = SQLDatabase.from_uri(mysql_uri, sample_rows_in_table_info=3)
        # 1. Get just the names of the tables
    table_names = db.get_usable_table_names()
    print(f"✅ Connection active. Found {len(table_names)} tables: {table_names}")

    # 2. Get detailed Schema (CREATE statements + Sample Rows)
    # You can pass a list of specific tables if you don't want all of them
    detailed_schema = db.get_table_info(table_names=['customers', 'products', 'orders', 'order_items'])

    print("\n--- Detailed Database Schema ---")
    print(detailed_schema)
except Exception as e:
    print(f"Still failing. Error details: {e}")