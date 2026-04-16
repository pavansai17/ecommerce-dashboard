import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="📊",
    layout="wide"
)

DATA_PATH = "data/"

@st.cache_data
def load_orders():
    path = os.path.join(DATA_PATH, "olist_orders_dataset.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)

@st.cache_data
def load_items():
    path = os.path.join(DATA_PATH, "olist_order_items_dataset.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)

@st.cache_data
def load_products():
    path = os.path.join(DATA_PATH, "olist_products_dataset.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)

orders = load_orders()
items = load_items()
products = load_products()

data_loaded = all(df is not None for df in [orders, items, products])

st.sidebar.title("E-Commerce Dashboard")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate to", ["Sales & Revenue", "Product Analytics", "Inventory Tracking"])

if not data_loaded:
    st.error("Data files not found in the data/ folder. Please download the Olist dataset first.")
    st.code("kaggle datasets download -d olistbr/brazilian-ecommerce --path data/ --unzip")
    st.stop()

if page == "Sales & Revenue":
    import plotly.express as px

    st.title("Sales & Revenue")
    st.markdown("Overview of orders, revenue trends, and delivery performance.")

    merged = items.merge(orders, on="order_id")
    merged["order_purchase_timestamp"] = pd.to_datetime(merged["order_purchase_timestamp"])
    merged["month"] = merged["order_purchase_timestamp"].dt.to_period("M").astype(str)

    total_revenue = merged["price"].sum()
    total_orders = orders["order_id"].nunique()
    avg_order_value = total_revenue / total_orders

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"R$ {total_revenue:,.0f}")
    c2.metric("Total Orders", f"{total_orders:,}")
    c3.metric("Avg Order Value", f"R$ {avg_order_value:,.2f}")

    st.markdown("---")

    monthly = merged.groupby("month")["price"].sum().reset_index()
    monthly.columns = ["Month", "Revenue"]
    fig = px.line(monthly, x="Month", y="Revenue", title="Monthly Revenue Trend", markers=True)
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    status_counts = orders["order_status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig2 = px.bar(status_counts, x="Status", y="Count", title="Orders by Status", color="Status")
    st.plotly_chart(fig2, use_container_width=True)

elif page == "Product Analytics":
    import plotly.express as px

    st.title("Product Analytics")
    st.markdown("Top products, category performance, and pricing distribution.")

    merged = items.merge(products, on="product_id")

    top_cats = merged.groupby("product_category_name")["price"].sum().sort_values(ascending=False).head(10).reset_index()
    top_cats.columns = ["Category", "Revenue"]
    fig = px.bar(top_cats, x="Revenue", y="Category", orientation="h", title="Top 10 Categories by Revenue", color="Revenue", color_continuous_scale="Blues")
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.histogram(merged, x="price", nbins=50, title="Product Price Distribution", labels={"price": "Price (R$)"})
    fig2.update_layout(bargap=0.1)
    st.plotly_chart(fig2, use_container_width=True)

    top_products = merged.groupby("product_id")["price"].sum().sort_values(ascending=False).head(10).reset_index()
    top_products.columns = ["Product ID", "Total Revenue"]
    st.subheader("Top 10 Products by Revenue")
    st.dataframe(top_products, use_container_width=True)

elif page == "Inventory Tracking":
    import plotly.express as px

    st.title("Inventory Tracking")
    st.markdown("Product counts, category stock overview, and size/weight metrics.")

    c1, c2 = st.columns(2)
    c1.metric("Total Products", f"{products['product_id'].nunique():,}")
    c2.metric("Total Categories", f"{products['product_category_name'].nunique():,}")

    st.markdown("---")

    cat_counts = products["product_category_name"].value_counts().head(15).reset_index()
    cat_counts.columns = ["Category", "Product Count"]
    fig = px.bar(cat_counts, x="Category", y="Product Count", title="Top 15 Categories by Product Count", color="Product Count", color_continuous_scale="Teal")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    weight_data = products[["product_category_name", "product_weight_g"]].dropna()
    fig2 = px.box(weight_data, x="product_category_name", y="product_weight_g", title="Weight Distribution by Category")
    fig2.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)
