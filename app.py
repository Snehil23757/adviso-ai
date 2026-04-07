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

        col1, col2 = st.columns(2)
        col1.metric("Rows", data.shape[0])
        col2.metric("Columns", data.shape[1])

        # Missing Values
        st.subheader("🧹 Missing Values Analysis")
        missing = data.isnull().sum()
        percent = (missing / len(data)) * 100

        miss_df = pd.DataFrame({
            "Column": missing.index,
            "Missing": missing.values,
            "%": percent.values
        }).sort_values(by="Missing", ascending=False)

        st.dataframe(miss_df)
        st.metric("Total Missing", int(missing.sum()))
        st.bar_chart(missing)

        # Full Data
        with st.expander("📂 View Full Data"):
            st.dataframe(data)

        st.subheader("🔍 Preview")
        st.dataframe(data.head(10))

        # Statistical Summary
        st.subheader("📊 Statistical Summary")
        stats = data.describe()
        st.dataframe(stats)

        # AI Insights on Stats
        if st.button("🤖 Generate Statistical Insights"):
            with st.spinner("Analyzing..."):
                output = safe_ai([{
                    "role":"user",
                    "content":f"Explain key insights from this dataset:\n{stats.to_string()}"
                }])
                st.success(output)
                save_history("Stats Insights", output)

    # ---------- CHARTS ----------
    with tab2:
        st.subheader("📈 Smart Charts")

        chart = st.selectbox("Chart Type", ["Scatter","Line","Bar","Histogram"])
        x = st.selectbox("X Axis", data.columns)
        y = st.selectbox("Y Axis", data.select_dtypes(include=['int64','float64']).columns)

        filtered = data.copy()

        cat_cols = data.select_dtypes(include=['object']).columns
        if len(cat_cols)>0:
            cat = st.selectbox("Category Filter", ["None"]+list(cat_cols))
            if cat!="None":
                vals = st.multiselect("Values", data[cat].unique())
                if vals:
                    filtered = filtered[filtered[cat].isin(vals)]

        num_cols = data.select_dtypes(include=['int64','float64']).columns
        if len(num_cols)>0:
            rc = st.selectbox("Range Filter", ["None"]+list(num_cols))
            if rc!="None":
                r = st.slider("Range", float(data[rc].min()), float(data[rc].max()),
                              (float(data[rc].min()), float(data[rc].max()))
                )
                filtered = filtered[(filtered[rc]>=r[0]) & (filtered[rc]<=r[1])]

        st.dataframe(filtered.head(20))

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
            save_history("AI", out)

    # ---------- CHAT ----------
    with tab4:
        q = st.text_input("Ask")
        if q:
            out = safe_ai([{"role":"user","content":q}])
            st.write(out)
            save_history("Chat", out)

    # ---------- IDEAS ----------
    with tab5:
        if st.button("Ideas"):
            out = safe_ai([{"role":"user","content":"startup ideas"}])
            st.write(out)
            save_history("Ideas", out)

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

    # ---------- KPI ----------
    with tab11:
        col = st.selectbox("KPI Column", data.select_dtypes(include=['int64','float64']).columns)
        k = data[col].dropna().values

        if len(k)>0:
            st.metric("Current", k[-1])
            st.metric("Average", round(np.mean(k),2))

            if len(k)>1 and k[-2]!=0:
                growth = ((k[-1]-k[-2])/k[-2])*100
                st.metric("Growth %", round(growth,2))

            st.line_chart(k)

            if len(k)>3:
                m = LinearRegression().fit(np.arange(len(k)).reshape(-1,1), k)
                pred = m.predict([[len(k)]])[0]
                st.metric("Next Prediction", round(pred,2))
                st.line_chart(np.append(k,pred))
