import streamlit as st
import pandas as pd
from openai import OpenAI

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

# ---------------- CLEAN UI ----------------
st.markdown("""
<style>

/* -------- GLOBAL -------- */
.stApp {
    background-color: #0a0a0a;
    color: #f5f5f7;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
}

/* CENTER CONTENT */
.main > div {
    max-width: 900px;
    margin: auto;
}

/* REMOVE EXTRA SPACE */
.block-container {
    padding-top: 2rem;
}

/* TITLE */
.title {
    font-size: 34px;
    font-weight: 600;
    text-align: center;
}

/* SUBTITLE */
.subtitle {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 30px;
}

/* KPI CARD */
.kpi {
    background: #111111;
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 10px;
}

/* CHAT */
.chat-user {
    background: #2563eb;
    padding: 12px;
    border-radius: 16px;
}

.chat-bot {
    background: #1c1c1e;
    padding: 12px;
    border-radius: 16px;
}

/* CHAT INPUT FIX */
section[data-testid="stChatInput"] {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #050505;
    border-right: 1px solid #1f2937;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<div class='title'>Adviso AI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Turning data into decisions</div>", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 📁 Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])
st.sidebar.markdown("---")
st.sidebar.caption("Adviso AI v1.0")

# ---------------- OPENAI ----------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- LOAD DATA ----------------
data = None

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        st.sidebar.success("Data uploaded")

    except Exception as e:
        st.error(e)

# ---------------- EMPTY STATE ----------------
if data is None:
    st.markdown("""
    <div style='text-align:center; margin-top:80px;'>
        <h3>Upload your data to get started</h3>
        <p style='color:#9ca3af'>Analyze, visualize, and chat with your data</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------- OVERVIEW ----------------
if data is not None:
    st.markdown("## Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", data.shape[0])
    c2.metric("Columns", data.shape[1])
    c3.metric("Missing", data.isnull().sum().sum())

# ---------------- KPI ----------------
if data is not None:
    st.markdown("## Key Metrics")

    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns

    selected = st.multiselect("Select metrics", numeric_cols, default=list(numeric_cols[:3]))

    cols = st.columns(3)

    for i, col in enumerate(selected):
        values = data[col]
        total = int(values.sum())

        change = values.iloc[-1] - values.iloc[-2] if len(values) > 2 else 0

        if change > 0:
            trend = "↑ Up"
            color = "#30d158"
        elif change < 0:
            trend = "↓ Down"
            color = "#ff453a"
        else:
            trend = "→ Stable"
            color = "#9ca3af"

        with cols[i % 3]:
            st.markdown(f"""
            <div class="kpi">
                <h4>{col}</h4>
                <h2>{total:,}</h2>
                <p style="color:{color}">{trend}</p>
            </div>
            """, unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
if data is not None:
    st.markdown("## Analytics")

    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Trend")
        if len(numeric_cols) > 0:
            st.line_chart(data[numeric_cols[0]])

    with col2:
        st.markdown("### Comparison")
        if len(numeric_cols) > 1:
            st.bar_chart(data[numeric_cols[:2]])

# ---------------- AI INSIGHTS ----------------
if data is not None:
    with st.expander("AI Insights"):
        try:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Analyze:\n{data.head().to_string()}"}]
            )
            st.write(res.choices[0].message.content)
        except:
            st.warning("AI unavailable")

# ---------------- CHAT ----------------
st.markdown("## 🤖 Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ask anything about your data...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}]
        )
        reply = res.choices[0].message.content
    except Exception as e:
        reply = str(e)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
