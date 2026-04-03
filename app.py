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

/* Chat bubbles */
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

/* Cards */
.kpi-card {
    background: linear-gradient(145deg, #1f2937, #111827);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}

/* Inputs */
.stTextInput, .stSelectbox, .stMultiSelect {
    background-color: #1e293b !important;
}

/* Buttons */
.stButton button {
    background: linear-gradient(to right, #2563eb, #1d4ed8);
    color: white;
    border-radius: 8px;
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

    st.subheader("📈 Statistical Summary")
    st.dataframe(data.describe())

# ---------------- VISUALIZATION ----------------
if data is not None:
    st.subheader("📊 Visualization")

    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns

    if len(numeric_cols) >= 2:
        col1, col2 = st.columns(2)

        with col1:
            x = st.selectbox("X-axis", numeric_cols)

        with col2:
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

# ---------------- ADVANCED KPI DASHBOARD ----------------
if data is not None:
    st.markdown("## 📊 KPI Dashboard")

    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns

    if len(numeric_cols) > 0:

        selected_metrics = st.multiselect(
            "Select KPIs",
            numeric_cols,
            default=list(numeric_cols[:3])
        )

        cols = st.columns(3)

        for i, col_name in enumerate(selected_metrics):
            values = data[col_name]

            total = int(values.sum())
            avg = round(values.mean(), 2)
            max_val = int(values.max())

            # ---- KPI COMPARISON ----
            if len(values) > 2:
                current = values.iloc[-1]
                previous = values.iloc[-2]

                change = current - previous
                percent_change = (change / previous) * 100 if previous != 0 else 0

                # ---- TREND ----
                if change > 0:
                    arrow = "↑"
                    color = "#22c55e"  # green
                elif change < 0:
                    arrow = "↓"
                    color = "#ef4444"  # red
                else:
                    arrow = "→"
                    color = "#9ca3af"

                trend_text = f"{arrow} {round(percent_change,2)}%"

            else:
                trend_text = "N/A"
                color = "#9ca3af"

            with cols[i % 3]:
                st.markdown(f"""
                <div class="kpi-card">
                    <h4 style="color:#9ca3af;">{col_name}</h4>
                    <h1 style="color:white;">{total:,}</h1>
                    <p style="color:{color}; font-size:18px;">{trend_text}</p>
                    <p style="color:#6b7280;">Avg: {avg} | Max: {max_val}</p>
                </div>
                """, unsafe_allow_html=True)

# ---------------- CHAT ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bot'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

user_input = st.chat_input("Ask anything about your data...")

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
