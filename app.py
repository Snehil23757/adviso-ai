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
            return "⏳ Please wait a few seconds"

        st.session_state.last_call = time.time()

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return res.choices[0].message.content

    except Exception as e:
        return f"⚠️ {str(e)}"

# ---------------- AUTH ----------------
if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
st.sidebar.title("👤 Login")

if not st.session_state.logged_in:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.success("Logged in")
        else:
            st.error("Invalid credentials")

    st.stop()

# ---------------- FILE ----------------
file = st.sidebar.file_uploader("Upload Data", type=["csv","xlsx"])

if file:
    data = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    # ---------------- TABS ----------------
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs(
        ["📊 Overview","📈 Charts","🧠 AI","🤖 Chat","💡 Ideas","💰 Profit","📈 Forecast","💰 Budget","🌱 Sustainability","📊 Competitor","📊 KPI Dashboard"]
    )

    # ---------- OVERVIEW ----------
    with tab1:
        st.metric("Rows", data.shape[0])
        st.metric("Columns", data.shape[1])

        missing = data.isnull().sum()
        st.subheader("Missing Values")
        st.dataframe(missing)
        st.bar_chart(missing)

    # ---------- CHARTS ----------
    with tab2:
        chart = st.selectbox("Chart", ["Scatter","Line","Bar","Histogram"])

        x = st.selectbox("X", data.columns)
        y = st.selectbox("Y", data.select_dtypes(include=['int64','float64']).columns)

        filtered = data.copy()

        # Category filter
        cat_cols = data.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            cat = st.selectbox("Category Filter", ["None"] + list(cat_cols))
            if cat != "None":
                vals = st.multiselect("Values", data[cat].unique())
                if vals:
                    filtered = filtered[filtered[cat].isin(vals)]

        # Range filter
        num_cols = data.select_dtypes(include=['int64','float64']).columns
        if len(num_cols) > 0:
            rcol = st.selectbox("Range Filter", ["None"] + list(num_cols))
            if rcol != "None":
                minv = float(data[rcol].min())
                maxv = float(data[rcol].max())
                r = st.slider("Range", minv, maxv, (minv, maxv))
                filtered = filtered[(filtered[rcol] >= r[0]) & (filtered[rcol] <= r[1])]

        # Sorting
        sort = st.selectbox("Sort", ["None"] + list(filtered.columns))
        if sort != "None":
            filtered = filtered.sort_values(sort)

        st.dataframe(filtered.head(20))

        if chart == "Scatter":
            st.plotly_chart(px.scatter(filtered, x=x, y=y))
        elif chart == "Line":
            st.plotly_chart(px.line(filtered, x=x, y=y))
        elif chart == "Bar":
            st.plotly_chart(px.bar(filtered, x=x, y=y))
        elif chart == "Histogram":
            st.plotly_chart(px.histogram(filtered, x=x))

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
        if st.button("Ideas"):
            st.write(safe_ai([{"role":"user","content":"startup ideas"}]))

    # ---------- PROFIT ----------
    with tab6:
        rev = st.number_input("Revenue")
        cost = st.number_input("Cost")
        if st.button("Calc"):
            st.success(rev-cost)

    # ---------- FORECAST ----------
    with tab7:
        col = st.selectbox("Column", data.select_dtypes(include=['int64','float64']).columns)
        vals = data[col].dropna().values

        if len(vals)>3:
            model = LinearRegression().fit(np.arange(len(vals)).reshape(-1,1), vals)
            pred = model.predict([[len(vals)]])[0]
            st.metric("Prediction", round(pred,2))

    # ---------- BUDGET ----------
    with tab8:
        inc = st.number_input("Income")
        exp = st.number_input("Expense")
        if st.button("Analyze"):
            st.write(safe_ai([{"role":"user","content":f"income {inc}, expense {exp}"}]))

    # ---------- SUSTAINABILITY ----------
    with tab9:
        bud = st.number_input("Budget")
        green = st.number_input("Green Spend")
        if st.button("Check"):
            st.write(safe_ai([{"role":"user","content":f"{bud}, {green} sustainability"}]))

    # ---------- COMPETITOR ----------
    with tab10:
        y = st.number_input("Your Revenue")
        c = st.number_input("Competitor")
        if st.button("Compare"):
            st.write(safe_ai([{"role":"user","content":f"{y} vs {c}"}]))

    # ---------- KPI ----------
    with tab11:
        col = st.selectbox("KPI Column", data.select_dtypes(include=['int64','float64']).columns)
        k = data[col].dropna().values

        if len(k)>0:
            st.metric("Current", k[-1])
            st.metric("Avg", np.mean(k))

            if len(k)>1 and k[-2]!=0:
                growth = ((k[-1]-k[-2])/k[-2])*100
                st.metric("Growth %", round(growth,2))

            st.line_chart(k)

            if len(k)>3:
                model = LinearRegression().fit(np.arange(len(k)).reshape(-1,1), k)
                pred = model.predict([[len(k)]])[0]
                st.metric("Next", round(pred,2))
                st.line_chart(np.append(k,pred))
