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

# ---------------- RATE LIMIT ----------------
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

# ---------------- HISTORY ----------------
if "history" not in st.session_state:
    st.session_state.history = []

def save_history(title, content):
    st.session_state.history.append({
        "title": title,
        "content": content
    })

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

# ---------------- SIDEBAR ----------------
file = st.sidebar.file_uploader("Upload Data", type=["csv","xlsx"])

st.sidebar.markdown("## 📜 History")

if len(st.session_state.history) == 0:
    st.sidebar.info("No history yet")
else:
    for i, item in enumerate(reversed(st.session_state.history)):
        if st.sidebar.button(f"{item['title']} #{i+1}"):
            st.sidebar.write(item["content"])

# ---------------- MAIN ----------------
if file:
    data = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(
        ["📊 Overview","📈 Charts","🧠 AI","🤖 Chat","💡 Ideas","💰 Profit","📈 Forecast","💰 Budget","🌱 Sustainability","📊 Competitor"]
    )

    # ---------- OVERVIEW ----------
    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", data.shape[0])
        c2.metric("Columns", data.shape[1])
        c3.metric("Missing", data.isnull().sum().sum())

        with st.expander("View Full Data"):
            st.dataframe(data)

        st.dataframe(data.head(10))

    # ---------- CHART ----------
    with tab2:
        chart_type = st.selectbox("Chart", [
            "Scatter","Line","Bar","Histogram","Box","Violin",
            "Pie","Area","Heatmap","Density Contour"
        ])

        num_cols = data.select_dtypes(include=['int64','float64']).columns
        cat_cols = data.select_dtypes(include=['object']).columns

        x = st.selectbox("X", data.columns)
        y = st.selectbox("Y", num_cols)

        fig = None

        if chart_type == "Scatter":
            fig = px.scatter(data, x=x, y=y)
        elif chart_type == "Line":
            fig = px.line(data, x=x, y=y)
        elif chart_type == "Bar":
            fig = px.bar(data, x=x, y=y)
        elif chart_type == "Histogram":
            fig = px.histogram(data, x=x)
        elif chart_type == "Box":
            fig = px.box(data, x=x, y=y)
        elif chart_type == "Violin":
            fig = px.violin(data, x=x, y=y)
        elif chart_type == "Pie" and len(cat_cols)>0:
            fig = px.pie(data, names=cat_cols[0], values=y)
        elif chart_type == "Area":
            fig = px.area(data, x=x, y=y)
        elif chart_type == "Heatmap":
            fig = px.imshow(data[num_cols].corr())
        elif chart_type == "Density Contour":
            fig = px.density_contour(data, x=x, y=y)

        if fig:
            st.plotly_chart(fig)

    # ---------- AI ----------
    with tab3:
        if st.button("Generate Insights"):
            output = safe_ai([{"role":"user","content":data.head(10).to_string()}])
            st.success(output)
            save_history("AI Insights", output)

    # ---------- CHAT ----------
    with tab4:
        q = st.text_input("Ask")
        if q:
            output = safe_ai([{"role":"user","content":q}])
            st.write(output)
            save_history("Chat", output)

    # ---------- IDEAS ----------
    with tab5:
        if st.button("Ideas"):
            output = safe_ai([{"role":"user","content":"startup ideas"}])
            st.write(output)
            save_history("Ideas", output)

    # ---------- PROFIT ----------
    with tab6:
        inv = st.number_input("Investment")
        rev = st.number_input("Revenue")
        cost = st.number_input("Cost")

        if st.button("Calculate"):
            st.success(f"Profit ₹{rev-cost}")

    # ---------- FORECAST ----------
    with tab7:
        col = st.selectbox("Column", data.select_dtypes(include=['int64','float64']).columns)
        values = data[col].dropna().values

        if len(values)>3:
            X = np.arange(len(values)).reshape(-1,1)
            model = LinearRegression().fit(X, values)
            pred = model.predict([[len(values)]])[0]

            st.metric("Predicted", round(pred,2))

    # ---------- BUDGET ----------
    with tab8:
        income = st.number_input("Income")
        exp = st.number_input("Expenses")

        if st.button("Analyze"):
            output = safe_ai([{"role":"user","content":f"income {income}, expense {exp} advice"}])
            st.success(output)
            save_history("Budget", output)

    # ---------- SUSTAINABILITY ----------
    with tab9:
        budget = st.number_input("Total Budget")
        green = st.number_input("Green Investment")

        if st.button("Analyze"):
            output = safe_ai([{"role":"user","content":f"budget {budget}, green {green} strategy"}])
            st.success(output)
            save_history("Sustainability", output)

    # ---------- COMPETITOR ----------
    with tab10:
        rev = st.number_input("Your Revenue")
        comp = st.number_input("Competitor Revenue")

        if st.button("Compare"):
            output = safe_ai([{"role":"user","content":f"my {rev}, competitor {comp}, strategy"}])
            st.success(output)
            save_history("Competitor", output)
