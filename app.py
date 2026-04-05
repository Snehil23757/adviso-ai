import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

# ---------------- LOADING ----------------
if "loaded" not in st.session_state:
    with st.spinner("🚀 Loading Adviso AI..."):
        time.sleep(1.5)
    st.session_state.loaded = True

# ---------------- SAFE UI FIX ----------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: radial-gradient(circle at top, #0f172a, #020617);
}

/* Main text */
.block-container {
    color: #ffffff;
}

/* Sidebar FIX */
section[data-testid="stSidebar"] {
    background-color: #020617;
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* File uploader FIX */
[data-testid="stFileUploader"] * {
    color: #ffffff !important;
}

/* Labels */
label {
    color: #e2e8f0 !important;
}

/* Inputs */
input, textarea {
    color: #ffffff !important;
    background-color: rgba(255,255,255,0.05) !important;
}

/* Dropdown */
div[data-baseweb="select"] * {
    color: #ffffff !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #ffffff !important;
}

/* Buttons */
.stButton>button {
    border-radius: 12px;
    background: linear-gradient(90deg, #6366f1, #3b82f6);
    color: white;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.05);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.08);
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LANDING ----------------
if "visited" not in st.session_state:
    st.session_state.visited = False

if not st.session_state.visited:
    st.markdown("<h1 style='text-align:center;'>Adviso AI 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>AI Business Intelligence Platform</p>", unsafe_allow_html=True)

    if st.button("Get Started"):
        st.session_state.visited = True
        st.rerun()

    st.stop()

# ---------------- LOGIN ----------------
users = {"admin": "1234"}

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
    st.sidebar.success("Premium User")
else:
    if st.sidebar.button("Upgrade ₹199"):
        st.session_state.premium = True

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align:center;'>Adviso AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Turning data into decisions</p>", unsafe_allow_html=True)

# ---------------- FILE ----------------
file = st.sidebar.file_uploader("Upload Data", type=["csv","xlsx"])

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

    # ---------- OVERVIEW ----------
    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'>Rows<br><h2>{data.shape[0]}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'>Columns<br><h2>{data.shape[1]}</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'>Missing<br><h2>{data.isnull().sum().sum()}</h2></div>", unsafe_allow_html=True)

    # ---------- CHARTS ----------
    with tab2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        chart = st.selectbox("Chart", ["Scatter","Bar","Line","Histogram"])
        num = data.select_dtypes(include=['int64','float64']).columns

        if len(num) > 1:
            x = st.selectbox("X", num)
            y = st.selectbox("Y", num)

            with st.spinner("Rendering chart..."):
                time.sleep(1)

            if chart == "Scatter":
                fig = px.scatter(data, x=x, y=y, color=y, template="plotly_dark")
            elif chart == "Bar":
                fig = px.bar(data, x=x, y=y, template="plotly_dark")
            elif chart == "Line":
                fig = px.line(data, x=x, y=y, template="plotly_dark")
            else:
                fig = px.histogram(data, x=x, template="plotly_dark")

            st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- AI ----------
    with tab3:
        if st.button("Generate Insights"):
            if not st.session_state.premium:
                st.warning("Upgrade required 🚀")
            else:
                with st.spinner("AI thinking..."):
                    time.sleep(1.5)
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role":"user","content":data.head().to_string()}]
                    )
                st.write(res.choices[0].message.content)

    # ---------- CHAT ----------
    with tab4:
        q = st.text_input("Ask anything")

        if q:
            if not st.session_state.premium:
                st.warning("Upgrade required 🚀")
            else:
                with st.spinner("Thinking..."):
                    time.sleep(1.5)
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role":"user","content":q}]
                    )
                st.write(res.choices[0].message.content)

    # ---------- IDEAS ----------
    with tab5:
        b = st.number_input("Budget")
        s = st.text_area("Skills")
        l = st.text_input("Location")

        if st.button("Generate Ideas"):
            if not st.session_state.premium:
                st.warning("Upgrade required 🚀")
            else:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":f"{b},{s},{l}"}]
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
            if profit > 0:
                st.success(f"Profit ₹{profit}")
                st.info(f"Break-even {inv/profit:.1f} months")
            else:
                st.error("No profit")
