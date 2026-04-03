import streamlit as st
import pandas as pd
from openai import OpenAI
import time
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
.chat-user {
    background-color: #1f6feb;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
}
.chat-bot {
    background-color: #2d2f34;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🤖 Adviso AI")
uploaded_file = st.sidebar.file_uploader("Upload Data", type=["csv", "xlsx"])

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

        st.sidebar.success("✅ Data uploaded")

    except Exception as e:
        st.error(e)

# ---------------- DASHBOARD ----------------
if data is not None:
    st.sidebar.markdown("### 📊 Dashboard")
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Rows", data.shape[0])
    col2.metric("Columns", data.shape[1])

# ---------------- TITLE ----------------
st.title("💬 Adviso AI Copilot")

# ---------------- AUTO INSIGHTS ----------------
if data is not None:
    with st.expander("🧠 Auto Insights"):
        try:
            context = f"Analyze dataset:\n{data.head().to_string()}"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": context}]
            )
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.warning(e)

# ---------------- FULL INSIGHTS ----------------
if data is not None:
    st.markdown("## 📊 Full Data Insights")

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", data.shape[0])
    col2.metric("Columns", data.shape[1])
    col3.metric("Missing", data.isnull().sum().sum())

    st.subheader("📈 Statistics")
    st.dataframe(data.describe())

# ---------------- VISUALIZATION ----------------
if data is not None:
    st.subheader("📊 Visualization")

    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns

    if len(numeric_cols) >= 2:
        x = st.selectbox("X-axis", numeric_cols)
        y = st.selectbox("Y-axis", numeric_cols)

        st.line_chart(data[[x, y]])

# ---------------- AUTO DASHBOARD ----------------
if data is not None:
    st.markdown("## 🤖 Auto Dashboard")

    if st.button("Generate Dashboard"):
        numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns

        if len(numeric_cols) >= 2:
            st.line_chart(data[numeric_cols[:2]])
            st.bar_chart(data[numeric_cols[:2]])
            st.dataframe(data[numeric_cols].corr())

# ---------------- KPI ----------------
if data is not None:
    st.markdown("## 📊 KPI Metrics")

    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns

    if len(numeric_cols) > 0:
        st.metric("Total", int(data[numeric_cols[0]].sum()))

# ---------------- CHAT ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bot'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

user_input = st.chat_input("Ask anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    context = ""
    if data is not None:
        context = f"Dataset:\n{data.head().to_string()}"

    placeholder = st.empty()
    full_response = ""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": context + "\n" + user_input}]
        )

        reply = response.choices[0].message.content

        for word in reply.split():
            full_response += word + " "
            placeholder.markdown(
                f"<div class='chat-bot'>🤖 {full_response}</div>",
                unsafe_allow_html=True
            )
            time.sleep(0.02)

    except Exception as e:
        full_response = f"❌ {e}"

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()
