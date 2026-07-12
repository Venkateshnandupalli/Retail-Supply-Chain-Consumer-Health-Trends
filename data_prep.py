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

# 3. Inject the Trend by doubling units sold for Health items
units_col = "Units_Sold" if "Units_Sold" in df.columns else None
if units_col is None:
    raise KeyError("Expected 'Units_Sold' column in the dataset")

is_health = df["Category"] == "Health"
print("Injecting trend into:", units_col)
df.loc[is_health, units_col] = df.loc[is_health, units_col] * 2

# 4. Save the new, modified data to a new CSV file
output_file = Path("raw_data.csv") / "modified_health_trend_data.csv"
df.to_csv(output_file, index=False)
print(f"Done! Check your folder for '{output_file}'")
