import streamlit as st
import pandas as pd
from modules.parser import extract_data
from modules.exporter import to_excel

st.set_page_config(page_title="HTML → Excel Extractor", layout="centered")

st.title("HTML → Excel Extractor (Persona)")

uploaded_file = st.file_uploader("Upload file HTML", type=["html"])

if uploaded_file:
    html_content = uploaded_file.read().decode("utf-8")
    result = extract_data(html_content)

    st.subheader("Preview dữ liệu")
    st.json(result)

    df = pd.DataFrame(list(result.items()), columns=["Field", "Value"])

    st.subheader("Bảng dữ liệu")
    st.dataframe(df)

    excel_data = to_excel(df)

    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name="persona.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Upload file HTML để bắt đầu")
