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
        "contactinfo", "lienhe", "liênhệ", "thongtinlienhe", "thôngtinliênhệ"
    ],
    "summary": [
        "muctieu", "mụctiêu", "summary", "profile", "aboutme", "tomtat", 
        "tómtắt", "careerobjective", "gioithieu", "giớithiệu",
        "muctieunghenghiep", "mụctiêunghềnghiệp", "profilesummary"
    ],
    "education": [
        "hocvan", "họcvấn", "education", "bangcap", "bằngcấp", "academic", 
        "daotao", "đàotạo", "trinhdohocvan", "trìnhđộhọcvấn", "hocvanbangcap", "họcvấnbằngcấp"
    ],
    "skills": [
        "kynang", "kỹnăng", "skills", "technicalskills", "chuyenmon", 
        "chuyênmôn", "technologies", "congnghe", "côngnghệ",
        "kynangchuyenmon", "kỹnăngchuyênmôn"
    ],
    "experience": [
        "kinhnghiem", "kinhnghiệm", "experience", "workexperience", 
        "employment", "lichsulaviec", "kinhnghiemlamviec", "kinhnghiệmlàmviệc",
        "professionalexperience", "workhistory", "practicalexperience",
        "kinhnghiemduan", "kinhnghiệmdựán"
    ],
    "projects": [
        "duan", "dựán", "doan", "đồán", "projects", "personalprojects", 
        "hoatdong", "hoạtđộng", "duancanhan", "dựáncánhân", "academicprojects",
        "duanhoctap", "dựánhọctập", "projectsexperience", "experienceprojects",
        "duanvakinhnghiem", "dựánvàkinhnghiệm", "duankinhnghiem", "dựánkinhnghiệm"
    ],
    "others": [
        "chungchi", "chứngchỉ", "certificates", "certifications", 
        "nguoigioithieu", "ngườigiớithiệu", "references", "danhhieu", 
        "danhhiệu", "giaithuong", "giảithưởng", "awards", "sothich", "sởthích"
    ],
}

# Các từ ngữ đặc trưng của câu văn mô tả thường (không thể là tiêu đề mục)
STOP_WORDS_IN_HEADER = {"là", "tại", "với", "cho", "của", "trong", "được", "nhằm", "đạt", "khi"}


def detect_section_header(line: str) -> Optional[str]:
    """
    Nhận diện tiêu đề mục, miễn nhiễm với lỗi dính dấu cách giữa các chữ cái của TopCV.
    Ngăn chặn tuyệt đối việc bắt nhầm câu văn nội dung thành tiêu đề (False Positive Guard).
    """
    clean_line = line.strip()

    # 1. Bỏ qua dòng rỗng hoặc câu văn dài (> 50 ký tự hoặc > 6 từ)
    words = clean_line.split()
    if not clean_line or len(clean_line) > 50 or len(words) > 6:
        return None

    # 2. Bỏ qua câu văn có dấu chấm kết thúc câu hoặc dấu phẩy liệt kê
    if clean_line.endswith(".") or "," in clean_line:
        return None

    # 3. Bỏ qua nếu chứa liên từ/giới từ của câu văn thường (ví dụ: "Dự án tại công ty ABC", "Đồ án đạt điểm A")
    line_lower_words = set(re.findall(r"\w+", clean_line.lower()))
    if line_lower_words & STOP_WORDS_IN_HEADER:
        return None

    # 4. Dọn rác trang trí ở hai đầu: bullet, số thứ tự, viền gạch
    clean_line = re.sub(r"^[^a-zA-Z0-9À-ỹ]+", "", clean_line)
    clean_line = re.sub(r"[^a-zA-Z0-9À-ỹ]+$", "", clean_line)
    clean_line = re.sub(r"^(\d+(\.\d+)*|[IVXLCDMivxlcdm]+|[A-Za-z])[\.\)\-:]\s*", "", clean_line)

    # 5. Gom lại dạng condensed: xóa toàn bộ khoảng trắng và dấu gạch để chống lỗi font
    condensed = re.sub(r"[\s\-_:•\.\(\)\[\]\|/&]+", "", clean_line).lower()

    if len(condensed) > 30 or len(condensed) < 3:
        return None

    # 6. Đối chiếu từ khóa chính xác hoặc hậu tố số/la mã hợp lệ (ví dụ: "Dự án 1", "Projects I")
    for sec_name, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            if condensed == kw:
                return sec_name
            if condensed.startswith(kw):
                suffix = condensed[len(kw):]
                if suffix.isdigit() or suffix in {"i", "ii", "iii", "iv", "v", "vi"}:
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


if __name__ == "__main__":
    from pathlib import Path
    from core.intake import extract_cv

    # Tìm file CV mẫu để test thử
    test_paths = [
        Path("test/sample_cv.pdf"),
        Path("tests/sample_cv.pdf"),
        Path("tests/CV Test/CV_backend_1.pdf")
    ]
    target_path = next((p for p in test_paths if p.exists()), None)

    if not target_path:
        print("⚠️ Không tìm thấy file CV kiểm thử.")
    else:
        intake_res = extract_cv(str(target_path))
        if intake_res.is_valid:
            parsed_sections = parse_cv_sections(intake_res.clean_text)
            print(f"--- CÁC SECTION BÓC TÁCH ĐƯỢC TỪ {target_path.name} ---")
            for sec_name, content in parsed_sections.items():
                print(f"\n[SECTION: {sec_name.upper()}] (Độ dài: {len(content)} ký tự)")
                print(content[:150] + ("..." if len(content) > 150 else ""))
        else:
            print(f"❌ Lỗi đọc CV: {intake_res.error_message}")
