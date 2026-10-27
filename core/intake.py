from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union
import re
import unicodedata
import pymupdf

"""TASK 1: CLEAN TEXT & EXTRACT PDF"""

@dataclass
class IntakeResult:
    """Kết quả sau khi upload CV"""
    is_valid: bool                      # Trạng thái hợp lệ
    clean_text: str                     # Nội dung "sạch"
    char_count: int                     # Số lượng ký tự
    page_count: int = 1                 # Số trang
    error_message: Optional[str] = None  # Thông báo lỗi nếu có


def clean_raw_text(raw_text: str) -> str:
    """Làm sạch và chuẩn hóa văn bản thô"""
    if not raw_text:
        return ""

    # 1. Chuẩn hóa Unicode NFKC
    text = unicodedata.normalize("NFKC", raw_text)

    # 2. Xóa các ký tự ẩn
    text = re.sub(r"[\u200b\u200c\u200d\ufeff\xa0]", " ", text)

    # 3. Chuẩn hóa dấu xuống dòng
    text = re.sub(r"\r\n|\r", "\n", text)

    # 4. Loại bỏ ký tự rác & icon đặc thù của TopCV/Canva
    text = re.sub(r"[\uf095\uf133\uf3c5\uf05a\uf0b7•▪●■◆*–]", "- ", text)

    # 5. Thu gọn khoảng trắng từng dòng
    lines = []
    for line in text.split("\n"):
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(cleaned_line)
    text = "\n".join(lines)

    # 6. Thu gọn nhiều dòng trống liên tiếp 
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Gọi hàm strip() có dấu ngoặc tròn
    return text.strip()


def extract_text_by_columns(doc: pymupdf.Document) -> str:
    """
    Trích xuất text theo từng cột độc lập (Block-based reading order),
    chống dính dòng ngang giữa 2 cột của layout TopCV.
    """
    full_text_pages = []

    for page in doc:
        # Lấy danh sách blocks: (x0, y0, x1, y1, text, block_no, block_type)
        blocks = page.get_text("blocks")
        # Chỉ lấy block văn bản (block_type == 0)
        text_blocks = [b for b in blocks if b[6] == 0 and b[4].strip()]

        if not text_blocks:
            continue

        # Trục chia 2 cột 
        page_width = page.rect.width
        split_x = page_width * 0.38

        left_col = [b for b in text_blocks if b[0] < split_x]
        right_col = [b for b in text_blocks if b[0] >= split_x]

        # Sắp xếp từng cột độc lập theo trục dọc (y0) từ trên xuống dưới
        left_col.sort(key=lambda b: b[1])
        right_col.sort(key=lambda b: b[1])

        # Đọc trọn vẹn cột trái rồi sang cột phải
        page_lines = []
        for b in left_col + right_col:
            for line in b[4].splitlines():
                line_str = line.strip()
                if line_str:
                    page_lines.append(line_str)

        full_text_pages.append("\n".join(page_lines))

    return "\n\n".join(full_text_pages)


def extract_cv(input_data: Union[str, Path, bytes]) -> IntakeResult:
    """
    Hàm đọc và tiền xử lý CV dạng PDF, hỗ trợ cả đường dẫn file lẫn bytes.
    """
    try:
        if isinstance(input_data, (str, Path)):
            doc = pymupdf.open(str(input_data))
        elif isinstance(input_data, bytes):
            doc = pymupdf.open(stream=input_data, filetype="pdf")
        else:
            return IntakeResult(
                is_valid=False,
                clean_text="",
                page_count=0,
                char_count=0,
                error_message="Định dạng đầu vào không hợp lệ.",
            )

        page_count = len(doc)

        # Kiểm tra số trang (1 - 5 trang)
        if page_count < 1 or page_count > 5:
            doc.close()
            return IntakeResult(
                is_valid=False,
                clean_text="",
                page_count=page_count,
                char_count=0,
                error_message=f"Số trang không hợp lệ ({page_count} trang). CV phải từ 1 đến 5 trang.",
            )

        # Trích xuất văn bản chống dính cột
        raw_text = extract_text_by_columns(doc)
        doc.close()

        clean_text = clean_raw_text(raw_text)
        char_count = len(clean_text)

        # Kiểm tra PDF ảnh scan hoặc file rỗng
        if char_count < 100:
            return IntakeResult(
                is_valid=False,
                clean_text="",
                page_count=page_count,
                char_count=char_count,
                error_message="PDF không chứa lớp văn bản hợp lệ (có thể là file scan hoặc ảnh).",
            )

        return IntakeResult(
            is_valid=True,
            clean_text=clean_text,
            page_count=page_count,
            char_count=char_count,
        )

    except Exception as e:
        return IntakeResult(
            is_valid=False,
            clean_text="",
            page_count=0,
            char_count=0,
            error_message=f"Lỗi khi đọc file PDF: {str(e)}",
        )