import streamlit as st
import pandas as pd
from openai import OpenAI
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

# ---------------- CLEAN PROFESSIONAL UI ----------------
st.markdown("""
<style>

/* -------- GLOBAL -------- */
.stApp {
    background-color: #0b1220;
    color: #e5e7eb;
    font-family: 'Inter', sans-serif;
}

/* -------- SPACING -------- */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* -------- HEADINGS -------- */
h1, h2, h3 {
    font-weight: 600;
}

/* -------- CARD -------- */
.card {
    background: #111827;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #1f2937;
}

/* -------- KPI -------- */
.kpi {
    background: #111827;
    border: 1px solid #1f2937;
    padding: 18px;
    border-radius: 12px;
}

.kpi-title {
    font-size: 14px;
    color: #9ca3af;
}

.kpi-value {
    font-size: 28px;
    font-weight: 600;
}

.kpi-trend {
    font-size: 14px;
}

/* -------- CHAT -------- */
.chat-user {
    background: #2563eb;
    padding: 10px;
    border-radius: 10px;
    margin: 6px 0;
}

.chat-bot {
    background: #1f2937;
    padding: 10px;
    border-radius: 10px;
    margin: 6px 0;
}

/* -------- BUTTON -------- */
.stButton button {
    background: #2563eb;
    color: white;
    border-radius: 8px;
}

/* -------- SIDEBAR -------- */
section[data-testid="stSidebar"] {
    background-color: #020617;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
col1, col2 = st.columns([1, 6])

with col1:
    st.image("logo.png", width=60)

with col2:
    st.markdown("### Adviso AI Copilot")
    st.caption("Turning Data into Decisions")

# ---------------- SIDEBAR ----------------
st.sidebar.title("Upload Data")
uploaded_file = st.sidebar.file_uploader("", type=["csv", "xlsx"])

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- LOAD DATA ----------------
data = None

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.sidebar.success("Data uploaded successfully")

# ---------------- BASIC METRICS ----------------
if data is not None:
    st.markdown("## Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", data.shape[0])
    c2.metric("Columns", data.shape[1])
    c3.metric("Missing Values", data.isnull().sum().sum())

# ---------------- KPI DASHBOARD ----------------
if data is not None:
    st.markdown("## KPI Dashboard")

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
                trend = "↑ Positive"
                color = "#22c55e"
            elif change < 0:
                trend = "↓ Negative"
                color = "#ef4444"
            else:
                trend = "→ Stable"
                color = "#9ca3af"
        else:
            trend = "-"
            color = "#9ca3af"

        with cols[i % 3]:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-title">{col_name}</div>
                <div class="kpi-value">{total:,}</div>
                <div class="kpi-trend" style="color:{color}">
                    {trend}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
if data is not None:
    st.markdown("## Dashboard")

    df = data.copy()

    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # Filters
    st.sidebar.markdown("Filters")

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
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Trend Analysis")
        if len(numeric_cols) > 0:
            st.line_chart(df[numeric_cols[0]])

    with col2:
        st.markdown("#### Comparison")
        if len(numeric_cols) > 1:
            st.bar_chart(df[numeric_cols[:2]])

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
st.markdown("## AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-user'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bot'>{msg['content']}</div>", unsafe_allow_html=True)

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
