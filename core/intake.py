import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

from pathlib import Path
from typing import Union
import pymupdf

"""TASK 1: CLEAN TEXT"""
@dataclass
class IntakeResult: 
    """Kết quả sau khi upload CV"""
    is_valid: bool # trạng thái
    clean_text: str # nội dung "sạch"
    char_count: int
    page_count: int = 1
    error_message: Optional[str] = None # thông báo lỗi

def clean_raw_text(raw_text: str) -> str:
    text = raw_text
    if not text:
        return ""

    #Chuẩn hóa Unicode
    text = unicodedata.normalize('NFKC', text) 

    #Xóa các kí tự ẩn
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)

    #Chuẩn hóa dấu xuống dòng
    text = re.sub(r"\r\n|\r", "\n", text)

    #Loại bỏ kí tự rác
    text = re.sub(r"[\uf0b7•▪●]", "- ", text)

    #Thu gọn khoảng trắng từng dòng
    lines = []
    for line in text.split("\n"):
        #Nhiều ' ' hoặc tab -> 1 dấu ' ' 
        cleaned_line = re.sub(r'[ \t]+', ' ', line).strip()
        lines.append(cleaned_line)
    text = "\n".join(lines)

    #Thu gọn \n
    text = re.sub(r'\n{3,}', "\n\n", text)

    return text.strip()

"""TASK 2: """
def extract_cv(pdf_source: Union[str, Path, bytes]) -> IntakeResult:
    doc = None
    try:
        if isinstance(pdf_source, bytes):
            doc = pymupdf.open(stream=pdf_source, filetype="pdf")
        elif isinstance(pdf_source, (str, Path)):
            doc = pymupdf.open(str(pdf_source))
        else:
            raise TypeError(f"Định dạng nguồn không hỗ trợ: {type(pdf_source)}")

        if doc.page_count <= 0 or doc.page_count > 5 :
            return IntakeResult(
                is_valid=False,
                clean_text="",
                char_count=0,
                page_count=doc.page_count,
                error_message=f"Số trang không hợp lệ ({doc.page_count} trang). CV phải từ 1 đến 5 trang."
            )

        # Đọc nội dung từng trang
        raw_text_parts = []
        for page in doc:
            raw_text_parts.append(page.get_text("text", sort=True))
        raw_text = "".join(raw_text_parts)

        # Làm sạch
        cleaned = clean_raw_text(raw_text)

        if not cleaned:
            return IntakeResult(
                is_valid=False,
                clean_text="",
                char_count=0,
                page_count=doc.page_count,
                error_message="File PDF không chứa văn bản có thể trích xuất (có thể là file scan hoặc ảnh)"
            )

        return IntakeResult(
            is_valid=True,
            clean_text=cleaned,
            char_count=len(cleaned),
            page_count=doc.page_count
        )

    except FileNotFoundError:
        return IntakeResult(
            is_valid=False,
            clean_text="",
            char_count=0,
            page_count=0,
            error_message="Không tìm thấy file theo đường dẫn được cung cấp."
        )

    except pymupdf.FileDataError:
        return IntakeResult(
            is_valid=False,
            clean_text="",
            char_count=0,
            page_count=0,
            error_message="File PDF bị hỏng hoặc định dạng không hợp lệ"
        )

    except Exception as e:
        return IntakeResult(
            is_valid=False,
            clean_text="",
            char_count=0,
            page_count=0,
            error_message=f"Lỗi không xác định khi đọc PDF: {str(e)}"
        )
