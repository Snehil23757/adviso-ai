import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# ---------------- LOGIN SYSTEM ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

st.sidebar.title("🔐 Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if username != "admin" or password != "1234":
    st.warning("Please login to continue")
    st.stop()

# ---------------- API SETUP ----------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- UI DESIGN ----------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 Adviso AI")
st.markdown("### 📊 Smart Business Insights Platform")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload Excel or CSV", type=["csv", "xlsx"])

data = None

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        st.success("✅ File uploaded successfully")

        # Preview
        st.subheader("📄 Data Preview")
        st.dataframe(data.head())

        # ---------------- CHARTS ----------------
        st.subheader("📊 Data Visualization")

        numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns

        if len(numeric_cols) >= 2:
            col1 = st.selectbox("Select X-axis", numeric_cols)
            col2 = st.selectbox("Select Y-axis", numeric_cols)

            st.line_chart(data[[col1, col2]])

    except Exception as e:
        st.error(f"Error: {e}")

# ---------------- AUTO AI INSIGHTS ----------------
if data is not None:
    st.subheader("🧠 AI Auto Insights")

    if st.button("Generate Insights"):
        try:
            context = f"Analyze this dataset:\n{data.head().to_string()}"

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a business analyst."},
                    {"role": "user", "content": context}
                ]
            )

            st.success(response.choices[0].message.content)

        except Exception as e:
            st.error(f"AI Error: {e}")

# ---------------- CHATBOT ----------------
st.subheader("💬 Ask Questions")

question = st.chat_input("Ask anything about your data...")

if question and data is not None:
    try:
        context = f"Dataset:\n{data.head().to_string()}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": context + "\n" + question}
            ]
        )

        st.chat_message("user").write(question)
        st.chat_message("assistant").write(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Error: {e}")
