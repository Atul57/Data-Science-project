"""
Cafe Sales Analytics Dashboard
A production-ready Streamlit application for analyzing cafe sales data.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import io
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# CONFIG & THEME
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Cafe Sales Analytics Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CONSTANTS
# ─────────────────────────────────────────────
DATA_FILE = "cafe_sales_cleaned_ADC.csv"
COLORS = {
    "primary":   "#F59E0B",
    "secondary": "#10B981",
    "accent":    "#6366F1",
    "danger":    "#EF4444",
    "info":      "#3B82F6",
    "bg":        "#0F172A",
    "card":      "#1E293B",
    "border":    "#334155",
    "text":      "#F1F5F9",
    "muted":     "#94A3B8",
}
PALETTE = [
    "#F59E0B", "#10B981", "#6366F1", "#EF4444",
    "#3B82F6", "#8B5CF6", "#EC4899", "#14B8A6",
]

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
def inject_css():
    st.markdown(f"""
    <style>
    /* ── Base ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        background-color: {COLORS['bg']};
        color: {COLORS['text']};
    }}
    .stApp {{ background-color: {COLORS['bg']}; }}

    /* ── Hide default chrome ── */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stDeployButton {{ display: none; }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        border-right: 1px solid {COLORS['border']};
    }}
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {{
        color: {COLORS['primary']};
    }}

    /* ── KPI cards ── */
    .kpi-card {{
        background: linear-gradient(135deg, {COLORS['card']} 0%, #162032 100%);
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 24px 20px;
        text-align: center;
        transition: transform .2s, box-shadow .2s;
        position: relative;
        overflow: hidden;
    }}
    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent']});
    }}
    .kpi-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(245,158,11,.15);
    }}
    .kpi-label {{
        font-size: .75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: .1em;
        color: {COLORS['muted']};
        margin-bottom: 8px;
    }}
    .kpi-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['text']};
        line-height: 1.1;
    }}
    .kpi-sub {{
        font-size: .8rem;
        color: {COLORS['muted']};
        margin-top: 6px;
    }}
    .kpi-icon {{
        font-size: 2rem;
        margin-bottom: 8px;
        display: block;
    }}

    /* ── Section headings ── */
    .section-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.15rem;
        font-weight: 700;
        color: {COLORS['text']};
        margin: 28px 0 16px;
        padding-bottom: 10px;
        border-bottom: 2px solid {COLORS['border']};
    }}
    .section-header span.icon {{
        font-size: 1.3rem;
    }}

    /* ── Insight cards ── */
    .insight-card {{
        background: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
    }}
    .insight-title {{
        font-size: .8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: .08em;
        color: {COLORS['primary']};
        margin-bottom: 6px;
    }}
    .insight-body {{
        font-size: .95rem;
        color: {COLORS['text']};
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {COLORS['card']};
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        font-weight: 600;
        color: {COLORS['muted']};
    }}
    .stTabs [aria-selected="true"] {{
        background: {COLORS['primary']} !important;
        color: #000 !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['primary']}, #D97706);
        color: #000;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: opacity .2s;
    }}
    .stButton > button:hover {{ opacity: .85; }}

    /* ── Inputs ── */
    .stSelectbox > div > div,
    .stDateInput > div > div,
    .stTextInput > div > div,
    .stNumberInput > div > div {{
        background: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        color: {COLORS['text']};
    }}

    /* ── Dataframe ── */
    .stDataFrame {{ border-radius: 12px; overflow: hidden; }}

    /* ── Success / warning / error ── */
    .stSuccess {{ border-radius: 8px; }}

    /* ── Page title bar ── */
    .page-title {{
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    .page-title h1 {{
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .page-title p {{
        margin: 4px 0 0;
        color: {COLORS['muted']};
        font-size: .9rem;
    }}
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LAYER
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(filepath: str) -> pd.DataFrame:
    """Load and clean the CSV dataset."""
    df = pd.read_csv(filepath)

    # Normalise column names
    df.columns = df.columns.str.strip()

    # Parse dates
    df["Transaction Date"] = pd.to_datetime(
        df["Transaction Date"], format="mixed", errors="coerce"
    )

    # Numeric coercion
    for col in ["Quantity", "Price Per Unit", "Total Spent"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with critical nulls
    df = df.dropna(subset=["Transaction ID", "Transaction Date"])

    # Remove exact duplicates
    df = df.drop_duplicates(subset=["Transaction ID"])

    # Derived time columns
    df["Month"]   = df["Transaction Date"].dt.to_period("M").astype(str)
    df["Weekday"] = df["Transaction Date"].dt.day_name()
    df["Quarter"] = "Q" + df["Transaction Date"].dt.quarter.astype(str)
    df["Year"]    = df["Transaction Date"].dt.year

    return df.reset_index(drop=True)


def save_data(df: pd.DataFrame, filepath: str):
    """Persist DataFrame back to CSV (drop derived cols first)."""
    cols_to_drop = [c for c in ["Month", "Weekday", "Quarter", "Year"] if c in df.columns]
    df.drop(columns=cols_to_drop).to_csv(filepath, index=False)


def reload():
    """Clear cache and rerun."""
    st.cache_data.clear()
    st.rerun()


# ─────────────────────────────────────────────
# FILTER HELPERS
# ─────────────────────────────────────────────
def apply_filters(df: pd.DataFrame, item, location, payment, date_range) -> pd.DataFrame:
    fdf = df.copy()
    if item != "All":
        fdf = fdf[fdf["Item"] == item]
    if location != "All":
        fdf = fdf[fdf["Location"] == location]
    if payment != "All":
        fdf = fdf[fdf["Payment Method"] == payment]
    if date_range and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        fdf = fdf[(fdf["Transaction Date"] >= start) & (fdf["Transaction Date"] <= end)]
    return fdf


# ─────────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color=COLORS["text"]),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS["text"])),
    xaxis=dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"]),
    yaxis=dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"]),
)

def styled(fig) -> go.Figure:
    fig.update_layout(**CHART_LAYOUT)
    return fig


# ─────────────────────────────────────────────
# KPI SECTION
# ─────────────────────────────────────────────
def render_kpis(df: pd.DataFrame):
    total_rev   = df["Total Spent"].sum()
    total_orders= len(df)
    total_qty   = df["Quantity"].sum()
    avg_order   = df["Total Spent"].mean() if total_orders else 0
    top_product = df.groupby("Item")["Quantity"].sum().idxmax() if total_orders else "N/A"
    top_payment = df["Payment Method"].value_counts().idxmax() if total_orders else "N/A"

    cards = [
        ("💰", "Total Revenue",       f"${total_rev:,.2f}",       "Filtered period"),
        ("🧾", "Total Orders",         f"{total_orders:,}",         "Transactions"),
        ("📦", "Quantity Sold",        f"{int(total_qty):,}",       "Units"),
        ("📊", "Avg Order Value",      f"${avg_order:.2f}",         "Per transaction"),
        ("🏆", "Top Product",          top_product,                  "By quantity"),
        ("💳", "Top Payment",          top_payment,                  "By frequency"),
    ]

    cols = st.columns(6)
    for col, (icon, label, value, sub) in zip(cols, cards):
        col.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-icon">{icon}</span>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# REVENUE CHARTS
# ─────────────────────────────────────────────
def chart_monthly_revenue(df: pd.DataFrame):
    mrev = (
        df.groupby("Month")["Total Spent"]
          .sum()
          .reset_index()
          .sort_values("Month")
    )
    fig = px.line(
        mrev, x="Month", y="Total Spent",
        title="Monthly Revenue Trend",
        markers=True, color_discrete_sequence=[COLORS["primary"]],
    )
    fig.update_traces(line_width=2.5, marker_size=7,
                      fill="tozeroy",
                      fillcolor=f"rgba(245,158,11,.1)")
    return styled(fig)


def chart_daily_revenue(df: pd.DataFrame):
    drev = (
        df.groupby(df["Transaction Date"].dt.date)["Total Spent"]
          .sum()
          .reset_index()
    )
    drev.columns = ["Date", "Total Spent"]
    fig = px.bar(
        drev, x="Date", y="Total Spent",
        title="Daily Revenue",
        color_discrete_sequence=[COLORS["accent"]],
    )
    return styled(fig)


def chart_revenue_growth(df: pd.DataFrame):
    mrev = (
        df.groupby("Month")["Total Spent"]
          .sum()
          .reset_index()
          .sort_values("Month")
    )
    mrev["Growth %"] = mrev["Total Spent"].pct_change() * 100
    mrev = mrev.dropna()
    colors = [COLORS["secondary"] if v >= 0 else COLORS["danger"] for v in mrev["Growth %"]]
    fig = go.Figure(go.Bar(
        x=mrev["Month"], y=mrev["Growth %"],
        marker_color=colors, name="Growth %",
    ))
    fig.update_layout(title="Monthly Revenue Growth %")
    return styled(fig)


# ─────────────────────────────────────────────
# PRODUCT CHARTS
# ─────────────────────────────────────────────
def chart_revenue_by_product(df: pd.DataFrame):
    pdata = (
        df.groupby("Item")["Total Spent"]
          .sum()
          .reset_index()
          .sort_values("Total Spent", ascending=False)
    )
    fig = px.bar(
        pdata, x="Total Spent", y="Item",
        orientation="h", title="Revenue by Product",
        color="Total Spent", color_continuous_scale="YlOrBr",
    )
    fig.update_layout(coloraxis_showscale=False, yaxis_title="")
    return styled(fig)


def chart_qty_by_product(df: pd.DataFrame):
    qdata = (
        df.groupby("Item")["Quantity"]
          .sum()
          .reset_index()
          .sort_values("Quantity", ascending=False)
    )
    fig = px.bar(
        qdata, x="Item", y="Quantity",
        title="Quantity Sold by Product",
        color="Item", color_discrete_sequence=PALETTE,
    )
    fig.update_layout(showlegend=False)
    return styled(fig)


def chart_top5_products(df: pd.DataFrame):
    top5 = (
        df.groupby("Item")["Total Spent"]
          .sum()
          .nlargest(5)
          .reset_index()
    )
    fig = px.pie(
        top5, names="Item", values="Total Spent",
        title="Top 5 Products – Revenue Share",
        hole=.45, color_discrete_sequence=PALETTE,
    )
    fig.update_traces(textposition="outside", textinfo="label+percent")
    return styled(fig)


def chart_revenue_contribution(df: pd.DataFrame):
    contrib = (
        df.groupby("Item")["Total Spent"]
          .sum()
          .reset_index()
    )
    contrib["Contribution %"] = contrib["Total Spent"] / contrib["Total Spent"].sum() * 100
    fig = px.funnel(
        contrib.sort_values("Contribution %", ascending=False),
        x="Contribution %", y="Item",
        title="Revenue Contribution % by Product",
        color_discrete_sequence=PALETTE,
    )
    return styled(fig)


# ─────────────────────────────────────────────
# LOCATION CHARTS
# ─────────────────────────────────────────────
def chart_revenue_by_location(df: pd.DataFrame):
    ldata = df.groupby("Location")["Total Spent"].sum().reset_index()
    fig = px.pie(
        ldata, names="Location", values="Total Spent",
        title="Revenue by Location",
        hole=.5, color_discrete_sequence=[COLORS["primary"], COLORS["accent"]],
    )
    return styled(fig)


def chart_orders_by_location(df: pd.DataFrame):
    odata = df["Location"].value_counts().reset_index()
    odata.columns = ["Location", "Orders"]
    fig = px.bar(
        odata, x="Location", y="Orders",
        title="Orders by Location",
        color="Location",
        color_discrete_sequence=[COLORS["secondary"], COLORS["info"]],
    )
    fig.update_layout(showlegend=False)
    return styled(fig)


# ─────────────────────────────────────────────
# PAYMENT CHARTS
# ─────────────────────────────────────────────
def chart_payment_distribution(df: pd.DataFrame):
    pdata = df["Payment Method"].value_counts().reset_index()
    pdata.columns = ["Method", "Count"]
    fig = px.pie(
        pdata, names="Method", values="Count",
        title="Payment Method Distribution",
        hole=.4, color_discrete_sequence=PALETTE,
    )
    return styled(fig)


def chart_revenue_by_payment(df: pd.DataFrame):
    rdata = (
        df.groupby("Payment Method")["Total Spent"]
          .sum()
          .reset_index()
          .sort_values("Total Spent", ascending=False)
    )
    fig = px.bar(
        rdata, x="Payment Method", y="Total Spent",
        title="Revenue by Payment Method",
        color="Payment Method", color_discrete_sequence=PALETTE,
    )
    fig.update_layout(showlegend=False)
    return styled(fig)


# ─────────────────────────────────────────────
# TIME CHARTS
# ─────────────────────────────────────────────
def chart_revenue_by_weekday(df: pd.DataFrame):
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    wdata = df.groupby("Weekday")["Total Spent"].sum().reindex(order).reset_index()
    fig = px.bar(
        wdata, x="Weekday", y="Total Spent",
        title="Revenue by Weekday",
        color="Total Spent", color_continuous_scale="YlOrBr",
    )
    fig.update_layout(coloraxis_showscale=False)
    return styled(fig)


def chart_revenue_by_quarter(df: pd.DataFrame):
    qdata = (
        df.groupby("Quarter")["Total Spent"]
          .sum()
          .reset_index()
          .sort_values("Quarter")
    )
    fig = px.bar(
        qdata, x="Quarter", y="Total Spent",
        title="Revenue by Quarter",
        color="Quarter", color_discrete_sequence=PALETTE,
    )
    fig.update_layout(showlegend=False)
    return styled(fig)


# ─────────────────────────────────────────────
# FORECAST
# ─────────────────────────────────────────────
def chart_forecast(df: pd.DataFrame):
    mrev = (
        df.groupby("Month")["Total Spent"]
          .sum()
          .reset_index()
          .sort_values("Month")
    )
    if len(mrev) < 3:
        return None
    y = mrev["Total Spent"].values
    x = np.arange(len(y))
    # Simple linear regression
    m, b = np.polyfit(x, y, 1)
    forecast_steps = 3
    x_fore = np.arange(len(y), len(y) + forecast_steps)

    # Generate future month labels
    last_period = pd.Period(mrev["Month"].iloc[-1], freq="M")
    future_months = [(last_period + i + 1).strftime("%Y-%m") for i in range(forecast_steps)]
    y_fore = m * x_fore + b

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mrev["Month"], y=y,
        mode="lines+markers", name="Actual",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=7),
    ))
    fig.add_trace(go.Scatter(
        x=future_months, y=y_fore,
        mode="lines+markers", name="Forecast",
        line=dict(color=COLORS["accent"], width=2.5, dash="dash"),
        marker=dict(size=7, symbol="diamond"),
    ))
    fig.update_layout(title="Revenue Forecast (Next 3 Months)")
    return styled(fig)


# ─────────────────────────────────────────────
# SECTION HEADER HELPER
# ─────────────────────────────────────────────
def section(icon: str, title: str):
    st.markdown(
        f'<div class="section-header"><span class="icon">{icon}</span>{title}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# TAB 1 – DASHBOARD
# ─────────────────────────────────────────────
def tab_dashboard(df: pd.DataFrame):
    # KPIs
    section("📌", "Key Performance Indicators")
    render_kpis(df)

    # Revenue Analysis
    section("💹", "Revenue Analysis")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_monthly_revenue(df), use_container_width=True)
    with c2:
        st.plotly_chart(chart_revenue_growth(df), use_container_width=True)
    st.plotly_chart(chart_daily_revenue(df), use_container_width=True)

    # Product Analysis
    section("🛍️", "Product Analysis")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_revenue_by_product(df), use_container_width=True)
    with c2:
        st.plotly_chart(chart_qty_by_product(df), use_container_width=True)
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(chart_top5_products(df), use_container_width=True)
    with c4:
        st.plotly_chart(chart_revenue_contribution(df), use_container_width=True)

    # Location Analysis
    section("📍", "Location Analysis")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_revenue_by_location(df), use_container_width=True)
    with c2:
        st.plotly_chart(chart_orders_by_location(df), use_container_width=True)

    # Payment Analysis
    section("💳", "Payment Analysis")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_payment_distribution(df), use_container_width=True)
    with c2:
        st.plotly_chart(chart_revenue_by_payment(df), use_container_width=True)

    # Time Analysis
    section("🕐", "Time Analysis")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_revenue_by_weekday(df), use_container_width=True)
    with c2:
        st.plotly_chart(chart_revenue_by_quarter(df), use_container_width=True)


