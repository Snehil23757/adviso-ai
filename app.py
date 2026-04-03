import streamlit as st
import pandas as pd
from openai import OpenAI

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

# ---------------- APPLE-LEVEL UI ----------------
st.markdown("""
<style>

/* GLOBAL */
.stApp {
    background-color: #0a0a0a;
    color: #f5f5f7;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
}

/* SPACING */
.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
}

/* HEADINGS */
h1, h2, h3 {
    font-weight: 600;
}

/* SUBTEXT */
p {
    color: #9ca3af;
}

/* CARD */
.apple-card {
    background: #111111;
    padding: 24px;
    border-radius: 18px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.6);
}

/* KPI */
.kpi-title {
    font-size: 13px;
    color: #9ca3af;
}

.kpi-value {
    font-size: 34px;
    font-weight: 600;
}

.kpi-trend {
    font-size: 13px;
}

/* CHAT */
.chat-user {
    background: #2563eb;
    padding: 12px;
    border-radius: 16px;
    margin: 6px 0;
}

.chat-bot {
    background: #1c1c1e;
    padding: 12px;
    border-radius: 16px;
    margin: 6px 0;
}

/* BUTTON */
.stButton button {
    background: #2563eb;
    border-radius: 999px;
    padding: 8px 18px;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #050505;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("## Adviso AI")
st.caption("Turning data into decisions")

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("### Upload Data")
uploaded_file = st.sidebar.file_uploader("", type=["csv", "xlsx"])

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- LOAD DATA ----------------
data = None

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        st.sidebar.success("Data uploaded successfully")

    except Exception as e:
        st.error(e)

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

    selected = st.multiselect(
        "Select metrics",
        numeric_cols,
        default=list(numeric_cols[:3])
    )

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
            <div class="apple-card">
                <div class="kpi-title">{col}</div>
                <div class="kpi-value">{total:,}</div>
                <div class="kpi-trend" style="color:{color}">{trend}</div>
            </div>
            """, unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
if data is not None:
    st.markdown("## Analytics")

    df = data.copy()
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Trend")
        if len(num_cols) > 0:
            st.line_chart(df[num_cols[0]])

    with col2:
        st.markdown("### Comparison")
        if len(num_cols) > 1:
            st.bar_chart(df[num_cols[:2]])

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
st.markdown("## Assistant")

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
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}]
        )
        reply = res.choices[0].message.content
    except Exception as e:
        reply = str(e)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
