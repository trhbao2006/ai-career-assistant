import re
from typing import Dict, Optional

"""TASK 3: Phân tách nội dung CV thành từng section (Xử lý cả PDF TopCV vỡ font)"""

SECTION_NAMES = [
    "contact",
    "summary",
    "education",
    "skills",
    "experience",
    "projects",
    "others",
]

# Bộ từ khóa nhận diện ở dạng "condensed" (không dấu cách)
SECTION_KEYWORDS = {
    "contact": [
        "thongtincanhan", "thôngtincánhân", "personalinfo", "contact", 
        "contactinfo", "lienhe", "liênhệ"
    ],
    "summary": [
        "muctieu", "mụctiêu", "summary", "profile", "aboutme", "tomtat", 
        "tómtắt", "careerobjective", "gioithieu", "giớithiệu"
    ],
    "education": [
        "hocvan", "họcvấn", "education", "bangcap", "bằngcấp", "academic", 
        "daotao", "đàotạo", "trinhdohocvan", "trìnhđộhọcvấn"
    ],
    "skills": [
        "kynang", "kỹnăng", "skills", "technicalskills", "chuyenmon", 
        "chuyênmôn", "technologies", "congnghe", "côngnghệ"
    ],
    "experience": [
        "kinhnghiem", "kinhnghiệm", "experience", "workexperience", 
        "employment", "lichsulaviec", "kinhnghiemlamviec", "kinhnghiệmlàmviệc"
    ],
    "projects": [
        "duan", "dựán", "doan", "đồán", "projects", "personalprojects", 
        "hoatdong", "hoạtđộng"
    ],
    "others": [
        "chungchi", "chứngchỉ", "certificates", "certifications", 
        "nguoigioithieu", "ngườigiớithiệu", "references", "danhhieu", 
        "danhhiệu", "giaithuong", "giảithưởng", "awards", "sothich", "sởthích"
    ],
}


def detect_section_header(line: str) -> Optional[str]:
    """
    Nhận diện tiêu đề mục, miễn nhiễm với lỗi dính dấu cách giữa các chữ cái của TopCV.
    """
    clean_line = line.strip()

    # 1. Bỏ qua dòng rỗng hoặc câu văn dài (> 50 ký tự)
    if not clean_line or len(clean_line) > 50:
        return None

    # 2. Bỏ qua câu văn có dấu chấm kết thúc câu
    if clean_line.endswith("."):
        return None

    # 3. Dọn rác trang trí ở hai đầu: bullet, số thứ tự, viền gạch
    clean_line = re.sub(r"^[^a-zA-Z0-9À-ỹ]+", "", clean_line)
    clean_line = re.sub(r"[^a-zA-Z0-9À-ỹ]+$", "", clean_line)
    clean_line = re.sub(r"^(\d+(\.\d+)*|[IVXLCDMivxlcdm]+|[A-Za-z])[\.\)\-:]\s*", "", clean_line)

    # 4. Gom lại dạng condensed: xóa toàn bộ khoảng trắng và dấu gạch để chống lỗi font
    condensed = re.sub(r"[\s\-_:•\.\(\)\[\]\|/]+", "", clean_line).lower()

    if len(condensed) > 30 or len(condensed) < 3:
        return None

    # 5. Đối chiếu từ khóa
    for sec_name, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            if condensed == kw or condensed.startswith(kw):
                return sec_name

    return None


def parse_cv_sections(clean_text: str) -> Dict[str, str]:
    sections = {name: [] for name in SECTION_NAMES}
    current_section = "contact"

    for line in clean_text.split("\n"):
        line_clean = line.strip()
        if not line_clean:
            continue

        header = detect_section_header(line_clean)
        if header is not None:
            current_section = header
        else:
            sections[current_section].append(line_clean)

    return {
        sec: "\n".join(lines).strip()
        for sec, lines in sections.items()
        if lines
    }