from pathlib import Path
from core.intake import extract_cv
from core.section_parser import parse_cv_sections
from core.skills_extractor import analyze_cv_skills

def test_stage3_samples():
    base_dir = Path("tests/backend")
    sample_files = [
        base_dir / "sample_cv_1.pdf",
        base_dir / "sample_cv_2.pdf",
        base_dir / "sample_cv_3.pdf",
        base_dir / "sample_cv_4.pdf",
    ]

    print("=" * 65)
    print("    KIỂM TRA CHẶNG 3: BÓC TÁCH KỸ NĂNG (EXPLICIT & IMPLICIT)")
    print("=" * 65)

    for pdf_path in sample_files:
        print(f"\n[TESTING] File: {pdf_path}")
        if not pdf_path.exists():
            print(f"  ❌ Không tìm thấy file: {pdf_path}")
            continue

        intake_res = extract_cv(pdf_path)
        if not intake_res.is_valid:
            print(f"  ⚠️ Bỏ qua (PDF không hợp lệ): {intake_res.error_message}")
            continue

        sections = parse_cv_sections(intake_res.clean_text)
        res = analyze_cv_skills(sections)

        total_skills = sum(len(v) for v in res.all_found_skills.values())
        print(f"  Tổng kỹ năng phát hiện: {total_skills}")

        # In kỹ năng Explicit
        print("  -> Explicit (khai báo ở mục Skills):")
        explicit_items = [f"{cat}: {', '.join(sks)}" for cat, sks in res.explicit_skills.items() if sks]
        if explicit_items:
            for item in explicit_items:
                print(f"     • {item}")
        else:
            print("     (Không có)")

        # In kỹ năng Implicit
        print("  -> Implicit (ẩn trong Projects/Experience):")
        implicit_items = [f"{cat}: {', '.join(sks)}" for cat, sks in res.implicit_skills.items() if sks]
        if implicit_items:
            for item in implicit_items:
                print(f"     • {item}")
        else:
            print("     (Không có kỹ năng ẩn mới)")

    print("\n" + "=" * 65)

if __name__ == "__main__":
    test_stage3_samples()