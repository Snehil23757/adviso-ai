import streamlit as st
import pandas as pd
from openai import OpenAI
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

# ---------------- PREMIUM UI ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #0f172a, #020617);
    color: white;
}
.chat-user {
    background: #2563eb;
    padding: 12px;
    border-radius: 12px;
    margin: 6px 0;
}
.chat-bot {
    background: #1e293b;
    padding: 12px;
    border-radius: 12px;
    margin: 6px 0;
}
.kpi-card {
    background: linear-gradient(145deg, #1f2937, #111827);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🤖 Adviso AI")
uploaded_file = st.sidebar.file_uploader("Upload Data", type=["csv", "xlsx"])

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- LOAD DATA ----------------
data = None

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.sidebar.success("✅ Data uploaded")

# ---------------- TITLE ----------------
st.title("💬 Adviso AI Copilot")

# ---------------- AUTO INSIGHTS ----------------
if data is not None:
    with st.expander("🧠 AI Insights"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Analyze:\n{data.head().to_string()}"}]
            )
            st.write(response.choices[0].message.content)
        except:
            st.warning("AI unavailable")

# ---------------- BASIC METRICS ----------------
if data is not None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", data.shape[0])
    col2.metric("Columns", data.shape[1])
    col3.metric("Missing", data.isnull().sum().sum())

# ---------------- ADVANCED KPI ----------------
if data is not None:
    st.markdown("## 📊 KPI Dashboard")

    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns

    selected_metrics = st.multiselect(
        "Select KPIs",
        numeric_cols,
        default=list(numeric_cols[:3])
    )

    cols = st.columns(3)

    for i, col_name in enumerate(selected_metrics):
        values = data[col_name]

        total = int(values.sum())

        if len(values) > 2:
            change = values.iloc[-1] - values.iloc[-2]

            if change > 0:
                trend = "↑"
                color = "#22c55e"
            elif change < 0:
                trend = "↓"
                color = "#ef4444"
            else:
                trend = "→"
                color = "#9ca3af"
        else:
            trend = "-"
            color = "#9ca3af"

        with cols[i % 3]:
            st.markdown(f"""
            <div class="kpi-card">
                <h4>{col_name}</h4>
                <h1>{total:,}</h1>
                <p style="color:{color}">{trend}</p>
            </div>
            """, unsafe_allow_html=True)

# ---------------- ADVANCED DASHBOARD ----------------
if data is not None:
    st.markdown("## 📊 Advanced Dashboard")

    df = data.copy()

    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    st.sidebar.markdown("### 🔍 Filters")

    if len(categorical_cols) > 0:
        cat = st.sidebar.selectbox("Category", categorical_cols)
        vals = st.sidebar.multiselect("Values", df[cat].unique())
        if vals:
            df = df[df[cat].isin(vals)]

    if len(numeric_cols) > 0:
        num = st.sidebar.selectbox("Numeric", numeric_cols)
        min_val, max_val = st.sidebar.slider(
            "Range",
            float(df[num].min()),
            float(df[num].max()),
            (float(df[num].min()), float(df[num].max()))
        )
        df = df[(df[num] >= min_val) & (df[num] <= max_val)]

    # Charts
    c1, c2 = st.columns(2)

    with c1:
        if len(numeric_cols) > 0:
            st.line_chart(df[numeric_cols[0]])

    with c2:
        if len(numeric_cols) > 1:
            st.bar_chart(df[numeric_cols[:2]])

# ---------------- CHAT ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-user'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bot'>{msg['content']}</div>", unsafe_allow_html=True)

user_input = st.chat_input("Ask anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}]
        )

        reply = response.choices[0].message.content

    except Exception as e:
        reply = f"❌ {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