# ─────────────────────────────────────────────
# TAB 2 – ADD TRANSACTION
# ─────────────────────────────────────────────
def tab_add_transaction(df: pd.DataFrame):
    section("➕", "Add New Transaction")

    items        = sorted(df["Item"].dropna().unique().tolist())
    locations    = sorted(df["Location"].dropna().unique().tolist())
    pay_methods  = sorted(df["Payment Method"].dropna().unique().tolist())

    with st.form("add_txn_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            txn_id  = st.text_input("Transaction ID *", placeholder="e.g. TXN_1234567")
            item    = st.selectbox("Item *", items)
            qty     = st.number_input("Quantity *", min_value=1, max_value=100, value=1, step=1)
            ppu     = st.number_input("Price Per Unit ($) *", min_value=0.01, value=2.00, step=0.50)
        with c2:
            payment  = st.selectbox("Payment Method *", pay_methods)
            location = st.selectbox("Location *", locations)
            txn_date = st.date_input("Transaction Date *", value=datetime.today())

        # Live total calc
        total = qty * ppu
        st.metric("Auto-calculated Total Spent", f"${total:.2f}")

        submitted = st.form_submit_button("💾 Save Transaction", use_container_width=True)

    if submitted:
        errors = []
        if not txn_id.strip():
            errors.append("Transaction ID is required.")
        elif txn_id.strip() in df["Transaction ID"].values:
            errors.append(f"Transaction ID **{txn_id}** already exists.")
        if errors:
            for e in errors:
                st.error(e)
        else:
            new_row = {
                "Transaction ID":  txn_id.strip(),
                "Item":            item,
                "Quantity":        float(qty),
                "Price Per Unit":  float(ppu),
                "Total Spent":     round(float(total), 2),
                "Payment Method":  payment,
                "Location":        location,
                "Transaction Date": str(txn_date),
            }
            updated = pd.concat([df.drop(columns=["Month","Weekday","Quarter","Year"], errors="ignore"),
                                  pd.DataFrame([new_row])], ignore_index=True)
            save_data(updated, DATA_FILE)
            st.success(f"✅ Transaction **{txn_id}** saved successfully!")
            reload()


# ─────────────────────────────────────────────
# TAB 3 – MANAGE DATASET
# ─────────────────────────────────────────────
def tab_manage(df: pd.DataFrame):
    section("📋", "Manage Dataset")

    # ── Search filters ──
    c1, c2, c3 = st.columns(3)
    search_id  = c1.text_input("🔍 Search Transaction ID")
    search_prd = c2.text_input("🔍 Search Product")
    search_loc = c3.text_input("🔍 Search Location")

    view_df = df.copy()
    if search_id:
        view_df = view_df[view_df["Transaction ID"].str.contains(search_id, case=False, na=False)]
    if search_prd:
        view_df = view_df[view_df["Item"].str.contains(search_prd, case=False, na=False)]
    if search_loc:
        view_df = view_df[view_df["Location"].str.contains(search_loc, case=False, na=False)]

    display_cols = ["Transaction ID","Item","Quantity","Price Per Unit","Total Spent","Payment Method","Location","Transaction Date"]
    view_df_show = view_df[display_cols].copy()
    view_df_show["Transaction Date"] = view_df_show["Transaction Date"].dt.strftime("%Y-%m-%d")

    st.info(f"Showing **{len(view_df_show):,}** of **{len(df):,}** records")

    # ── Editable table ──
    edited = st.data_editor(
        view_df_show,
        use_container_width=True,
        num_rows="dynamic",
        key="data_editor",
        hide_index=True,
    )

    col_a, col_b = st.columns(2)

    # ── Save Changes ──
    if col_a.button("💾 Save Changes", use_container_width=True):
        try:
            # Merge edits back into master df
            base = df.drop(columns=["Month","Weekday","Quarter","Year"], errors="ignore")
            # Remove rows that were in view, then append edited version
            edited_ids = edited["Transaction ID"].tolist()
            base = base[~base["Transaction ID"].isin(edited_ids)]
            edited["Transaction Date"] = pd.to_datetime(edited["Transaction Date"], errors="coerce").dt.strftime("%Y-%m-%d")
            merged = pd.concat([base, edited], ignore_index=True)
            save_data(merged, DATA_FILE)
            st.success("✅ Changes saved!")
            reload()
        except Exception as ex:
            st.error(f"Error saving: {ex}")

    # ── Download ──
    csv_buf = io.StringIO()
    view_df_show.to_csv(csv_buf, index=False)
    col_b.download_button(
        "⬇️ Download Filtered CSV",
        data=csv_buf.getvalue(),
        file_name="cafe_filtered.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # ── Delete Transaction ──
    section("🗑️", "Delete Transaction")
    if len(view_df_show) == 0:
        st.warning("No records to delete in current view.")
    else:
        del_id = st.selectbox(
            "Select Transaction to Delete",
            options=view_df_show["Transaction ID"].tolist(),
        )
        confirm = st.checkbox(f"✅ I confirm I want to delete **{del_id}**")
        if st.button("🗑️ Delete Transaction", use_container_width=False):
            if confirm:
                updated = df[df["Transaction ID"] != del_id].copy()
                save_data(updated, DATA_FILE)
                st.success(f"Transaction **{del_id}** deleted.")
                reload()
            else:
                st.warning("Please check the confirmation box first.")

    # ── Download full dataset ──
    st.markdown("---")
    full_buf = io.StringIO()
    df[display_cols].copy().assign(**{
        "Transaction Date": df["Transaction Date"].dt.strftime("%Y-%m-%d")
    }).to_csv(full_buf, index=False)
    st.download_button(
        "⬇️ Download Full Dataset",
        data=full_buf.getvalue(),
        file_name="cafe_sales_full.csv",
        mime="text/csv",
    )


# ─────────────────────────────────────────────
# TAB 4 – ADVANCED INSIGHTS
# ─────────────────────────────────────────────
def tab_insights(df: pd.DataFrame):
    section("🧠", "Advanced Analytics")

    # ── Summary metrics ──
    total_rev     = df["Total Spent"].sum()
    prod_rev      = df.groupby("Item")["Total Spent"].sum()
    prod_qty      = df.groupby("Item")["Quantity"].sum()
    loc_rev       = df.groupby("Location")["Total Spent"].sum()
    pay_rev       = df.groupby("Payment Method")["Total Spent"].sum()
    mrev          = df.groupby("Month")["Total Spent"].sum().sort_index()
    growth        = mrev.pct_change().mean() * 100

    best_prod   = prod_rev.idxmax()
    worst_prod  = prod_rev.idxmin()
    best_loc    = loc_rev.idxmax()
    best_pay    = pay_rev.idxmax()

    insights = [
        ("🏆 Best Selling Product",      f"{best_prod} — ${prod_rev[best_prod]:,.2f} revenue, {int(prod_qty[best_prod]):,} units sold"),
        ("📉 Worst Selling Product",     f"{worst_prod} — ${prod_rev[worst_prod]:,.2f} revenue, {int(prod_qty[worst_prod]):,} units sold"),
        ("📍 Highest Revenue Location",  f"{best_loc} — ${loc_rev[best_loc]:,.2f} ({loc_rev[best_loc]/total_rev*100:.1f}% of total)"),
        ("💳 Top Payment Method",        f"{best_pay} — ${pay_rev[best_pay]:,.2f} revenue"),
        ("📈 Avg Monthly Growth Rate",   f"{growth:+.2f}% per month"),
        ("🗓️ Peak Month",                f"{mrev.idxmax()} — ${mrev.max():,.2f}"),
        ("💤 Slowest Month",             f"{mrev.idxmin()} — ${mrev.min():,.2f}"),
    ]

    for title, body in insights:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">{title}</div>
            <div class="insight-body">{body}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Forecast ──
    section("🔭", "Revenue Forecast")
    fc = chart_forecast(df)
    if fc:
        st.plotly_chart(fc, use_container_width=True)

    # ── Monthly growth table ──
    section("📅", "Month-over-Month Performance")
    mdf = mrev.reset_index()
    mdf.columns = ["Month", "Revenue"]
    mdf["MoM Growth %"] = mdf["Revenue"].pct_change() * 100
    mdf["Revenue"] = mdf["Revenue"].map("${:,.2f}".format)
    mdf["MoM Growth %"] = mdf["MoM Growth %"].map(
        lambda v: f"+{v:.1f}%" if pd.notna(v) and v >= 0 else (f"{v:.1f}%" if pd.notna(v) else "—")
    )
    st.dataframe(mdf, use_container_width=True, hide_index=True)

    # ── Recommendations ──
    section("💡", "Business Recommendations")
    recs = []
    if growth < 0:
        recs.append(("⚠️ Revenue Declining", f"Average monthly growth is {growth:.2f}%. Consider promotions on slow days."))
    else:
        recs.append(("✅ Healthy Growth", f"Revenue is growing at {growth:.2f}% per month on average."))

    pct_best = prod_rev[best_prod] / total_rev * 100
    if pct_best > 40:
        recs.append(("📌 Concentration Risk", f"{best_prod} accounts for {pct_best:.1f}% of revenue. Diversify product marketing."))

    for r_title, r_body in recs:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">{r_title}</div>
            <div class="insight-body">{r_body}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Export summary report ──
    section("📤", "Export Summary Report")
    report_lines = ["Cafe Sales Analytics – Summary Report", "=" * 48, ""]
    report_lines.append(f"Total Revenue:         ${total_rev:,.2f}")
    report_lines.append(f"Total Transactions:    {len(df):,}")
    report_lines.append(f"Best Product:          {best_prod}")
    report_lines.append(f"Worst Product:         {worst_prod}")
    report_lines.append(f"Top Location:          {best_loc}")
    report_lines.append(f"Top Payment:           {best_pay}")
    report_lines.append(f"Avg Monthly Growth:    {growth:+.2f}%")
    report_lines.append("")
    report_lines.append("Monthly Revenue:")
    for _, row in mrev.reset_index().iterrows():
        report_lines.append(f"  {row['Month']}: ${row['Total Spent']:,.2f}")
    report_text = "\n".join(report_lines)

    st.download_button(
        "⬇️ Download Summary Report (.txt)",
        data=report_text,
        file_name="cafe_summary_report.txt",
        mime="text/plain",
    )


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame):
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 16px 0 8px;'>
            <span style='font-size:2.5rem'>☕</span>
            <h2 style='margin:4px 0 0; color:#F59E0B; font-size:1.1rem;'>Cafe Analytics</h2>
            <p style='color:#94A3B8; font-size:.8rem; margin:0'>Sales Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 🔧 Filters")

        # Item
        items_opts = ["All"] + sorted(df["Item"].dropna().unique().tolist())
        item = st.selectbox("☕ Item", items_opts)

        # Location
        loc_opts = ["All"] + sorted(df["Location"].dropna().unique().tolist())
        location = st.selectbox("📍 Location", loc_opts)

        # Payment Method
        pay_opts = ["All"] + sorted(df["Payment Method"].dropna().unique().tolist())
        payment = st.selectbox("💳 Payment Method", pay_opts)

        # Date Range
        st.markdown("#### 📅 Date Range")
        min_date = df["Transaction Date"].min().date()
        max_date = df["Transaction Date"].max().date()
        d_from = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
        d_to   = st.date_input("To",   value=max_date, min_value=min_date, max_value=max_date)

        # Reset
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.rerun()

        st.markdown("---")
        st.markdown(
            f"<p style='color:#94A3B8;font-size:.75rem;text-align:center;'>"
            f"Dataset: <b>{len(df):,}</b> records<br>"
            f"Last updated: {datetime.now().strftime('%H:%M')}</p>",
            unsafe_allow_html=True,
        )

    return item, location, payment, (d_from, d_to)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    inject_css()

    # ── Load data ──
    if not os.path.exists(DATA_FILE):
        st.error(f"Dataset not found: **{DATA_FILE}**. Please place it in the same directory as app.py.")
        st.stop()

    df = load_data(DATA_FILE)

    # ── Sidebar ──
    item, location, payment, date_range = render_sidebar(df)

    # ── Page title ──
    st.markdown(f"""
    <div class="page-title">
        <span style='font-size:2.5rem'>☕</span>
        <div>
            <h1>Cafe Sales Analytics Dashboard</h1>
            <p>Real-time insights into your cafe's sales performance</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Apply filters ──
    fdf = apply_filters(df, item, location, payment, date_range)
    if fdf.empty:
        st.warning("⚠️ No data matches the selected filters. Try resetting them.")
        return

    # ── Tabs ──
    t1, t2, t3, t4 = st.tabs([
        "📊 Dashboard",
        "➕ Add Transaction",
        "📋 Manage Dataset",
        "📈 Advanced Insights",
    ])
    with t1:
        tab_dashboard(fdf)
    with t2:
        tab_add_transaction(df)   # Always full df to check duplicates
    with t3:
        tab_manage(df)            # Full df for management
    with t4:
        tab_insights(fdf)


if __name__ == "__main__":
    main()
