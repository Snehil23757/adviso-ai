import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from openai import OpenAI

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

# ---------------- CLEAN UI ----------------
st.markdown("""
<style>
.stApp {
    background-color: #0a0a0a;
    color: #f5f5f7;
}

.main > div {
    max-width: 900px;
    margin: auto;
}

.block-container {
    padding-top: 2rem;
}

.title {
    font-size: 34px;
    font-weight: 600;
    text-align: center;
}

.subtitle {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 30px;
}

.kpi {
    background: #111;
    padding: 20px;
    border-radius: 16px;
}

section[data-testid="stSidebar"] {
    background-color: #050505;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<div class='title'>Adviso AI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Turning data into decisions</div>", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 📁 Upload Data")
uploaded_file = st.sidebar.file_uploader("", type=["csv", "xlsx"])

# ---------------- OPENAI ----------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- LOAD DATA ----------------
data = None
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

# ---------------- EMPTY STATE ----------------
if data is None:
    st.markdown("<h3 style='text-align:center;margin-top:80px;'>Upload your data to begin</h3>", unsafe_allow_html=True)

# ---------------- OVERVIEW ----------------
if data is not None:
    st.markdown("## Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", data.shape[0])
    c2.metric("Columns", data.shape[1])
    c3.metric("Missing", data.isnull().sum().sum())

# ---------------- FILTERS ----------------
if data is not None:
    st.markdown("## Filters")

    df = data.copy()
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    cat_cols = df.select_dtypes(include=['object']).columns

    if len(cat_cols) > 0:
        cat = st.selectbox("Category Filter", cat_cols)
        val = st.multiselect("Values", df[cat].unique())
        if val:
            df = df[df[cat].isin(val)]

# ---------------- KPI ----------------
if data is not None:
    st.markdown("## Key Metrics")

    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns
    cols = st.columns(3)

    for i, col in enumerate(numeric_cols[:3]):
        with cols[i]:
            st.markdown(f"<div class='kpi'><h4>{col}</h4><h2>{int(data[col].sum()):,}</h2></div>", unsafe_allow_html=True)

# ---------------- CHARTS ----------------
if data is not None:
    st.markdown("## Charts")

    chart_type = st.selectbox("Select Chart", ["Bar", "Line", "Histogram", "Pie"])

    num_cols = data.select_dtypes(include=['int64', 'float64']).columns
    cat_cols = data.select_dtypes(include=['object']).columns

    if chart_type in ["Bar", "Line"]:
        x = st.selectbox("X", num_cols)
        y = st.selectbox("Y", num_cols)

        if chart_type == "Bar":
            st.bar_chart(data[[x, y]])
        else:
            st.line_chart(data[[x, y]])

    elif chart_type == "Histogram":
        col = st.selectbox("Column", num_cols)
        fig, ax = plt.subplots()
        ax.hist(data[col], bins=20)
        st.pyplot(fig)

    elif chart_type == "Pie" and len(cat_cols) > 0:
        col = st.selectbox("Category", cat_cols)
        counts = data[col].value_counts()
        fig, ax = plt.subplots()
        ax.pie(counts, labels=counts.index, autopct='%1.1f%%')
        st.pyplot(fig)

# ---------------- LINEAR REGRESSION ----------------
if data is not None:
    st.markdown("## Linear Regression")

    num_cols = data.select_dtypes(include=['int64', 'float64']).columns

    if len(num_cols) >= 2:
        x_col = st.selectbox("X Variable", num_cols)
        y_col = st.selectbox("Y Variable", num_cols)

        x = data[x_col]
        y = data[y_col]

        coeff = np.polyfit(x, y, 1)
        line = np.poly1d(coeff)

        fig, ax = plt.subplots()
        ax.scatter(x, y)
        ax.plot(x, line(x))
        st.pyplot(fig)

# ---------------- LOGISTIC REGRESSION ----------------
if data is not None:
    st.markdown("## Logistic Regression")

    num_cols = data.select_dtypes(include=['int64', 'float64']).columns

    if len(num_cols) >= 2:
        X = data[[num_cols[0]]]
        y = (data[num_cols[1]] > data[num_cols[1]].median()).astype(int)

        model = LogisticRegression()
        model.fit(X, y)

        st.success("Model trained successfully")

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
st.markdown("## 🤖 Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

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
