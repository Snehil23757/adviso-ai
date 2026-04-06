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
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a);
    color: #e2e8f0;
}
.block-container {
    padding: 2rem 4rem;
    max-width: 1400px;
}
.title {
    font-size: 48px;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg,#38bdf8,#6366f1,#22c55e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.card {
    background: rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 0 30px rgba(99,102,241,0.2);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🚀 Adviso AI</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>AI Financial Intelligence Dashboard</p>", unsafe_allow_html=True)

# ---------------- FILE UPLOAD ----------------
file = st.sidebar.file_uploader("Upload Data", type=["csv","xlsx"])

if file:
    data = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    # ---------------- TABS ----------------
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(
        ["📊 Overview","📈 Charts","🧠 AI","🤖 Chat","💡 Ideas","💰 Profit","📈 Forecast","💰 Budget + AI","📊 KPI Dashboard"]
    )

    # ---------- OVERVIEW ----------
    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", data.shape[0])
        c2.metric("Columns", data.shape[1])
        c3.metric("Missing", data.isnull().sum().sum())

        with st.expander("View Data"):
            st.dataframe(data)

    # ---------- CHARTS ----------
    with tab2:
        num = data.select_dtypes(include=['int64','float64']).columns

        if len(num) > 1:
            x = st.selectbox("X-axis", num)
            y = st.selectbox("Y-axis", num)
            fig = px.scatter(data, x=x, y=y)
            st.plotly_chart(fig, use_container_width=True)

    # ---------- AI ----------
    with tab3:
        if st.button("Generate Insights"):
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":data.head().to_string()}]
            )
            st.success(res.choices[0].message.content)

    # ---------- CHAT ----------
    with tab4:
        q = st.text_input("Ask anything")
        if q:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":q}]
            )
            st.write(res.choices[0].message.content)

    # ---------- IDEAS ----------
    with tab5:
        if st.button("Generate Ideas"):
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":"Give startup ideas"}]
            )
            st.write(res.choices[0].message.content)

    # ---------- PROFIT ----------
    with tab6:
        inv = st.number_input("Investment")
        rev = st.number_input("Revenue")
        cost = st.number_input("Cost")

        if st.button("Calculate Profit"):
            profit = rev - cost
            st.success(f"Profit: ₹{profit}")

    # ---------- FORECAST ----------
    with tab7:
        num_cols = data.select_dtypes(include=['int64','float64']).columns

        if len(num_cols) > 0:
            col = st.selectbox("Select Column", num_cols)

            values = data[col].dropna().values
            X = np.arange(len(values)).reshape(-1,1)

            model = LinearRegression()
            model.fit(X, values)

            pred = model.predict([[len(values)]])[0]

            st.metric("Current", values[-1])
            st.metric("Predicted", round(pred,2))

            fig = px.line(values, title="Trend")
            st.plotly_chart(fig)

    # ---------- BUDGET ----------
    with tab8:
        income = st.number_input("Income")
        fixed = st.number_input("Fixed Expenses")
        variable = st.number_input("Variable Expenses")

        if st.button("Analyze"):
            savings = income - (fixed + variable)
            st.success(f"Savings: ₹{savings}")

    # ---------- KPI DASHBOARD ----------
    with tab9:
        st.markdown("## 📊 KPI Dashboard")

        # Safe column handling
        if all(col in data.columns for col in ["Revenue","Units_Sold","Price"]):

            total_revenue = data["Revenue"].sum()
            total_units = data["Units_Sold"].sum()
            avg_price = data["Price"].mean()

            growth = ((data["Revenue"].iloc[-1] - data["Revenue"].iloc[0]) / data["Revenue"].iloc[0]) * 100

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
            c2.metric("Units Sold", total_units)
            c3.metric("Avg Price", f"₹{avg_price:,.0f}")
            c4.metric("Growth %", f"{growth:.2f}%")

            # Prediction
            st.markdown("## 🔮 KPI Prediction")

            kpi_col = st.selectbox("Select KPI", ["Revenue","Units_Sold"])

            values = data[kpi_col].values
            X = np.arange(len(values)).reshape(-1,1)

            model = LinearRegression()
            model.fit(X, values)

            future = model.predict([[len(values)]])[0]

            st.success(f"Predicted Next {kpi_col}: {round(future,2)}")

            fig = px.line(data[kpi_col], title=f"{kpi_col} Trend")
            st.plotly_chart(fig)

        else:
            st.error("Dataset must contain: Revenue, Units_Sold, Price")
