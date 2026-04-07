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

    except Exception:
        return "⚠️ AI unavailable (limit reached)"

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

# ---------------- SIDEBAR LOGIN ----------------
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

# ---------------- HISTORY ----------------
st.sidebar.markdown("## 📜 History")

if len(st.session_state.history) == 0:
    st.sidebar.info("No history yet")
else:
    for i, item in enumerate(reversed(st.session_state.history)):
        if st.sidebar.button(f"{item['title']} {i}"):
            st.sidebar.write(item["content"])

# ---------------- BLOCK ----------------
if not st.session_state.logged_in:
    st.warning("🔐 Please login to use the app")
    st.stop()

# ---------------- FILE ----------------
file = st.sidebar.file_uploader("Upload Data", type=["csv","xlsx"])

# ---------------- MAIN ----------------
if file:
    data = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(
        ["📊 Overview","📈 Charts","🧠 AI","🤖 Chat","💡 Ideas","💰 Profit","📈 Forecast","💰 Budget","🌱 Sustainability","📊 Competitor"]
    )

    # ---------- OVERVIEW ----------
    with tab1:
        st.metric("Rows", data.shape[0])
        st.metric("Columns", data.shape[1])

        # 🔹 Missing Values Analysis
        st.subheader("🧹 Missing Values Analysis")

        missing = data.isnull().sum()
        missing_percent = (missing / len(data)) * 100

        missing_df = pd.DataFrame({
            "Column": missing.index,
            "Missing Values": missing.values,
            "Percentage (%)": missing_percent.values
        }).sort_values(by="Missing Values", ascending=False)

        st.dataframe(missing_df)

        # 🔹 Total Missing
        st.metric("Total Missing Values", int(missing.sum()))

        # 🔹 Visualization
        st.subheader("📊 Missing Values Visualization")
        st.bar_chart(missing)

        with st.expander("View Full Data"):
            st.dataframe(data)

        st.dataframe(data.head(10))

    # ---------- CHARTS ----------
    with tab2:
        chart = st.selectbox("Chart Type", ["Scatter","Line","Bar","Histogram","Box","Pie"])

        x = st.selectbox("X Axis", data.columns)
        y = st.selectbox("Y Axis", data.select_dtypes(include=['int64','float64']).columns)

        if chart == "Scatter":
            st.plotly_chart(px.scatter(data,x=x,y=y))
        elif chart == "Line":
            st.plotly_chart(px.line(data,x=x,y=y))
        elif chart == "Bar":
            st.plotly_chart(px.bar(data,x=x,y=y))
        elif chart == "Histogram":
            st.plotly_chart(px.histogram(data,x=x))
        elif chart == "Box":
            st.plotly_chart(px.box(data,x=x,y=y))
        elif chart == "Pie":
            st.plotly_chart(px.pie(data,names=x,values=y))

    # ---------- AI ----------
    with tab3:
        if st.button("Generate Insights"):
            output = safe_ai([{"role":"user","content":data.head(10).to_string()}])
            st.success(output)
            save_history("AI", output)

    # ---------- CHAT ----------
    with tab4:
        q = st.text_input("Ask Question")
        if q:
            output = safe_ai([{"role":"user","content":q}])
            st.write(output)
            save_history("Chat", output)

    # ---------- IDEAS ----------
    with tab5:
        if st.button("Generate Ideas"):
            output = safe_ai([{"role":"user","content":"startup ideas"}])
            st.write(output)
            save_history("Ideas", output)

    # ---------- PROFIT ----------
    with tab6:
        rev = st.number_input("Revenue")
        cost = st.number_input("Cost")
        if st.button("Calculate Profit"):
            st.success(f"Profit ₹{rev-cost}")

    # ---------- FORECAST ----------
    with tab7:
        col = st.selectbox("Column", data.select_dtypes(include=['int64','float64']).columns)
        values = data[col].dropna().values

        if len(values)>3:
            model = LinearRegression().fit(np.arange(len(values)).reshape(-1,1), values)
            pred = model.predict([[len(values)]])[0]
            st.metric("Prediction", round(pred,2))

    # ---------- BUDGET ----------
    with tab8:
        income = st.number_input("Income")
        exp = st.number_input("Expenses")

        if st.button("Analyze Budget"):
            output = safe_ai([{"role":"user","content":f"income {income}, expense {exp} advice"}])
            st.success(output)
            save_history("Budget", output)

    # ---------- SUSTAINABILITY ----------
    with tab9:
        budget = st.number_input("Total Budget")
        green = st.number_input("Green Investment")

        if st.button("Analyze Sustainability"):
            output = safe_ai([{"role":"user","content":f"budget {budget}, green {green} sustainability"}])
            st.success(output)
            save_history("Sustainability", output)

    # ---------- COMPETITOR ----------
    with tab10:
        your = st.number_input("Your Revenue")
        comp = st.number_input("Competitor Revenue")

        if st.button("Compare"):
            output = safe_ai([{"role":"user","content":f"my {your}, competitor {comp} strategy"}])
            st.success(output)
            save_history("Competitor", output)
