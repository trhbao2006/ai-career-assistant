from core.intake import extract_cv
from core.section_parser import parse_cv_sections
from core.skills_extractor import analyze_cv_skills
from core.ats_scorer import evaluate_cv_ats
from tests.test_utils import get_test_cvs, render_table, truncate_text

# JD mẫu để kiểm thử tính năng so khớp trực tiếp
SAMPLE_JD = """
Tuyển dụng Backend Developer Fresher / Junior:
- Thành thạo Java (Spring Boot) hoặc Python (FastAPI/Django) hoặc Node.js.
- Có kinh nghiệm với cơ sở dữ liệu quan hệ (PostgreSQL / MySQL) và Redis.
- Hiểu rõ RESTful API, OOP, Docker, Git và CI/CD.
"""


def test_stage4_samples():
    cv_files = get_test_cvs()
    if not cv_files:
        print("❌ Không tìm thấy file PDF nào!")
        return

    # Bảng 1: Chi tiết 4 Trụ cột Điểm ATS (theo mô hình Product)
    headers_breakdown = [
        "STT",
        "Tên File CV",
        "Cấu trúc (/20)",
        "Kỹ năng (/40)",
        "Impact (/25)",
        "Trình bày (/15)",
        "TỔNG ĐIỂM",
        "Xếp loại",
    ]
    alignments_breakdown = ["center", "left", "center", "center", "center", "center", "right", "center"]
    rows_breakdown = []

    # Bảng 2: So sánh Đa mô hình (Product vs Outsourcing vs Startup vs Custom JD)
    headers_archetypes = [
        "STT",
        "Tên File CV",
        "Product",
        "Outsourcing",
        "Startup",
        "Custom JD",
        "Kỹ năng Ẩn",
        "Lỗ hổng cốt lõi (Missing Skills Product)",
    ]
    alignments_archetypes = ["center", "left", "center", "center", "center", "center", "left", "left"]
    rows_archetypes = []

    total_product_score = 0.0

    for idx, pdf_path in enumerate(cv_files, 1):
        intake_res = extract_cv(pdf_path)
        if not intake_res.is_valid:
            continue

        sections = parse_cv_sections(intake_res.clean_text)
        skills = analyze_cv_skills(sections)

        # Chấm Product
        res_prod = evaluate_cv_ats(
            sections=sections,
            all_found_skills=skills.all_found_skills,
            explicit_skills=skills.explicit_skills,
            implicit_skills=skills.implicit_skills,
            archetype="product",
        )
        total_product_score += res_prod.total_score
        b = res_prod.breakdown

        rows_breakdown.append([
            str(idx),
            truncate_text(pdf_path.name, 32),
            f"{b['section_completeness']:.1f}",
            f"{b['skill_coverage']:.1f}",
            f"{b['impact_and_metrics']:.1f}",
            f"{b['presentation_and_links']:.1f}",
            f"{res_prod.total_score:.1f} đ",
            res_prod.match_level,
        ])

        # Chấm Outsourcing & Startup & JD
        res_out = evaluate_cv_ats(
            sections=sections,
            all_found_skills=skills.all_found_skills,
            explicit_skills=skills.explicit_skills,
            implicit_skills=skills.implicit_skills,
            archetype="outsourcing",
        )
        res_start = evaluate_cv_ats(
            sections=sections,
            all_found_skills=skills.all_found_skills,
            explicit_skills=skills.explicit_skills,
            implicit_skills=skills.implicit_skills,
            archetype="startup",
        )
        res_jd = evaluate_cv_ats(
            sections=sections,
            all_found_skills=skills.all_found_skills,
            explicit_skills=skills.explicit_skills,
            implicit_skills=skills.implicit_skills,
            archetype="product",
            jd_text=SAMPLE_JD,
        )

        missing_flat = [s for lst in res_prod.missing_skills.values() for s in lst]
        missing_preview = truncate_text(", ".join(missing_flat), 38) if missing_flat else "(Đã đạt kỳ vọng)"

        rows_archetypes.append([
            str(idx),
            truncate_text(pdf_path.name, 28),
            f"{res_prod.total_score:.1f}",
            f"{res_out.total_score:.1f}",
            f"{res_start.total_score:.1f}",
            f"{res_jd.total_score:.1f}",
            truncate_text(", ".join(res_prod.unlisted_project_skills), 25) or "—",
            missing_preview,
        ])

    render_table(
        headers=headers_breakdown,
        rows=rows_breakdown,
        title="KẾT QUẢ KIỂM THỬ CHẶNG 4: BẢNG ĐIỂM ATS 4 TRỤ CỘT (PRODUCT ARCHETYPE)",
        alignments=alignments_breakdown,
    )

    render_table(
        headers=headers_archetypes,
        rows=rows_archetypes,
        title="SO SÁNH ĐIỂM SỐ ĐA MÔ HÌNH (PRODUCT vs OUTSOURCING vs STARTUP vs CUSTOM JD)",
        alignments=alignments_archetypes,
    )

    avg_score = round(total_product_score / len(cv_files), 1)
    print(f"📊 Điểm ATS trung bình toàn bộ tập CV (Mô hình Product): {avg_score} / 100 điểm\n")


if __name__ == "__main__":
    test_stage4_samples()
