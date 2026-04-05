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

# ---------------- LANDING PAGE ----------------
if "visited" not in st.session_state:
    st.session_state.visited = False

if not st.session_state.visited:
    st.markdown("<h1 style='text-align:center;'>Adviso AI 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Your AI Business Advisor</p>", unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.markdown("### 📊 Analyze Data")
    col2.markdown("### 💡 Business Ideas")
    col3.markdown("### 🤖 AI Assistant")

    if st.button("Get Started"):
        st.session_state.visited = True
        st.rerun()

    st.stop()

# ---------------- LOGIN SYSTEM ----------------
users = {"admin": "1234", "user": "abcd"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to Adviso AI")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ---------------- PREMIUM ----------------
if "premium" not in st.session_state:
    st.session_state.premium = False

st.sidebar.markdown("## 💎 Plan")

if not st.session_state.premium:
    if st.sidebar.button("Upgrade ₹199"):
        st.session_state.premium = True
        st.sidebar.success("Premium Activated 🚀")
else:
    st.sidebar.success("Premium User ✅")

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp { background-color: #0a0a0a; color: #f5f5f7; }
.block-container { padding: 2rem 3rem; max-width: 1400px; margin: auto; }
.title { font-size: 40px; text-align: center; }
.subtitle { text-align: center; color: #9ca3af; margin-bottom: 40px; }
.kpi { background: #111; padding: 20px; border-radius: 16px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>Adviso AI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Turning data into decisions</div>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- SIDEBAR ----------------
uploaded_file = st.sidebar.file_uploader("Upload CSV/XLSX", type=["csv", "xlsx"])

# ---------------- OPENAI ----------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- LOAD DATA ----------------
data = None
if uploaded_file:
    data = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

# ---------------- PDF ----------------
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

# ---------------- MAIN APP ----------------
if data is None:
    st.info("Upload your dataset to begin")
else:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["📊 Overview", "📈 Charts", "🧠 AI", "🤖 Chat", "💡 Ideas", "💰 Profit"]
    )

    # ---------- OVERVIEW ----------
    with tab1:
        st.metric("Rows", data.shape[0])
        st.metric("Columns", data.shape[1])
        st.metric("Missing", data.isnull().sum().sum())

    # ---------- CHARTS ----------
    with tab2:
        chart_type = st.selectbox("Chart", ["Bar", "Line", "Histogram"])

        num_cols = data.select_dtypes(include=['int64','float64']).columns

        if len(num_cols) > 1:
            x = st.selectbox("X", num_cols)
            y = st.selectbox("Y", num_cols)

            if chart_type == "Bar":
                st.bar_chart(data[[x,y]])
            elif chart_type == "Line":
                st.line_chart(data[[x,y]])
            else:
                fig, ax = plt.subplots()
                ax.hist(data[x])
                st.pyplot(fig)

    # ---------- AI ----------
    with tab3:
        if st.button("Generate Insights"):
            if not st.session_state.premium:
                st.warning("Upgrade to Premium 🚀")
            else:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":data.head().to_string()}]
                )
                st.write(res.choices[0].message.content)

    # ---------- CHAT ----------
    with tab4:
        user_input = st.text_input("Ask something")

        if user_input:
            if not st.session_state.premium:
                st.warning("Upgrade to Premium 🚀")
            else:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":user_input}]
                )
                st.write(res.choices[0].message.content)

    # ---------- BUSINESS IDEAS ----------
    with tab5:
        budget = st.number_input("Budget ₹")
        skills = st.text_area("Skills")
        location = st.text_input("Location")

        if st.button("Get Ideas"):
            if not st.session_state.premium:
                st.warning("Upgrade to Premium 🚀")
            else:
                prompt = f"Suggest business ideas for ₹{budget}, skills: {skills}, location: {location}"
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt}]
                )

                output = res.choices[0].message.content
                st.write(output)

                pdf = generate_pdf(output)
                with open(pdf, "rb") as f:
                    st.download_button("Download Report", f, file_name="report.pdf")

    # ---------- PROFIT ----------
    with tab6:
        invest = st.number_input("Investment")
        revenue = st.number_input("Revenue")
        cost = st.number_input("Cost")

        if st.button("Calculate"):
            profit = revenue - cost
            if profit > 0:
                st.success(f"Profit: ₹{profit}")
                st.info(f"Break-even: {invest/profit:.1f} months")
            else:
                st.error("No profit")
