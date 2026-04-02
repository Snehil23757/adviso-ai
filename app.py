import streamlit as st
import pandas as pd
import openai

openai.api_key = "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"

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
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": question}]
        )

        st.write(response["choices"][0]["message"]["content"])
