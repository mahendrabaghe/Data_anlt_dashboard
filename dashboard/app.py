"""
app.py  –  E-Commerce Sales & Customer Analytics Dashboard
-----------------------------------------------------------
Run with:  streamlit run dashboard/app.py
"""

import sys
import os
from pathlib import Path

# ── Allow imports from src/ ─────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# ── Project modules ─────────────────────────────────────
from analytics import (
    load_data, calculate_kpis,
    monthly_sales, category_performance, subcategory_performance,
    state_performance, city_performance, top_products,
    customer_summary, age_group_analysis, gender_analysis,
    payment_mode_analysis, order_status_analysis,
    generate_insights,
)
from customer_segmentation import run_segmentation

# ═══════════════════════════════════════════════════════════
# Page config & global styling
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] { background: #0f1117; }
[data-testid="stSidebar"]          { background: #1a1d27; border-right: 1px solid #2d3040; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg,#1e2130,#252840);
    border: 1px solid #3d4060;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,.4);
}
[data-testid="metric-container"] label { color:#a0a8c0 !important; font-size:.8rem !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color:#e8eaf6 !important; font-size:1.55rem !important; font-weight:700 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size:.8rem !important; }

/* ── Section headers ── */
.section-header {
    font-size:1.3rem; font-weight:700; color:#7c83fd;
    border-left:4px solid #7c83fd; padding-left:12px;
    margin:28px 0 16px 0;
}

/* ── Insight card ── */
.insight-card {
    background:#1e2130; border:1px solid #3d4060; border-radius:10px;
    padding:14px 18px; margin:8px 0; color:#c8cee0; font-size:.93rem;
    line-height:1.6;
}
.insight-num { color:#7c83fd; font-weight:700; margin-right:8px; }

/* ── Sidebar nav ── */
.nav-item {
    display:block; padding:10px 14px; border-radius:8px;
    color:#c0c6e0; text-decoration:none; font-size:.92rem; margin:4px 0;
    cursor:pointer; transition:background .2s;
}
.nav-item:hover, .nav-item.active { background:#2d3250; color:#fff; }

/* ── Tables ── */
[data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; }

/* ── Plotly charts ── */
.js-plotly-plot .plotly { border-radius:12px !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background:linear-gradient(90deg,#7c83fd,#5c6bc0);
    color:#fff; border:none; border-radius:8px;
    padding:8px 18px; font-size:.88rem;
}
.stDownloadButton > button:hover { opacity:.88; }

/* ── Info / warning boxes ── */
.stAlert { border-radius:10px; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#1a1d27",
    plot_bgcolor="#1a1d27",
    font=dict(color="#c8cee0", family="Inter, sans-serif"),
    margin=dict(t=50, l=10, r=10, b=10),
)
COLOR_SEQ = px.colors.qualitative.Vivid


# ═══════════════════════════════════════════════════════════
# Data loading (cached)
# ═══════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def get_data() -> pd.DataFrame:
    clean_path = PROJECT_ROOT / "data" / "processed" / "cleaned_sales.csv"
    if not clean_path.exists():
        # Auto-generate + clean if files missing
        raw_path = PROJECT_ROOT / "data" / "raw" / "ecommerce_sales.csv"
        if not raw_path.exists():
            from generate_dataset import main as gen
            gen()
        from data_cleaning import clean_data
        clean_data()
    return load_data(clean_path)


@st.cache_data(show_spinner=False)
def get_segmentation(df: pd.DataFrame):
    return run_segmentation(df)


# ═══════════════════════════════════════════════════════════
# Helper utilities
# ═══════════════════════════════════════════════════════════
def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    f = df.copy()
    if filters.get("date_range"):
        s, e = filters["date_range"]
        f = f[(f["Order_Date"].dt.date >= s) & (f["Order_Date"].dt.date <= e)]
    for col, key in [("State","state"),("City","city"),("Category","category"),
                     ("Sub_Category","sub_category"),("Gender","gender"),
                     ("Payment_Mode","payment_mode"),("Order_Status","order_status")]:
        if filters.get(key):
            f = f[f[col].isin(filters[key])]
    return f


def fmt_currency(v: float) -> str:
    if v >= 1e7:
        return f"₹{v/1e7:.2f} Cr"
    elif v >= 1e5:
        return f"₹{v/1e5:.2f} L"
    else:
        return f"₹{v:,.0f}"


def fmt_num(v: float | int) -> str:
    return f"{int(v):,}" if v < 1e6 else f"{v/1e6:.2f}M"


def kpi_card_row(data: dict, cols_per_row: int = 4) -> None:
    keys = list(data.keys())
    for i in range(0, len(keys), cols_per_row):
        row = keys[i:i+cols_per_row]
        cols = st.columns(len(row))
        for col, k in zip(cols, row):
            v = data[k]
            col.metric(label=k, value=v)


def section(title: str) -> None:
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def apply_layout(fig: go.Figure, height: int = 400) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    return fig


def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


# ═══════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════
def render_sidebar(df: pd.DataFrame) -> dict:
    with st.sidebar:
        st.markdown(
            "<h2 style='color:#7c83fd;margin-bottom:4px'>📊 Analytics</h2>"
            "<p style='color:#6b7280;font-size:.8rem;margin-top:0'>E-Commerce Dashboard v1.0</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        # Navigation
        page = st.radio(
            "Navigation",
            ["🏠 Executive Overview", "📈 Sales Analysis",
             "👥 Customer Analytics", "🎯 Customer Segmentation",
             "📦 Product Analytics"],
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("**🔍 Filters**")

        min_d, max_d = df["Order_Date"].min().date(), df["Order_Date"].max().date()
        date_range = st.date_input("Date Range", value=(min_d, max_d),
                                   min_value=min_d, max_value=max_d)

        states   = st.multiselect("State",        sorted(df["State"].dropna().unique()))
        cities   = st.multiselect("City",         sorted(df["City"].dropna().unique()))
        cats     = st.multiselect("Category",     sorted(df["Category"].dropna().unique()))
        subcats  = st.multiselect("Sub-Category", sorted(df["Sub_Category"].dropna().unique()))
        genders  = st.multiselect("Gender",       sorted(df["Gender"].dropna().unique()))
        payments = st.multiselect("Payment Mode", sorted(df["Payment_Mode"].dropna().unique()))
        statuses = st.multiselect("Order Status", sorted(df["Order_Status"].dropna().unique()))

        if st.button("🔄 Reset Filters", use_container_width=True):
            st.rerun()

        st.divider()
        st.caption("Built with Streamlit · Plotly · Pandas")

    filters = {
        "date_range": date_range if len(date_range) == 2 else None,
        "state":       states    or None,
        "city":        cities    or None,
        "category":    cats      or None,
        "sub_category": subcats  or None,
        "gender":      genders   or None,
        "payment_mode": payments or None,
        "order_status": statuses or None,
    }
    return page, filters


# ═══════════════════════════════════════════════════════════
# PAGE 1 – Executive Overview
# ═══════════════════════════════════════════════════════════
def page_executive(df: pd.DataFrame) -> None:
    st.title("🏠 Executive Overview")
    st.caption("High-level business performance at a glance.")

    if df.empty:
        st.warning("No data matches the selected filters."); return

    kpis = calculate_kpis(df)

    # ── KPI row ─────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("💰 Revenue",      fmt_currency(kpis["Total Revenue"]))
    c2.metric("📈 Profit",       fmt_currency(kpis["Total Profit"]))
    c3.metric("🛒 Orders",       fmt_num(kpis["Total Orders"]))
    c4.metric("👥 Customers",    fmt_num(kpis["Total Customers"]))
    c5.metric("🧾 Avg Order Val",fmt_currency(kpis["Average Order Value"]))
    c6.metric("📊 Profit Margin",f"{kpis['Profit Margin (%)']:.1f}%")

    st.divider()

    # ── Monthly trend ────────────────────────────────────
    section("Monthly Revenue & Profit Trend")
    mon = monthly_sales(df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mon["Month"], y=mon["Revenue"],
                             name="Revenue", fill="tozeroy", mode="lines+markers",
                             line=dict(color="#7c83fd", width=2.5),
                             fillcolor="rgba(124,131,253,0.15)"))
    fig.add_trace(go.Scatter(x=mon["Month"], y=mon["Profit"],
                             name="Profit", mode="lines+markers",
                             line=dict(color="#52c41a", width=2, dash="dash")))
    apply_layout(fig, 380)
    fig.update_layout(xaxis_tickangle=-45, yaxis_tickformat="₹,.0f")
    st.plotly_chart(fig, use_container_width=True)

    # ── Category row ─────────────────────────────────────
    col_l, col_r = st.columns(2)
    cat_perf = category_performance(df)

    with col_l:
        section("Sales by Category")
        fig2 = px.bar(cat_perf, x="Revenue", y="Category", orientation="h",
                      color="Revenue", color_continuous_scale="Viridis",
                      text=cat_perf["Revenue"].apply(fmt_currency))
        apply_layout(fig2, 380)
        fig2.update_traces(textposition="outside")
        fig2.update_coloraxes(showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col_r:
        section("Profit by Category")
        fig3 = px.pie(cat_perf, values="Profit", names="Category",
                      hole=0.42, color_discrete_sequence=COLOR_SEQ)
        apply_layout(fig3, 380)
        fig3.update_traces(textinfo="percent+label", textfont_size=12)
        st.plotly_chart(fig3, use_container_width=True)

    # ── Top products ─────────────────────────────────────
    section("Top 10 Products by Revenue")
    tp = top_products(df, 10)
    fig4 = px.bar(tp, x="Revenue", y="Product_Name", orientation="h",
                  color="Profit", color_continuous_scale="Plasma",
                  text=tp["Revenue"].apply(fmt_currency))
    apply_layout(fig4, 420)
    fig4.update_traces(textposition="outside")
    st.plotly_chart(fig4, use_container_width=True)

    # ── Business insights ────────────────────────────────
    section("💡 Auto-Generated Business Insights")
    insights = generate_insights(df)
    for i, insight in enumerate(insights, 1):
        st.markdown(
            f'<div class="insight-card"><span class="insight-num">{i}.</span>{insight}</div>',
            unsafe_allow_html=True,
        )

    # ── Downloads ─────────────────────────────────────────
    section("📥 Downloads")
    dc1, dc2 = st.columns(2)
    kpi_df = pd.DataFrame(list(kpis.items()), columns=["KPI", "Value"])
    dc1.download_button("📊 Download KPI Summary",   csv_bytes(kpi_df), "kpi_summary.csv",   "text/csv")
    dc2.download_button("📋 Download Filtered Data", csv_bytes(df),     "filtered_data.csv", "text/csv")


# ═══════════════════════════════════════════════════════════
# PAGE 2 – Sales Analysis
# ═══════════════════════════════════════════════════════════
def page_sales(df: pd.DataFrame) -> None:
    st.title("📈 Sales Analysis")
    st.caption("Deep-dive into sales performance across time, geography, and products.")

    if df.empty:
        st.warning("No data matches the selected filters."); return

    # ── Monthly + daily tabs ─────────────────────────────
    section("Time-Series Sales")
    t1, t2 = st.tabs(["Monthly", "Daily"])

    with t1:
        mon = monthly_sales(df)
        fig = px.line(mon, x="Month", y=["Revenue","Profit"], markers=True,
                      color_discrete_sequence=["#7c83fd","#52c41a"])
        apply_layout(fig, 360)
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        daily = df.groupby(df["Order_Date"].dt.date)[["Sales","Profit"]].sum().reset_index()
        daily.columns = ["Date","Revenue","Profit"]
        fig_d = px.line(daily, x="Date", y="Revenue", color_discrete_sequence=["#fa8c16"])
        apply_layout(fig_d, 360)
        st.plotly_chart(fig_d, use_container_width=True)

    # ── Sub-category treemap ─────────────────────────────
    section("Revenue Treemap – Category → Sub-Category")
    sc = subcategory_performance(df)
    fig_tree = px.treemap(sc, path=["Category","Sub_Category"],
                          values="Revenue", color="Profit",
                          color_continuous_scale="RdYlGn",
                          color_continuous_midpoint=sc["Profit"].median())
    apply_layout(fig_tree, 480)
    st.plotly_chart(fig_tree, use_container_width=True)

    # ── State & City ─────────────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        section("Revenue by State")
        state = state_performance(df)
        fig_s = px.bar(state, x="Revenue", y="State", orientation="h",
                       color="Profit", color_continuous_scale="Teal",
                       text=state["Revenue"].apply(fmt_currency))
        apply_layout(fig_s, 400)
        fig_s.update_traces(textposition="outside")
        st.plotly_chart(fig_s, use_container_width=True)

    with col_r:
        section("Top 15 Cities by Revenue")
        city = city_performance(df).head(15)
        fig_c = px.bar(city, x="Revenue", y="City", orientation="h",
                       color="Revenue", color_continuous_scale="Sunset",
                       text=city["Revenue"].apply(fmt_currency))
        apply_layout(fig_c, 400)
        fig_c.update_traces(textposition="outside")
        fig_c.update_coloraxes(showscale=False)
        st.plotly_chart(fig_c, use_container_width=True)

    # ── Payment & order-status ───────────────────────────
    col_l2, col_r2 = st.columns(2)

    with col_l2:
        section("Payment Mode Distribution")
        pay = payment_mode_analysis(df)
        fig_p = px.pie(pay, values="Orders", names="Payment_Mode",
                       hole=0.35, color_discrete_sequence=COLOR_SEQ)
        apply_layout(fig_p, 360)
        st.plotly_chart(fig_p, use_container_width=True)

    with col_r2:
        section("Order Status Breakdown")
        ost = order_status_analysis(df)
        clr = {"Delivered":"#52c41a","Cancelled":"#ff4d4f","Pending":"#faad14","Returned":"#722ed1"}
        fig_o = px.bar(ost, x="Order_Status", y="Orders",
                       color="Order_Status",
                       color_discrete_map=clr,
                       text="Orders")
        apply_layout(fig_o, 360)
        fig_o.update_traces(textposition="outside")
        fig_o.update_layout(showlegend=False)
        st.plotly_chart(fig_o, use_container_width=True)

    # ── Download ─────────────────────────────────────────
    st.divider()
    st.download_button("📥 Download Sales Report", csv_bytes(monthly_sales(df)),
                       "sales_report.csv", "text/csv")


# ═══════════════════════════════════════════════════════════
# PAGE 3 – Customer Analytics
# ═══════════════════════════════════════════════════════════
def page_customers(df: pd.DataFrame) -> None:
    st.title("👥 Customer Analytics")
    st.caption("Understand your customer base: demographics, geography, and behaviour.")

    if df.empty:
        st.warning("No data matches the selected filters."); return

    cust = customer_summary(df)
    order_counts   = df.groupby("Customer_ID")["Order_ID"].nunique()
    repeat_cust    = int((order_counts > 1).sum())
    new_cust       = int((order_counts == 1).sum())
    total_cust     = cust["Customer_ID"].nunique()
    avg_cust_rev   = cust["Total_Revenue"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers",    fmt_num(total_cust))
    c2.metric("Repeat Customers",   fmt_num(repeat_cust))
    c3.metric("New Customers",      fmt_num(new_cust))
    c4.metric("Avg Revenue/Customer", fmt_currency(avg_cust_rev))

    st.divider()

    # ── Top customers ─────────────────────────────────────
    section("Top 15 Customers by Revenue")
    top_c = cust.head(15)
    fig_tc = px.bar(top_c, x="Total_Revenue", y="Customer_Name", orientation="h",
                    color="Total_Revenue", color_continuous_scale="Magma",
                    text=top_c["Total_Revenue"].apply(fmt_currency),
                    hover_data=["Total_Orders","Gender","City"])
    apply_layout(fig_tc, 480)
    fig_tc.update_traces(textposition="outside")
    fig_tc.update_coloraxes(showscale=False)
    st.plotly_chart(fig_tc, use_container_width=True)

    # ── Gender & Age row ─────────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        section("Gender Distribution")
        gen = gender_analysis(df)
        fig_g = px.pie(gen, values="Revenue", names="Gender",
                       hole=0.4, color_discrete_sequence=["#7c83fd","#ff6fa8"])
        apply_layout(fig_g, 360)
        fig_g.update_traces(textinfo="percent+label+value",
                            texttemplate="%{label}<br>%{percent}")
        st.plotly_chart(fig_g, use_container_width=True)

    with col_r:
        section("Revenue by Age Group")
        ag = age_group_analysis(df)
        fig_ag = px.bar(ag, x="Age_Group", y="Revenue",
                        color="Age_Group", text=ag["Revenue"].apply(fmt_currency),
                        color_discrete_sequence=COLOR_SEQ)
        apply_layout(fig_ag, 360)
        fig_ag.update_traces(textposition="outside")
        fig_ag.update_layout(showlegend=False)
        st.plotly_chart(fig_ag, use_container_width=True)

    # ── Customers by state ───────────────────────────────
    section("Customer Count by State")
    by_state = cust.groupby("State")["Customer_ID"].count().reset_index(name="Customers")
    fig_st = px.bar(by_state.sort_values("Customers", ascending=False),
                    x="Customers", y="State", orientation="h",
                    color="Customers", color_continuous_scale="Purples",
                    text="Customers")
    apply_layout(fig_st, 380)
    fig_st.update_traces(textposition="outside")
    fig_st.update_coloraxes(showscale=False)
    st.plotly_chart(fig_st, use_container_width=True)

    # ── Detailed table ───────────────────────────────────
    with st.expander("📋 Detailed Customer Table (Top 100)"):
        display = cust.head(100)[["Customer_ID","Customer_Name","Gender","Age","City","State",
                                   "Total_Revenue","Total_Orders","Avg_Order_Value"]].copy()
        display["Total_Revenue"]   = display["Total_Revenue"].apply(fmt_currency)
        display["Avg_Order_Value"] = display["Avg_Order_Value"].apply(fmt_currency)
        st.dataframe(display, use_container_width=True)

    st.divider()
    st.download_button("📥 Download Customer Data", csv_bytes(cust),
                       "customer_data.csv", "text/csv")


# ═══════════════════════════════════════════════════════════
# PAGE 4 – Customer Segmentation
# ═══════════════════════════════════════════════════════════
SEGMENT_COLORS = {
    "VIP Customers":      "#FFD700",
    "Loyal Customers":    "#52c41a",
    "Potential Loyal":    "#1890ff",
    "New Customers":      "#13c2c2",
    "At-Risk Customers":  "#fa8c16",
    "Lost Customers":     "#ff4d4f",
}


def page_segmentation(df: pd.DataFrame) -> None:
    st.title("🎯 Customer Segmentation  —  RFM Analysis")
    st.caption("Customers classified using Recency · Frequency · Monetary analysis.")

    if df.empty:
        st.warning("No data matches the selected filters."); return

    with st.spinner("Running RFM segmentation …"):
        rfm_df, summary = get_segmentation(df)

    # ── Segment KPI row ───────────────────────────────────
    total_seg = summary["Customers"].sum()
    for seg in summary["Segment"]:
        row = summary[summary["Segment"] == seg].iloc[0]

    n_cols = min(len(summary), 6)
    cols = st.columns(n_cols)
    for col, (_, row) in zip(cols, summary.iterrows()):
        col.metric(
            label=row["Segment"],
            value=fmt_num(row["Customers"]),
            delta=f"{row['Customers']/total_seg*100:.1f}% of base",
        )

    st.divider()

    # ── Segment distribution chart ────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        section("Customers per Segment")
        fig_s = px.pie(summary, values="Customers", names="Segment",
                       hole=0.42,
                       color="Segment",
                       color_discrete_map=SEGMENT_COLORS)
        apply_layout(fig_s, 380)
        fig_s.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_s, use_container_width=True)

    with col_r:
        section("Revenue per Segment")
        fig_r = px.bar(summary, x="Segment", y="Total_Revenue",
                       color="Segment",
                       color_discrete_map=SEGMENT_COLORS,
                       text=summary["Total_Revenue"].apply(fmt_currency))
        apply_layout(fig_r, 380)
        fig_r.update_traces(textposition="outside")
        fig_r.update_layout(showlegend=False, xaxis_tickangle=-25)
        st.plotly_chart(fig_r, use_container_width=True)

    # ── RFM scatter ───────────────────────────────────────
    section("RFM Scatter Plot — Recency vs Monetary")
    fig_sc = px.scatter(
        rfm_df, x="Recency", y="Monetary",
        size="Frequency", color="Segment",
        color_discrete_map=SEGMENT_COLORS,
        hover_data=["Customer_Name","City","Frequency"],
        opacity=0.75,
        size_max=24,
    )
    apply_layout(fig_sc, 500)
    fig_sc.update_layout(yaxis_tickformat="₹,.0f")
    st.plotly_chart(fig_sc, use_container_width=True)

    # ── Avg metrics table ─────────────────────────────────
    section("Segment Performance Summary")
    disp = summary.copy()
    disp["Total_Revenue"] = disp["Total_Revenue"].apply(fmt_currency)
    disp["Avg_Revenue"]   = disp["Avg_Revenue"].apply(fmt_currency)
    disp["Avg_Recency"]   = disp["Avg_Recency"].round(0).astype(int).astype(str) + " days"
    disp["Avg_Frequency"] = disp["Avg_Frequency"].round(1)
    disp.columns = ["Segment","# Customers","Avg Recency",
                    "Avg Frequency","Total Revenue","Avg Revenue"]
    st.dataframe(disp.set_index("Segment"), use_container_width=True)

    # ── Explanations ─────────────────────────────────────
    with st.expander("ℹ️ How are segments calculated?"):
        st.markdown("""
| Segment | Rule |
|---|---|
| **VIP Customers** | R≥4, F≥4, M≥4 — Most recent, most frequent, highest spenders |
| **Loyal Customers** | F≥4, M≥3 — Buy frequently with good spend |
| **Potential Loyal** | R≥3, F≥2, M≥2 — Recent with moderate engagement |
| **New Customers** | R≥4, F=1 — Ordered recently but only once |
| **At-Risk Customers** | R∈{2,3}, F≥3 — Previously active, now drifting |
| **Lost Customers** | R=1 — Haven't ordered in a very long time |

Scores 1–5 are assigned per quintile. R uses **inverse** scoring (lower recency = higher score).
        """)

    st.divider()
    st.download_button("📥 Download Segmentation Data", csv_bytes(rfm_df),
                       "customer_segments.csv", "text/csv")


# ═══════════════════════════════════════════════════════════
# PAGE 5 – Product Analytics
# ═══════════════════════════════════════════════════════════
def page_products(df: pd.DataFrame) -> None:
    st.title("📦 Product Analytics")
    st.caption("Product-level performance: revenue, profit, quantity, and category insights.")

    if df.empty:
        st.warning("No data matches the selected filters."); return

    tp = top_products(df, n=len(df["Product_Name"].unique()))

    # ── Best sellers ──────────────────────────────────────
    section("Top 10 Products by Revenue")
    fig_rev = px.bar(tp.head(10), x="Revenue", y="Product_Name", orientation="h",
                     color="Profit", color_continuous_scale="Bluered",
                     text=tp.head(10)["Revenue"].apply(fmt_currency))
    apply_layout(fig_rev, 420)
    fig_rev.update_traces(textposition="outside")
    st.plotly_chart(fig_rev, use_container_width=True)

    col_l, col_r = st.columns(2)

    with col_l:
        section("Most Profitable Products (Top 10)")
        tp_profit = tp.sort_values("Profit", ascending=False).head(10)
        fig_pf = px.bar(tp_profit, x="Profit", y="Product_Name", orientation="h",
                        color="Profit", color_continuous_scale="Greens",
                        text=tp_profit["Profit"].apply(fmt_currency))
        apply_layout(fig_pf, 400)
        fig_pf.update_traces(textposition="outside")
        fig_pf.update_coloraxes(showscale=False)
        st.plotly_chart(fig_pf, use_container_width=True)

    with col_r:
        section("Quantity Sold — Top 10 Products")
        tp_qty = tp.sort_values("Quantity_Sold", ascending=False).head(10)
        fig_q = px.bar(tp_qty, x="Quantity_Sold", y="Product_Name", orientation="h",
                       color="Quantity_Sold", color_continuous_scale="Oranges",
                       text="Quantity_Sold")
        apply_layout(fig_q, 400)
        fig_q.update_traces(textposition="outside")
        fig_q.update_coloraxes(showscale=False)
        st.plotly_chart(fig_q, use_container_width=True)

    # ── Category sunburst ─────────────────────────────────
    section("Category & Sub-Category Revenue Sunburst")
    sc = subcategory_performance(df)
    fig_sun = px.sunburst(sc, path=["Category","Sub_Category"],
                          values="Revenue", color="Profit",
                          color_continuous_scale="RdYlGn",
                          color_continuous_midpoint=0)
    apply_layout(fig_sun, 500)
    st.plotly_chart(fig_sun, use_container_width=True)

    # ── Low-performing products ───────────────────────────
    with st.expander("⚠️ Low-Performing Products (Bottom 10 by Revenue)"):
        low = tp.sort_values("Revenue").head(10)
        st.dataframe(low.reset_index(drop=True), use_container_width=True)

    # ── Full product table ───────────────────────────────
    with st.expander("📋 Full Product Performance Table"):
        disp = tp.copy()
        disp["Revenue"]       = disp["Revenue"].apply(fmt_currency)
        disp["Profit"]        = disp["Profit"].apply(fmt_currency)
        disp["Profit_Margin"] = (
            (tp["Profit"] / tp["Revenue"].replace(0, np.nan) * 100).round(1).astype(str) + "%"
        )
        st.dataframe(disp.reset_index(drop=True), use_container_width=True)

    st.divider()
    st.download_button("📥 Download Product Report", csv_bytes(tp),
                       "product_report.csv", "text/csv")


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════
def main() -> None:
    # ── Load data ─────────────────────────────────────────
    try:
        with st.spinner("Loading data …"):
            df_raw = get_data()
    except FileNotFoundError:
        st.error(
            "Dataset not found.  Run the setup script first:\n\n"
            "```bash\npython src/generate_dataset.py\npython src/data_cleaning.py\n```"
        )
        return
    except Exception as exc:
        st.error(f"Unexpected error loading data: {exc}")
        return

    if df_raw.empty:
        st.error("The dataset is empty. Please check the data files.")
        return

    # ── Sidebar filters ───────────────────────────────────
    page, filters = render_sidebar(df_raw)
    df = apply_filters(df_raw, filters)

    if df.empty:
        st.warning(
            "⚠️ No records match the selected filters. "
            "Please widen the filter criteria."
        )
        return

    # ── Route to page ─────────────────────────────────────
    if "Executive Overview" in page:
        page_executive(df)
    elif "Sales Analysis" in page:
        page_sales(df)
    elif "Customer Analytics" in page:
        page_customers(df)
    elif "Customer Segmentation" in page:
        page_segmentation(df)
    elif "Product Analytics" in page:
        page_products(df)


if __name__ == "__main__":
    main()
