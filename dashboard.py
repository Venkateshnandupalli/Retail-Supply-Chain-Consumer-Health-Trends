import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SupplyIQ · Retail Analytics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Venkateshnandupalli/Retail-Supply-Chain-Consumer-Health-Trends',
        'About': "SupplyIQ — Retail Supply Chain & Consumer Health Trends Analytics Dashboard"
    }
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS  (glassmorphism · dark palette · Inter font · micro-animations)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1b2a 40%, #0f2440 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #0a1628 60%, #071020 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.25) !important;
}
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] .stMarkdown h4 {
    color: #a5b4fc !important;
    letter-spacing: 0.04em;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    font-weight: 600;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
}

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1e3a5f 0%, #1a1a5e 40%, #2d1b69 100%);
    border: 1px solid rgba(99,102,241,0.4);
    border-radius: 20px;
    padding: 36px 44px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero-banner::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: 20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(34,211,238,0.1) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #e0e7ff 0%, #a5b4fc 50%, #22d3ee 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 8px 0;
    line-height: 1.2;
}
.hero-subtitle {
    color: #94a3b8;
    font-size: 1.05rem;
    font-weight: 400;
    margin: 0 0 20px 0;
}
.hero-badges {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
.badge {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #cbd5e1;
    backdrop-filter: blur(10px);
    letter-spacing: 0.03em;
}
.badge-blue  { border-color: rgba(99,102,241,0.5); color: #a5b4fc; }
.badge-teal  { border-color: rgba(34,211,238,0.5); color: #67e8f9; }
.badge-green { border-color: rgba(16,185,129,0.5); color: #6ee7b7; }
.badge-amber { border-color: rgba(245,158,11,0.5); color: #fcd34d; }
.hero-timestamp {
    position: absolute;
    top: 24px;
    right: 32px;
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 500;
    letter-spacing: 0.02em;
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 28px;
}
.kpi-card {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px;
    padding: 24px 22px 20px;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(20px);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.5);
    border-color: rgba(99,102,241,0.5);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}
.kpi-card.blue::before  { background: linear-gradient(90deg, #6366f1, #818cf8); }
.kpi-card.teal::before  { background: linear-gradient(90deg, #06b6d4, #22d3ee); }
.kpi-card.green::before { background: linear-gradient(90deg, #10b981, #34d399); }
.kpi-card.amber::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.kpi-icon-badge {
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    margin-bottom: 14px;
}
.kpi-icon-badge.blue  { background: rgba(99,102,241,0.2); border: 1px solid rgba(99,102,241,0.4); }
.kpi-icon-badge.teal  { background: rgba(6,182,212,0.2);  border: 1px solid rgba(6,182,212,0.4);  }
.kpi-icon-badge.green { background: rgba(16,185,129,0.2); border: 1px solid rgba(16,185,129,0.4); }
.kpi-icon-badge.amber { background: rgba(245,158,11,0.2); border: 1px solid rgba(245,158,11,0.4); }
.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #e2e8f0;
    line-height: 1;
    margin-bottom: 6px;
}
.kpi-delta {
    font-size: 0.78rem;
    font-weight: 600;
    color: #64748b;
}
.kpi-glow {
    position: absolute;
    bottom: -20px; right: -20px;
    width: 80px; height: 80px;
    border-radius: 50%;
    opacity: 0.08;
}
.kpi-glow.blue  { background: #6366f1; }
.kpi-glow.teal  { background: #06b6d4; }
.kpi-glow.green { background: #10b981; }
.kpi-glow.amber { background: #f59e0b; }

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(99,102,241,0.2);
}
.section-header-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #6366f1, #818cf8);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.section-header-text h3 {
    margin: 0;
    font-size: 1.15rem;
    font-weight: 700;
    color: #e2e8f0;
}
.section-header-text p {
    margin: 2px 0 0;
    font-size: 0.78rem;
    color: #64748b;
}

/* ── Chart Container ── */
.chart-panel {
    background: rgba(15,23,42,0.8);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(15,23,42,0.9) !important;
    border-radius: 14px !important;
    padding: 6px !important;
    gap: 4px !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    margin-bottom: 24px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: #fff !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.4) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.02em !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.5) !important;
}

/* ── Selectbox / Slider / Text Input ── */
.stSelectbox [data-baseweb="select"] > div,
.stTextInput > div > div {
    background: rgba(15,23,42,0.9) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
.stTextArea textarea {
    background: rgba(15,23,42,0.9) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    font-size: 0.85rem !important;
}
.stTextArea textarea:focus {
    border-color: rgba(99,102,241,0.7) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}

/* ── Info / Warning / Error ── */
.stAlert {
    border-radius: 12px !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
}

/* ── Radio ── */
.stRadio > label {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(15,23,42,0.8) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    color: #a5b4fc !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
}

/* ── Footer ── */
.footer-panel {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px;
    padding: 22px 30px;
    margin-top: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    backdrop-filter: blur(10px);
}
.footer-left {
    display: flex; flex-direction: column; gap: 4px;
}
.footer-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #a5b4fc;
}
.footer-sub {
    font-size: 0.72rem;
    color: #475569;
}
.tech-badges {
    display: flex; gap: 8px; flex-wrap: wrap;
}
.tech-badge {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.7rem;
    font-weight: 600;
    color: #a5b4fc;
    letter-spacing: 0.03em;
}

/* ── Divider ── */
.styled-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.4), transparent);
    margin: 28px 0;
    border: none;
}

/* ── Info boxes ── */
.info-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #a5b4fc;
    margin: 4px;
}
.warning-pill {
    background: rgba(245,158,11,0.12);
    border-color: rgba(245,158,11,0.3);
    color: #fcd34d;
}
.danger-pill {
    background: rgba(239,68,68,0.12);
    border-color: rgba(239,68,68,0.3);
    color: #fca5a5;
}
.success-pill {
    background: rgba(16,185,129,0.12);
    border-color: rgba(16,185,129,0.3);
    color: #6ee7b7;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# MATPLOTLIB DARK THEME  (used throughout)
# ──────────────────────────────────────────────────────────────────────────────
CHART_BG      = "#0a0f1e"
CHART_PANEL   = "#0d1b2a"
CHART_BORDER  = "#1e2d45"
PALETTE       = ["#6366f1", "#22d3ee", "#10b981", "#f59e0b", "#f43f5e", "#8b5cf6"]

def apply_dark_style(ax, fig):
    fig.patch.set_facecolor(CHART_BG)
    ax.set_facecolor(CHART_PANEL)
    ax.tick_params(colors="#64748b", labelsize=9)
    ax.xaxis.label.set_color("#94a3b8")
    ax.yaxis.label.set_color("#94a3b8")
    ax.title.set_color("#e2e8f0")
    for spine in ax.spines.values():
        spine.set_edgecolor(CHART_BORDER)
    ax.grid(True, color=CHART_BORDER, linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)

# ──────────────────────────────────────────────────────────────────────────────
# DATABASE HELPER
# ──────────────────────────────────────────────────────────────────────────────
def run_query(query):
    conn = sqlite3.connect('supply_chain.db')
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df, None
    except Exception as e:
        conn.close()
        return None, str(e)

# ──────────────────────────────────────────────────────────────────────────────
# AUTO-INIT DATABASE
# ──────────────────────────────────────────────────────────────────────────────
db_exists = os.path.exists('supply_chain.db')

if not db_exists:
    with st.spinner("⏳ First-time setup: Building the data pipeline and database…"):
        try:
            result = subprocess.run([sys.executable, 'run_pipeline.py'], capture_output=True, text=True)
            if result.returncode == 0:
                db_exists = True
            else:
                st.error(f"❌ Failed to initialize database:\n```\n{result.stderr}\n```")
        except Exception as e:
            st.error(f"❌ Error running pipeline: {str(e)}")

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 16px 0 24px;">
        <div style="font-size:2.6rem; margin-bottom:8px;">📦</div>
        <div style="font-size:1.1rem; font-weight:800; 
                    background:linear-gradient(135deg,#a5b4fc,#22d3ee);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    background-clip:text; letter-spacing:-0.02em;">SupplyIQ</div>
        <div style="font-size:0.68rem; color:#475569; font-weight:500; 
                    text-transform:uppercase; letter-spacing:0.1em; margin-top:3px;">
            Retail Analytics Platform
        </div>
    </div>
    <hr style="border:none; border-top:1px solid rgba(99,102,241,0.25); margin:0 0 20px;">
    """, unsafe_allow_html=True)

    st.markdown("### 🔍 Filters")
    if db_exists:
        categories_df, _ = run_query("SELECT DISTINCT Category FROM retail_data")
        regions_df, _    = run_query("SELECT DISTINCT Region FROM retail_data")
        categories = ["All"] + sorted(categories_df["Category"].tolist())
        regions    = ["All"] + sorted(regions_df["Region"].tolist())
        selected_category = st.selectbox("Product Category", categories, key="cat_filter")
        selected_region   = st.selectbox("Region", regions, key="reg_filter")
    else:
        selected_category = "All"
        selected_region   = "All"

    st.markdown("<hr style='border:none;border-top:1px solid rgba(99,102,241,0.2);margin:20px 0;'>", unsafe_allow_html=True)

    st.markdown("### 🛡️ Safety Stock")
    service_level = st.selectbox("Target Service Level", ["90%", "95%", "99%"], index=1, key="svc_lvl")
    z_score_map   = {"90%": 1.28, "95%": 1.64, "99%": 2.33}
    Z             = z_score_map[service_level]

    st.markdown("<hr style='border:none;border-top:1px solid rgba(99,102,241,0.2);margin:20px 0;'>", unsafe_allow_html=True)

    st.markdown("### ⚡ Stress Test")
    demand_surge   = st.slider("Demand Surge (%)",       0, 100, 0, 10, key="demand_surge")
    supplier_delay = st.slider("Supplier Delay (Days)",  0,  10, 0,  1, key="sup_delay")

    st.markdown("<hr style='border:none;border-top:1px solid rgba(99,102,241,0.2);margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.7rem; color:#334155; text-align:center; line-height:1.7;">
        Built with 🐍 Python · SQLite · Streamlit<br>
        <a href="https://github.com/Venkateshnandupalli/Retail-Supply-Chain-Consumer-Health-Trends" 
           target="_blank" style="color:#6366f1; text-decoration:none;">View on GitHub ↗</a>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT
# ──────────────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%d %b %Y · %H:%M")

st.markdown(f"""
<div class="hero-banner">
    <span class="hero-timestamp">🕐 {now_str}</span>
    <h1 class="hero-title">Retail Supply Chain &amp;<br>Consumer Health Trends</h1>
    <p class="hero-subtitle">
        Enterprise-grade analytics for supply chain intelligence, demand forecasting, 
        and supplier risk assessment — powered by real simulation data.
    </p>
    <div class="hero-badges">
        <span class="badge badge-blue">📦 Supply Chain</span>
        <span class="badge badge-teal">💊 Health Trends</span>
        <span class="badge badge-green">📊 Real-Time KPIs</span>
        <span class="badge badge-amber">🔮 Demand Forecasting</span>
        <span class="badge">🛡️ Safety Stock Optimizer</span>
        <span class="badge">💻 SQL Sandbox</span>
    </div>
</div>
""", unsafe_allow_html=True)

if not db_exists:
    st.error("⚠️ Database initialization failed. Please run `python run_pipeline.py` in your terminal.")
    st.stop()

# ── SQL FILTER CLAUSE ──────────────────────────────────────────────────────
where_clauses = []
if selected_category != "All":
    where_clauses.append(f"Category = '{selected_category}'")
if selected_region != "All":
    where_clauses.append(f"Region = '{selected_region}'")
where_stmt = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

# ── LOAD KPIs ──────────────────────────────────────────────────────────────
kpi_data, _ = run_query(f"""
    SELECT 
        SUM(Units_Sold)                                                   AS total_units,
        SUM(Units_Sold * Unit_Price)                                      AS total_revenue,
        AVG(Supplier_Lead_Time_Days)                                      AS avg_lead_time,
        SUM(CASE WHEN Inventory_Level <= Reorder_Point THEN 1 ELSE 0 END) AS reorder_alerts
    FROM retail_data {where_stmt}
""")
total_units    = int(kpi_data['total_units'].iloc[0])    if kpi_data['total_units'].iloc[0]    is not None else 0
total_revenue  = float(kpi_data['total_revenue'].iloc[0]) if kpi_data['total_revenue'].iloc[0] is not None else 0.0
avg_lead_time  = float(kpi_data['avg_lead_time'].iloc[0]) if kpi_data['avg_lead_time'].iloc[0] is not None else 0.0
reorder_alerts = int(kpi_data['reorder_alerts'].iloc[0]) if kpi_data['reorder_alerts'].iloc[0] is not None else 0

# ── KPI CARDS ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card blue">
    <div class="kpi-glow blue"></div>
    <div class="kpi-icon-badge blue">💰</div>
    <div class="kpi-label">Total Revenue</div>
    <div class="kpi-value">${total_revenue/1e6:.2f}M</div>
    <div class="kpi-delta">Across all transactions</div>
  </div>
  <div class="kpi-card teal">
    <div class="kpi-glow teal"></div>
    <div class="kpi-icon-badge teal">📦</div>
    <div class="kpi-label">Units Sold</div>
    <div class="kpi-value">{total_units:,}</div>
    <div class="kpi-delta">Total units dispatched</div>
  </div>
  <div class="kpi-card green">
    <div class="kpi-glow green"></div>
    <div class="kpi-icon-badge green">🚚</div>
    <div class="kpi-label">Avg Lead Time</div>
    <div class="kpi-value">{avg_lead_time:.1f}d</div>
    <div class="kpi-delta">Supplier delivery average</div>
  </div>
  <div class="kpi-card amber">
    <div class="kpi-glow amber"></div>
    <div class="kpi-icon-badge amber">⚠️</div>
    <div class="kpi-label">Reorder Alerts</div>
    <div class="kpi-value">{reorder_alerts:,}</div>
    <div class="kpi-delta">SKUs below reorder point</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📈 Executive Overview",
    "🛡️ Inventory Optimization",
    "🔮 Demand Forecasting",
    "🤝 Supplier Risk Profile",
    "💻 SQL Sandbox"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 · EXECUTIVE OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("""
    <div class="section-header">
        <div class="section-header-icon">📊</div>
        <div class="section-header-text">
            <h3>Key Performance Visualizations</h3>
            <p>Sales trends, regional breakdown, and operational bottlenecks</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)

    # --- Sales Trend Chart ---
    with chart_col1:
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        daily_df, _ = run_query(f"""
            SELECT Date, Category, SUM(Units_Sold) AS Units_Sold
            FROM retail_data {where_stmt}
            GROUP BY Date, Category ORDER BY Date ASC
        """)
        if daily_df is not None and not daily_df.empty:
            daily_pivot = daily_df.pivot(index='Date', columns='Category', values='Units_Sold').fillna(0)
            fig, ax = plt.subplots(figsize=(7, 3.8))
            apply_dark_style(ax, fig)
            for i, col in enumerate(daily_pivot.columns):
                dates = range(len(daily_pivot))
                ax.plot(dates, daily_pivot[col].values, color=PALETTE[i], linewidth=2,
                        label=col, alpha=0.9)
                ax.fill_between(dates, daily_pivot[col].values, alpha=0.08, color=PALETTE[i])
            ax.set_title("📅 Daily Sales Trends by Category", fontsize=11, fontweight='bold', pad=12, color="#e2e8f0")
            ax.set_xlabel("Day Index", fontsize=9)
            ax.set_ylabel("Units Sold", fontsize=9)
            step = max(1, len(daily_pivot) // 6)
            ax.set_xticks(range(0, len(daily_pivot), step))
            ax.set_xticklabels([daily_pivot.index[i] for i in range(0, len(daily_pivot), step)],
                               rotation=30, ha='right', fontsize=7.5, color="#64748b")
            legend = ax.legend(frameon=True, facecolor="#0d1b2a", edgecolor="#1e2d45",
                                labelcolor="#94a3b8", fontsize=8.5)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        else:
            st.info("No data for selected filters.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Regional Bar Chart ---
    with chart_col2:
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        region_df, _ = run_query(f"""
            SELECT Region, Category, SUM(Units_Sold) AS Units_Sold
            FROM retail_data {where_stmt}
            GROUP BY Region, Category
        """)
        if region_df is not None and not region_df.empty:
            region_pivot = region_df.pivot(index='Region', columns='Category', values='Units_Sold').fillna(0)
            fig, ax = plt.subplots(figsize=(7, 3.8))
            apply_dark_style(ax, fig)
            n_cats = len(region_pivot.columns)
            x = np.arange(len(region_pivot))
            width = 0.7 / n_cats
            for i, col in enumerate(region_pivot.columns):
                bars = ax.bar(x + i * width, region_pivot[col].values,
                              width=width, color=PALETTE[i], alpha=0.9,
                              label=col, edgecolor="none", linewidth=0)
                for bar in bars:
                    bar.set_linewidth(0)
            ax.set_title("🏢 Regional Sales Volume", fontsize=11, fontweight='bold', pad=12, color="#e2e8f0")
            ax.set_xticks(x + width * (n_cats - 1) / 2)
            ax.set_xticklabels(region_pivot.index, fontsize=9, color="#94a3b8")
            ax.set_ylabel("Units Sold", fontsize=9)
            legend = ax.legend(frameon=True, facecolor="#0d1b2a", edgecolor="#1e2d45",
                                labelcolor="#94a3b8", fontsize=8.5)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        else:
            st.info("No data for selected filters.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Stockout Rate Pie Chart + Warehouse Table ---
    pie_col, tbl_col = st.columns([1, 2])

    with pie_col:
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        stockout_df, _ = run_query(f"""
            SELECT Category,
                   SUM(Stockout_Flag) AS stockouts,
                   COUNT(*) - SUM(Stockout_Flag) AS healthy
            FROM retail_data {where_stmt}
            GROUP BY Category
        """)
        if stockout_df is not None and not stockout_df.empty:
            fig, ax = plt.subplots(figsize=(4.5, 3.8))
            fig.patch.set_facecolor(CHART_BG)
            labels, sizes, colors_pie = [], [], []
            c_map = {"Health Stockout": "#f43f5e", "Health Healthy": "#10b981",
                     "Standard Stockout": "#f59e0b", "Standard Healthy": "#6366f1"}
            for _, row in stockout_df.iterrows():
                labels += [f"{row['Category']} Stockout", f"{row['Category']} Healthy"]
                sizes  += [row['stockouts'], row['healthy']]
                colors_pie += [c_map.get(f"{row['Category']} Stockout", "#f43f5e"),
                               c_map.get(f"{row['Category']} Healthy", "#10b981")]
            wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.0f%%',
                colors=colors_pie, startangle=90, pctdistance=0.75,
                wedgeprops=dict(width=0.55, edgecolor=CHART_BG, linewidth=2))
            for t in autotexts:
                t.set_color("#e2e8f0"); t.set_fontsize(8)
            ax.set_title("🚨 Stockout vs Healthy", fontsize=10, fontweight='bold',
                          color="#e2e8f0", pad=10)
            patches = [mpatches.Patch(color=colors_pie[i], label=labels[i]) for i in range(len(labels))]
            ax.legend(handles=patches, loc='lower center', bbox_to_anchor=(0.5,-0.12),
                      ncol=2, frameon=False, labelcolor="#94a3b8", fontsize=7)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        st.markdown('</div>', unsafe_allow_html=True)

    with tbl_col:
        st.markdown("""
        <div class="section-header" style="margin-top:0;">
            <div class="section-header-icon" style="background:linear-gradient(135deg,#f59e0b,#fbbf24);">⚙️</div>
            <div class="section-header-text">
                <h3>Top Warehouse Bottlenecks</h3>
                <p>Warehouses with highest static reorder alerts</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        warehouse_df, _ = run_query(f"""
            SELECT Warehouse_ID, Region,
                   COUNT(CASE WHEN Inventory_Level <= Reorder_Point THEN 1 END) AS Reorder_Triggers,
                   ROUND(AVG(Supplier_Lead_Time_Days), 2) AS Avg_Lead_Time
            FROM retail_data {where_stmt}
            GROUP BY Warehouse_ID, Region
            ORDER BY Reorder_Triggers DESC LIMIT 8
        """)
        if warehouse_df is not None and not warehouse_df.empty:
            st.dataframe(
                warehouse_df,
                use_container_width=True,
                column_config={
                    "Warehouse_ID":      st.column_config.TextColumn("Warehouse"),
                    "Region":            st.column_config.TextColumn("Region"),
                    "Reorder_Triggers":  st.column_config.ProgressColumn("Reorder Triggers", format="%d",
                                            min_value=0, max_value=int(warehouse_df["Reorder_Triggers"].max())),
                    "Avg_Lead_Time":     st.column_config.NumberColumn("Avg Lead Time (d)", format="%.2f"),
                },
                hide_index=True
            )
        else:
            st.info("No warehouse data.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 · INVENTORY OPTIMIZATION
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("""
    <div class="section-header">
        <div class="section-header-icon" style="background:linear-gradient(135deg,#10b981,#34d399);">🛡️</div>
        <div class="section-header-text">
            <h3>Dynamic Safety Stock &amp; Reorder Optimization</h3>
            <p>Calculates optimal safety stock and dynamic reorder points from demand variability &amp; supplier lead time</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25); 
                border-radius:12px; padding:16px 20px; margin-bottom:20px; font-size:0.85rem; color:#94a3b8;">
        📐 <strong style="color:#6ee7b7;">Safety Stock Formula:</strong> 
        &nbsp;SS = Z × √(L̄ · σ_d² + d̄² · σ_L²) &nbsp;|&nbsp;
        <strong style="color:#6ee7b7;">Dynamic ROP</strong> = (d̄ × L̄) + SS
    </div>
    """, unsafe_allow_html=True)

    opt_df, _ = run_query(f"""
        SELECT SKU_ID, Category, Units_Sold, Supplier_Lead_Time_Days, 
               Inventory_Level, Date, Reorder_Point, Order_Quantity
        FROM retail_data {where_stmt}
    """)

    if opt_df is not None and not opt_df.empty:
        stats = opt_df.groupby(['SKU_ID', 'Category']).agg(
            avg_demand    =('Units_Sold',               'mean'),
            std_demand    =('Units_Sold',               'std'),
            avg_lead_time =('Supplier_Lead_Time_Days',  'mean'),
            std_lead_time =('Supplier_Lead_Time_Days',  'std'),
            avg_order_qty =('Order_Quantity',           'mean')
        ).reset_index()
        latest_idx = opt_df.groupby('SKU_ID')['Date'].idxmax()
        latest_inv = opt_df.loc[latest_idx, ['SKU_ID', 'Inventory_Level']]
        stats = pd.merge(stats, latest_inv, on='SKU_ID').fillna(0)

        # Normal calc
        stats['Safety_Stock'] = Z * np.sqrt(
            stats['avg_lead_time'] * (stats['std_demand'] ** 2) +
            (stats['avg_demand']   ** 2) * (stats['std_lead_time'] ** 2)
        )
        stats['Dynamic_ROP'] = (stats['avg_demand'] * stats['avg_lead_time']) + stats['Safety_Stock']
        stats['Status'] = np.where(stats['Inventory_Level'] <= stats['Dynamic_ROP'], "🚨 Reorder", "✅ Healthy")

        # Stress calc
        shock_demand    = stats['avg_demand']    * (1 + demand_surge / 100)
        shock_lead_time = stats['avg_lead_time'] + supplier_delay
        stats['Shock_Safety_Stock'] = Z * np.sqrt(
            shock_lead_time * (stats['std_demand'] ** 2) +
            (shock_demand   ** 2) * (stats['std_lead_time'] ** 2)
        )
        stats['Shock_ROP'] = (shock_demand * shock_lead_time) + stats['Shock_Safety_Stock']
        stats['Shock_Status'] = np.where(stats['Inventory_Level'] <= stats['Shock_ROP'], "🚨 Reorder", "✅ Healthy")
        stats['Vulnerability'] = np.where(
            (stats['Status'] == "✅ Healthy") & (stats['Shock_Status'] == "🚨 Reorder"), "⚠️ Vulnerable",
            np.where(stats['Status'] == "🚨 Reorder", "🚨 Reorder", "✅ Stable")
        )
        stats['Shock_Suggested_Order_Qty'] = np.where(
            stats['Inventory_Level'] <= stats['Shock_ROP'],
            np.maximum(stats['avg_order_qty'], stats['Shock_ROP'] - stats['Inventory_Level']).round(0), 0
        )
        for col in ['Safety_Stock','Dynamic_ROP','Shock_Safety_Stock','Shock_ROP','avg_demand','avg_lead_time']:
            stats[col] = stats[col].round(1)

        reorder_count       = len(stats[stats['Status']        == "🚨 Reorder"])
        shock_reorder_count = len(stats[stats['Shock_Status']  == "🚨 Reorder"])
        vulnerable_count    = len(stats[stats['Vulnerability'] == "⚠️ Vulnerable"])

        # Sub-KPI cards
        st.markdown(f"""
        <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr); margin-bottom:20px;">
          <div class="kpi-card blue">
            <div class="kpi-icon-badge blue">📐</div>
            <div class="kpi-label">Z-Score ({service_level})</div>
            <div class="kpi-value">{Z}</div>
            <div class="kpi-delta">Confidence threshold</div>
          </div>
          <div class="kpi-card green">
            <div class="kpi-icon-badge green">✅</div>
            <div class="kpi-label">Normal Reorder Alerts</div>
            <div class="kpi-value">{reorder_count}</div>
            <div class="kpi-delta">SKUs needing restock</div>
          </div>
          <div class="kpi-card amber">
            <div class="kpi-icon-badge amber">🌡️</div>
            <div class="kpi-label">Shocked Reorder Alerts</div>
            <div class="kpi-value">{shock_reorder_count}</div>
            <div class="kpi-delta">+{shock_reorder_count - reorder_count} vs normal</div>
          </div>
          <div class="kpi-card {'amber' if vulnerable_count > 0 else 'green'}">
            <div class="kpi-icon-badge {'amber' if vulnerable_count > 0 else 'green'}">⚠️</div>
            <div class="kpi-label">Vulnerable SKUs</div>
            <div class="kpi-value">{vulnerable_count}</div>
            <div class="kpi-delta">{'At risk under stress' if vulnerable_count > 0 else 'All stable'}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if vulnerable_count > 0:
            st.warning(f"⚠️ **Stress Test Warning:** Shock scenario (Demand +{demand_surge}%, Lead Time +{supplier_delay}d) "
                       f"puts **{vulnerable_count} SKUs** at risk! These appear as ⚠️ Vulnerable below.")

        show_mode = st.radio("Display Filter:", [
            "Show All SKUs", "Show Reorder Alerts (Normal) Only",
            "Show Reorder Alerts (Shocked) Only", "Show Vulnerable SKUs Only"
        ], horizontal=True, key="inv_radio")

        display_stats = stats.copy()
        if show_mode == "Show Reorder Alerts (Normal) Only":
            display_stats = display_stats[display_stats['Status']        == "🚨 Reorder"]
        elif show_mode == "Show Reorder Alerts (Shocked) Only":
            display_stats = display_stats[display_stats['Shock_Status']  == "🚨 Reorder"]
        elif show_mode == "Show Vulnerable SKUs Only":
            display_stats = display_stats[display_stats['Vulnerability'] == "⚠️ Vulnerable"]

        st.dataframe(
            display_stats[['SKU_ID','Category','Inventory_Level','avg_demand',
                           'avg_lead_time','Safety_Stock','Dynamic_ROP','Shock_ROP','Vulnerability','Shock_Suggested_Order_Qty']],
            use_container_width=True,
            column_config={
                "SKU_ID":                    st.column_config.TextColumn("SKU"),
                "Category":                  st.column_config.TextColumn("Category"),
                "Inventory_Level":           st.column_config.NumberColumn("Current Stock",     format="%d"),
                "avg_demand":                st.column_config.NumberColumn("Avg Daily Demand",  format="%.1f"),
                "avg_lead_time":             st.column_config.NumberColumn("Avg Lead Time (d)", format="%.1f"),
                "Safety_Stock":              st.column_config.NumberColumn("Safety Stock",      format="%.1f"),
                "Dynamic_ROP":               st.column_config.NumberColumn("Dynamic ROP",       format="%.1f"),
                "Shock_ROP":                 st.column_config.NumberColumn("Shocked ROP",       format="%.1f"),
                "Vulnerability":             st.column_config.TextColumn("Risk Status"),
                "Shock_Suggested_Order_Qty": st.column_config.NumberColumn("Suggested Order",   format="%d"),
            },
            hide_index=True
        )
    else:
        st.info("No stock data found for the selected filters.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 · DEMAND FORECASTING
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("""
    <div class="section-header">
        <div class="section-header-icon" style="background:linear-gradient(135deg,#8b5cf6,#a78bfa);">🔮</div>
        <div class="section-header-text">
            <h3>30-Day Demand Forecasting</h3>
            <p>Linear regression trend + weekly seasonal index · projects next 30 days of sales volume</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    fc_df, _ = run_query(f"""
        SELECT Date, SUM(Units_Sold) AS Units_Sold
        FROM retail_data {where_stmt}
        GROUP BY Date ORDER BY Date ASC
    """)

    if fc_df is not None and len(fc_df) >= 7:
        fc_df['Date']     = pd.to_datetime(fc_df['Date'])
        fc_df['DayIndex'] = (fc_df['Date'] - fc_df['Date'].min()).dt.days
        x = fc_df['DayIndex'].values
        y = fc_df['Units_Sold'].values
        m, c = np.polyfit(x, y, 1)

        fc_df['DayOfWeek']    = fc_df['Date'].dt.dayofweek
        avg_by_dow            = fc_df.groupby('DayOfWeek')['Units_Sold'].mean()
        overall_mean          = fc_df['Units_Sold'].mean()
        seasonal_factors      = (avg_by_dow / overall_mean).to_dict()

        last_date    = fc_df['Date'].max()
        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, 31)]
        future_idx   = [(d - fc_df['Date'].min()).days for d in future_dates]

        future_data = []
        for d, idx in zip(future_dates, future_idx):
            trend = m * idx + c
            factor = seasonal_factors.get(d.dayofweek, 1.0)
            future_data.append({'Date': d, 'Units_Sold': round(max(0, trend * factor), 1), 'Type': 'Forecasted'})
        future_df = pd.DataFrame(future_data)

        # Premium chart
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(13, 4))
        apply_dark_style(ax, fig)

        # Historical
        ax.plot(fc_df['Date'], fc_df['Units_Sold'], color="#6366f1", linewidth=1.8,
                label="Historical", alpha=0.9)
        ax.fill_between(fc_df['Date'], fc_df['Units_Sold'], alpha=0.1, color="#6366f1")

        # Trend line
        trend_line = m * x + c
        ax.plot(fc_df['Date'], trend_line, color="#818cf8", linewidth=1.2,
                linestyle="--", alpha=0.5, label="Trend")

        # Forecast
        ax.plot(future_df['Date'], future_df['Units_Sold'], color="#22d3ee",
                linewidth=2.2, label="30-Day Forecast", linestyle="-", alpha=0.95)
        ax.fill_between(future_df['Date'], future_df['Units_Sold'], alpha=0.12, color="#22d3ee")

        # Forecast boundary
        ax.axvline(x=last_date, color="#f59e0b", linewidth=1.5, linestyle="--", alpha=0.7)
        ax.text(last_date, ax.get_ylim()[1] * 0.95, "  Forecast →",
                color="#f59e0b", fontsize=8.5, fontweight="bold", va="top")

        legend = ax.legend(frameon=True, facecolor="#0d1b2a", edgecolor="#1e2d45",
                            labelcolor="#94a3b8", fontsize=9, loc="upper left")
        ax.set_title("📈 Historical Sales vs 30-Day Forecast (Linear Trend + Weekly Seasonality)",
                     fontsize=11, fontweight='bold', color="#e2e8f0", pad=12)
        ax.set_xlabel("Date", fontsize=9)
        ax.set_ylabel("Units Sold", fontsize=9)
        plt.xticks(rotation=20, ha='right', fontsize=8, color="#64748b")
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.markdown('</div>', unsafe_allow_html=True)

        # Forecast table
        fc_col1, fc_col2, fc_col3 = st.columns(3)
        fc_col1.metric("📅 Forecast Start",    future_df['Date'].iloc[0].strftime("%d %b %Y"))
        fc_col2.metric("📅 Forecast End",      future_df['Date'].iloc[-1].strftime("%d %b %Y"))
        fc_col3.metric("📦 Projected Total",   f"{int(future_df['Units_Sold'].sum()):,} units")

        with st.expander("📋 View 30-Day Forecast Table"):
            out_df = future_df.copy()
            out_df['Date'] = out_df['Date'].dt.strftime("%d %b %Y")
            st.dataframe(out_df[['Date','Units_Sold']].rename(
                columns={'Units_Sold': 'Forecasted Units'}),
                use_container_width=True, hide_index=True)
    else:
        st.warning("Insufficient historical data (needs ≥ 7 days) to generate a forecast.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 · SUPPLIER RISK PROFILE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("""
    <div class="section-header">
        <div class="section-header-icon" style="background:linear-gradient(135deg,#f43f5e,#fb7185);">🤝</div>
        <div class="section-header-text">
            <h3>Supplier Reliability Scorecard</h3>
            <p>Score = 100 − (Avg Lead Time × 4) − (Std Dev × 12) · ranked out of 100</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sup_df, _ = run_query(f"""
        SELECT Supplier_ID, Supplier_Lead_Time_Days
        FROM retail_data {where_stmt}
    """)

    if sup_df is not None and not sup_df.empty:
        sup_stats = sup_df.groupby('Supplier_ID').agg(
            avg_lead_time   =('Supplier_Lead_Time_Days', 'mean'),
            std_lead_time   =('Supplier_Lead_Time_Days', 'std'),
            total_deliveries=('Supplier_Lead_Time_Days', 'count')
        ).reset_index().fillna(0)

        sup_stats['Score'] = (100 - (sup_stats['avg_lead_time'] * 4) - (sup_stats['std_lead_time'] * 12)).clip(0, 100).round(1)
        conditions = [(sup_stats['Score'] >= 75), (sup_stats['Score'] >= 50)]
        choices    = ['🟢 Low Risk',              '🟡 Medium Risk']
        sup_stats['Risk_Category'] = np.select(conditions, choices, default='🔴 High Risk')
        sup_stats['avg_lead_time']  = sup_stats['avg_lead_time'].round(2)
        sup_stats['std_lead_time']  = sup_stats['std_lead_time'].round(2)
        sup_sorted = sup_stats.sort_values('Score', ascending=False)

        chart_col, tbl_col = st.columns([2, 1])

        with chart_col:
            st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(9, max(4, len(sup_sorted) * 0.42)))
            apply_dark_style(ax, fig)
            colors_bar = ["#10b981" if s >= 75 else "#f59e0b" if s >= 50 else "#f43f5e"
                          for s in sup_sorted['Score']]
            bars = ax.barh(sup_sorted['Supplier_ID'], sup_sorted['Score'],
                           color=colors_bar, alpha=0.9, edgecolor="none", height=0.65)
            # Score labels
            for bar, score in zip(bars, sup_sorted['Score']):
                ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                        f"{score:.1f}", va='center', ha='left', fontsize=8.5, color="#94a3b8")
            ax.axvline(x=75, color="#10b981", linestyle="--", linewidth=1, alpha=0.5)
            ax.axvline(x=50, color="#f59e0b", linestyle="--", linewidth=1, alpha=0.5)
            ax.set_xlim(0, 105)
            ax.set_title("🤝 Supplier Reliability Scores (out of 100)",
                         fontsize=11, fontweight='bold', color="#e2e8f0", pad=12)
            ax.set_xlabel("Reliability Score", fontsize=9)
            legend_patches = [
                mpatches.Patch(color="#10b981", label="🟢 Low Risk   (≥75)"),
                mpatches.Patch(color="#f59e0b", label="🟡 Medium Risk (50-74)"),
                mpatches.Patch(color="#f43f5e", label="🔴 High Risk  (<50)"),
            ]
            ax.legend(handles=legend_patches, frameon=True, facecolor="#0d1b2a",
                      edgecolor="#1e2d45", labelcolor="#94a3b8", fontsize=8.5, loc="lower right")
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            st.markdown('</div>', unsafe_allow_html=True)

        with tbl_col:
            low_risk    = len(sup_stats[sup_stats['Score'] >= 75])
            medium_risk = len(sup_stats[(sup_stats['Score'] >= 50) & (sup_stats['Score'] < 75)])
            high_risk   = len(sup_stats[sup_stats['Score'] < 50])
            st.markdown(f"""
            <div style="display:flex; flex-direction:column; gap:14px; margin-top:10px;">
              <div class="kpi-card green" style="padding:18px;">
                <div class="kpi-icon-badge green" style="width:36px;height:36px;">🟢</div>
                <div class="kpi-label">Low Risk Suppliers</div>
                <div class="kpi-value" style="font-size:2rem;">{low_risk}</div>
                <div class="kpi-delta">Score ≥ 75</div>
              </div>
              <div class="kpi-card amber" style="padding:18px;">
                <div class="kpi-icon-badge amber" style="width:36px;height:36px;">🟡</div>
                <div class="kpi-label">Medium Risk Suppliers</div>
                <div class="kpi-value" style="font-size:2rem;">{medium_risk}</div>
                <div class="kpi-delta">Score 50–74</div>
              </div>
              <div class="kpi-card" style="border-color:rgba(244,63,94,0.3); padding:18px;">
                <div class="kpi-glow" style="background:#f43f5e;"></div>
                <div class="kpi-icon-badge" style="background:rgba(244,63,94,0.2);border:1px solid rgba(244,63,94,0.4);width:36px;height:36px;">🔴</div>
                <div class="kpi-label" style="color:#64748b;">High Risk Suppliers</div>
                <div class="kpi-value" style="font-size:2rem;">{high_risk}</div>
                <div class="kpi-delta">Score &lt; 50</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        st.dataframe(
            sup_sorted,
            use_container_width=True,
            column_config={
                "Supplier_ID":      st.column_config.TextColumn("Supplier"),
                "avg_lead_time":    st.column_config.NumberColumn("Avg Lead Time (d)", format="%.2f"),
                "std_lead_time":    st.column_config.NumberColumn("Consistency (σ)",   format="%.2f"),
                "total_deliveries": st.column_config.NumberColumn("Total Deliveries",  format="%d"),
                "Score":            st.column_config.ProgressColumn("Reliability Score", format="%.1f",
                                        min_value=0, max_value=100),
                "Risk_Category":    st.column_config.TextColumn("Risk Status"),
            },
            hide_index=True
        )
    else:
        st.info("No supplier data for the selected filters.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 · SQL SANDBOX
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("""
    <div class="section-header">
        <div class="section-header-icon" style="background:linear-gradient(135deg,#0891b2,#22d3ee);">💻</div>
        <div class="section-header-text">
            <h3>Interactive SQL Sandbox</h3>
            <p>Write, run, and explore custom queries against the <code style="color:#22d3ee;">retail_data</code> table</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1, 2])

    with left:
        st.markdown("""
        <div style="font-size:0.8rem; font-weight:700; color:#a5b4fc; text-transform:uppercase; 
                    letter-spacing:0.08em; margin-bottom:12px;">💡 Sample Queries</div>
        """, unsafe_allow_html=True)

        sample_queries = {
            "Revenue by Category": """SELECT Category, 
       SUM(Units_Sold) AS Total_Units, 
       ROUND(SUM(Units_Sold * Unit_Price), 2) AS Total_Revenue 
FROM retail_data 
GROUP BY Category;""",
            "Forecast vs Actual": """SELECT Category, 
       SUM(Units_Sold) AS Actual_Sold, 
       ROUND(SUM(Demand_Forecast), 2) AS Forecasted,
       ROUND(AVG(ABS(Units_Sold - Demand_Forecast)), 2) AS MAE
FROM retail_data 
GROUP BY Category;""",
            "Worst Suppliers (Lead Time)": """SELECT Supplier_ID, 
       ROUND(AVG(Supplier_Lead_Time_Days), 2) AS Avg_Lead_Time_Days
FROM retail_data 
GROUP BY Supplier_ID 
ORDER BY Avg_Lead_Time_Days DESC 
LIMIT 5;""",
            "Stockout Rate by Region": """SELECT Region, 
       ROUND(100.0 * SUM(Stockout_Flag) / COUNT(*), 2) AS Stockout_Pct
FROM retail_data 
GROUP BY Region 
ORDER BY Stockout_Pct DESC;"""
        }

        selected_sample = st.selectbox("Pick a sample to load:", list(sample_queries.keys()), key="sample_picker")
        st.code(sample_queries[selected_sample], language="sql")

        with st.expander("📋 Database Schema"):
            st.markdown("""
| Column | Type | Description |
|--------|------|-------------|
| Date | TEXT | Transaction date |
| SKU_ID | TEXT | Product ID |
| Warehouse_ID | TEXT | Warehouse |
| Supplier_ID | TEXT | Supplier |
| Region | TEXT | Distribution region |
| Units_Sold | INT | Quantity sold |
| Inventory_Level | INT | Current stock |
| Supplier_Lead_Time_Days | INT | Lead time |
| Reorder_Point | INT | Reorder threshold |
| Order_Quantity | INT | Order size |
| Unit_Cost | REAL | Cost per unit |
| Unit_Price | REAL | Sell price per unit |
| Promotion_Flag | INT | 1 = active promo |
| Stockout_Flag | INT | 1 = stockout |
| Demand_Forecast | REAL | Projected demand |
| Category | TEXT | Health / Standard |
            """)

    with right:
        st.markdown("""
        <div style="font-size:0.8rem; font-weight:700; color:#a5b4fc; text-transform:uppercase; 
                    letter-spacing:0.08em; margin-bottom:12px;">✍️ SQL Query Editor</div>
        """, unsafe_allow_html=True)

        if 'sql_editor_value' not in st.session_state:
            st.session_state['sql_editor_value'] = sample_queries["Revenue by Category"]

        # Load sample button
        if st.button("📥 Load Selected Sample", key="load_sample"):
            st.session_state['sql_editor_value'] = sample_queries[selected_sample]

        query_input = st.text_area("", value=st.session_state['sql_editor_value'],
                                   height=200, key="sql_editor", label_visibility="collapsed")

        run_col, clear_col = st.columns([2, 1])
        with run_col:
            run_btn = st.button("⚡ Execute Query", type="primary", use_container_width=True, key="run_sql")
        with clear_col:
            if st.button("🗑️ Clear", use_container_width=True, key="clear_sql"):
                st.session_state['sql_editor_value'] = ""
                st.rerun()

        if run_btn and query_input.strip():
            with st.spinner("Running query…"):
                results_df, err = run_query(query_input)
            if err:
                st.error(f"❌ SQL Error: `{err}`")
            else:
                st.success(f"✅ Query returned **{len(results_df):,}** row(s)")
                st.dataframe(results_df, use_container_width=True, hide_index=True)

                # Download
                csv_data = results_df.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Download as CSV", data=csv_data,
                                   file_name="query_results.csv", mime="text/csv")

# ──────────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="styled-divider"></div>
<div class="footer-panel">
    <div class="footer-left">
        <span class="footer-title">📦 SupplyIQ · Retail Analytics Platform</span>
        <span class="footer-sub">
            Built as an end-to-end Data Engineering & Analytics portfolio project ·
            <a href="https://github.com/Venkateshnandupalli/Retail-Supply-Chain-Consumer-Health-Trends" 
               target="_blank" style="color:#6366f1; text-decoration:none;">
               View Source on GitHub ↗
            </a>
        </span>
    </div>
    <div class="tech-badges">
        <span class="tech-badge">🐍 Python</span>
        <span class="tech-badge">🗄️ SQLite</span>
        <span class="tech-badge">📊 Streamlit</span>
        <span class="tech-badge">🐼 Pandas</span>
        <span class="tech-badge">📈 Matplotlib</span>
        <span class="tech-badge">🔢 NumPy</span>
    </div>
</div>
""", unsafe_allow_html=True)
