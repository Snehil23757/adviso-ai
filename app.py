import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
from sklearn.linear_model import LinearRegression
import numpy as np
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#020617,#0f172a);color:#e2e8f0;}
.title {
    font-size:40px;font-weight:900;text-align:center;
    background:linear-gradient(90deg,#38bdf8,#6366f1,#22c55e);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🚀 Adviso AI</div>", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

if "last_call" not in st.session_state:
    st.session_state.last_call = 0

# ---------------- FUNCTIONS ----------------
def can_call():
    return time.time() - st.session_state.last_call > 5

def safe_ai(messages):
    try:
        if not can_call():
            return "⏳ Wait a few seconds"
        st.session_state.last_call = time.time()
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"⚠️ {str(e)}"

def save_history(title, content):
    st.session_state.history.append({"title": title, "content": content})

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 👤 Profile")

if not st.session_state.logged_in:
    mode = st.sidebar.radio("Login / Signup", ["Login", "Signup"])
    user = st.sidebar.text_input("Username")
    pwd = st.sidebar.text_input("Password", type="password")

    if mode == "Login":
        if st.sidebar.button("Login"):
            if user in st.session_state.users and st.session_state.users[user] == pwd:
                st.session_state.logged_in = True
                st.success("Logged in")
            else:
                st.error("Invalid credentials")
    else:
        if st.sidebar.button("Signup"):
            st.session_state.users[user] = pwd
            st.success("Account created")
else:
    st.sidebar.success("Logged in")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False

# ---------------- HISTORY ----------------
st.sidebar.markdown("## 📜 History")

if len(st.session_state.history) == 0:
    st.sidebar.info("No history yet")
else:
    for i, h in enumerate(reversed(st.session_state.history)):
        if st.sidebar.button(f"{h['title']} {i}"):
            st.sidebar.write(h["content"])

# ---------------- BLOCK ----------------
if not st.session_state.logged_in:
    st.warning("🔐 Please login")
    st.stop()

# ---------------- FILE ----------------
file = st.sidebar.file_uploader("Upload Data", type=["csv","xlsx"])

# ---------------- MAIN ----------------
if file:
    data = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs(
        ["📊 Overview","📈 Charts","🧠 AI","🤖 Chat","💡 Ideas","💰 Profit","📈 Forecast","💰 Budget","🌱 Sustainability","📊 Competitor","📊 KPI"]
    )

    # ---------- OVERVIEW ----------
    with tab1:
        st.subheader("📊 Dataset Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", data.shape[0])
    col2.metric("Columns", data.shape[1])
    col3.metric("Missing Values", data.isnull().sum().sum())

    st.markdown("---")

    # 🔹 Missing Values Table
    st.subheader("🧩 Missing Data Analysis")

    missing = data.isnull().sum()
    percent = (missing / len(data)) * 100

    missing_df = pd.DataFrame({
        "Column": missing.index,
        "Missing Count": missing.values,
        "Missing %": percent.values
    }).sort_values(by="Missing %", ascending=False)

    st.dataframe(missing_df, use_container_width=True)

    st.bar_chart(missing)

    st.markdown("---")

    # 🔹 Data Preview
    st.subheader("📄 Data Preview")

    st.dataframe(data.head(), use_container_width=True)

    with st.expander("View Full Dataset"):
        st.dataframe(data, use_container_width=True)

    st.markdown("---")

    # 🔹 Statistics
    st.subheader("📈 Statistical Summary")

    stats = data.describe()
    st.dataframe(stats, use_container_width=True)

    # ---------- CHARTS ----------
    with tab2:
        st.subheader("📈 Data Visualization")

    # 🔹 Column separation
    numeric_cols = data.select_dtypes(include=['int64','float64']).columns.tolist()
    cat_cols = data.select_dtypes(include=['object']).columns.tolist()

    if len(numeric_cols) == 0:
        st.error("❌ No numeric columns available for plotting")
        st.stop()

    # 🔹 Layout (2 columns)
    col_left, col_right = st.columns([1,2])

    with col_left:
        st.markdown("### ⚙️ Chart Controls")

        chart = st.selectbox("Chart Type", ["Scatter","Line","Bar","Histogram"])

        x = st.selectbox("X-axis", data.columns)

        y = None
        if chart != "Histogram":
            y = st.selectbox("Y-axis", numeric_cols)

        # 🔹 Filter section
        st.markdown("### 🎯 Filter Data")

        filtered = data.copy()

        if len(cat_cols) > 0:
            cat = st.selectbox("Category Filter", ["None"] + cat_cols)

            if cat != "None":
                vals = st.multiselect("Select Values", data[cat].dropna().unique())

                if vals:
                    filtered = filtered[filtered[cat].isin(vals)]

        st.markdown("---")
        st.write(f"Filtered Rows: {filtered.shape[0]}")

    with col_right:
        st.markdown("### 📊 Chart Output")

        if filtered.empty:
            st.warning("⚠️ No data available after filtering")
        else:
            try:
                if chart == "Scatter":
                    fig = px.scatter(filtered, x=x, y=y)
                elif chart == "Line":
                    fig = px.line(filtered, x=x, y=y)
                elif chart == "Bar":
                    fig = px.bar(filtered, x=x, y=y)
                else:
                    fig = px.histogram(filtered, x=x)

                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"⚠️ Chart error: {str(e)}")

        st.markdown("---")
        st.subheader("📄 Data Preview")
        st.dataframe(filtered.head(), use_container_width=True)

    # ---------- AI ----------
    with tab3:
        if st.button("Generate Insights"):
            st.write(safe_ai([{"role":"user","content":data.head().to_string()}]))

    # ---------- CHAT ----------
    with tab4:
        q = st.text_input("Ask")
        if q:
            st.write(safe_ai([{"role":"user","content":q}]))

    # ---------- IDEAS ----------
    with tab5:
        st.subheader("💡 AI Business Ideation Engine")
        industry = st.text_input("Industry")
        if st.button("Generate Ideas"):
            st.write(safe_ai([{"role":"user","content":industry}]))

    # ---------- PROFIT ----------
    with tab6:
        revenue = st.number_input("Revenue")
        cost = st.number_input("Cost")
        st.metric("Profit", revenue - cost)

    # ---------- FORECAST ----------
    with tab7:
        col = st.selectbox("Column", data.select_dtypes(include=['int64','float64']).columns)
        st.line_chart(data[col])

    # ---------- BUDGET ----------
    with tab8:
        income = st.number_input("Income")
        expense = st.number_input("Expense")
        st.metric("Savings", income - expense)

    # ---------- SUSTAINABILITY ----------
    with tab9:
        st.write("Sustainability Dashboard")

    # ---------- COMPETITOR ----------
    with tab10:
        st.write("Competitor Analysis")

    # ---------- KPI ----------
    with tab11:
        col = st.selectbox("KPI Column", data.select_dtypes(include=['int64','float64']).columns)
        st.line_chart(data[col])
