import sys
from pathlib import Path
from core.intake import extract_cv
from core.section_parser import parse_cv_sections
from core.skills_extractor import analyze_cv_skills
from core.ats_scorer import evaluate_cv_ats

# 1. Đảm bảo UTF-8 cho console trên mọi môi trường (Windows PowerShell/CMD)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 2. JD mẫu để test tính năng so khớp trực tiếp
SAMPLE_JD = """
Tuyển dụng Backend Developer (Fresher/Junior):
- Thành thạo Python hoặc Node.js (Express.js, NestJS, FastAPI).
- Có kinh nghiệm làm việc với PostgreSQL, MongoDB và Redis.
- Hiểu rõ RESTful API, OOP, biết sử dụng Docker, Git và CI/CD.
"""

def test_stage4_samples():
    base_dir = Path("tests/backend") if Path("tests/backend").exists() else Path("test/backend")
    sample_files = [base_dir / f"sample_cv_{i}.pdf" for i in range(1, 4)]

    print("=" * 70)
    print("   KIỂM TRA CHẶNG 4: ĐA MÔ HÌNH (ARCHETYPES) & SO KHỚP JD")
    print("=" * 70)

    for pdf_path in sample_files:
        if not pdf_path.exists():
            print(f"\n[!] Bỏ qua (không tìm thấy): {pdf_path}")
            continue

        intake = extract_cv(pdf_path)
        if not intake.is_valid:
            print(f"\n[!] File lỗi {pdf_path.name}: {intake.error_message}")
            continue

        sections = parse_cv_sections(intake.clean_text)
        skills = analyze_cv_skills(sections)

        print(f"\n📄 FILE: {pdf_path.name}")
        print("-" * 70)

        # A. Chấm điểm lần lượt với 3 Archetypes
        for arch in ["product", "outsourcing", "startup"]:
            res = evaluate_cv_ats(
                sections=sections,
                all_found_skills=skills.all_found_skills,
                explicit_skills=skills.explicit_skills,
                implicit_skills=skills.implicit_skills,
                archetype=arch,
            )
            b = res.breakdown
            print(
                f"  • [{arch.upper():<11}] Tổng: {res.total_score:>5}/100 ({res.match_level:<15}) | "
                f"Cấu trúc: {b['section_completeness']} | Kỹ năng: {b['skill_coverage']} | "
                f"Impact: {b['impact_and_metrics']} | Trình bày: {b['presentation_and_links']}"
            )

        # B. Chấm điểm khi truyền trực tiếp jd_text
        jd_res = evaluate_cv_ats(
            sections=sections,
            all_found_skills=skills.all_found_skills,
            explicit_skills=skills.explicit_skills,
            implicit_skills=skills.implicit_skills,
            archetype="product",
            jd_text=SAMPLE_JD,
        )
        missing_flat = [s for lst in jd_res.missing_skills.values() for s in lst]
        print(f"  • [CUSTOM JD  ] Tổng: {jd_res.total_score:>5}/100 | Thiếu so với JD: {', '.join(missing_flat) or 'Đủ 100%'}")

        if jd_res.unlisted_Project_skills:
            print(f"  🔍 Kỹ năng ẩn (quên ghi ở mục Skills): {', '.join(jd_res.unlisted_Project_skills)}")

if __name__ == "__main__":
    test_stage4_samples()