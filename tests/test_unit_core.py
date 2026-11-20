import pytest
from config.taxonomies.backend import (
    COMPANY_ARCHETYPES,
    ARCHETYPE_CORE_SKILLS,
    backend_skills_taxonomy,
    get_skills,
)
from core.intake import clean_raw_text
from core.section_parser import detect_section_header, parse_cv_sections
from core.skills_extractor import extract_skills, analyze_cv_skills
from core.ats_scorer import (
    score_section_completeness,
    score_skill_coverage,
    score_impact_and_metrics,
    score_presentation_and_consistency,
    evaluate_cv_ats,
)
from core.resume_schema import (
    extract_candidate_name,
    extract_contact_info,
    build_structured_resume,
    build_markdown_resume,
)


# =====================================================================
# 1. KIỂM THỬ TÍNH TOÀN VẸN CẤU HÌNH (config/backend.py)
# =====================================================================

def test_backend_config_integrity():
    """Kiểm tra tổng trọng số các mô hình và taxonomy không bị lỗi logic."""
    for name, weights in COMPANY_ARCHETYPES.items():
        total_w = sum(weights.values())
        assert abs(total_w - 1.0) < 1e-6, f"Tổng trọng số archetype '{name}' phải bằng 1.0 (hiện tại: {total_w})"
        assert set(weights.keys()) <= set(backend_skills_taxonomy.keys()), (
            f"Archetype '{name}' có nhóm kỹ năng không tồn tại trong taxonomy"
        )

    for arch_name, core_dict in ARCHETYPE_CORE_SKILLS.items():
        for cat, skills in core_dict.items():
            assert cat in backend_skills_taxonomy, f"Category '{cat}' trong archetype '{arch_name}' không hợp lệ"

    alias_map = get_skills()
    assert len(alias_map) > 50, "Alias map phải chứa ít nhất 50 từ khóa nhận diện"


# =====================================================================
# 2. KIỂM THỬ TIỀN XỬ LÝ & LÀM SẠCH VĂN BẢN (core/intake.py)
# =====================================================================

def test_clean_raw_text():
    """Kiểm tra chuẩn hóa Unicode NFKC, ký tự ẩn và icon bullet TopCV."""
    raw = "Nguye\u0302\u0303n Va\u0306n A\u200b\xa0\r\n\uf0b7 Ky nang: Python \t\t\n\n\n\n- Kinh nghiem"
    cleaned = clean_raw_text(raw)
    assert "\u200b" not in cleaned
    assert "\xa0" not in cleaned
    assert "\r" not in cleaned
    assert "- Ky nang: Python" in cleaned
    assert "\n\n\n" not in cleaned


# =====================================================================
# 3. KIỂM THỬ PHÂN TÁCH CẤU TRÚC 7 SECTIONS (core/section_parser.py)
# =====================================================================

def test_detect_section_header():
    """Kiểm tra nhận diện tiêu đề mục và hàng rào chống bắt nhầm câu văn."""
    # Các tiêu đề chuẩn
    assert detect_section_header("HỌC VẤN") == "education"
    assert detect_section_header("KỸ NĂNG CHUYÊN MÔN") == "skills"
    assert detect_section_header("KINH NGHIỆM LÀM VIỆC") == "experience"
    assert detect_section_header("DỰ ÁN CÁ NHÂN") == "projects"
    assert detect_section_header("Projects 1") == "projects"

    # Chặn câu văn thường (False Positive Guard)
    assert detect_section_header("Dự án tốt nghiệp đạt điểm A.") is None
    assert detect_section_header("Đồ án môn học tại trường đại học") is None
    assert detect_section_header("Có mục tiêu trở thành Senior Backend Engineer") is None


def test_parse_cv_sections():
    """Kiểm tra phân tách một văn bản CV mẫu thành 7 vùng độc lập."""
    mock_cv = """
Nguyen Van A
Email: test@gmail.com | Phone: 0912345678

HỌC VẤN
Dai hoc Bach Khoa Ha Noi - CNTT

KỸ NĂNG
Python, FastAPI, Docker, PostgreSQL

DỰ ÁN
E-commerce Platform: Xay dung he thong ban hang bang FastAPI va PostgreSQL.
"""
    sections = parse_cv_sections(mock_cv)
    assert "contact" in sections
    assert "Nguyen Van A" in sections["contact"]
    assert "education" in sections
    assert "Bach Khoa" in sections["education"]
    assert "skills" in sections
    assert "FastAPI" in sections["skills"]
    assert "projects" in sections
    assert "E-commerce" in sections["projects"]


