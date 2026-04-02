import streamlit as st
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

st.title("🤖 Adviso AI")

uploaded_file = st.file_uploader("Upload Excel or CSV", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.dataframe(data.head())

    question = st.text_input("Ask about your data")

    if question:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": question}]
        )

        st.write(response.choices[0].message.content)
