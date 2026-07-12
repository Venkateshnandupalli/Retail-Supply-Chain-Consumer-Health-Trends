import sqlite3
import pandas as pd

# 1. Connect to your existing database
conn = sqlite3.connect('supply_chain.db')

print("Executing SQL Queries...\n")

# --- Query 1: Revenue & Sales ---
query1 = """
SELECT 
    Category,
    SUM(Units_Sold) AS Total_Units_Sold,
    SUM(Units_Sold * Unit_Price) AS Total_Revenue
FROM retail_data
GROUP BY Category;
"""
print("--- 1. Revenue & Sales by Category ---")
df_revenue = pd.read_sql_query(query1, conn)
print(df_revenue.to_string(index=False))
print("\n")


# --- Query 2: Stockout Risk ---
query2 = """
SELECT 
    Category,
    SUM(Stockout_Flag) as Total_Stockouts,
    COUNT(*) as Total_Records,
    ROUND((CAST(SUM(Stockout_Flag) AS FLOAT) / COUNT(*)) * 100, 2) as Stockout_Percentage
FROM retail_data
GROUP BY Category;
"""
print("--- 2. Stockout Risk by Category ---")
df_stockouts = pd.read_sql_query(query2, conn)
print(df_stockouts.to_string(index=False))
print("\n")


# --- Query 3: Supply Chain Bottlenecks ---
query3 = """
SELECT 
    Warehouse_ID,
    Region,
    SUM(Stockout_Flag) as Total_Stockouts,
    AVG(Supplier_Lead_Time_Days) as Avg_Lead_Time
FROM retail_data
GROUP BY Warehouse_ID, Region
ORDER BY Total_Stockouts DESC
LIMIT 5;
"""
print("--- 3. Top 5 Worst Warehouses for Stockouts ---")
df_bottlenecks = pd.read_sql_query(query3, conn)
print(df_bottlenecks.to_string(index=False))
print("\n")

# Close the connection
conn.close()