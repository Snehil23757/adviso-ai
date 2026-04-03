import streamlit as st
import pandas as pd
from openai import OpenAI
import time

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

# ---------------- DATA ----------------
data = None

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.sidebar.success("✅ Data uploaded")

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

        except:
            st.warning("AI insights unavailable")

# ---------------- CHAT ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bot'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

# ---------------- INPUT ----------------
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

        # ✨ Typing animation
        for word in reply.split():
            full_response += word + " "
            placeholder.markdown(
                f"<div class='chat-bot'>🤖 {full_response}</div>",
                unsafe_allow_html=True
            )
            time.sleep(0.03)

    except Exception as e:
        full_response = f"❌ Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # ---------------- CHART IN CHAT ----------------
    if data is not None:
        numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns

        if len(numeric_cols) >= 2:
            st.markdown("### 📊 Quick Chart")
            st.line_chart(data[numeric_cols[:2]])

    st.rerun()
