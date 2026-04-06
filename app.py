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

# ---------------- RATE LIMIT FIX ----------------
if "last_call" not in st.session_state:
    st.session_state.last_call = 0

def can_call():
    return time.time() - st.session_state.last_call > 5

def safe_ai(messages):
    try:
        if not can_call():
            return "⏳ Please wait a few seconds before next request"

        st.session_state.last_call = time.time()

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return res.choices[0].message.content

    except Exception:
        return "⚠️ AI unavailable (rate limit / quota exceeded)"

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#020617,#0f172a);color:#e2e8f0;}
.block-container {padding:2rem 4rem;max-width:1400px;}
.card {
    background: rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.1);
}
.title {
    font-size:48px;
    font-weight:900;
    text-align:center;
    background: linear-gradient(90deg,#38bdf8,#6366f1,#22c55e);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🚀 Adviso AI</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>AI Business Intelligence Platform</p>", unsafe_allow_html=True)

# ---------------- FILE ----------------
file = st.sidebar.file_uploader("Upload Data", type=["csv","xlsx"])

if file:
    data = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(
        ["📊 Overview","📈 Charts","🧠 AI","🤖 Chat","💡 Ideas","💰 Profit","📈 Forecast","💰 Budget + AI","🌱 Sustainability"]
    )

    # ---------- OVERVIEW ----------
    with tab1:
        st.markdown("## 📊 Dashboard Overview")

        c1, c2, c3 = st.columns(3)

        c1.markdown(f"<div class='card'><h4>📊 Rows</h4><h1>{data.shape[0]}</h1></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h4>📁 Columns</h4><h1>{data.shape[1]}</h1></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h4>⚠️ Missing</h4><h1>{data.isnull().sum().sum()}</h1></div>", unsafe_allow_html=True)

        st.markdown("---")

        # 📄 FULL DATA VIEW
        st.markdown("### 📄 Dataset Preview")
        with st.expander("🔍 Click to View Full Data"):
            st.dataframe(data, use_container_width=True)

        # ⚡ QUICK VIEW
        st.markdown("### ⚡ Quick View (Top 10 Rows)")
        st.dataframe(data.head(10), use_container_width=True)

    # ---------- CHART ----------
   with tab2:
    st.markdown("## 📈 Advanced Charts Dashboard")

    chart_type = st.selectbox("Select Chart Type", [
        "Scatter",
        "Line",
        "Bar",
        "Histogram",
        "Box",
        "Violin",
        "Pie",
        "Area",
        "Heatmap",
        "Density Contour"
    ])

    num_cols = data.select_dtypes(include=['int64','float64']).columns
    cat_cols = data.select_dtypes(include=['object']).columns

    # Common selectors
    x = st.selectbox("X Axis", data.columns)
    y = st.selectbox("Y Axis", num_cols)

    with st.spinner("📊 Generating chart..."):
        time.sleep(0.8)

        # -------- CHART LOGIC --------
        if chart_type == "Scatter":
            fig = px.scatter(data, x=x, y=y, color=y)

        elif chart_type == "Line":
            fig = px.line(data, x=x, y=y)

        elif chart_type == "Bar":
            fig = px.bar(data, x=x, y=y)

        elif chart_type == "Histogram":
            fig = px.histogram(data, x=x)

        elif chart_type == "Box":
            fig = px.box(data, x=x, y=y)

        elif chart_type == "Violin":
            fig = px.violin(data, x=x, y=y, box=True)

        elif chart_type == "Pie":
            if len(cat_cols) > 0:
                cat = st.selectbox("Category", cat_cols)
                fig = px.pie(data, names=cat, values=y)
            else:
                st.warning("No categorical columns for pie chart")
                fig = None

        elif chart_type == "Area":
            fig = px.area(data, x=x, y=y)

        elif chart_type == "Heatmap":
            corr = data[num_cols].corr()
            fig = px.imshow(corr, text_auto=True, title="Correlation Heatmap")

        elif chart_type == "Density Contour":
            fig = px.density_contour(data, x=x, y=y)

        # -------- DISPLAY --------
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # ---------- AI ----------
    with tab3:
        if st.button("Generate Insights"):
            with st.spinner("AI analyzing..."):
                output = safe_ai([
                    {"role":"user","content":data.head(10).to_string()}
                ])
            st.success(output)

    # ---------- CHAT ----------
    with tab4:
        q = st.text_input("Ask anything")
        if q:
            output = safe_ai([{"role":"user","content":q}])
            st.write(output)

    # ---------- IDEAS ----------
    with tab5:
        if st.button("Generate Ideas"):
            output = safe_ai([{"role":"user","content":"Give startup ideas"}])
            st.write(output)

    # ---------- PROFIT ----------
    with tab6:
        inv = st.number_input("Investment")
        rev = st.number_input("Revenue")
        cost = st.number_input("Cost")

        if st.button("Calculate"):
            profit = rev - cost
            st.success(f"Profit ₹{profit}")

    # ---------- FORECAST ----------
    with tab7:
        num_cols = data.select_dtypes(include=['int64','float64']).columns

        if len(num_cols) > 0:
            col = st.selectbox("Column", num_cols)
            values = data[col].dropna().values

            if len(values) > 3:
                X = np.arange(len(values)).reshape(-1,1)
                model = LinearRegression().fit(X, values)
                pred = model.predict([[len(values)]])[0]

                st.metric("Current", values[-1])
                st.metric("Predicted", round(pred,2))

                fig = px.line(values)
                st.plotly_chart(fig)

    # ---------- BUDGET ----------
    with tab8:
        income = st.number_input("Income")
        fixed = st.number_input("Fixed Expenses")
        variable = st.number_input("Variable Expenses")

        if st.button("Analyze Budget"):
            total = fixed + variable
            savings = income - total

            st.metric("Savings", savings)

            output = safe_ai([
                {"role":"user","content":f"Income {income}, Expenses {total}. Give advice"}
            ])
            st.success(output)

    # ---------- SUSTAINABILITY ----------
    with tab9:
        total_budget = st.number_input("Total Budget", min_value=0)
        green_spending = st.number_input("Green Investment", min_value=0)

        if st.button("Analyze Sustainability"):
            percent = (green_spending/total_budget*100) if total_budget>0 else 0

            st.metric("Sustainability %", f"{percent:.2f}%")

            df = pd.DataFrame({
                "Category":["Green","Other"],
                "Value":[green_spending,total_budget-green_spending]
            })

            fig = px.pie(df, names="Category", values="Value")
            st.plotly_chart(fig)

            output = safe_ai([
                {"role":"user","content":f"Budget {total_budget}, green {green_spending}. Suggest sustainability strategy"}
            ])
            st.success(output)
