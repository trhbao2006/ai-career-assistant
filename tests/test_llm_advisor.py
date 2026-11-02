import sys
from pathlib import Path
from core.intake import extract_cv
from core.section_parser import parse_cv_sections
from core.skills_extractor import analyze_cv_skills
from core.ats_scorer import evaluate_cv_ats
from core.llm_advisor import LLMAdvisor

# Đảm bảo UTF-8 cho console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def test_stage5_pipeline():
    print("=" * 80)
    print("      KIỂM TRA CHẶNG 5: LLM ADVISOR (KIẾN TRÚC & VIẾT LẠI MÔ TẢ ĐỒ ÁN CV)")
    print("=" * 80)

    # 1. Khởi tạo LLMAdvisor
    advisor = LLMAdvisor()
    mode = "Gemini Live API (Online) 🌐" if advisor.is_connected else "Deterministic Fallback Engine (Offline) 🛡️"
    print(f"\n[KHỞI TẠO] Chế độ hoạt động: {mode}")

    # 2. Sử dụng sample_cv_3.pdf (Backend Developer) để chạy chuỗi Pipeline từ Chặng 1 -> Chặng 5
    pdf_path = Path("tests/backend/sample_cv_3.pdf")
    if not pdf_path.exists():
        pdf_path = Path("test/backend/sample_cv_3.pdf")

    print(f"\n[PIPELINE] Xử lý CV: {pdf_path.name}")
    intake = extract_cv(pdf_path)
    sections = parse_cv_sections(intake.clean_text)
    skills = analyze_cv_skills(sections)
    ats_res = evaluate_cv_ats(
        sections=sections,
        all_found_skills=skills.all_found_skills,
        explicit_skills=skills.explicit_skills,
        implicit_skills=skills.implicit_skills,
        archetype="product",
    )

    projects_text = sections.get("projects", "") or sections.get("experience", "")
    print(f"  • Điểm ATS: {ats_res.total_score}/100 ({ats_res.match_level})")
    print(f"  • Kỹ năng ẩn: {', '.join(ats_res.unlisted_project_skills) or 'Không'}")
    print(f"  • Skill Gap ghi nhận: {ats_res.missing_skills or 'Đã đủ'}")

    # -------------------------------------------------------------
    # PHẦN 1: TƯ VẤN NÂNG CẤP KIẾN TRÚC ĐỒ ÁN
    # -------------------------------------------------------------
    print("\n" + "-" * 80)
    print("1. TƯ VẤN NÂNG CẤP KIẾN TRÚC ĐỒ ÁN (ARCHITECTURE UPGRADE ADVISOR)")
    print("-" * 80)

    arch_advice = advisor.suggest_architecture_upgrades(
        projects_text=projects_text,
        missing_skills=ats_res.missing_skills,
        all_found_skills=skills.all_found_skills,
        archetype="product",
    )

    print(f"\n[ĐÁNH GIÁ TỔNG QUAN]:\n{arch_advice.overall_assessment}\n")
    print(f"[DANH SÁCH {len(arch_advice.upgrades)} GIẢI PHÁP ĐỀ XUẤT]:")
    for idx, up in enumerate(arch_advice.upgrades, 1):
        print(f"\n  #{idx}. {up.title}")
        print(f"     • Áp dụng cho    : {up.target_project}")
        print(f"     • Bù đắp kỹ năng  : {', '.join(up.addressed_skill_gaps)}")
        print(f"     • Vấn đề kỹ thuật: {up.problem_statement}")
        print(f"     • Giải pháp       : {up.technical_solution}")
        print(f"     • Tác động kỳ vọng: {up.expected_metrics_impact}")

    # -------------------------------------------------------------
    # PHẦN 2: VIẾT LẠI MÔ TẢ DỰ ÁN THEO CHUẨN GOOGLE XYZ (BEFORE vs. AFTER)
    # -------------------------------------------------------------
    print("\n" + "-" * 80)
    print("2. VIẾT LẠI MÔ TẢ DỰ ÁN CHUẨN ATS (GOOGLE XYZ FORMULA: BEFORE vs. AFTER)")
    print("-" * 80)

    for idx, bullet in enumerate(arch_advice.rewritten_project_bullets, 1):
        print(f"\n  [MẪU #{idx}]")
        print(f"   🔴 Trước (CV gốc) : \"{bullet.original_description}\"")
        print(f"   🟢 Sau (Chuẩn ATS): \"{bullet.improved_bullet_point}\"")
        print(f"   🔑 Kỹ năng nổi bật: {', '.join(bullet.highlighted_skills)}")
        print(f"   💡 Lý do vượt trội: {bullet.why_it_is_better}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_stage5_pipeline()
