import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Connect to the database
conn = sqlite3.connect('supply_chain.db')

print("Fetching analytical metrics from database...")

# Query 1: Sales and Stockouts by Category
query_cat = """
SELECT Category, 
       SUM(Units_Sold) AS Total_Units_Sold,
       AVG(Stockout_Flag) * 100 AS Stockout_Rate
FROM retail_data
GROUP BY Category;
"""
df_cat = pd.read_sql_query(query_cat, conn)

# Query 2: Supplier Reliability raw lead times (grouping in pandas for stddev)
query_sup = """
SELECT Supplier_ID, Supplier_Lead_Time_Days
FROM retail_data;
"""
df_sup = pd.read_sql_query(query_sup, conn)
df_sup_stats = df_sup.groupby('Supplier_ID')['Supplier_Lead_Time_Days'].agg(['mean', 'std']).reset_index()

conn.close()

# 2. Setup matplotlib settings for high-quality layout
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
sns.set_theme(style="whitegrid")

# Create a 1x3 subplot grid
fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
fig.suptitle("Supply Chain & Retail Health Trend Insights", fontsize=18, fontweight='bold', y=1.02)

# Panel 1: Total Units Sold
sns.barplot(
    data=df_cat, 
    x='Category', 
    y='Total_Units_Sold', 
    ax=axes[0], 
    palette=['#10b981', '#3b82f6'],
    hue='Category',
    legend=False
)
axes[0].set_title("Total Sales Volume by Category", fontsize=13, fontweight='bold')
axes[0].set_ylabel("Total Units Sold", fontsize=11)
axes[0].set_xlabel("Product Category", fontsize=11)
for p in axes[0].patches:
    axes[0].annotate(f"{int(p.get_height()):,}", (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 5), textcoords='offset points', fontweight='semibold')

# Panel 2: Stockout Percentage
sns.barplot(
    data=df_cat, 
    x='Category', 
    y='Stockout_Rate', 
    ax=axes[1], 
    palette=['#f43f5e', '#f59e0b'],
    hue='Category',
    legend=False
)
axes[1].set_title("Stockout Risk Rate (%)", fontsize=13, fontweight='bold')
axes[1].set_ylabel("Stockout Percentage (%)", fontsize=11)
axes[1].set_xlabel("Product Category", fontsize=11)
for p in axes[1].patches:
    axes[1].annotate(f"{p.get_height():.2f}%", (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 5), textcoords='offset points', fontweight='semibold')

# Panel 3: Supplier Reliability (Lead Time Averages & StdDev)
axes[2].bar(
    df_sup_stats['Supplier_ID'], 
    df_sup_stats['mean'], 
    yerr=df_sup_stats['std'], 
    align='center', 
    alpha=0.8, 
    ecolor='black', 
    capsize=8,
    color='#6366f1'
)
axes[2].set_title("Supplier Lead Time Reliability (Days)", fontsize=13, fontweight='bold')
axes[2].set_ylabel("Avg Lead Time (Days + Error Bar)", fontsize=11)
axes[2].set_xlabel("Supplier ID", fontsize=11)
axes[2].set_xticks(range(len(df_sup_stats['Supplier_ID'])))
axes[2].set_xticklabels(df_sup_stats['Supplier_ID'], rotation=15)

# Tight layout
plt.tight_layout()

# Save image
output_img = "supply_chain_insights.png"
print(f"Saving high-quality visualization to '{output_img}'...")
plt.savefig(output_img, dpi=300, bbox_inches='tight')

# Display window
print("Opening chart in a new window...")
plt.show()