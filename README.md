# Retail Supply Chain & Consumer Health Trends Analysis

This project simulates and analyzes supply chain performance and sales trends, with a particular focus on consumer health products. It demonstrates the end-to-end journey of a **Data Analyst**: raw data cleaning/manipulation, database construction, SQL-based business analysis, and data visualization.

---

## 📂 Project Structure & File Directory

Here is an overview of the files in this repository, including their functions and what they store:

| File / Folder | Type | Description | Data Stored / Handled |
| :--- | :--- | :--- | :--- |
| **`raw_data.csv/`** | Directory | Contains the raw source datasets. | Directory containing the CSV datasets. |
| ├── `supply_chain_dataset1.csv` | CSV Data | The original, un-modified supply chain dataset. | Raw supply chain transaction details (Sales, inventory, lead times). |
| ├── `modified_health_trend_data.csv` | CSV Data | Output of the data preparation script. | Cleaned supply chain data with an injected "Health Category" trend. |
| **`data_prep.py`** | Python Script | Cleans data and injects a "Health" category trend for analysis. | Modifies columns (`Category`, `Units_Sold`) and outputs a new CSV. |
| **`create_db.py`** | Python Script | Automates SQLite database creation and loads data. | Populates `supply_chain.db` with data from the modified CSV. |
| **`supply_chain.db`** | SQLite DB | The core relational database (Git ignored). | Contains the `retail_data` table storing all retail transaction logs. |
| **`analysis.py`** | Python Script | Runs SQL queries to calculate business metrics. | Computes Revenue by Category, Stockout Risks, and Warehouse Lead Times. |
| **`visualize.py`** | Python Script | Generates analytical charts from the database. | Uses `matplotlib` and `seaborn` to output a comparison of Units Sold. |
| **`analytics_metrics.sql`** | SQL Script | Contains SQL View definitions for reuse. | Creates a SQL View (`vw_sales_trend`) for daily sales trends. |
| **`requirements.txt`** | Config File | Lists Python dependencies for this project. | Package requirements (`pandas`, `numpy`, `matplotlib`, `seaborn`). |
| **`.gitignore`** | Git Config | Tells Git which files/folders to ignore. | Excludes virtual environments, database files, and local log files. |

---

## 🚀 Data Pipeline Workflow

Follow these steps to run the pipeline sequentially:

1. **Data Prep & Trend Injection**:
   ```bash
   python data_prep.py
   ```
   *What it does:* Reads `raw_data.csv/supply_chain_dataset1.csv`, classifies products as `Health` (if skincare/cosmetics) or `Standard`, doubles the units sold for `Health` items to simulate a consumer trend, and saves the result.

2. **Database Initialization**:
   ```bash
   python create_db.py
   ```
   *What it does:* Reads the modified CSV data and writes it into a table called `retail_data` inside a newly created SQLite database file, `supply_chain.db`.

3. **Metrics Analysis (SQL)**:
   ```bash
   python analysis.py
   ```
   *What it does:* Connects to `supply_chain.db` and runs SQL queries to print critical KPI summaries (Revenue and Sales, Stockout Risks, Top Warehouse Bottlenecks).

4. **Data Visualization**:
   ```bash
   python visualize.py
   ```
   *What it does:* Queries the database and opens a Seaborn-based bar chart showcasing a visual comparison of Total Units Sold: Health vs. Standard.

---

## 🛠 Setup & Installation

To run this project on a new system:

1. **Set up a Virtual Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
