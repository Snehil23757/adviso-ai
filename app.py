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
        st.dataframe(data.head())

    # ---------- CHARTS ----------
    with tab2:
        chart = st.selectbox("Chart", ["Scatter","Line","Bar","Histogram"], key="chart_type")
        x = st.selectbox("X", data.columns, key="chart_x")
        y = st.selectbox("Y", data.select_dtypes(include=['int64','float64']).columns, key="chart_y")

        if chart=="Scatter":
            st.plotly_chart(px.scatter(data,x=x,y=y))
        elif chart=="Line":
            st.plotly_chart(px.line(data,x=x,y=y))
        elif chart=="Bar":
            st.plotly_chart(px.bar(data,x=x,y=y))
        else:
            st.plotly_chart(px.histogram(data,x=x))

    # ---------- IDEAS ----------
    with tab5:
        industry = st.text_input("Industry", key="idea_industry")
        if st.button("Generate Ideas", key="idea_btn"):
            st.write(safe_ai([{"role":"user","content":industry}]))

    # ---------- PROFIT ----------
    with tab6:
        revenue = st.number_input("Revenue", key="profit_rev")
        cost = st.number_input("Cost", key="profit_cost")
        st.metric("Profit", revenue - cost)

    # ---------- FORECAST ----------
    with tab7:
        col = st.selectbox("Column", data.select_dtypes(include=['int64','float64']).columns, key="forecast_col")
        values = data[col].dropna().values

        if len(values)>3:
            years = st.slider("Years",1,10,3,key="forecast_years")
            model = LinearRegression().fit(np.arange(len(values)).reshape(-1,1), values)
            pred = model.predict(np.arange(len(values),len(values)+years).reshape(-1,1))
            st.line_chart(np.concatenate([values,pred]))

    # ---------- BUDGET ----------
    with tab8:
        income = st.number_input("Income", key="budget_income")
        expense = st.number_input("Expense", key="budget_expense")
        st.metric("Savings", income-expense)

    # ---------- SUSTAINABILITY ----------
    with tab9:
        carbon = st.number_input("Carbon", key="sustain_carbon")
        years = st.slider("Years",1,10,5,key="sustain_years")
        st.line_chart([carbon*(0.9**i) for i in range(years)])

    # ---------- COMPETITOR ----------
    with tab10:
        your = st.number_input("Your Revenue", key="comp_you")
        comp = st.number_input("Competitor Revenue", key="comp_comp")
        st.metric("Difference", your-comp)

    # ---------- KPI ----------
    with tab11:
        col = st.selectbox("KPI Column", data.select_dtypes(include=['int64','float64']).columns, key="kpi_col")
        k = data[col].dropna().values
        if len(k)>3:
            model = LinearRegression().fit(np.arange(len(k)).reshape(-1,1), k)
            pred = model.predict([[len(k)]])[0]
            st.metric("Next KPI", round(pred,2))
            st.line_chart(np.append(k,pred))
