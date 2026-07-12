import streamlit as st
import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config for a premium wide layout
st.set_page_config(
    page_title="Retail Supply Chain & Consumer Health Trends Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    .sql-box {
        background-color: #212529;
        color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to run query
def run_query(query):
    conn = sqlite3.connect('supply_chain.db')
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df, None
    except Exception as e:
        conn.close()
        return None, str(e)

# Check if database exists
db_exists = os.path.exists('supply_chain.db')

# Title
st.title("📈 Retail Supply Chain & Consumer Health Trends Dashboard")
st.markdown("---")

if not db_exists:
    st.error("⚠️ Database 'supply_chain.db' not found! Please run the database creator script first:")
    st.code("python create_db.py", language="bash")
else:
    # --- Sidebar Filters ---
    st.sidebar.header("🔍 Filters")
    st.sidebar.markdown("Filter the dashboard visuals and KPIs:")

    # Get filter choices from database
    categories_df, _ = run_query("SELECT DISTINCT Category FROM retail_data")
    regions_df, _ = run_query("SELECT DISTINCT Region FROM retail_data")
    
    categories = ["All"] + sorted(categories_df["Category"].tolist())
    regions = ["All"] + sorted(regions_df["Region"].tolist())

    selected_category = st.sidebar.selectbox("Product Category", categories)
    selected_region = st.sidebar.selectbox("Region", regions)

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### ℹ️ About this Project
    This dashboard provides interactive business intelligence tools to analyze sales trends and warehouse performance, contrasting Standard items with Consumer Health items.
    """)

    # Build SQL filter clause
    where_clauses = []
    if selected_category != "All":
        where_clauses.append(f"Category = '{selected_category}'")
    if selected_region != "All":
        where_clauses.append(f"Region = '{selected_region}'")
    
    where_stmt = ""
    if where_clauses:
        where_stmt = "WHERE " + " AND ".join(where_clauses)

    # --- Load Data for KPIs ---
    kpi_query = f"""
    SELECT 
        SUM(Units_Sold) AS total_units,
        SUM(Units_Sold * Unit_Price) AS total_revenue,
        AVG(Supplier_Lead_Time_Days) AS avg_lead_time,
        SUM(CASE WHEN Inventory_Level <= Reorder_Point THEN 1 ELSE 0 END) AS reorder_alerts,
        COUNT(*) AS total_records
    FROM retail_data
    {where_stmt}
    """
    kpi_data, _ = run_query(kpi_query)

    # Extract KPI values
    total_units = int(kpi_data['total_units'].iloc[0]) if kpi_data['total_units'].iloc[0] is not None else 0
    total_revenue = float(kpi_data['total_revenue'].iloc[0]) if kpi_data['total_revenue'].iloc[0] is not None else 0.0
    avg_lead_time = float(kpi_data['avg_lead_time'].iloc[0]) if kpi_data['avg_lead_time'].iloc[0] is not None else 0.0
    reorder_alerts = int(kpi_data['reorder_alerts'].iloc[0]) if kpi_data['reorder_alerts'].iloc[0] is not None else 0
    total_records = int(kpi_data['total_records'].iloc[0]) if kpi_data['total_records'].iloc[0] is not None else 0

    # --- KPI Cards Layout ---
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}", delta=None)
    with kpi_cols[1]:
        st.metric(label="Total Units Sold", value=f"{total_units:,}", delta=None)
    with kpi_cols[2]:
        st.metric(label="Avg Supplier Lead Time", value=f"{avg_lead_time:.2f} Days", delta=None)
    with kpi_cols[3]:
        st.metric(label="Reorder Alerts (Low Stock)", value=f"{reorder_alerts:,}", delta=None, delta_color="inverse")

    st.markdown("### 📊 Key Visualizations")

    # --- Charts Row ---
    chart_cols = st.columns(2)

    with chart_cols[0]:
        st.subheader("📅 Sales Trends Over Time")
        # Load daily sales
        daily_query = f"""
        SELECT Date, Category, SUM(Units_Sold) AS Units_Sold
        FROM retail_data
        {where_stmt}
        GROUP BY Date, Category
        ORDER BY Date ASC
        """
        daily_df, _ = run_query(daily_query)
        if not daily_df.empty:
            # Pivot data for plotting
            daily_pivot = daily_df.pivot(index='Date', columns='Category', values='Units_Sold').fillna(0)
            st.line_chart(daily_pivot)
        else:
            st.info("No data available for the selected filters.")

    with chart_cols[1]:
        st.subheader("🏢 Regional Sales & Volume")
        # Load sales by region
        region_query = f"""
        SELECT Region, Category, SUM(Units_Sold) AS Units_Sold
        FROM retail_data
        {where_stmt}
        GROUP BY Region, Category
        """
        region_df, _ = run_query(region_query)
        if not region_df.empty:
            region_pivot = region_df.pivot(index='Region', columns='Category', values='Units_Sold').fillna(0)
            st.bar_chart(region_pivot)
        else:
            st.info("No data available for the selected filters.")

    # --- Warehouse Performance ---
    st.subheader("⚙️ Top Warehouse Bottlenecks (Highest Reorder Counts)")
    warehouse_query = f"""
    SELECT 
        Warehouse_ID, 
        Region,
        COUNT(CASE WHEN Inventory_Level <= Reorder_Point THEN 1 END) AS Reorder_Triggers,
        AVG(Supplier_Lead_Time_Days) AS Avg_Supplier_Lead_Time
    FROM retail_data
    {where_stmt}
    GROUP BY Warehouse_ID, Region
    ORDER BY Reorder_Triggers DESC
    LIMIT 5
    """
    warehouse_df, _ = run_query(warehouse_query)
    if not warehouse_df.empty:
        st.dataframe(warehouse_df, use_container_width=True)
    else:
        st.info("No warehouse logs fit the active filter selection.")

    st.markdown("---")

    # --- SQL Sandbox ---
    st.header("💻 Interactive SQL Sandbox")
    st.markdown("""
    Type your custom SQL queries against the database. The database contains a single main table: **`retail_data`**. 
    Press **Ctrl+Enter** or click **Execute Query** to run.
    """)

    # Show columns for reference
    with st.expander("📋 Click here to view available Database Columns & Schema"):
        columns_info = """
        - **Date**: The transaction or record date.
        - **SKU_ID**: Product identifier.
        - **Warehouse_ID**: Warehouse processing the order.
        - **Supplier_ID**: Supplier providing the SKU.
        - **Region**: Distribution region (East, North, South, West).
        - **Units_Sold**: Total quantity sold.
        - **Inventory_Level**: Current quantity in stock.
        - **Supplier_Lead_Time_Days**: Lead time for supply orders.
        - **Reorder_Point**: Inventory level that triggers a replenishment order.
        - **Order_Quantity**: Size of replenishment orders.
        - **Unit_Cost**: Cost price per unit.
        - **Unit_Price**: Selling price per unit.
        - **Promotion_Flag**: Binary indicator of promotions (1 = active, 0 = inactive).
        - **Stockout_Flag**: Binary indicator of stockout (1 = stockout, 0 = normal).
        - **Demand_Forecast**: Projected future customer demand.
        - **Category**: Product category (Health, Standard).
        """
        st.markdown(columns_info)

    # Layout for SQL sandbox
    sql_cols = st.columns([1, 2])

    with sql_cols[0]:
        st.markdown("#### 💡 Sample Queries to Try:")
        
        sample_1 = """-- Query 1: Sales & Revenue by Product Category
SELECT Category, 
       SUM(Units_Sold) AS Total_Units_Sold, 
       SUM(Units_Sold * Unit_Price) AS Total_Revenue 
FROM retail_data 
GROUP BY Category;"""

        sample_2 = """-- Query 2: Compare Forecast vs Actual Units Sold by Category
SELECT Category, 
       SUM(Units_Sold) AS Actual_Sold, 
       ROUND(SUM(Demand_Forecast), 2) AS Forecasted_Demand,
       ROUND(AVG(ABS(Units_Sold - Demand_Forecast)), 2) AS Mean_Absolute_Error
FROM retail_data 
GROUP BY Category;"""

        sample_3 = """-- Query 3: Top 5 Suppliers with Worst Average Lead Times
SELECT Supplier_ID, 
       AVG(Supplier_Lead_Time_Days) AS Avg_Lead_Time_Days
FROM retail_data 
GROUP BY Supplier_ID 
ORDER BY Avg_Lead_Time_Days DESC 
LIMIT 5;"""

        st.code(sample_1, language="sql")
        st.code(sample_2, language="sql")
        st.code(sample_3, language="sql")

    with sql_cols[1]:
        st.markdown("#### ✍️ SQL Query Editor:")
        default_query = "SELECT Category, SUM(Units_Sold) AS Total_Units FROM retail_data GROUP BY Category;"
        query_input = st.text_area("Write SQL here:", value=default_query, height=180)
        
        run_btn = st.button("⚡ Execute Query", type="primary")

        if run_btn or query_input != default_query:
            if query_input.strip() == "":
                st.warning("Please type a valid SQL query.")
            else:
                with st.spinner("Executing query..."):
                    results_df, err = run_query(query_input)
                    if err:
                        st.error(f"❌ SQL Execution Error:\n`{err}`")
                    else:
                        st.success(f"✓ Success! Query returned {len(results_df)} row(s).")
                        st.dataframe(results_df, use_container_width=True)
