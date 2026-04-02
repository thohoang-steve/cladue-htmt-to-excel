import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import io

st.set_page_config(page_title="HTML to Excel Converter", layout="centered")

st.title("Chuyển đổi Customer Persona HTML sang Excel")
st.write("Tải lên file HTML chứa thông tin khách hàng để xuất ra file Excel (.xlsx).")

uploaded_file = st.file_uploader("Chọn file HTML", type=['html', 'htm'])

def get_value(element):
    """Lấy giá trị từ thuộc tính 'value' hoặc nội dung text của thẻ"""
    if element:
        # Ưu tiên lấy value từ input, nếu không có thì lấy text
        return element.get('value', '').strip() or element.text.strip()
    return ""

def get_list_items(soup, container_id):
    """Lấy danh sách các giá trị từ các list-input trong một vùng cụ thể"""
    container = soup.find(id=container_id)
    if container:
        inputs = container.find_all('input', class_='list-input')
        values = [get_value(i) for i in inputs if get_value(i)]
        return "; ".join(values)
    return ""

if uploaded_file is not None:
    # Đọc nội dung file HTML
    html_content = uploaded_file.read().decode('utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')

    # Trích xuất dữ liệu
    data = {
        "Tên Khách Hàng": [get_value(soup.find(id='p-name'))],
        "Vai Trò": [get_value(soup.find(id='p-role'))],
        "Ngành": [get_value(soup.find(id='p-industry'))],
        "Quy Mô Công Ty": [get_value(soup.find(id='p-company'))],
        "Điểm Đau (Pain Points)": [get_list_items(soup, 'pains')],
        "Mục Tiêu & Kỳ Vọng": [get_list_items(soup, 'goals')],
        "Insight Sâu": [get_list_items(soup, 'insights')],
        "Thông Điệp Phù Hợp": [get_list_items(soup, 'messages')],
        "Rào Cản Chuyển Đổi": [get_list_items(soup, 'barriers')]
    }

    # Tạo DataFrame
    df = pd.DataFrame(data)
    
    st.subheader("Dữ liệu trích xuất:")
    st.dataframe(df)

    # Chuyển đổi DataFrame thành file Excel trong bộ nhớ tạm
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Persona')
    
    excel_data = output.getvalue()

    # Nút tải xuống
    st.download_button(
        label="Tải xuống file Excel 📥",
        data=excel_data,
        file_name="Customer_Persona.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
