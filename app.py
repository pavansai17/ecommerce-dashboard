import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import os
from datetime import datetime

# Import S3 helper functions
from s3_helper import upload_csv_to_s3, list_files_in_s3

# Page Configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid #0066cc;
    }
    .upload-box {
        border: 2px dashed #0066cc;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ─── HELPER FUNCTIONS ───────────────────────────────────────────

def detect_columns(df):
    """Auto-detect which columns are sales, product, date, quantity, category."""
    cols = {c.lower(): c for c in df.columns}
    detected = {}

    for key, keywords in {
        "date":     ["date","time","order_date","purchase","created","timestamp"],
        "sales":    ["sales","revenue","price","amount","total","payment","value"],
        "quantity": ["quantity","qty","count","units","sold","volume"],
        "product":  ["product","item","name","title","sku","description"],
        "category": ["category","type","segment","department","class","group"],
        "region":   ["region","state","city","country","location","area","zone"],
        "customer": ["customer","client","buyer","user","member"],
        "profit":   ["profit","margin","gain","net","earning"],
    }.items():
        for kw in keywords:
            match = next((orig for low, orig in cols.items() if kw in low), None)
            if match:
                detected[key] = match
                break

    return detected

def smart_summary(df, detected):
    """Generate a text summary of the dataset."""
    lines = []
    lines.append(f"Dataset contains **{len(df):,} rows** and **{len(df.columns)} columns**.")

    if "sales" in detected:
        total = df[detected["sales"]].sum()
        avg   = df[detected["sales"]].mean()
        lines.append(f"Total revenue: **{total:,.2f}** | Average per transaction: **{avg:,.2f}**")

    if "quantity" in detected:
        total_qty = df[detected["quantity"]].sum()
        lines.append(f"Total units sold: **{total_qty:,.0f}**")

    if "category" in detected:
        top_cat = df[detected["category"]].value_counts().idxmax()
        lines.append(f"Top category: **{top_cat}**")

    if "product" in detected:
        unique_products = df[detected["product"]].nunique()
        lines.append(f"Unique products: **{unique_products:,}**")

    if "region" in detected:
        top_region = df[detected["region"]].value_counts().idxmax()
        lines.append(f"Top region: **{top_region}**")

    if "date" in detected:
        try:
            df[detected["date"]] = pd.to_datetime(df[detected["date"]], errors="coerce")
            date_range = df[detected["date"]].dropna()
            if not date_range.empty:
                lines.append(f"Date range: **{date_range.min().date()}** to **{date_range.max().date()}**")
        except:
            pass

    return lines

def generate_pdf_report(df, detected, summary_lines, charts_info):
    """Generate a downloadable text report."""
    report = []
    report.append("E-COMMERCE ANALYTICS REPORT")
    report.append("=" * 50)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("DATASET SUMMARY")
    report.append("-" * 30)
    for line in summary_lines:
        clean = line.replace("**", "")
        report.append(clean)
    report.append("")
    report.append("DETECTED COLUMNS")
    report.append("-" * 30)
    for k, v in detected.items():
        report.append(f"  {k.capitalize()}: {v}")
    report.append("")
    report.append("ALL COLUMNS IN DATASET")
    report.append("-" * 30)
    for col in df.columns:
        dtype = str(df[col].dtype)
        nulls = df[col].isnull().sum()
        report.append(f"  {col} | type: {dtype} | missing: {nulls}")
    report.append("")
    report.append("STATISTICAL SUMMARY")
    report.append("-" * 30)
    try:
        stats = df.describe().to_string()
        report.append(stats)
    except:
        report.append("Could not generate statistics.")

    return "\n".join(report)

# ─── SIDEBAR ────────────────────────────────────────────────────

st.sidebar.image("https://img.icons8.com/color/96/combo-chart--v2.png", width=60)
st.sidebar.title("E-Commerce Analytics")
st.sidebar.markdown("---")
st.sidebar.markdown("**Upload your data**")
st.sidebar.caption("Supports CSV and Excel files from any e-commerce platform.")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "Choose your file",
    type=["csv", "xlsx", "xls"],
    help="Upload any e-commerce CSV or Excel file"
)

# ─── MAIN AREA ──────────────────────────────────────────────────

