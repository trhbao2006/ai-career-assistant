import json
import sys
from pathlib import Path
from core.intake import extract_cv
from core.section_parser import parse_cv_sections
from core.skills_extractor import analyze_cv_skills
from core.ats_scorer import evaluate_cv_ats
from core.resume_schema import build_structured_resume, build_markdown_resume
from core.llm_advisor import LLMAdvisor

# Đảm bảo UTF-8 cho console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def test_resume_standardization():
    print("=" * 80)
    print("  KIỂM TRA CHUẨN HÓA TRUNG GIAN: JSON RESUME & STRUCTURED MARKDOWN")
    print("=" * 80)

    pdf_path = Path("tests/backend/sample_cv_3.pdf")
    if not pdf_path.exists():
        pdf_path = Path("test/backend/sample_cv_3.pdf")

    print(f"\n[1] Xử lý bóc tách CV: {pdf_path.name}")
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

    # 1. Chuyển đổi sang JSON Resume Standard
    print("\n[2] Xuất ra chuẩn JSON Resume (jsonresume.org):")
    json_resume = build_structured_resume(sections, skills, ats_res)
    print(f"  • Schema URI : {json_resume.get('$schema')}")
    print(f"  • Email      : {json_resume['basics'].get('email')}")
    print(f"  • Phone      : {json_resume['basics'].get('phone')}")
    print(f"  • Profiles   : {json_resume['basics'].get('profiles')}")
    print(f"  • Điểm ATS   : {json_resume['ats_evaluation']['total_score']}/100 ({json_resume['ats_evaluation']['match_level']})")
    print(f"  • Skill Gap  : {json_resume['ats_evaluation']['missing_skills'] or 'Đầy đủ'}")

    # 2. Chuyển đổi sang Structured Markdown
    print("\n[3] Chuyển đổi sang Structured Markdown (H1, H2, H3, Bullets):")
    md_content = build_markdown_resume(sections, skills, ats_res.missing_skills)
    preview_md = "\n".join(md_content.splitlines()[:25])
    print("-" * 50)
    print(preview_md)
    print("...\n[Đoạn trích 25 dòng đầu của file Markdown]")
    print("-" * 50)

    # 3. Nạp Structured Markdown vào Chặng 5 (LLM Advisor)
    print("\n[4] Nạp Structured Markdown vào LLM Advisor (Gemini/Fallback):")
    advisor = LLMAdvisor()
    advice = advisor.suggest_architecture_upgrades(
        projects_text=sections.get("projects", ""),
        missing_skills=ats_res.missing_skills,
        all_found_skills=skills.all_found_skills,
        archetype="product",
        structured_markdown=md_content,
    )

    print(f"  • Số lượng giải pháp nâng cấp : {len(advice.upgrades)}")
    print(f"  • Số lượng dòng CV viết lại   : {len(advice.rewritten_project_bullets)}")
    print(f"  • Mẫu viết lại đầu tiên       : {advice.rewritten_project_bullets[0].improved_bullet_point[:100]}...")

    # Lưu thử nghiệm ra thư mục tests/output
    out_dir = Path("tests/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    json_file = out_dir / "sample_cv_3_resume.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_resume, f, ensure_ascii=False, indent=2)
    print(f"\n[5] Đã lưu file JSON Resume mẫu tại: {json_file}")

    md_file = out_dir / "sample_cv_3_resume.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"    Đã lưu file Markdown mẫu tại   : {md_file}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_resume_standardization()
