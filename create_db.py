import pandas as pd
import sqlite3

# 1. Load the synthetic data you just created
print("Loading CSV data...")
# Load CSV from the raw_data.csv subfolder
df = pd.read_csv('raw_data.csv/modified_health_trend_data.csv')

# 2. Create a connection to a new SQLite database 
# (If this file doesn't exist, Python creates it for you!)
conn = sqlite3.connect('supply_chain.db')

# 3. Push the Pandas DataFrame into a SQL table named 'retail_data'
print("Building SQL Database...")
df.to_sql('retail_data', conn, if_exists='replace', index=False)

# 4. Create database views from SQL script
print("Creating views and database metrics...")
try:
    with open('analytics_metrics.sql', 'r') as sql_file:
        sql_script = sql_file.read()
    conn.executescript(sql_script)
    print("Database views created successfully.")
except Exception as e:
    print(f"Error executing SQL script: {e}")

# 5. Close the connection
conn.close()
print("Success! Check your folder for 'supply_chain.db'")