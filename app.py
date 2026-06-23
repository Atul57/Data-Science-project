import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="Cafe Sales Dashboard",
    page_icon="☕",
    layout="wide"
)

# -----------------------------------
# Load Data
# -----------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("cafe_sales_cleaned_ADC.csv")

df = load_data()

# -----------------------------------
# Title
# -----------------------------------
st.title("☕ Cafe Sales Dashboard")
st.markdown("---")

# -----------------------------------
# Sidebar Filters
# -----------------------------------
st.sidebar.header("Filters")

# Item Filter
if 'Item' in df.columns:
    item_list = ["All"] + sorted(df['Item'].astype(str).unique().tolist())
    selected_item = st.sidebar.selectbox("Select Item", item_list)

    if selected_item != "All":
        df = df[df['Item'] == selected_item]

# Location Filter
if 'Location' in df.columns:
    location_list = ["All"] + sorted(df['Location'].astype(str).unique().tolist())
    selected_location = st.sidebar.selectbox("Select Location", location_list)

    if selected_location != "All":
        df = df[df['Location'] == selected_location]

# -----------------------------------
# KPI Section
# -----------------------------------
st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", len(df))

if 'Total Spent' in df.columns:
    col2.metric("Revenue", f"₹{df['Total Spent'].sum():,.2f}")

if 'Quantity' in df.columns:
    col3.metric("Quantity Sold", int(df['Quantity'].sum()))

col4.metric("Columns", len(df.columns))

st.markdown("---")

# -----------------------------------
# Charts
# -----------------------------------

# Sales by Item
if 'Item' in df.columns and 'Total Spent' in df.columns:

    st.subheader("💰 Sales by Item")

    sales_item = (
        df.groupby('Item')['Total Spent']
        .sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(5,3))
    sales_item.plot(kind='bar', ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Quantity by Item
if 'Item' in df.columns and 'Quantity' in df.columns:

    st.subheader("📦 Quantity Sold by Item")

    qty_item = (
        df.groupby('Item')['Quantity']
        .sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(5,3))
    qty_item.plot(kind='bar', ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Location Pie Chart
if 'Location' in df.columns and 'Total Spent' in df.columns:

    st.subheader("📍 Revenue by Location")

    location_sales = df.groupby('Location')['Total Spent'].sum()

    fig, ax = plt.subplots(figsize=(6,6))
    ax.pie(
        location_sales,
        labels=location_sales.index,
        autopct='%1.1f%%'
    )

    st.pyplot(fig)

# Payment Method Chart
if 'Payment Method' in df.columns:

    st.subheader("💳 Payment Method Distribution")

    payment_counts = df['Payment Method'].value_counts()

    fig, ax = plt.subplots(figsize=(6,4))
    payment_counts.plot(kind='bar', ax=ax)

    st.pyplot(fig)

# -----------------------------------
# Summary Statistics
# -----------------------------------
st.subheader("📈 Summary Statistics")

st.dataframe(df.describe(include='all'))

# -----------------------------------
# Missing Values
# -----------------------------------
st.subheader("🔍 Missing Values")

missing = df.isnull().sum()
st.dataframe(missing)

# -----------------------------------
# Dataset Preview
# -----------------------------------
st.subheader("📋 Cleaned Dataset")

st.dataframe(df)

# -----------------------------------
# Download Button
# -----------------------------------
csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="⬇ Download Filtered Data",
    data=csv,
    file_name="filtered_cafe_sales.csv",
    mime="text/csv"
)