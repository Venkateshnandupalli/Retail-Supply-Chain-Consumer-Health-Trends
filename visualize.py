import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Connect to the database
conn = sqlite3.connect('supply_chain.db')

# 2. Query the data for our chart (Revenue by Category)
query = """
SELECT Category, SUM(Units_Sold) AS Total_Units
FROM retail_data
GROUP BY Category;
"""
df = pd.read_sql_query(query, conn)
conn.close()

# 3. Build the chart
plt.figure(figsize=(8, 5))
sns.barplot(data=df, x='Category', y='Total_Units', palette=['#3498db', '#e74c3c'])

# 4. Add titles and labels
plt.title("Total Units Sold: Health vs Standard", fontsize=16)
plt.ylabel("Total Units", fontsize=12)
plt.xlabel("Product Category", fontsize=12)

# 5. THIS is the command that creates the pop-up window!
print("Opening chart in a new window...")
plt.show()