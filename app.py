# streamlit_app.py
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup

st.set_page_config(page_title="HTML → Excel Extractor", layout="centered")

st.title("HTML → Excel Extractor (Persona)")

uploaded_file = st.file_uploader("Upload file HTML", type=["html"])


def extract_data(html):
    soup = BeautifulSoup(html, "html.parser")

    def get_values(selector):
        return [el.get("value") or el.text for el in soup.select(selector) if (el.get("value") or el.text).strip()]

    data = {
        "Name": soup.select_one("#p-name").get("value") if soup.select_one("#p-name") else "",
        "Role": soup.select_one("#p-role").get("value") if soup.select_one("#p-role") else "",
        "Pains": "; ".join(get_values("#pains .li-in")),
        "Goals": "; ".join(get_values("#goals .li-in")),
        "Insights": "; ".join(get_values("#insights .li-in")),
        "Solutions": "; ".join(get_values("#solutions .li-in")),
        "Messages": "; ".join(get_values("#messages .li-in")),
    }

    return data


if uploaded_file:
    html_content = uploaded_file.read().decode("utf-8")
    result = extract_data(html_content)

    st.subheader("Preview dữ liệu")
    st.json(result)

    df = pd.DataFrame(list(result.items()), columns=["Field", "Value"])

    st.subheader("Bảng dữ liệu")
    st.dataframe(df)

    # Export Excel
    def to_excel(df):
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Persona')
        return output.getvalue()

    excel_data = to_excel(df)

    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name="persona.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Upload file HTML để bắt đầu")


# Hướng dẫn chạy:
# pip install streamlit pandas beautifulsoup4 xlsxwriter
# streamlit run streamlit_app.py
