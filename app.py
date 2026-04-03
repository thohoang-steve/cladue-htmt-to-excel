import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import io

st.set_page_config(page_title="HTML Extractor to Excel", layout="wide")

st.title("Trích xuất dữ liệu Customer Persona từ HTML sang Excel")
st.write("Tải lên file HTML chứa dữ liệu khách hàng (do Claude tạo ra) để tự động bóc tách thành bảng Excel.")

uploaded_file = st.file_uploader("Tải lên file HTML", type=['html', 'htm'])

def extract_text_or_value(element):
    """Hàm thông minh: Lấy dữ liệu từ value của thẻ input/textarea hoặc text nội bộ của thẻ HTML thường."""
    if not element:
        return ""
    # Nếu Claude giữ nguyên thẻ input, ưu tiên lấy thuộc tính value
    if element.name == 'input':
        return element.get('value', '').strip()
    # Nếu Claude giữ nguyên thẻ textarea
    if element.name == 'textarea':
        return element.text.strip() or element.get('value', '').strip()
    # Nếu Claude đã chuyển input thành thẻ chữ bình thường (div, span, p...)
    return element.text.strip()

if uploaded_file is not None:
    html_content = uploaded_file.read().decode('utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    
    data_records = []

    # 1. TRÍCH XUẤT KHỐI HEADER (Tên, Vai trò, Ngành, Quy mô)
    # Tìm Tên persona
    name_el = soup.find(id='p-name') or soup.find(class_='persona-name')
    if name_el:
        name_val = extract_text_or_value(name_el)
        if name_val:
            data_records.append({"Danh mục": "Thông tin chung", "Trường": "Tên khách hàng", "Nội dung": name_val})

    # Tìm các trường (f-item) trong header và nhân khẩu học
    for f_item in soup.find_all(class_='f-item'):
        label_el = f_item.find(class_='f-label')
        val_el = f_item.find(class_='f-val')
        if label_el and val_el:
            label = label_el.text.strip()
            val = extract_text_or_value(val_el)
            if val:
                data_records.append({"Danh mục": "Đặc điểm & Nhân khẩu học", "Trường": label, "Nội dung": val})

    # 2. TRÍCH XUẤT CÁC KHỐI GRID/CARD (Điểm đau, Mục tiêu, Insight, Hành trình...)
    cards = soup.find_all('div', class_='card')
    for card in cards:
        card_label_el = card.find(class_='card-label')
        if not card_label_el:
            continue
        
        # Dọn dẹp tên danh mục (xóa các ký tự icon)
        category = card_label_el.text.replace('!', '').replace('✓', '').replace('→', '').replace('★', '').replace('✗', '').strip()
        
        # A. Quét các dạng danh sách (list-item)
        list_items = card.find_all(class_='list-item')
        if list_items:
            items_content = []
            for li in list_items:
                bullet = li.find(class_='list-bullet')
                input_el = li.find('input', class_='list-input') or li.find(class_='list-input')
                
                if input_el:
                    val = extract_text_or_value(input_el)
                    if val: items_content.append(f"- {val}")
                else:
                    # Trường hợp Claude dùng text thường thay vì cấu trúc input
                    text_val = li.text
                    if bullet:
                        text_val = text_val.replace(bullet.text, '', 1) # Xóa text của bullet point bị dính vào
                    text_val = text_val.strip()
                    if text_val: items_content.append(f"- {text_val}")
            
            if items_content:
                data_records.append({"Danh mục": category, "Trường": "Danh sách chi tiết", "Nội dung": "\n".join(items_content)})
        
        # B. Quét các đoạn trích dẫn (quote-box / textarea)
        textarea = card.find('textarea', class_='quote-input') or card.find(class_='quote-input')
        if textarea:
            val = extract_text_or_value(textarea)
            if val:
                data_records.append({"Danh mục": category, "Trường": "Trích dẫn", "Nội dung": val})
        
        # C. Quét các thẻ Tag (Kênh thông tin, Từ khóa tìm kiếm)
        tags_wraps = card.find_all(class_='tag-input-wrap')
        if tags_wraps:
            for wrap in tags_wraps:
                prev_label = wrap.find_previous_sibling(class_='f-label')
                label = prev_label.text.strip() if prev_label else "Tags"
                tags = wrap.find_all(class_='tag')
                # Lấy text và xóa dấu 'x' đóng tag
                tag_list = [t.text.replace('×', '').strip() for t in tags]
                if tag_list:
                    data_records.append({"Danh mục": category, "Trường": label, "Nội dung": ", ".join(tag_list)})

        # D. Quét thanh điểm số (Score-item)
        scores = card.find_all(class_='score-item')
        if scores:
            score_contents = []
            for score in scores:
                s_name = score.find(class_='score-name')
                s_val = score.find(class_='score-val')
                if s_name and s_val:
                    score_contents.append(f"{s_name.text.strip()}: {s_val.text.strip()}/10")
            if score_contents:
                data_records.append({"Danh mục": category, "Trường": "Chỉ số đánh giá", "Nội dung": "\n".join(score_contents)})

    # --- HIỂN THỊ & XUẤT FILE EXCEL ---
    if data_records:
        df = pd.DataFrame(data_records)
        st.success(f"Đã trích xuất thành công {len(df)} dòng dữ liệu từ file HTML!")
        st.dataframe(df, use_container_width=True)

        # Định dạng file Excel tự động giãn dòng, chỉnh độ rộng cột
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Customer_Persona')
            worksheet = writer.sheets['Customer_Persona']
            worksheet.column_dimensions['A'].width = 30
            worksheet.column_dimensions['B'].width = 30
            worksheet.column_dimensions['C'].width = 80
            
            # Kích hoạt Wrap Text cho cột Nội dung
            for row in worksheet.iter_rows(min_row=2, max_col=3, max_row=len(df)+1):
                row[2].alignment = row[2].alignment.copy(wrapText=True)

        st.download_button(
            label="📥 Tải xuống file Excel",
            data=output.getvalue(),
            file_name="Customer_Persona_Extracted.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
    else:
        st.warning("Không tìm thấy dữ liệu hoặc cấu trúc HTML không khớp với Template. Hãy đảm bảo file bạn tải lên là file HTML chứa nội dung đã được Claude xuất ra.")
