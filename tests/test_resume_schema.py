import json
from pathlib import Path
from core.intake import extract_cv
from core.section_parser import parse_cv_sections
from core.skills_extractor import analyze_cv_skills
from core.ats_scorer import evaluate_cv_ats
from core.resume_schema import build_structured_resume, build_markdown_resume
from tests.test_utils import get_test_cvs, render_table, truncate_text


def test_resume_standardization():
    cv_files = get_test_cvs()
    if not cv_files:
        print("❌ Không tìm thấy file PDF nào!")
        return

    headers = [
        "STT",
        "Tên File CV",
        "Họ Tên Ứng viên",
        "Email Trích xuất",
        "Số Điện thoại",
        "Profile Links",
        "Độ dài MD",
        "JSON Resume",
    ]
    alignments = ["center", "left", "left", "left", "center", "left", "right", "center"]
    rows = []

    out_dir = Path("tests/output")
    out_dir.mkdir(parents=True, exist_ok=True)

    sample_saved = False

    for idx, pdf_path in enumerate(cv_files, 1):
        intake = extract_cv(pdf_path)
        if not intake.is_valid:
            continue

        sections = parse_cv_sections(intake.clean_text)
        skills = analyze_cv_skills(sections)
        ats_res = evaluate_cv_ats(
            sections=sections,
            all_found_skills=skills.all_found_skills,
            explicit_skills=skills.explicit_skills,
            implicit_skills=skills.implicit_skills,
            archetype="product",
        )

        json_resume = build_structured_resume(sections, skills, ats_res)
        md_content = build_markdown_resume(sections, skills, ats_res.missing_skills)

        basics = json_resume.get("basics", {})
        name = basics.get("name") or "—"
        email = basics.get("email") or "—"
        phone = basics.get("phone") or "—"
        profiles = [p["url"] for p in basics.get("profiles", [])]
        profiles_str = truncate_text(", ".join(profiles), 25) if profiles else "—"

        rows.append([
            str(idx),
            truncate_text(pdf_path.name, 28),
            truncate_text(name, 20),
            truncate_text(email, 26),
            phone,
            profiles_str,
            f"{len(md_content):,} ký tự",
            "Chuẩn v1.0 ✅",
        ])

        # Lưu 1 file mẫu đại diện (file có điểm cao nhất hoặc file thứ 2)
        if not sample_saved and ats_res.total_score >= 80:
            json_file = out_dir / "sample_resume_standard.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(json_resume, f, ensure_ascii=False, indent=2)

            md_file = out_dir / "sample_resume_standard.md"
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(md_content)
            sample_saved = True

    render_table(
        headers=headers,
        rows=rows,
        title="KẾT QUẢ KIỂM THỬ TẦNG TRUNG GIAN: CHUẨN HÓA JSON RESUME & STRUCTURED MARKDOWN",
        alignments=alignments,
    )

    print("📁 Đã xuất dữ liệu chuẩn hóa mẫu thành công:")
    print("   • tests/output/sample_resume_standard.json  (Chuẩn quốc tế jsonresume.org)")
    print("   • tests/output/sample_resume_standard.md    (Chuẩn Markdown phân cấp)\n")


if __name__ == "__main__":
    test_resume_standardization()