if uploaded_file is None:
    st.title("E-Commerce Analytics Dashboard")
    st.markdown("##### Upload any e-commerce CSV or Excel file to get instant analysis")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### What this does")
        st.markdown("""
- Upload **any** e-commerce CSV or Excel
- Auto-detects your columns
- Generates **interactive charts**
- Provides **AI-powered text summary**
- Creates a **downloadable report**
        """)
    with col2:
        st.markdown("### Works with")
        st.markdown("""
- Amazon / Flipkart exports
- Shopify / WooCommerce
- Kaggle datasets
- Custom sales CSVs
        """)
    with col3:
        st.markdown("### Analysis includes")
        st.markdown("""
- Sales & Revenue trends
- Product performance
- Category breakdown
- Regional analysis
- Statistical summary
        """)

    st.markdown("---")
    st.info("Upload a file using the sidebar on the left to get started.")

else:
    # ─── LOAD DATA & S3 UPLOAD ──────────────────────────────────

    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    # --- AUTOMATIC S3 BACKUP ---
    try:
        success, key = upload_csv_to_s3(df, uploaded_file.name)
        if success:
            st.sidebar.success("✓ Backup saved to AWS S3!")
        else:
            st.sidebar.warning("App working locally (S3 upload failed)")
    except Exception as s3_err:
        pass  # Ensure the app keeps running even if S3 is down
    # ---------------------------

    detected = detect_columns(df)

    # ─── HEADER ─────────────────────────────────────────────────

    st.title(f"Analysis: {uploaded_file.name}")
    st.caption(f"{len(df):,} rows × {len(df.columns)} columns — Auto-detected {len(detected)} key column types")

    # ─── SIDEBAR FILTERS ────────────────────────────────────────

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Filters**")

    df_filtered = df.copy()

    if "category" in detected:
        cats = ["All"] + sorted(df[detected["category"]].dropna().unique().tolist())
        sel_cat = st.sidebar.selectbox("Category", cats)
        if sel_cat != "All":
            df_filtered = df_filtered[df_filtered[detected["category"]] == sel_cat]

    if "region" in detected:
        regions = ["All"] + sorted(df[detected["region"]].dropna().unique().tolist())
        sel_reg = st.sidebar.selectbox("Region", regions)
        if sel_reg != "All":
            df_filtered = df_filtered[df_filtered[detected["region"]] == sel_reg]

    if "date" in detected:
        try:
            df_filtered[detected["date"]] = pd.to_datetime(df_filtered[detected["date"]], errors="coerce")
            min_d = df_filtered[detected["date"]].min().date()
            max_d = df_filtered[detected["date"]].max().date()
            date_range = st.sidebar.date_input("Date range", [min_d, max_d])
            if isinstance(date_range, list) and len(date_range) == 2:
                df_filtered = df_filtered[
                    (df_filtered[detected["date"]].dt.date >= date_range[0]) &
                    (df_filtered[detected["date"]].dt.date <= date_range[1])
                ]
        except:
            pass

    if "sales" in detected:
        try:
            min_val = float(df[detected["sales"]].min())
            max_val = float(df[detected["sales"]].max())
            if min_val < max_val:
                price_range = st.sidebar.slider(
                    "Price / Sales range",
                    min_val, max_val, (min_val, max_val)
                )
                df_filtered = df_filtered[
                    (df_filtered[detected["sales"]] >= price_range[0]) &
                    (df_filtered[detected["sales"]] <= price_range[1])
                ]
        except:
            pass

    st.sidebar.markdown(f"**Showing {len(df_filtered):,} of {len(df):,} rows**")

    # ─── TABS ───────────────────────────────────────────────────

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview", "Sales Analysis", "Product Analysis",
        "AI Summary", "Download Report"
    ])

    # ── TAB 1: OVERVIEW ─────────────────────────────────────────
    with tab1:
        st.subheader("Dataset Overview")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Rows",    f"{len(df_filtered):,}")
        c2.metric("Columns",       f"{len(df.columns)}")
        c3.metric("Detected Keys", f"{len(detected)}")
        c4.metric("Missing Values",f"{df_filtered.isnull().sum().sum():,}")

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Auto-detected column mapping**")
            if detected:
                det_df = pd.DataFrame(
                    [(k.capitalize(), v) for k, v in detected.items()],
                    columns=["Type", "Your Column Name"]
                )
                st.dataframe(det_df, use_container_width=True, hide_index=True)
            else:
                st.warning("Could not auto-detect column types.")

        with col2:
            st.markdown("**Data types and missing values**")
            info_df = pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes.astype(str).values,
                "Missing": df.isnull().sum().values,
                "Unique": df.nunique().values
            })
            st.dataframe(info_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("**Preview — first 10 rows**")
        st.dataframe(df_filtered.head(10), use_container_width=True)

    # ── TAB 2: SALES ANALYSIS ───────────────────────────────────
    with tab2:
        st.subheader("Sales Analysis")

        if "sales" not in detected:
            st.warning("No sales/revenue column detected.")
        else:
            sales_col = detected["sales"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Revenue",  f"{df_filtered[sales_col].sum():,.2f}")
            c2.metric("Average Sale",   f"{df_filtered[sales_col].mean():,.2f}")
            c3.metric("Highest Sale",   f"{df_filtered[sales_col].max():,.2f}")
            c4.metric("Lowest Sale",    f"{df_filtered[sales_col].min():,.2f}")

            st.markdown("---")

            if "date" in detected:
                try:
                    df_filtered[detected["date"]] = pd.to_datetime(df_filtered[detected["date"]], errors="coerce")
                    monthly = (
                        df_filtered.groupby(
                            df_filtered[detected["date"]].dt.to_period("M").astype(str)
                        )[sales_col].sum().reset_index()
                    )
                    monthly.columns = ["Month", "Revenue"]
                    fig = px.line(monthly, x="Month", y="Revenue", title="Revenue Over Time", markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    pass

            col1, col2 = st.columns(2)
            with col1:
                if "category" in detected:
                    cat_sales = df_filtered.groupby(detected["category"])[sales_col].sum().sort_values(ascending=False).head(10).reset_index()
                    cat_sales.columns = ["Category", "Revenue"]
                    fig2 = px.bar(cat_sales, x="Revenue", y="Category", orientation="h", title="Top 10 Categories")
                    st.plotly_chart(fig2, use_container_width=True)
            with col2:
                if "region" in detected:
                    reg_sales = df_filtered.groupby(detected["region"])[sales_col].sum().sort_values(ascending=False).head(10).reset_index()
                    fig3 = px.pie(reg_sales, names=detected["region"], values=sales_col, title="Revenue by Region")
                    st.plotly_chart(fig3, use_container_width=True)

    # ── TAB 3: PRODUCT ANALYSIS ──────────────────────────────────
    with tab3:
        st.subheader("Product Analysis")
        if "product" in detected and "sales" in detected:
            top_products = df_filtered.groupby(detected["product"])[detected["sales"]].sum().sort_values(ascending=False).head(15).reset_index()
            fig = px.bar(top_products, x=detected["product"], y=detected["sales"], title="Top 15 Products by Revenue")
            st.plotly_chart(fig, use_container_width=True)

    # ── TAB 4: AI SUMMARY ────────────────────────────────────────
    with tab4:
        st.subheader("AI-Generated Analysis Summary")
        summary_lines = smart_summary(df_filtered, detected)
        for line in summary_lines:
            st.markdown(f"- {line}")

        st.markdown("---")
        numeric_cols = df_filtered.select_dtypes(include="number")
        if not numeric_cols.empty:
            st.markdown("### Statistical Summary")
            st.dataframe(numeric_cols.describe().round(2), use_container_width=True)

    # ── TAB 5: DOWNLOAD REPORT ───────────────────────────────────
    with tab5:
        st.subheader("Download Your Report")
        summary_lines = smart_summary(df_filtered, detected)
        report_text   = generate_pdf_report(df_filtered, detected, summary_lines, {})

        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("Download Text Report", data=report_text, file_name="report.txt")
        with c2:
            st.download_button("Download Filtered CSV", data=df_filtered.to_csv(index=False), file_name="filtered.csv")
        with c3:
            st.download_button("Download Full CSV", data=df.to_csv(index=False), file_name="full_data.csv")