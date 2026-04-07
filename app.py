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
        st.metric("Rows", data.shape[0])
        st.metric("Columns", data.shape[1])

        missing = data.isnull().sum()
        percent = (missing / len(data)) * 100

        st.dataframe(pd.DataFrame({
            "Column": missing.index,
            "Missing": missing.values,
            "%": percent.values
        }))

        st.bar_chart(missing)

        with st.expander("Full Data"):
            st.dataframe(data)

        st.dataframe(data.head())

        stats = data.describe()
        st.dataframe(stats)

    # ---------- CHARTS ----------
    with tab2:
        chart = st.selectbox("Chart", ["Scatter","Line","Bar","Histogram"])
        x = st.selectbox("X", data.columns)
        y = st.selectbox("Y", data.select_dtypes(include=['int64','float64']).columns)

        filtered = data.copy()

        cat_cols = data.select_dtypes(include=['object']).columns
        if len(cat_cols)>0:
            cat = st.selectbox("Category", ["None"]+list(cat_cols))
            if cat!="None":
                vals = st.multiselect("Values", data[cat].unique())
                if vals:
                    filtered = filtered[filtered[cat].isin(vals)]

        st.dataframe(filtered.head())

        if chart=="Scatter":
            st.plotly_chart(px.scatter(filtered,x=x,y=y))
        elif chart=="Line":
            st.plotly_chart(px.line(filtered,x=x,y=y))
        elif chart=="Bar":
            st.plotly_chart(px.bar(filtered,x=x,y=y))
        else:
            st.plotly_chart(px.histogram(filtered,x=x))

    # ---------- AI ----------
    with tab3:
        if st.button("Generate Insights"):
            out = safe_ai([{"role":"user","content":data.head().to_string()}])
            st.write(out)

    # ---------- CHAT ----------
    with tab4:
        q = st.text_input("Ask")
        if q:
            st.write(safe_ai([{"role":"user","content":q}]))

      # ---------- IDEAS ----------
with tab5:
    st.subheader("💡 AI Business Ideation Engine")

    # 🔹 Inputs
    industry = st.text_input("Industry (e.g., Retail, Healthcare, EdTech)")
    problem = st.text_area("Problem Statement (optional)")
    budget = st.selectbox("Budget Level", ["Low","Medium","High"])
    risk = st.selectbox("Risk Appetite", ["Low","Moderate","High"])

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    # 🚀 Startup Ideas
    if col1.button("🚀 Startup Ideas"):
        prompt = f"""
        Suggest 5 innovative startup ideas in {industry} industry.
        Budget: {budget}, Risk: {risk}.
        Problem: {problem}

        Provide:
        - Idea Name
        - Description
        - Revenue Model
        - Target Customers
        """
        with st.spinner("Generating ideas..."):
            out = safe_ai([{"role":"user","content":prompt}])
            st.success(out)
            save_history("Startup Ideas", out)

    # 📈 Growth Ideas
    if col2.button("📈 Growth Strategies"):
        prompt = f"""
        Suggest growth strategies for {industry}.
        Budget: {budget}.
        Include marketing, scaling, and digital expansion.
        """
        with st.spinner("Analyzing..."):
            out = safe_ai([{"role":"user","content":prompt}])
            st.success(out)
            save_history("Growth Ideas", out)

    # 💰 Cost Optimization
    if col3.button("💰 Cost Optimization"):
        prompt = f"""
        Suggest cost reduction strategies in {industry}.
        Focus on improving efficiency and profitability.
        """
        with st.spinner("Optimizing..."):
            out = safe_ai([{"role":"user","content":prompt}])
            st.success(out)
            save_history("Cost Ideas", out)

    st.markdown("---")

    # 📊 Business Plan
    if st.button("📊 Generate Business Plan"):
        prompt = f"""
        Create a structured business plan for {industry}.
        Budget: {budget}, Risk: {risk}.
        Problem: {problem}

        Include:
        - Executive Summary
        - Market Analysis
        - Revenue Model
        - Cost Structure
        - Growth Strategy
        """
        with st.spinner("Building plan..."):
            out = safe_ai([{"role":"user","content":prompt}])
            st.success(out)
            save_history("Business Plan", out)

    st.markdown("---")

    # 🤖 Data-Based Ideas (MOST POWERFUL 🔥)
    if st.button("🤖 Ideas from Uploaded Data"):
        sample = data.head(10).to_string()

        prompt = f"""
        Analyze this dataset:
        {sample}

        Provide:
        - Key insights
        - Business opportunities
        - Monetization strategies
        """
        with st.spinner("Analyzing dataset..."):
            out = safe_ai([{"role":"user","content":prompt}])
            st.success(out)
            save_history("Data Ideas", out)

    # ---------- PROFIT ----------
    with tab6:
        r = st.number_input("Revenue")
        c = st.number_input("Cost")
        if st.button("Calc"):
            st.success(r-c)

    # ---------- FORECAST ----------
    with tab7:
        col = st.selectbox("Column", data.select_dtypes(include=['int64','float64']).columns)
        v = data[col].dropna().values
        if len(v)>3:
            m = LinearRegression().fit(np.arange(len(v)).reshape(-1,1), v)
            st.metric("Prediction", round(m.predict([[len(v)]])[0],2))

    # ---------- BUDGET ----------
    with tab8:
        i = st.number_input("Income")
        e = st.number_input("Expense")
        if st.button("Analyze"):
            st.write(safe_ai([{"role":"user","content":f"{i},{e}"}]))

    # ---------- SUSTAINABILITY ----------
    with tab9:
        b = st.number_input("Budget")
        g = st.number_input("Green")
        if st.button("Check"):
            st.write(safe_ai([{"role":"user","content":f"{b},{g}"}]))

    # ---------- COMPETITOR ----------
    with tab10:
        y = st.number_input("Your Revenue")
        c = st.number_input("Competitor")
        if st.button("Compare"):
            st.write(safe_ai([{"role":"user","content":f"{y} vs {c}"}]))

    # ---------- KPI ----------
    with tab11:
        col = st.selectbox("KPI", data.select_dtypes(include=['int64','float64']).columns)
        k = data[col].dropna().values

        if len(k)>0:
            st.metric("Current", k[-1])
            st.line_chart(k)

            if len(k)>3:
                m = LinearRegression().fit(np.arange(len(k)).reshape(-1,1), k)
                pred = m.predict([[len(k)]])[0]
                st.metric("Next", round(pred,2))
