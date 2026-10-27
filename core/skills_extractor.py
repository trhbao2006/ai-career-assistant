import re
from typing import Dict, List, Set
from config.backend import backend_skills_tamoxy
from dataclasses import dataclass

def build_regex_pattern(alias: str) -> re.Pattern:
    """
    Sinh biểu thức chính quy an toàn cho từng alias.
    """
    alias_clean = alias.strip().lower()

    # Java (không được khớp nhầm JavaScript)
    if alias_clean == "java":
        return re.compile(r"\bjava\b(?!\s*script)", re.IGNORECASE)

    # Kỹ năng có ký tự đặc biệt ở rìa (+, #, .)
    special_chars = {'+', '#', '.'}
    has_special_edge = alias_clean[0] in special_chars or alias_clean[-1] in special_chars

    escaped = re.escape(alias_clean)
    if has_special_edge:
        # Dùng lookaround thay vì \b
        pattern_str = rf"(?<![a-zA-Z0-9_]){escaped}(?![a-zA-Z0-9_+#])"
    else:
        # Từ thông thường dùng \b
        pattern_str = rf"\b{escaped}\b"

    return re.compile(pattern_str, re.IGNORECASE)


# Tiền biên dịch (Pre-compile) một lần duy nhất
COMPILED_TAXONOMY = {
    category: {
        canonical_name: [build_regex_pattern(alias) for alias in aliases]
        for canonical_name, aliases in skills.items()
    }
    for category, skills in backend_skills_tamoxy.items()
}

def extract_skills(text: str) -> Dict[str, List[str]]:
    if not text:
        return {cat: [] for cat in COMPILED_TAXONOMY}

    results: Dict[str, List[str]] = {}
    for category, skills_dict in COMPILED_TAXONOMY.items():
        results[category] = [
            skill for skill, patterns in skills_dict.items()
            if any(p.search(text) for p in patterns)
        ]
    return results

@dataclass
class SkillExtractionResult:
    explicit_skills: Dict[str, List[str]]   # Kỹ năng khai báo ở mục Skills
    implicit_skills: Dict[str, List[str]]   # Kỹ năng tìm thấy trong Projects/Experience nhưng không có ở Skills
    all_found_skills: Dict[str, List[str]]  # Hợp của cả 2 nhóm trên


def analyze_cv_skills(sections: Dict[str, str]) -> SkillExtractionResult:
    """
    Phân tích kỹ năng từ các section đã bóc tách của CV.
    """
    # 1. Trích xuất kỹ năng khai báo tường minh ở section 'skills'
    skills_text = sections.get("skills", "")
    explicit_skills = extract_skills(skills_text)

    # 2. Gom text từ các section kinh nghiệm/đồ án và trích xuất kỹ năng
    project_exp_text = f"{sections.get('projects', '')}\n{sections.get('experience', '')}".strip()
    project_skills = extract_skills(project_exp_text)

    implicit_skills: Dict[str, List[str]] = {}
    all_found_skills: Dict[str, List[str]] = {}

    # Lấy toàn bộ danh sách category xuất hiện ở cả 2 bên
    all_categories = set(explicit_skills.keys()) | set(project_skills.keys())

    for category in all_categories:
        exp_list = explicit_skills.get(category, [])
        proj_list = project_skills.get(category, [])

        exp_set = set(exp_list)

        # 3. Kỹ năng có trong dự án nhưng chưa được khai báo ở section 'skills'
        implicit_skills[category] = [skill for skill in proj_list if skill not in exp_set]

        # 4. Hợp (Union) của 2 nhóm: giữ nguyên thứ tự của explicit trước, sau đó thêm implicit
        all_found_skills[category] = exp_list + implicit_skills[category]

    # 5. Đóng gói kết quả trả về
    return SkillExtractionResult(
        explicit_skills=explicit_skills,
        implicit_skills=implicit_skills,
        all_found_skills=all_found_skills,
    )

if __name__ == "__main__":
    from core.intake import extract_cv
    from core.section_parser import parse_cv_sections

    # 1. Đọc file
    intake = extract_cv("test/sample_cv.pdf")
    if intake.is_valid:
        # 2. Bóc tách section
        sections = parse_cv_sections(intake.clean_text)
        
        # 3. Trích xuất kỹ năng
        res = analyze_cv_skills(sections)
        
        print("=== KỸ NĂNG KHAI BÁO (EXPLICIT) ===")
        for cat, sks in res.explicit_skills.items():
            if sks:
                print(f"  [{cat}]: {', '.join(sks)}")

        print("\n=== KỸ NĂNG THỰC CHIẾN ẨN TRONG DỰ ÁN (IMPLICIT) ===")
        for cat, sks in res.implicit_skills.items():
            if sks:
                print(f"  [{cat}]: {', '.join(sks)}")