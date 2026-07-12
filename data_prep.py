import pandas as pd
import numpy as np
from pathlib import Path

# 1. Load the actual dataset file
source_file = Path("raw_data.csv") / "supply_chain_dataset1.csv"
print("Loading data from:", source_file)

df = pd.read_csv(source_file)
print("Original Columns:", df.columns.tolist())

# 2. Add a Category column using available data fields.
if "Product type" in df.columns:
    df["Category"] = np.where(df["Product type"].isin(["skincare", "cosmetics"]), "Health", "Standard")
elif "Promotion_Flag" in df.columns:
    df["Category"] = np.where(df["Promotion_Flag"] == 1, "Health", "Standard")
else:
    df["Category"] = "Standard"

# 3. Inject the Trend by simulating inventory changes and stockouts
print("Simulating stock levels & injecting demand trends...")

# Sort by SKU_ID and Date to ensure correct chronological simulation
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(by=['SKU_ID', 'Date']).reset_index(drop=True)

# Convert to list of dicts for high-speed computation
records = df.to_dict('records')

inventory = {}
restocks = {}

for r in records:
    sku = r['SKU_ID']
    date = r['Date']
    
    # Initialize tracking per SKU
    if sku not in inventory:
        inventory[sku] = r['Inventory_Level']
        restocks[sku] = {}
        
    current_inv = inventory[sku]
    
    # A. Add any restocks scheduled to arrive on this day
    if date in restocks[sku]:
        current_inv += restocks[sku][date]
        del restocks[sku][date]
        
    # B. Calculate demand (double demand for Health items to model trend)
    demand = r['Units_Sold']
    if r['Category'] == 'Health':
        demand = demand * 2
        
    # C. Match demand with current inventory levels
    if current_inv >= demand:
        current_inv -= demand
        actual_sold = demand
        stockout_flag = 0
    else:
        actual_sold = current_inv
        current_inv = 0
        stockout_flag = 1
        
    # D. Trigger replenishment if inventory drops below reorder point
    if current_inv <= r['Reorder_Point']:
        lead_days = int(round(r['Supplier_Lead_Time_Days']))
        arrival_date = date + pd.Timedelta(days=lead_days)
        restocks[sku][arrival_date] = restocks[sku].get(arrival_date, 0) + r['Order_Quantity']
        
    # E. Update record state
    r['Inventory_Level'] = current_inv
    r['Units_Sold'] = actual_sold
    r['Stockout_Flag'] = stockout_flag
    inventory[sku] = current_inv

# Convert back to DataFrame
df = pd.DataFrame(records)
# Format Date back to string format for consistency
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

# 4. Save the new, modified data to a new CSV file
output_file = Path("raw_data.csv") / "modified_health_trend_data.csv"
df.to_csv(output_file, index=False)
print(f"Done! Check your folder for '{output_file}'")
