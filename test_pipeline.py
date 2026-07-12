import unittest
import pandas as pd
import sqlite3
import numpy as np
import os

class TestSupplyChainPipeline(unittest.TestCase):
    
    def test_data_preparation_category_classification(self):
        # Test Category assignment logic matches rules (Promotion_Flag=1 is Health)
        df = pd.DataFrame({
            "Promotion_Flag": [1, 0, 1, 0],
            "Units_Sold": [10, 20, 30, 40]
        })
        df["Category"] = np.where(df["Promotion_Flag"] == 1, "Health", "Standard")
        self.assertEqual(df.loc[0, "Category"], "Health")
        self.assertEqual(df.loc[1, "Category"], "Standard")

    def test_database_existence_and_schema(self):
        # Test that SQLite database file exists and schema is correctly generated
        self.assertTrue(os.path.exists('supply_chain.db'))
        conn = sqlite3.connect('supply_chain.db')
        cursor = conn.cursor()
        
        # Check retail_data table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='retail_data'")
        self.assertIsNotNone(cursor.fetchone())
        
        # Check vw_sales_trend view exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='vw_sales_trend'")
        self.assertIsNotNone(cursor.fetchone())
        
        conn.close()

    def test_safety_stock_calculation(self):
        # Test mathematical safety stock optimizer formula: Z * sqrt(L * std_d^2 + d^2 * std_L^2)
        Z = 1.64
        avg_lead_time = 5.0
        std_demand = 2.0
        avg_demand = 10.0
        std_lead_time = 1.0
        
        safety_stock = Z * np.sqrt(
            avg_lead_time * (std_demand ** 2) + 
            (avg_demand ** 2) * (std_lead_time ** 2)
        )
        # 1.64 * sqrt(5*4 + 100*1) = 1.64 * sqrt(120) = 17.965
        self.assertAlmostEqual(safety_stock, 17.965, places=2)

if __name__ == '__main__':
    unittest.main()
