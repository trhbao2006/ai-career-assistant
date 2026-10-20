import re
import unicodedata
from dataclasses import dataclass
from typing import Optional


"""CLEAN TEXT"""
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


if __name__ == "__main__":
    dirty_sample = "  Họ và tên:\xa0\xa0Trần Văn A \u200b\r\n\r\n\r\n\uf0b7 Kỹ năng: Proﬁcient in   Python\t\t& C++   "
    cleaned = clean_raw_text(dirty_sample)
    print(repr(cleaned))


