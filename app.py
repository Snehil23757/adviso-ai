import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp { background-color: #0a0a0a; color: #f5f5f7; }

.block-container {
    padding: 2rem 3rem;
    max-width: 1400px;
    margin: auto;
}

.title { font-size: 40px; font-weight: 700; text-align: center; }
.subtitle { text-align: center; color: #9ca3af; margin-bottom: 40px; }

.kpi {
    background: #111;
    padding: 20px;
    border-radius: 16px;
    text-align: center;
}

section[data-testid="stSidebar"] {
    background-color: #050505;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<div class='title'>Adviso AI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Turning data into decisions</div>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 📁 Upload Data")
uploaded_file = st.sidebar.file_uploader("", type=["csv", "xlsx"])

# ---------------- OPENAI ----------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- LOAD DATA ----------------
data = None
if uploaded_file:
    data = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

# ---------------- EMPTY ----------------
if data is None:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h3 style='text-align:center;margin-top:80px;'>Upload your data to begin</h3>", unsafe_allow_html=True)

# ---------------- PDF FUNCTION ----------------
def generate_pdf(content):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(temp_file.name)
    styles = getSampleStyleSheet()

    elements = []
    for line in content.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    return temp_file.name

# ---------------- TABS ----------------
if data is not None:

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["📊 Overview", "📈 Charts", "🧠 AI Insights", "🤖 Chat", "💡 Business Ideas", "💰 Profit"]
    )

    # ---------- OVERVIEW ----------
    with tab1:
        st.markdown("## Overview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", data.shape[0])
        c2.metric("Columns", data.shape[1])
        c3.metric("Missing", data.isnull().sum().sum())

        numeric_cols = data.select_dtypes(include=['int64','float64']).columns
        cols = st.columns(3)

        for i, col in enumerate(numeric_cols[:3]):
            with cols[i]:
                st.markdown(f"<div class='kpi'><h4>{col}</h4><h2>{int(data[col].sum()):,}</h2></div>", unsafe_allow_html=True)

    # ---------- CHARTS ----------
    with tab2:
        st.markdown("## Charts")
        chart_type = st.selectbox("Select Chart", ["Bar","Line","Histogram","Pie"])

        num_cols = data.select_dtypes(include=['int64','float64']).columns
        cat_cols = data.select_dtypes(include=['object']).columns

        if chart_type in ["Bar","Line"]:
            x = st.selectbox("X", num_cols)
            y = st.selectbox("Y", num_cols)
            st.bar_chart(data[[x,y]]) if chart_type=="Bar" else st.line_chart(data[[x,y]])

        elif chart_type=="Histogram":
            col = st.selectbox("Column", num_cols)
            fig, ax = plt.subplots()
            ax.hist(data[col], bins=20)
            st.pyplot(fig)

        elif chart_type=="Pie" and len(cat_cols)>0:
            col = st.selectbox("Category", cat_cols)
            counts = data[col].value_counts()
            fig, ax = plt.subplots()
            ax.pie(counts, labels=counts.index, autopct='%1.1f%%')
            st.pyplot(fig)

    # ---------- AI INSIGHTS ----------
    with tab3:
        st.markdown("## AI Insights")

        if st.button("Generate Insights"):
            try:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "user",
                        "content": f"Analyze this dataset:\n{data.head().to_string()}"
                    }]
                )
                st.success(res.choices[0].message.content)
            except:
                st.warning("⚠️ AI unavailable")

    # ---------- CHAT ----------
    with tab4:
        st.markdown("## 🤖 Assistant")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_input = st.chat_input("Ask anything...")

        if user_input:
            st.session_state.messages.append({"role":"user","content":user_input})

            try:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":user_input}]
                )
                reply = res.choices[0].message.content
            except:
                reply = "⚠️ AI unavailable"

            st.session_state.messages.append({"role":"assistant","content":reply})
            st.rerun()

    # ---------- BUSINESS IDEAS ----------
    with tab5:
        st.markdown("## 💡 Business Recommendation Engine")

        col1, col2 = st.columns(2)

        with col1:
            budget = st.number_input("💰 Budget (₹)", min_value=1000)
            risk = st.selectbox("Risk Level", ["Low","Medium","High"])

        with col2:
            skills = st.text_area("Skills")
            location = st.text_input("Location")

        if st.button("Get Business Ideas"):

            prompt = f"""
            You are a startup advisor.

            Budget: ₹{budget}
            Skills: {skills}
            Risk: {risk}
            Location: {location}

            Suggest 5 realistic business ideas in India with:
            - Profit
            - Investment
            - Difficulty
            """

            try:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt}]
                )

                output = res.choices[0].message.content

                st.success(output)

                if st.button("Download PDF"):
                    pdf = generate_pdf(output)
                    with open(pdf, "rb") as f:
                        st.download_button("Download Report", f, file_name="report.pdf")

            except:
                st.error("⚠️ AI unavailable")

    # ---------- PROFIT CALCULATOR ----------
    with tab6:
        st.markdown("## 💰 Profit Calculator")

        investment = st.number_input("Investment (₹)", min_value=1000)
        revenue = st.number_input("Monthly Revenue (₹)", min_value=0)
        cost = st.number_input("Monthly Cost (₹)", min_value=0)

        if st.button("Calculate"):

            profit = revenue - cost

            if profit > 0:
                breakeven = investment / profit
                roi = (profit * 12 / investment) * 100

                st.success(f"Profit: ₹{profit}")
                st.info(f"Break-even: {breakeven:.1f} months")
                st.info(f"ROI: {roi:.1f}%")
            else:
                st.error("No profit")