# =====================================================================
# 4. KIỂM THỬ BÓC TÁCH KỸ NĂNG (core/skills_extractor.py)
# =====================================================================

def test_extract_skills_and_boundary():
    """Kiểm tra bóc tách kỹ năng an toàn với Negative Lookaround Regex."""
    # 1. Văn bản chỉ có JavaScript -> không được bắt nhầm Java
    js_only = "Lập trình viên JavaScript chuyên nghiệp với NestJS."
    skills_js = extract_skills(js_only)
    assert "JavaScript" in skills_js["languages"]
    assert "Java" not in skills_js["languages"]

    # 2. Văn bản chỉ có Java -> không được bắt nhầm JavaScript
    java_sample = (
        "Thành thạo Java (Spring Boot) và C++. "
        "Kinh nghiệm làm việc với .NET, C#, PostgreSQL, Redis, Docker và AWS S3."
    )
    skills = extract_skills(java_sample)

    assert "Java" in skills["languages"]
    assert "JavaScript" not in skills["languages"]

    # Phải bắt đúng C++, C#, .NET
    assert "C++" in skills["languages"]
    assert "C#" in skills["languages"]
    assert ".NET" in skills["frameworks"]

    # Bắt đúng databases, devops, cloud
    assert "PostgreSQL" in skills["databases"]
    assert "Redis" in skills["databases"]
    assert "Docker" in skills["devops_tools"]
    assert "AWS" in skills["cloud"]


def test_explicit_vs_implicit_skills():
    """Kiểm tra phân định kỹ năng tự khai báo vs kỹ năng ẩn trong đồ án."""
    mock_sections = {
        "skills": "Python, PostgreSQL",
        "projects": "Xây dựng hệ thống bằng FastAPI, Redis và triển khai Docker.",
        "experience": "",
    }
    result = analyze_cv_skills(mock_sections)

    assert "Python" in result.explicit_skills["languages"]
    assert "PostgreSQL" in result.explicit_skills["databases"]

    # FastAPI, Redis, Docker phải được phân loại là kỹ năng ẩn (Implicit)
    assert "FastAPI" in result.implicit_skills["frameworks"]
    assert "Redis" in result.implicit_skills["databases"]
    assert "Docker" in result.implicit_skills["devops_tools"]

    # Tổng all_found phải chứa cả 2
    assert "Python" in result.all_found_skills["languages"]
    assert "FastAPI" in result.all_found_skills["frameworks"]


# =====================================================================
# 5. KIỂM THỬ CHẤM ĐIỂM ATS 4 TRỤ CỘT (core/ats_scorer.py)
# =====================================================================

def test_ats_scorer_pillars():
    """Kiểm tra chấm điểm 4 trụ cột và xếp loại định lượng."""
    mock_sections = {
        "contact": "Nguyen Van A - Email: test@gmail.com - SĐT: 0987654321 - https://github.com/nguyenvana",
        "education": "Đại học Bách Khoa",
        "skills": "Python, Java, Spring Boot, FastAPI, PostgreSQL, Redis, Docker, Git",
        "projects": (
            "Thiết kế và triển khai RESTful API cho sàn TMĐT, tích hợp Redis cache "
            "giúp giảm 40% latency xuống còn 15ms và chịu tải hơn 10.000 requests/ngày."
        ),
        "experience": "Lập trình viên Backend Intern tại FPT Software.",
    }

    skills_res = analyze_cv_skills(mock_sections)
    ats_res = evaluate_cv_ats(
        sections=mock_sections,
        all_found_skills=skills_res.all_found_skills,
        explicit_skills=skills_res.explicit_skills,
        implicit_skills=skills_res.implicit_skills,
        archetype="product",
    )

    assert ats_res.total_score >= 70.0
    assert ats_res.match_level in ["Good Match", "Excellent Match"]
    assert ats_res.breakdown["section_completeness"] == 20.0  # Đầy đủ 4 phần
    assert ats_res.breakdown["impact_and_metrics"] >= 15.0   # Có 40%, 15ms, 10.000 requests


# =====================================================================
# 6. KIỂM THỬ TẦNG TRUNG GIAN JSON RESUME & MARKDOWN (core/resume_schema.py)
# =====================================================================

