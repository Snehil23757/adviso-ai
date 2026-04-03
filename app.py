import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# Load API key securely
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(page_title="Adviso AI", layout="centered")

# Title
st.title("🤖 Adviso AI")
st.markdown("### 📊 Upload your data & get smart AI insights")

# File upload
uploaded_file = st.file_uploader("Upload Excel or CSV", type=["csv", "xlsx"])

data = None

# Read file
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        st.success("✅ File uploaded successfully")

        # Show preview
        st.subheader("📄 Data Preview")
        st.dataframe(data.head())

    except Exception as e:
        st.error(f"Error reading file: {e}")

# Chat section
st.subheader("💬 Ask Questions About Your Data")

question = st.chat_input("Type your question here...")

if question:
    if data is None:
        st.warning("⚠️ Please upload a file first")
    else:
        try:
            # Create context from data
            context = f"""
            You are a business data analyst.
            Analyze the following dataset preview and answer clearly:

            {data.head().to_string()}
            """

            # API call
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful business analyst."},
                    {"role": "user", "content": context + "\n\nQuestion: " + question}
                ]
            )

            answer = response.choices[0].message.content

            # Display chat
            st.chat_message("user").write(question)
            st.chat_message("assistant").write(answer)

        except Exception as e:
            st.error(f"❌ Error: {e}")
