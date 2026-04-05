import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

# ---------------- AI SETUP ----------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
SYSTEM_PROMPT = "You are a professional business analyst. Give practical, actionable insights."

# ---------------- RATE LIMIT CONTROL ----------------
if "last_call" not in st.session_state:
    st.session_state.last_call = 0

def can_call():
    return time.time() - st.session_state.last_call > 5

def safe_ai_call(messages):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return res.choices[0].message.content
    except Exception:
        return "⚠️ AI unavailable (quota/rate limit reached). Try again later."

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp {background:#020617;color:white;}
</style>
""", unsafe_allow_html=True)

st.title("🚀 Adviso AI")

# ---------------- FILE ----------------
file = st.sidebar.file_uploader("Upload Data", type=["csv","xlsx"])

# ---------------- PDF ----------------
def generate_pdf(text):
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(f.name)
    styles = getSampleStyleSheet()

    elements = []
    for line in text.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1,10))

    doc.build(elements)
    return f.name

# ---------------- MAIN ----------------
if file:
    data = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
        ["📊 Overview","📈 Charts","🧠 AI","🤖 Chat","💡 Ideas","💰 Profit","🧠 Decision","📈 Forecast"]
    )

    # ---------- OVERVIEW ----------
    with tab1:
        st.metric("Rows", data.shape[0])
        st.metric("Columns", data.shape[1])
        st.metric("Missing", data.isnull().sum().sum())

        st.markdown("### 🧠 Auto Insights")

        if st.button("Generate Insights"):
            if can_call():
                st.session_state.last_call = time.time()

                with st.spinner("Analyzing..."):
                    output = safe_ai_call([
                        {"role":"system","content":SYSTEM_PROMPT},
                        {"role":"user","content":data.head(20).to_string()}
                    ])
                st.success(output)
            else:
                st.warning("⏳ Please wait before next request")

    # ---------- CHARTS ----------
    with tab2:
        num = data.select_dtypes(include=['int64','float64']).columns

        if len(num) > 1:
            x = st.selectbox("X", num)
            y = st.selectbox("Y", num)

            fig = px.scatter(data, x=x, y=y)
            st.plotly_chart(fig, use_container_width=True)

    # ---------- AI ----------
    with tab3:
        if st.button("Generate Insights (AI Tab)"):
            if can_call():
                st.session_state.last_call = time.time()

                output = safe_ai_call([
                    {"role":"system","content":SYSTEM_PROMPT},
                    {"role":"user","content":data.head(20).to_string()}
                ])
                st.write(output)
            else:
                st.warning("⏳ Wait a few seconds")

    # ---------- CHAT ----------
    with tab4:
        q = st.text_input("Ask anything")

        if q:
            if can_call():
                st.session_state.last_call = time.time()

                with st.spinner("Thinking..."):
                    output = safe_ai_call([
                        {"role":"system","content":SYSTEM_PROMPT},
                        {"role":"user","content":f"{data.head(20)}\n{q}"}
                    ])
                st.write(output)
            else:
                st.warning("⏳ Wait before next request")

    # ---------- IDEAS ----------
    with tab5:
        b = st.number_input("Budget")
        s = st.text_area("Skills")
        l = st.text_input("Location")

        if st.button("Generate Ideas"):
            if can_call():
                st.session_state.last_call = time.time()

                output = safe_ai_call([
                    {"role":"system","content":SYSTEM_PROMPT},
                    {"role":"user","content":f"{b},{s},{l}"}
                ])
                st.write(output)

                pdf = generate_pdf(output)
                with open(pdf,"rb") as f:
                    st.download_button("Download PDF", f)
            else:
                st.warning("⏳ Wait before next request")

    # ---------- PROFIT ----------
    with tab6:
        inv = st.number_input("Investment")
        rev = st.number_input("Revenue")
        cost = st.number_input("Cost")

        if st.button("Calculate"):
            profit = rev - cost
            if profit > 0:
                st.success(f"Profit ₹{profit}")
                st.info(f"Break-even {inv/profit:.1f} months")
            else:
                st.error("No profit")

    # ---------- DECISION ----------
    with tab7:
        decision_q = st.text_input("Should I invest?")

        if decision_q:
            if can_call():
                st.session_state.last_call = time.time()

                output = safe_ai_call([
                    {"role":"system","content":SYSTEM_PROMPT},
                    {"role":"user","content":decision_q}
                ])
                st.success(output)
            else:
                st.warning("⏳ Wait before next request")

    # ---------- FORECAST ----------
    with tab8:
        num_cols = data.select_dtypes(include=['int64','float64']).columns

        if len(num_cols) > 0:
            col = st.selectbox("Select Column", num_cols)
            values = data[col].dropna()

            if len(values) > 2:
                trend = values.iloc[-1] - values.iloc[0]

                if trend > 0:
                    st.success("📈 Upward trend detected")
                else:
                    st.warning("📉 Downward trend detected")
