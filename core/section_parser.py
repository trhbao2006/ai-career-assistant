import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field

"""TASK 3: Phân tách nội dung CV thành từng section"""

# Các section chuẩn hóa
SECTION_NAMES = [
    "contact",
    "summary",
    "education",
    "skills",
    "experience",
    "projects",
    "others",
]

# Từ điển Regex cho từng Section (song ngữ Anh - Việt)
# Dùng ^\s*(...)\s*$ kèm cờ re.IGNORECASE để chỉ khớp khi tiêu đề chiếm trọn một dòng ngắn
SECTION_PATTERNS: Dict[str, re.Pattern] = {
    "summary": re.compile(
        r"^\s*(profile\s+summary|profile|about\s+me|summary|objective|tóm\s+tắt|mục\s+tiêu)\s*[:\-\s]*$",
        re.IGNORECASE,
    ),
    "education": re.compile(
        r"^\s*(education|academic|học\s+vấn|bằng\s+cấp|trình\s+độ\s+học\s+vấn)\s*[:\-\s]*$",
        re.IGNORECASE,
    ),
    "skills": re.compile(
        r"^\s*(technical\s+skills|skills|technologies|kỹ\s+năng|chuyên\s+môn)\s*[:\-\s]*$",
        re.IGNORECASE,
    ),
    "experience": re.compile(
        r"^\s*(work\s+experience|professional\s+experience|experience|employment|kinh\s+nghiệm(\s+làm\s+việc)?)\s*[:\-\s]*$",
        re.IGNORECASE,
    ),
    "projects": re.compile(
        r"^\s*(projects|personal\s+projects|academic\s+projects|dự\s+án|đồ\s+án|dự\s+án\s+cá\s+nhân)\s*[:\-\s]*$",
        re.IGNORECASE,
    ),
}

def detect_section_header(line: str) -> Optional[str]:
    #Kiểm tra xem một dòng có phải là tiêu đề section hay không
    clean_line = line.strip()

    #line rỗng hoặc vượt 40 kí tự
    if len(clean_line) == 0 or len(clean_line) > 40:
        return None

    #Bỏ qua line có kết thúc bằng '.'
    if clean_line.endswith('.'):
        return None

    #Kiểm tra với pattern
    for sec_name, pattern in SECTION_PATTERNS.items():
        if pattern.match(clean_line):
            return sec_name

    return None

# Thực hiện phân tách
def parse_cv_sections(clean_text: str) -> Dict[str, str]:
    sections = {name: [] for name in SECTION_NAMES}
    current_section = "contact"

    for line in clean_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        header = detect_section_header(line)
        if header is not None:  
            current_section = header
        else:
            sections[current_section].append(line) 

    parser = {
        sec: "\n".join(lines).strip() 
        for sec, lines in sections.items() 
        if lines
    }
    return parser
