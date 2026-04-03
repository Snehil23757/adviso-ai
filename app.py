import streamlit as st
import pandas as pd
from openai import OpenAI
import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #0f172a, #020617);
    color: white;
}
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
.kpi-card {
    background: linear-gradient(145deg, #1f2937, #111827);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🤖 Adviso AI")
uploaded_file = st.sidebar.file_uploader("Upload Data", type=["csv", "xlsx"])

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- LOAD DATA ----------------
data = None

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.sidebar.success("✅ Data uploaded")

# ---------------- TITLE ----------------
st.title("💬 Adviso AI Copilot")

# ---------------- AI INSIGHTS ----------------
if data is not None:
    with st.expander("🧠 AI Insights"):
        try:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Analyze:\n{data.head().to_string()}"}]
            )
            st.write(res.choices[0].message.content)
        except:
            st.warning("AI unavailable")

# ---------------- BASIC METRICS ----------------
if data is not None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", data.shape[0])
    c2.metric("Columns", data.shape[1])
    c3.metric("Missing", data.isnull().sum().sum())

# ---------------- KPI ----------------
if data is not None:
    st.markdown("## 📊 KPI Dashboard")

    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns

    selected = st.multiselect("Select KPIs", numeric_cols, default=list(numeric_cols[:3]))
    cols = st.columns(3)

    for i, col in enumerate(selected):
        values = data[col]
        total = int(values.sum())

        if len(values) > 2:
            change = values.iloc[-1] - values.iloc[-2]
            color = "#22c55e" if change > 0 else "#ef4444"
            arrow = "↑" if change > 0 else "↓"
        else:
            color = "#9ca3af"
            arrow = "-"

        with cols[i % 3]:
            st.markdown(f"""
            <div class="kpi-card">
                <h4>{col}</h4>
                <h1>{total:,}</h1>
                <p style="color:{color}">{arrow}</p>
            </div>
            """, unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
if data is not None:
    st.markdown("## 📊 Advanced Dashboard")

    df = data.copy()
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    cat_cols = df.select_dtypes(include=['object']).columns

    st.sidebar.markdown("### 🔍 Filters")

    if len(cat_cols) > 0:
        cat = st.sidebar.selectbox("Category", cat_cols)
        vals = st.sidebar.multiselect("Values", df[cat].unique())
        if vals:
            df = df[df[cat].isin(vals)]

    if len(num_cols) > 0:
        num = st.sidebar.selectbox("Numeric", num_cols)
        min_val, max_val = st.sidebar.slider(
            "Range",
            float(df[num].min()), float(df[num].max()),
            (float(df[num].min()), float(df[num].max()))
        )
        df = df[(df[num] >= min_val) & (df[num] <= max_val)]

    col1, col2 = st.columns(2)

    with col1:
        if len(num_cols) > 0:
            st.line_chart(df[num_cols[0]])

    with col2:
        if len(num_cols) > 1:
            st.bar_chart(df[num_cols[:2]])

# ---------------- CHARTS + ML ----------------
if data is not None:
    st.markdown("## 📊 Advanced Charts & ML")

    chart = st.selectbox("Chart Type",
        ["Bar", "Line", "Histogram", "Pie", "Linear Regression", "Logistic Regression"]
    )

    num_cols = data.select_dtypes(include=['int64', 'float64']).columns
    cat_cols = data.select_dtypes(include=['object']).columns

    if chart == "Bar":
        x, y = st.selectbox("X", num_cols), st.selectbox("Y", num_cols)
        st.bar_chart(data[[x, y]])

    elif chart == "Line":
        x, y = st.selectbox("X", num_cols), st.selectbox("Y", num_cols)
        st.line_chart(data[[x, y]])

    elif chart == "Histogram":
        col = st.selectbox("Column", num_cols)
        fig, ax = plt.subplots()
        ax.hist(data[col], bins=20)
        st.pyplot(fig)

    elif chart == "Pie":
        if len(cat_cols) > 0:
            col = st.selectbox("Category", cat_cols)
            counts = data[col].value_counts()
            fig, ax = plt.subplots()
            ax.pie(counts, labels=counts.index, autopct='%1.1f%%')
            st.pyplot(fig)

    elif chart == "Linear Regression":
        x_col = st.selectbox("X", num_cols)
        y_col = st.selectbox("Y", num_cols)

        x = data[x_col]
        y = data[y_col]

        coeffs = np.polyfit(x, y, 1)
        line = np.poly1d(coeffs)

        fig, ax = plt.subplots()
        ax.scatter(x, y)
        ax.plot(x, line(x))
        st.pyplot(fig)

    elif chart == "Logistic Regression":
        if len(num_cols) >= 2:
            X = data[[num_cols[0]]]
            y = (data[num_cols[1]] > data[num_cols[1]].median()).astype(int)

            model = LogisticRegression()
            model.fit(X, y)

            st.success("Model trained")
            st.write(model.predict(X[:10]))

# ---------------- CHAT ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.markdown(f"<div class='chat-{msg['role']}'>{msg['content']}</div>", unsafe_allow_html=True)

user = st.chat_input("Ask anything...")

if user:
    st.session_state.messages.append({"role": "user", "content": user})

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user}]
        )
        reply = res.choices[0].message.content
    except Exception as e:
        reply = str(e)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
    # ---------------- TIME SERIES FORECAST ----------------
if data is not None:
    st.markdown("## 🔮 Forecast Future Trends")

    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns

    if len(numeric_cols) > 0:
        col = st.selectbox("Select Column to Forecast", numeric_cols)

        values = data[col].values
        x = np.arange(len(values))

        coeffs = np.polyfit(x, values, 1)
        trend = np.poly1d(coeffs)

        future_x = np.arange(len(values), len(values) + 10)
        future_y = trend(future_x)

        fig, ax = plt.subplots()
        ax.plot(x, values, label="Actual")
        ax.plot(future_x, future_y, label="Forecast", linestyle='dashed')

        ax.legend()
        st.pyplot(fig)

        st.success("Future values predicted successfully 🚀")
        # ---------------- AI CHART RECOMMENDER ----------------
if data is not None:
    st.markdown("## 🤖 AI Chart Recommendation")

    try:
        columns_info = ", ".join(data.columns)

        prompt = f"""
        Based on dataset columns: {columns_info}
        Suggest best chart type (bar, line, pie, histogram)
        """

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        suggestion = res.choices[0].message.content
        st.info(f"💡 AI Suggestion: {suggestion}")

    except:
        st.warning("AI suggestion unavailable")
        # ---------------- DOWNLOAD CHART ----------------
import io

if data is not None:
    st.markdown("## 📄 Export Chart")

    if st.button("Download Last Chart"):
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        st.download_button(
            label="📥 Download Image",
            data=buf.getvalue(),
            file_name="chart.png",
            mime="image/png"
        )
        # -------- AI EXPLANATION --------
try:
    explanation_prompt = f"""
    Explain this regression:
    X = {x_col}
    Y = {y_col}
    Relationship observed.
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": explanation_prompt}]
    )

    st.markdown("### 🧠 AI Explanation")
    st.write(res.choices[0].message.content)

except:
    st.warning("AI explanation unavailable")
