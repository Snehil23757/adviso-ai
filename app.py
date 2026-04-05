import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

# ---------------- UI (STEP 1) ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: #e2e8f0;
}

.block-container {
    padding: 2rem 4rem;
    max-width: 1400px;
    margin: auto;
}

.title {
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #38bdf8, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 40px;
}

.card {
    background: rgba(255,255,255,0.05);
    padding: 25px;
    border-radius: 18px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    transition: 0.3s;
}

.card:hover {
    transform: translateY(-5px);
}

section[data-testid="stSidebar"] {
    background: #020617;
}

.stButton>button {
    border-radius: 10px;
    background: linear-gradient(90deg, #6366f1, #3b82f6);
    color: white;
    border: none;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LANDING ----------------
if "visited" not in st.session_state:
    st.session_state.visited = False

if not st.session_state.visited:
    st.markdown("<div class='title'>Adviso AI 🚀</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>AI-powered Business Intelligence Platform</div>", unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.markdown("### 📊 Analyze Data")
    col2.markdown("### 💡 Business Ideas")
    col3.markdown("### 🤖 AI Assistant")

    if st.button("Get Started"):
        st.session_state.visited = True
        st.rerun()

    st.stop()

# ---------------- LOGIN ----------------
users = {"admin": "1234", "user": "abcd"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in users and users[u] == p:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# ---------------- PREMIUM ----------------
if "premium" not in st.session_state:
    st.session_state.premium = False

st.sidebar.markdown("## 💎 Plan")

if st.session_state.premium:
    st.sidebar.markdown("### 💎 Premium User")
else:
    st.sidebar.markdown("### 🆓 Free Plan")
    if st.sidebar.button("Upgrade ₹199"):
        st.session_state.premium = True

# ---------------- HEADER (STEP 2) ----------------
st.markdown("<div class='title'>Adviso AI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Turning data into decisions</div>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- FILE ----------------
file = st.sidebar.file_uploader("Upload Data", type=["csv","xlsx"])

# ---------------- OPENAI ----------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["📊 Overview","📈 Charts","🧠 AI","🤖 Chat","💡 Ideas","💰 Profit"]
    )

    # ---------- OVERVIEW (STEP 3) ----------
    with tab1:
        c1, c2, c3 = st.columns(3)

        c1.markdown(f"<div class='card'>📊 Rows<br><h2>{data.shape[0]}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'>📁 Columns<br><h2>{data.shape[1]}</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'>⚠️ Missing<br><h2>{data.isnull().sum().sum()}</h2></div>", unsafe_allow_html=True)

    # ---------- CHARTS (STEP 4) ----------
    with tab2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        chart = st.selectbox("Chart", ["Bar","Line","Histogram"])
        num = data.select_dtypes(include=['int64','float64']).columns

        if len(num)>1:
            x = st.selectbox("X", num)
            y = st.selectbox("Y", num)

            if chart=="Bar":
                st.bar_chart(data[[x,y]])
            elif chart=="Line":
                st.line_chart(data[[x,y]])
            else:
                fig, ax = plt.subplots()
                ax.hist(data[x])
                st.pyplot(fig)

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- AI ----------
    with tab3:
        if st.button("Generate Insights"):
            if not st.session_state.premium:
                st.warning("Upgrade required 🚀")
            else:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":data.head().to_string()}]
                )
                st.write(res.choices[0].message.content)

    # ---------- CHAT (STEP 5) ----------
    with tab4:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        user_input = st.text_input("Ask anything...")

        if user_input:
            if not st.session_state.premium:
                st.warning("Upgrade required 🚀")
            else:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":user_input}]
                )
                st.write(res.choices[0].message.content)

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- IDEAS ----------
    with tab5:
        budget = st.number_input("Budget")
        skills = st.text_area("Skills")
        loc = st.text_input("Location")

        if st.button("Generate Ideas"):
            if not st.session_state.premium:
                st.warning("Upgrade required 🚀")
            else:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":f"Business ideas for {budget}, {skills}, {loc}"}]
                )
                out = res.choices[0].message.content
                st.write(out)

                pdf = generate_pdf(out)
                with open(pdf,"rb") as f:
                    st.download_button("Download PDF", f)

    # ---------- PROFIT ----------
    with tab6:
        inv = st.number_input("Investment")
        rev = st.number_input("Revenue")
        cost = st.number_input("Cost")

        if st.button("Calculate"):
            profit = rev - cost
            if profit>0:
                st.success(f"Profit ₹{profit}")
                st.info(f"Break-even {inv/profit:.1f} months")
            else:
                st.error("No profit")
