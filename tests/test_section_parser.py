from pathlib import Path
from core.intake import extract_cv
from core.section_parser import parse_cv_sections

def test_stage2_samples():
    base_dir = Path("tests/backend")
    sample_files = [
        base_dir / "sample_cv_1.pdf",
        base_dir / "sample_cv_2.pdf",
        base_dir / "sample_cv_3.pdf",
        base_dir / "sample_cv_4.pdf",
    ]

    print("=" * 65)
    print("      KIỂM TRA CHẶNG 2: PHÂN TÁCH CẤU TRÚC CV (SECTION PARSER)")
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

        # Lọc ra các mục có nội dung và mục bị rỗng
        found_sections = {sec: len(text) for sec, text in sections.items() if text.strip()}
        empty_sections = [sec for sec, text in sections.items() if not text.strip()]

        print(f"  Số section bóc tách được: {len(found_sections)}/7")
        print("  Độ dài từng section (ký tự):")
        for sec, length in found_sections.items():
            print(f"    - {sec:<12}: {length:>5} ký tự")

        if empty_sections:
            print(f"  Section còn trống       : {', '.join(empty_sections)}")

    print("\n" + "=" * 65)

if __name__ == "__main__":
    test_stage2_samples()