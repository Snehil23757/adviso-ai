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
        st.dataframe(data.head())
        st.dataframe(data.describe())

    # ---------- CHARTS ----------
    # ---------- CHARTS ----------
    with tab2:
    st.subheader("📈 Advanced Data Visualization")

    numeric_cols = data.select_dtypes(include=['int64','float64']).columns.tolist()
    cat_cols = data.select_dtypes(include=['object']).columns.tolist()

    if len(numeric_cols) == 0:
        st.error("❌ No numeric columns available")
    else:
        left, right = st.columns([1,2])

        # -------- LEFT PANEL --------
        with left:
            st.markdown("### ⚙️ Controls")

            chart = st.selectbox(
                "Chart Type",
                ["Scatter","Line","Bar","Histogram","Box","Violin","Pie","Heatmap","Area","Density"]
            )

            x = st.selectbox("X-axis", data.columns)

            y = None
            if chart not in ["Histogram","Pie","Heatmap","Density"]:
                y = st.selectbox("Y-axis", numeric_cols)

            # 🔹 Filter
            st.markdown("### 🎯 Filters")

            filtered = data.copy()

            if len(cat_cols) > 0:
                cat = st.selectbox("Category", ["None"] + cat_cols)

                if cat != "None":
                    vals = st.multiselect("Values", data[cat].dropna().unique())

                    if vals:
                        filtered = filtered[filtered[cat].isin(vals)]

            st.write(f"Rows after filter: {filtered.shape[0]}")

        # -------- RIGHT PANEL --------
        with right:
            st.markdown("### 📊 Chart Output")

            if filtered.empty:
                st.warning("No data after filtering")
            else:
                try:
                    if chart == "Scatter":
                        fig = px.scatter(filtered, x=x, y=y)

                    elif chart == "Line":
                        fig = px.line(filtered, x=x, y=y)

                    elif chart == "Bar":
                        fig = px.bar(filtered, x=x, y=y)

                    elif chart == "Histogram":
                        fig = px.histogram(filtered, x=x)

                    elif chart == "Box":
                        fig = px.box(filtered, x=x, y=y)

                    elif chart == "Violin":
                        fig = px.violin(filtered, x=x, y=y, box=True)

                    elif chart == "Pie":
                        fig = px.pie(filtered, names=x)

                    elif chart == "Heatmap":
                        corr = filtered[numeric_cols].corr()
                        fig = px.imshow(corr, text_auto=True)

                    elif chart == "Area":
                        fig = px.area(filtered, x=x, y=y)

                    elif chart == "Density":
                        fig = px.density_contour(filtered, x=x, y=y)

                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Chart error: {str(e)}")

            st.markdown("---")
            st.subheader("📄 Data Preview")
            st.dataframe(filtered.head(), use_container_width=True)

        # -------- AI INSIGHTS --------
        st.markdown("---")
        st.subheader("🤖 Chart Insights (AI)")

        if st.button("Generate Chart Insights"):
            sample = filtered.head(20).to_string()

            prompt = f"""
            Analyze this dataset based on visual patterns:

            {sample}

            Provide:
            - Key trends
            - Relationships between variables
            - Outliers or anomalies
            - Business insights
            - Actionable recommendations
            """

            with st.spinner("Generating insights..."):
                output = safe_ai([{"role":"user","content":prompt}])
                st.success(output)
    # ---------- AI ----------
    with tab3:
        st.subheader("🧠 AI Business Intelligence Engine")

        analysis_type = st.selectbox("Analysis Type", [
            "Full Analysis","Growth","Risks","Optimization"
        ])

        if st.button("Generate AI Insights"):
            sample = data.head(10).to_string()
            output = safe_ai([{"role":"user","content":sample}])
            st.write(output)

    # ---------- CHAT ----------
  # ---------- CHAT ----------
with tab4:
    st.subheader("🤖 Smart Data Chat Assistant")

    # 🔹 Chat history (optional but useful)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 🔹 User input
    user_query = st.text_input("Ask anything about your dataset")

    if st.button("Ask AI") and user_query:

        # 🔥 Include dataset context
        sample = data.head(20).to_string()

        prompt = f"""
        You are a data analyst and business consultant.

        Here is a dataset sample:
        {sample}

        User Question:
        {user_query}

        Provide:

        1. 📊 Direct Answer
        - Answer the question clearly

        2. 🔍 Data Insights
        - What does the data say about this?

        3. 💡 Recommendations
        - What actions should be taken?

        4. ❓ Related Questions
        - Suggest 3 follow-up questions user should ask

        5. ⚠️ Observations
        - Any anomalies or patterns

        Keep it simple, practical, and business-focused.
        """

        with st.spinner("Analyzing your data..."):
            response = safe_ai([{"role": "user", "content": prompt}])

            st.success("✅ Response Generated")

            # Save chat
            st.session_state.chat_history.append({
                "question": user_query,
                "answer": response
            })

    st.markdown("---")

    # 🔹 Display chat history
    if st.session_state.chat_history:
        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**🧑 You:** {chat['question']}")
            st.markdown(f"**🤖 AI:** {chat['answer']}")
            st.markdown("---")

    # ---------- IDEAS ----------
    with tab5:
        st.subheader("💡 Ideas")
        industry = st.selectbox("Industry", ["Retail","Healthcare","Tech","Finance"])
        if st.button("Generate Ideas"):
            st.write(safe_ai([{"role":"user","content":industry}]))

    # ---------- PROFIT ----------
    with tab6:
        revenue = st.number_input("Revenue")
        cost = st.number_input("Cost")
        st.metric("Profit", revenue - cost)

    # ---------- FORECAST ----------
    with tab7:
        col = st.selectbox("Column", data.select_dtypes(include=['int64','float64']).columns)
        st.line_chart(data[col])

    # ---------- BUDGET ----------
    with tab8:
        income = st.number_input("Income")
        expense = st.number_input("Expense")
        st.metric("Savings", income - expense)

    # ---------- SUSTAINABILITY ----------
    with tab9:
        st.write("Sustainability Dashboard")

    # ---------- COMPETITOR ----------
    with tab10:
        st.write("Competitor Analysis")

    # ---------- KPI ----------
    with tab11:
        col = st.selectbox("KPI Column", data.select_dtypes(include=['int64','float64']).columns)
        st.line_chart(data[col])