def test_resume_schema_and_name_extraction():
    """Kiểm tra trích xuất Họ Tên và chuẩn hóa JSON Resume chuẩn quốc tế."""
    contact_sample = """
NGUYỄN VĂN A
Email: nguyenvana@gmail.com
SĐT: 0987.654.321
GitHub: https://github.com/nguyenvana
LinkedIn: https://linkedin.com/in/nguyenvana
"""
    name = extract_candidate_name(contact_sample)
    assert name == "NGUYỄN VĂN A"

    info = extract_contact_info(contact_sample)
    assert info["name"] == "NGUYỄN VĂN A"
    assert info["email"] == "nguyenvana@gmail.com"
    assert len(info["links"]) >= 2

    mock_sections = {"contact": contact_sample, "projects": "Project A"}
    skills_res = analyze_cv_skills(mock_sections)

    json_resume = build_structured_resume(mock_sections, skills_res)
    assert json_resume["basics"]["name"] == "NGUYỄN VĂN A"
    assert json_resume["basics"]["email"] == "nguyenvana@gmail.com"

    md_content = build_markdown_resume(mock_sections, skills_res)
    assert "# NGUYỄN VĂN A" in md_content
    assert "Technical Skills" in md_content


# =====================================================================
# 7. KIỂM THỬ CÁC QUY TẮC BIÊN MỚI (EDGE CASES)
# =====================================================================

def test_ats_anti_keyword_stuffing():
    """Kiểm tra cơ chế hạ trọng số khi kỹ năng chỉ ghi ở mục Skills mà không có trong Đồ án."""
    # Ứng viên liệt kê nhiều database nhưng trong đồ án chỉ làm PostgreSQL
    all_found = {"databases": ["PostgreSQL", "MongoDB", "Redis"]}
    project_skills_verified = {"databases": ["PostgreSQL"]}

    score_stuffed, _, fb = score_skill_coverage(
        all_found_skills=all_found,
        archetype="product",
        project_skills=project_skills_verified,
    )

    # Đã có cảnh báo Keyword Stuffing
    assert any("Keyword Stuffing" in msg for msg in fb)


def test_ats_anti_boilerplate_essay():
    """Kiểm tra chống câu văn sáo rỗng: viết dài (>300 ký tự) nhưng 0 thuật ngữ kỹ thuật Backend."""
    fluff_sections = {
        "experience": (
            "Tôi là một người rất chăm chỉ và có tinh thần trách nhiệm cao trong công việc. "
            "Tôi luôn cố gắng học hỏi mỗi ngày để hoàn thiện bản thân và cống hiến cho công ty. "
            "Kỹ năng giao tiếp và làm việc nhóm của tôi rất tốt, tôi có thể hòa nhập nhanh chóng "
            "với môi trường mới và các đồng nghiệp xung quanh trong mọi tình huống."
        ),
        "projects": "",
    }
    score, feedback = score_impact_and_metrics(fluff_sections)
    # Bị phạt vì sáo rỗng, chỉ được 5 điểm ở phần chi tiết
    assert any("sáo rỗng" in fb for fb in feedback)
    assert score <= 12.0  # Không được điểm tối đa


def test_ats_link_validation_and_placeholders():
    """Kiểm tra nhận diện link placeholder vs link ẩn danh vs link thật."""
    from core.ats_scorer import check_profile_link

    # 1. Link placeholder dạng mẫu
    score_p, fb_p = check_profile_link("GitHub: https://github.com/your-username")
    assert score_p == 2.5
    assert "placeholder" in fb_p.lower()

    # 2. Link ẩn danh thường gặp trong CV mẫu
    score_a, fb_a = check_profile_link("Thông tin liên hệ: [GitHub / Portfolio Link]")
    assert score_a == 3.5
    assert "ẩn danh" in fb_a.lower()

    # 3. Không có link
    score_empty, fb_empty = check_profile_link("Nguyen Van A - 0987654321")
    assert score_empty == 0.0


def test_merged_projects_experience_alias():
    """Kiểm tra nhận diện alias gộp Projects & Experience trên CV 1 trang."""
    from core.section_parser import detect_section_header
    assert detect_section_header("PROJECTS & EXPERIENCE") == "projects"
    assert detect_section_header("Dự án & Kinh nghiệm") == "projects"
    assert detect_section_header("Work History") == "experience"

