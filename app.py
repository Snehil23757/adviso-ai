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

# ---------------- PREMIUM UI ----------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a);
    color: #e2e8f0;
}

/* Container */
.block-container {
    padding: 2rem 4rem;
    max-width: 1400px;
}

/* Title */
.title {
    font-size: 48px;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg,#38bdf8,#6366f1,#22c55e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 0 30px rgba(99,102,241,0.2);
    transition: 0.3s;
}

.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 0 50px rgba(99,102,241,0.5);
}

/* Buttons */
.stButton>button {
    border-radius: 12px;
    background: linear-gradient(90deg,#6366f1,#3b82f6);
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(2,6,23,0.95);
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<div class='title'>🚀 Adviso AI</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#94a3b8;'>AI Financial Intelligence Dashboard</p>", unsafe_allow_html=True)

# ---------------- FILE ----------------
file = st.sidebar.file_uploader("Upload Data", type=["csv","xlsx"])

# ---------------- MAIN ----------------
if file:
    data = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
        ["📊 Overview","📈 Charts","🧠 AI","🤖 Chat","💡 Ideas","💰 Profit","📈 Forecast","💰 Budget + AI"]
    )

    # ---------- OVERVIEW ----------
    with tab1:
        st.markdown("## 📊 Dashboard Overview")

        c1, c2, c3 = st.columns(3)

        c1.markdown(f"<div class='card'><h4>📊 Rows</h4><h1>{data.shape[0]}</h1></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h4>📁 Columns</h4><h1>{data.shape[1]}</h1></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h4>⚠️ Missing</h4><h1>{data.isnull().sum().sum()}</h1></div>", unsafe_allow_html=True)

        with st.expander("🔍 View Data"):
            st.dataframe(data)

    # ---------- CHARTS ----------
    with tab2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        num = data.select_dtypes(include=['int64','float64']).columns

        if len(num) > 1:
            x = st.selectbox("X", num)
            y = st.selectbox("Y", num)

            with st.spinner("📊 Rendering chart..."):
                time.sleep(1)

            fig = px.scatter(data, x=x, y=y)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- AI ----------
    with tab3:
        if st.button("Generate Insights"):
            with st.spinner("🧠 AI analyzing..."):
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":data.head().to_string()}]
                )
            st.success(res.choices[0].message.content)

    # ---------- CHAT ----------
    with tab4:
        q = st.text_input("Ask anything")

        if q:
            with st.spinner("Thinking..."):
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":q}]
                )
            st.write(res.choices[0].message.content)

    # ---------- IDEAS ----------
    with tab5:
        if st.button("Generate Business Ideas"):
            with st.spinner("Generating ideas..."):
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

        if st.button("Calculate"):
            profit = rev - cost

            st.markdown(f"<div class='card'><h3>💰 Profit</h3><h1>₹{profit}</h1></div>", unsafe_allow_html=True)

    # ---------- FORECAST ----------
    with tab7:
        st.markdown("## 📈 Forecast + ML Prediction")

        num_cols = data.select_dtypes(include=['int64','float64']).columns

        if len(num_cols) > 0:
            col = st.selectbox("Select Column", num_cols)

            values = data[col].dropna().values

            if len(values) > 3:
                X = np.arange(len(values)).reshape(-1,1)

                model = LinearRegression()
                model.fit(X, values)

                next_value = model.predict([[len(values)]])[0]

                c1, c2 = st.columns(2)

                c1.markdown(f"<div class='card'><h4>📍 Current</h4><h1>{values[-1]}</h1></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='card'><h4>🔮 Predicted</h4><h1>{round(next_value,2)}</h1></div>", unsafe_allow_html=True)

                fig = px.line(values, title="Trend")
                st.plotly_chart(fig)

    # ---------- BUDGET + AI ----------
    with tab8:
        st.markdown("## 💰 Budget + AI Advisor")

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        income = st.number_input("Income")
        fixed = st.number_input("Fixed Expenses")
        variable = st.number_input("Variable Expenses")

        if st.button("Analyze Budget"):
            total = fixed + variable
            savings = income - total

            st.markdown(f"<h3>💸 Savings: ₹{savings}</h3>", unsafe_allow_html=True)

            with st.spinner("AI giving advice..."):
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role":"user",
                        "content": f"Income {income}, Expenses {total}. Give financial advice."
                    }]
                )

            st.success(res.choices[0].message.content)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### 🧠 Personal Financial Advisor")

        q = st.text_input("Ask financial advice")

        if q:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":q}]
            )
            st.write(res.choices[0].message.content)
