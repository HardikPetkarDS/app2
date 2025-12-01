# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, date

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Budget Dashboard",
    layout="wide",
    page_icon="💰"
)

# -------------------- CUSTOM CSS (UI/UX) --------------------
st.markdown("""
<style>

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}

.main-title {
    font-size: 42px;
    font-weight: 700;
    color: #3A3A3A;
    text-align: center;
    padding: 10px 0;
}

.card {
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(10px);
    border-radius: 18px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.3);
    box-shadow: 0px 4px 25px rgba(0,0,0,0.08);
}

.metric-card {
    background: linear-gradient(135deg,#6F6CFF,#4AD0EE);
    color: white;
    border-radius: 16px;
    padding: 20px;
    text-align:center;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.15);
}

.metric-value {
    font-size: 30px;
    font-weight: 700;
}

.metric-label {
    font-size: 16px;
    opacity: 0.85;
}

.section-title {
    font-size: 26px;
    font-weight: 600;
    margin-top: 20px;
    color: #333;
}

</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown("<div class='main-title'>💼 Modern Budget Analysis Dashboard</div>", unsafe_allow_html=True)
st.write("Upload a CSV budget file and enjoy an interactive, beautiful dashboard.")

# -------------------- FILE UPLOAD --------------------
uploaded = st.file_uploader("📁 Upload CSV file", type=["csv"])

def safe_read(file):
    try:
        return pd.read_csv(file)
    except:
        try:
            file.seek(0)
            return pd.read_csv(file, encoding="utf-8-sig")
        except:
            file.seek(0)
            return pd.read_csv(file, encoding="latin1")

if uploaded is None:
    st.info("Please upload your CSV file to continue.")
    st.stop()

df = safe_read(uploaded).copy()

if df.empty:
    st.error("Could not read the file. Upload a valid CSV.")
    st.stop()

# Preview
with st.expander("🔍 Show CSV Preview"):
    st.dataframe(df.head())

# -------------------- SIDEBAR DESIGN --------------------
st.sidebar.title("⚙️ Dashboard Settings")
columns = list(df.columns)

date_col = st.sidebar.selectbox("Select Date column", columns)
amount_col = st.sidebar.selectbox("Select Amount column", columns)
category_col = st.sidebar.selectbox("Select Category column", columns + ["(none)"])

# Convert fields
df["_date"] = pd.to_datetime(df[date_col], errors="coerce")
df["_amount"] = pd.to_numeric(df[amount_col].astype(str).str.replace(",", ""), errors="coerce")

if category_col != "(none)":
    df["_category"] = df[category_col].fillna("Uncategorized").astype(str)
else:
    df["_category"] = "Uncategorized"

# Filters
min_d = df["_date"].min()
max_d = df["_date"].max()

if pd.isna(min_d):
    min_d = date.today().replace(month=1, day=1)
    max_d = date.today()

date_range = st.sidebar.date_input("Select Date Range", [min_d, max_d])

if len(date_range) != 2:
    st.sidebar.error("Select a valid date range.")
    st.stop()

start, end = date_range
categories = st.sidebar.multiselect("Select Categories", df["_category"].unique(), default=list(df["_category"].unique()))

# Filter Data
filtered = df.copy()
filtered = filtered[filtered["_date"].between(start, end)]
filtered = filtered[filtered["_category"].isin(categories)]

if filtered.empty:
    st.warning("No records found for selected filters.")
    st.stop()

# -------------------- KPIs / METRICS --------------------
total = filtered["_amount"].sum()
avg = filtered["_amount"].mean()
max_amt = filtered["_amount"].max()
tx_count = len(filtered)

st.markdown("<div class='section-title'>📊 Key Metrics</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>₹{total:,.2f}</div>
        <div class='metric-label'>Total Amount</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>₹{avg:,.2f}</div>
        <div class='metric-label'>Average Amount</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>₹{max_amt:,.2f}</div>
        <div class='metric-label'>Max Expense</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{tx_count}</div>
        <div class='metric-label'>Transactions</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------- CATEGORY BAR CHART --------------------
st.markdown("<div class='section-title'>📂 Category Breakdown</div>", unsafe_allow_html=True)

cat_sum = filtered.groupby("_category")["_amount"].sum()
st.bar_chart(cat_sum)

# -------------------- MONTHLY TREND --------------------
st.markdown("<div class='section-title'>📈 Monthly Trend</div>", unsafe_allow_html=True)

filtered["year_month"] = filtered["_date"].dt.to_period("M").astype(str)
trend = filtered.groupby("year_month")["_amount"].sum()

st.line_chart(trend)

# -------------------- TABLE --------------------
st.markdown("<div class='section-title'>📋 Transaction Table</div>", unsafe_allow_html=True)

st.dataframe(filtered, height=350)

# -------------------- DOWNLOAD BUTTON --------------------
csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Filtered CSV", data=csv_data, file_name="filtered_budget.csv")

st.success("Dashboard Loaded Successfully 🎉 Enjoy your analytics!")
