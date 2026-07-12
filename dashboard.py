import streamlit as st
import pandas as pd
import sqlite3
import os
import numpy as np
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
    .stMetric {
        background-color: var(--secondary-background-color);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid var(--border-color, #e9ecef);
    }
    .sql-box {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        padding: 15px;
        border-radius: 5px;
        font-family: monospace;
        border: 1px solid var(--border-color, #e9ecef);
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
    # --- Sidebar Filters & Target Settings ---
    st.sidebar.header("🔍 Filters & Parameters")
    st.sidebar.markdown("Configure the dashboard parameters:")

    # Get filter choices from database
    categories_df, _ = run_query("SELECT DISTINCT Category FROM retail_data")
    regions_df, _ = run_query("SELECT DISTINCT Region FROM retail_data")
    
    categories = ["All"] + sorted(categories_df["Category"].tolist())
    regions = ["All"] + sorted(regions_df["Region"].tolist())

    selected_category = st.sidebar.selectbox("Product Category", categories)
    selected_region = st.sidebar.selectbox("Region", regions)

    st.sidebar.markdown("---")
    st.sidebar.header("🛡️ Safety Stock Settings")
    service_level = st.sidebar.selectbox("Target Service Level", ["90%", "95%", "99%"], index=1)
    
    st.sidebar.markdown("---")
    st.sidebar.header("⚡ SC Stress Testing")
    st.sidebar.markdown("Simulate supply chain shocks:")
    demand_surge = st.sidebar.slider("Demand Surge (% Increase)", min_value=0, max_value=100, value=0, step=10)
    supplier_delay = st.sidebar.slider("Supplier Delay (Days)", min_value=0, max_value=10, value=0, step=1)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### ℹ️ About this Project
    This industry-grade dashboard provides interactive intelligence to optimize stock levels, forecast retail demand, analyze supplier risk, and run custom queries.
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

    # --- KPI Cards Layout ---
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}", delta=None)
    with kpi_cols[1]:
        st.metric(label="Total Units Sold", value=f"{total_units:,}", delta=None)
    with kpi_cols[2]:
        st.metric(label="Avg Supplier Lead Time", value=f"{avg_lead_time:.2f} Days", delta=None)
    with kpi_cols[3]:
        st.metric(label="Low Stock Alerts (Static ROP)", value=f"{reorder_alerts:,}", delta=None)

    st.markdown("---")

    # Define Tabs
    tabs = st.tabs([
        "📈 Executive Overview", 
        "🛡️ Inventory Optimization", 
        "🔮 Demand Forecasting", 
        "🤝 Supplier Risk Profile", 
        "💻 SQL Sandbox"
    ])

    # ==========================================
    # TAB 1: EXECUTIVE OVERVIEW
    # ==========================================
    with tabs[0]:
        st.markdown("### 📊 Key Performance Visualizations")
        chart_cols = st.columns(2)

        with chart_cols[0]:
            st.subheader("📅 Sales Trends Over Time")
            daily_query = f"""
            SELECT Date, Category, SUM(Units_Sold) AS Units_Sold
            FROM retail_data
            {where_stmt}
            GROUP BY Date, Category
            ORDER BY Date ASC
            """
            daily_df, _ = run_query(daily_query)
            if not daily_df.empty:
                daily_pivot = daily_df.pivot(index='Date', columns='Category', values='Units_Sold').fillna(0)
                st.line_chart(daily_pivot)
            else:
                st.info("No data available for the selected filters.")

        with chart_cols[1]:
            st.subheader("🏢 Regional Sales Volume")
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

        # Warehouse Performance
        st.subheader("⚙️ Top Warehouse Bottlenecks (Highest Static Reorder Alerts)")
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
            st.dataframe(warehouse_df, width="stretch")
        else:
            st.info("No warehouse logs fit the active filter selection.")

    # ==========================================
    # TAB 2: INVENTORY OPTIMIZATION
    # ==========================================
    with tabs[1]:
        st.markdown("### 🛡️ Dynamic Safety Stock & Reorder Optimization")
        st.markdown("""
        This tab calculates **Safety Stock** and **Dynamic Reorder Points** based on historical sales variability and supplier lead time deviations. 
        It provides actionable recommendations on when to restock and how much to order.
        """)

        # Get Z-Score mapping
        z_score_map = {"90%": 1.28, "95%": 1.64, "99%": 2.33}
        Z = z_score_map[service_level]

        # Fetch optimization raw records
        opt_query = f"""
        SELECT SKU_ID, Category, Units_Sold, Supplier_Lead_Time_Days, Inventory_Level, Date, Reorder_Point, Order_Quantity
        FROM retail_data
        {where_stmt}
        """
        opt_df, _ = run_query(opt_query)
        
        if opt_df is not None and not opt_df.empty:
            # Group by SKU_ID and Category to get stats
            stats = opt_df.groupby(['SKU_ID', 'Category']).agg(
                avg_demand=('Units_Sold', 'mean'),
                std_demand=('Units_Sold', 'std'),
                avg_lead_time=('Supplier_Lead_Time_Days', 'mean'),
                std_lead_time=('Supplier_Lead_Time_Days', 'std'),
                avg_order_qty=('Order_Quantity', 'mean')
            ).reset_index()

            # Find the latest inventory record for each SKU
            latest_idx = opt_df.groupby('SKU_ID')['Date'].idxmax()
            latest_inv = opt_df.loc[latest_idx, ['SKU_ID', 'Inventory_Level']]

            # Merge
            stats = pd.merge(stats, latest_inv, on='SKU_ID')
            stats = stats.fillna(0)

            # 1. Base calculations
            stats['Safety_Stock'] = Z * np.sqrt(
                stats['avg_lead_time'] * (stats['std_demand'] ** 2) + 
                (stats['avg_demand'] ** 2) * (stats['std_lead_time'] ** 2)
            )

            # ROP = (Average Daily Demand * Average Lead Time) + Safety Stock
            stats['Dynamic_ROP'] = (stats['avg_demand'] * stats['avg_lead_time']) + stats['Safety_Stock']
            
            # Status and recommended order quantities
            stats['Status'] = np.where(stats['Inventory_Level'] <= stats['Dynamic_ROP'], "🚨 Reorder", "✅ Healthy")
            
            # 2. What-If Shock calculations
            shock_demand = stats['avg_demand'] * (1 + demand_surge / 100)
            shock_lead_time = stats['avg_lead_time'] + supplier_delay

            stats['Shock_Safety_Stock'] = Z * np.sqrt(
                shock_lead_time * (stats['std_demand'] ** 2) + 
                (shock_demand ** 2) * (stats['std_lead_time'] ** 2)
            )
            stats['Shock_ROP'] = (shock_demand * shock_lead_time) + stats['Shock_Safety_Stock']
            stats['Shock_Status'] = np.where(stats['Inventory_Level'] <= stats['Shock_ROP'], "🚨 Reorder", "✅ Healthy")
            
            # Determine vulnerability
            stats['Vulnerability'] = np.where(
                (stats['Status'] == "✅ Healthy") & (stats['Shock_Status'] == "🚨 Reorder"),
                "⚠️ Vulnerable",
                np.where(stats['Status'] == "🚨 Reorder", "🚨 Reorder", "✅ Stable")
            )
            
            # Shock recommended quantities
            stats['Shock_Suggested_Order_Qty'] = np.where(
                stats['Inventory_Level'] <= stats['Shock_ROP'],
                np.maximum(stats['avg_order_qty'], stats['Shock_ROP'] - stats['Inventory_Level']).round(0),
                0
            )

            # Format outputs for rendering
            stats['Safety_Stock'] = stats['Safety_Stock'].round(1)
            stats['Dynamic_ROP'] = stats['Dynamic_ROP'].round(1)
            stats['Shock_Safety_Stock'] = stats['Shock_Safety_Stock'].round(1)
            stats['Shock_ROP'] = stats['Shock_ROP'].round(1)
            stats['avg_demand'] = stats['avg_demand'].round(1)
            stats['avg_lead_time'] = stats['avg_lead_time'].round(1)

            # Compare counts
            reorder_count = len(stats[stats['Status'] == "🚨 Reorder"])
            shock_reorder_count = len(stats[stats['Shock_Status'] == "🚨 Reorder"])
            vulnerable_count = len(stats[stats['Vulnerability'] == "⚠️ Vulnerable"])
            
            sub_cols = st.columns(4)
            with sub_cols[0]:
                st.metric(label="Target Z-Score", value=f"{Z}")
            with sub_cols[1]:
                st.metric(label="Reorder Alerts (Normal)", value=f"{reorder_count}", delta=None)
            with sub_cols[2]:
                st.metric(
                    label="Reorder Alerts (Shocked)", 
                    value=f"{shock_reorder_count}", 
                    delta=f"+{shock_reorder_count - reorder_count}" if shock_reorder_count > reorder_count else None,
                    delta_color="inverse"
                )
            with sub_cols[3]:
                st.metric(
                    label="Vulnerable SKUs at Risk", 
                    value=f"{vulnerable_count}", 
                    delta="Risk Alert" if vulnerable_count > 0 else None,
                    delta_color="inverse"
                )

            # Warning callout
            if vulnerable_count > 0:
                st.warning(f"⚠️ **Stress Test Warning:** Simulated shock (Demand Surge: +{demand_surge}%, Supplier Delay: +{supplier_delay} Days) "
                           f"puts **{vulnerable_count} SKUs** at risk of running out of stock! These items are flagged as **⚠️ Vulnerable** below.")

            st.markdown("#### SKU-Level Restocking Recommendations under Stress Test")
            
            # View toggle
            show_mode = st.radio(
                "Display Filter:", 
                ["Show All SKUs", "Show Reorder Alerts (Normal) Only", "Show Reorder Alerts (Shocked) Only", "Show Vulnerable SKUs Only"],
                horizontal=True
            )

            display_stats = stats.copy()
            if show_mode == "Show Reorder Alerts (Normal) Only":
                display_stats = display_stats[display_stats['Status'] == "🚨 Reorder"]
            elif show_mode == "Show Reorder Alerts (Shocked) Only":
                display_stats = display_stats[display_stats['Shock_Status'] == "🚨 Reorder"]
            elif show_mode == "Show Vulnerable SKUs Only":
                display_stats = display_stats[display_stats['Vulnerability'] == "⚠️ Vulnerable"]

            st.dataframe(
                display_stats[[
                    'SKU_ID', 'Category', 'Inventory_Level', 'avg_demand', 
                    'avg_lead_time', 'Safety_Stock', 'Dynamic_ROP', 'Shock_ROP', 'Vulnerability', 'Shock_Suggested_Order_Qty'
                ]],
                width="stretch"
            )
        else:
            st.info("No stock data found.")

    # ==========================================
    # TAB 3: DEMAND FORECASTING
    # ==========================================
    with tabs[2]:
        st.markdown("### 🔮 30-Day Demand Forecasting (Linear Trend + Weekly Seasonality)")
        st.markdown("""
        This predictive model analyzes daily sales volume to project demand for the next 30 days. It fits a **linear regression trend line** 
        and overlays **weekly seasonal index factors** to model day-of-week sales fluctuations.
        """)

        fc_query = f"""
        SELECT Date, SUM(Units_Sold) AS Units_Sold
        FROM retail_data
        {where_stmt}
        GROUP BY Date
        ORDER BY Date ASC
        """
        fc_df, _ = run_query(fc_query)

        if fc_df is not None and len(fc_df) >= 7:
            fc_df['Date'] = pd.to_datetime(fc_df['Date'])
            
            # Numeric day indices for regression
            fc_df['DayIndex'] = (fc_df['Date'] - fc_df['Date'].min()).dt.days
            
            # Fit line: y = mx + c
            x = fc_df['DayIndex'].values
            y = fc_df['Units_Sold'].values
            m, c = np.polyfit(x, y, 1)

            # Weekly Seasonal Factor (Units_Sold_Avg_For_Weekday / Units_Sold_Avg_Overall)
            fc_df['DayOfWeek'] = fc_df['Date'].dt.dayofweek
            avg_by_dow = fc_df.groupby('DayOfWeek')['Units_Sold'].mean()
            overall_mean = fc_df['Units_Sold'].mean()
            seasonal_factors = (avg_by_dow / overall_mean).to_dict()

            # Generate 30 future dates
            last_date = fc_df['Date'].max()
            future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, 31)]
            future_indices = [(d - fc_df['Date'].min()).days for d in future_dates]

            future_data = []
            for d, idx in zip(future_dates, future_indices):
                trend = m * idx + c
                dow = d.dayofweek
                factor = seasonal_factors.get(dow, 1.0)
                forecasted_val = max(0, trend * factor)
                future_data.append({
                    'Date': d.strftime('%Y-%m-%d'),
                    'Units_Sold': round(forecasted_val, 1),
                    'Type': 'Forecasted'
                })

            future_df = pd.DataFrame(future_data)
            
            # Prepare plotting DataFrame
            historical_plot = fc_df[['Date', 'Units_Sold']].copy()
            historical_plot['Type'] = 'Historical'
            historical_plot['Date'] = historical_plot['Date'].dt.strftime('%Y-%m-%d')

            combined_df = pd.concat([historical_plot, future_df], ignore_index=True)
            combined_df = combined_df.pivot(index='Date', columns='Type', values='Units_Sold')

            # Render Chart
            st.subheader("Forecasted Sales Projections")
            st.line_chart(combined_df)
            
            st.subheader("Next 30-Day Forecast Table")
            st.dataframe(future_df, width="stretch")
        else:
            st.warning("Insufficient historical data to construct a robust time-series forecast. Requires at least 7 days of logs.")

    # ==========================================
    # TAB 4: SUPPLIER RISK PROFILE
    # ==========================================
    with tabs[3]:
        st.markdown("### 🤝 Supplier Reliability Scorecard")
        st.markdown("""
        Assess the reliability of suppliers based on delivery timeline consistency.
        **Scorecard Weighting:** Scores are out of 100. Points are deducted for long lead times (-4 pts/day) and delivery inconsistency / standard deviation (-12 pts/day).
        """)

        sup_query = f"""
        SELECT Supplier_ID, Supplier_Lead_Time_Days
        FROM retail_data
        {where_stmt}
        """
        sup_df, _ = run_query(sup_query)

        if sup_df is not None and not sup_df.empty:
            sup_stats = sup_df.groupby('Supplier_ID').agg(
                avg_lead_time=('Supplier_Lead_Time_Days', 'mean'),
                std_lead_time=('Supplier_Lead_Time_Days', 'std'),
                total_deliveries=('Supplier_Lead_Time_Days', 'count')
            ).reset_index()

            sup_stats = sup_stats.fillna(0)

            # Score Formula: 100 - (avg_lead_time * 4) - (std_lead_time * 12)
            sup_stats['Score'] = 100 - (sup_stats['avg_lead_time'] * 4) - (sup_stats['std_lead_time'] * 12)
            sup_stats['Score'] = sup_stats['Score'].clip(lower=0, upper=100).round(1)

            # Determine Risk Status
            conditions = [
                (sup_stats['Score'] >= 75),
                (sup_stats['Score'] >= 50) & (sup_stats['Score'] < 75),
                (sup_stats['Score'] < 50)
            ]
            choices = ['🟢 Low Risk', '🟡 Medium Risk', '🔴 High Risk']
            sup_stats['Risk_Category'] = np.select(conditions, choices, default='🔴 High Risk')

            # Round lead times for readability
            sup_stats['avg_lead_time'] = sup_stats['avg_lead_time'].round(2)
            sup_stats['std_lead_time'] = sup_stats['std_lead_time'].round(2)

            # Display
            st.dataframe(
                sup_stats.sort_values(by='Score', ascending=False),
                width="stretch"
            )
        else:
            st.info("No supplier records found.")

    # ==========================================
    # TAB 5: SQL SANDBOX
    # ==========================================
    with tabs[4]:
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
                            st.dataframe(results_df, width="stretch")
