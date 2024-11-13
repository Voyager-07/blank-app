import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts


# Load data
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path, parse_dates=["order_date"])

st.title("E-commerce Order Dashboard")
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Show raw data
    st.subheader("Raw Data")
    st.write(df.head())
    
    # Filter data by any field
    st.sidebar.header("Filters")
    product_filter = st.sidebar.multiselect("Select Product", df['product_name'].unique())
    category_filter = st.sidebar.multiselect("Select Category", df['category'].unique())
    
    if product_filter:
        df = df[df['product_name'].isin(product_filter)]
    if category_filter:
        df = df[df['category'].isin(category_filter)]
    
    # Date filter for Daily Profit / Loss
    st.subheader("Daily Profit / Loss")
    df['profit_loss'] = df['total_price'] - df['cost_price']
    
    # Define the date range for filtering
    min_date, max_date = df['order_date'].min(), df['order_date'].max()
    date_range = st.date_input("Select Date Range", [min_date, max_date])
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['order_date'] >= pd.Timestamp(start_date)) & (df['order_date'] <= pd.Timestamp(end_date))
        filtered_df = df[mask]
    else:
        filtered_df = df
    
    # Group data by date and calculate profit/loss
    daily_profit_loss = filtered_df.groupby('order_date')['profit_loss'].sum().reset_index()

    # Daily Profit / Loss Chart
    daily_options = {
        "title": {"text": "Daily Profit / Loss", "left": "center"},
        "xAxis": {"type": "category", "data": daily_profit_loss['order_date'].dt.strftime('%Y-%m-%d').tolist()},
        "yAxis": {"type": "value"},
        "series": [{"data": daily_profit_loss['profit_loss'].tolist(), "type": "line", "color": "#5470C6"}]
    }
    st_echarts(options=daily_options)

    st.subheader("Most Popular Products or Categories")
    product_popularity = df['product_name'].value_counts().reset_index()
    product_popularity.columns = ['product_name', 'count']  # Rename columns

    category_popularity = df['category'].value_counts().reset_index()
    category_popularity.columns = ['category', 'count']  # Rename columns

    choice = st.radio("View by", ["Product", "Category"])

    if choice == "Product":
        product_options = {
            "title": {"text": "Most Popular Products", "left": "center"},
            "xAxis": {"type": "category", "data": product_popularity['product_name'].tolist()},
            "yAxis": {"type": "value"},
            "series": [{"data": product_popularity['count'].tolist(), "type": "bar", "color": "#91CC75"}]
        }
        st_echarts(options=product_options)
    else:
        category_options = {
            "title": {"text": "Most Popular Categories", "left": "center"},
            "xAxis": {"type": "category", "data": category_popularity['category'].tolist()},
            "yAxis": {"type": "value"},
            "series": [{"data": category_popularity['count'].tolist(), "type": "bar", "color": "#EE6666"}]
        }
        st_echarts(options=category_options)


    # Bonus: Identify potential fraudulent orders (orders with very high discounts)
    st.subheader("Potential Fraudulent Orders")
    fraud_threshold = st.slider("Discount Threshold", min_value=50, max_value=500, value=100)
    fraudulent_orders = df[df['total_discount'] > fraud_threshold]
    st.write(fraudulent_orders)
