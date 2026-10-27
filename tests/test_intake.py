from pathlib import Path
from core.intake import extract_cv

def test_stage1_samples():
    base_dir = Path("tests/backend")
    sample_files = [
        base_dir / "sample_cv_1.pdf",
        base_dir / "sample_cv_2.pdf",
        base_dir / "sample_cv_3.pdf",
        base_dir / "sample_cv_4.pdf",
    ]

    print("           KIỂM TRA CHẶNG 1: INTAKE & VALIDATION")


    for pdf_path in sample_files:
        print(f"\n[TESTING] File: {pdf_path}")
        if not pdf_path.exists():
            print(f"  ❌ Không tìm thấy file tại đường dẫn: {pdf_path}")
            continue

        result = extract_cv(pdf_path)

        status = "PASSED ✅" if result.is_valid else "FAILED ⚠️"
        print(f"  Trạng thái  : {status}")
        print(f"  Số trang    : {result.page_count}")
        print(f"  Tổng ký tự  : {result.char_count}")

        if not result.is_valid:
            print(f"  Lỗi chi tiết: {result.error_message}")
        else:
            # In 100 ký tự đầu để xác nhận text sạch, không dính ký tự lạ/ligature
            preview = result.clean_text[:100].replace("\n", " ")
            print(f"  Preview     : {preview}...")

    print("\n" + "=" * 65)

if __name__ == "__main__":
    test_stage1_samples()