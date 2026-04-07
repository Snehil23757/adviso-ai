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
        return f"⚠️ Error: {str(e)}"

# ---------------- HISTORY ----------------
if "history" not in st.session_state:
    st.session_state.history = []

def save_history(title, content):
    st.session_state.history.append({"title": title, "content": content})

# ---------------- AUTH ----------------
if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#020617,#0f172a);color:#e2e8f0;}
.block-container {padding:2rem 4rem;}
.title {
    font-size:40px;font-weight:900;text-align:center;
    background:linear-gradient(90deg,#38bdf8,#6366f1,#22c55e);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🚀 Adviso AI</div>", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
st.sidebar.markdown("## 👤 Profile")

if not st.session_state.logged_in:
    mode = st.sidebar.radio("Login / Signup", ["Login", "Signup"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if mode == "Login":
        if st.sidebar.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in")
            else:
                st.error("Invalid credentials")
    else:
        if st.sidebar.button("Signup"):
            st.session_state.users[username] = password
            st.success("Account created")

else:
    st.sidebar.success(f"Welcome {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False

# ---------------- BLOCK ----------------
if not st.session_state.logged_in:
    st.warning("🔐 Please login to use the app")
    st.stop()

# ---------------- FILE ----------------
file = st.sidebar.file_uploader("Upload Data", type=["csv","xlsx"])

# ---------------- MAIN ----------------
if file:
    data = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs(
        ["📊 Overview","📈 Charts","🧠 AI","🤖 Chat","💡 Ideas","💰 Profit","📈 Forecast","💰 Budget","🌱 Sustainability","📊 Competitor","📊 KPI Dashboard"]
    )

    # ---------- OVERVIEW ----------
    with tab1:
        st.metric("Rows", data.shape[0])
        st.metric("Columns", data.shape[1])

        st.subheader("🧹 Missing Values Analysis")

        missing = data.isnull().sum()
        missing_percent = (missing / len(data)) * 100

        missing_df = pd.DataFrame({
            "Column": missing.index,
            "Missing Values": missing.values,
            "Percentage (%)": missing_percent.values
        }).sort_values(by="Missing Values", ascending=False)

        st.dataframe(missing_df)
        st.metric("Total Missing", int(missing.sum()))
        st.bar_chart(missing)

        with st.expander("View Full Data"):
            st.dataframe(data)

    # ---------- CHARTS ----------
    with tab2:
        st.subheader("📈 Smart Charts")

        chart = st.selectbox("Chart Type", ["Scatter","Line","Bar","Histogram","Box","Pie"])
        x = st.selectbox("X Axis", data.columns)
        y = st.selectbox("Y Axis", data.select_dtypes(include=['int64','float64']).columns)

        filtered_data = data.copy()

        # CATEGORY FILTER
        cat_cols = data.select_dtypes(include=['object']).columns.tolist()
        if len(cat_cols) > 0:
            cat_filter = st.selectbox("Category Filter", ["None"] + cat_cols)
            if cat_filter != "None":
                vals = st.multiselect("Select Values", data[cat_filter].dropna().unique())
                if vals:
                    filtered_data = filtered_data[filtered_data[cat_filter].isin(vals)]

        # RANGE FILTER
        num_cols = data.select_dtypes(include=['int64','float64']).columns.tolist()
        if len(num_cols) > 0:
            range_col = st.selectbox("Range Filter", ["None"] + num_cols)
            if range_col != "None":
                min_val = float(data[range_col].min())
                max_val = float(data[range_col].max())
                r = st.slider("Select Range", min_val, max_val, (min_val, max_val))
                filtered_data = filtered_data[(filtered_data[range_col] >= r[0]) & (filtered_data[range_col] <= r[1])]

        # SORT
        sort_col = st.selectbox("Sort Column", ["None"] + list(filtered_data.columns))
        order = st.radio("Order", ["Ascending","Descending"])
        if sort_col != "None":
            filtered_data = filtered_data.sort_values(by=sort_col, ascending=(order=="Ascending"))

        st.dataframe(filtered_data.head(20))

        if len(filtered_data) > 0:
            if chart == "Scatter":
                st.plotly_chart(px.scatter(filtered_data, x=x, y=y))
            elif chart == "Line":
                st.plotly_chart(px.line(filtered_data, x=x, y=y))
            elif chart == "Bar":
                st.plotly_chart(px.bar(filtered_data, x=x, y=y))
            elif chart == "Histogram":
                st.plotly_chart(px.histogram(filtered_data, x=x))
            elif chart == "Box":
                st.plotly_chart(px.box(filtered_data, x=x, y=y))
            elif chart == "Pie":
                st.plotly_chart(px.pie(filtered_data, names=x, values=y))
        else:
            st.warning("No data after filtering")

    # ---------- KPI DASHBOARD ----------
    with tab11:
        st.subheader("📊 KPI Tracker & Predictor")

        kpi_col = st.selectbox("Select KPI", data.select_dtypes(include=['int64','float64']).columns)
        kpi_data = data[kpi_col].dropna().values

        if len(kpi_data) > 0:
            current = kpi_data[-1]
            avg = np.mean(kpi_data)

            growth = 0
            if len(kpi_data) > 1 and kpi_data[-2] != 0:
                growth = ((kpi_data[-1] - kpi_data[-2]) / kpi_data[-2]) * 100

            c1,c2,c3 = st.columns(3)
            c1.metric("Current", round(current,2))
            c2.metric("Average", round(avg,2))
            c3.metric("Growth %", f"{round(growth,2)}%")

            st.line_chart(kpi_data)

            if len(kpi_data) > 3:
                X = np.arange(len(kpi_data)).reshape(-1,1)
                model = LinearRegression().fit(X, kpi_data)
                pred = model.predict([[len(kpi_data)]])[0]

                st.metric("Next Prediction", round(pred,2))
                st.line_chart(np.append(kpi_data, pred))
