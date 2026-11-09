from core.intake import extract_cv
from tests.test_utils import get_test_cvs, render_table, truncate_text


def test_stage1_samples():
    cv_files = get_test_cvs()
    if not cv_files:
        print("❌ Không tìm thấy file PDF nào trong thư mục tests/ hoặc tests/CV Test/!")
        return

    headers = ["STT", "Tên File CV", "Trạng thái", "Trang", "Ký tự", "Trích đoạn đầu (Preview)"]
    alignments = ["center", "left", "center", "center", "right", "left"]
    rows = []

    passed_count = 0
    total_chars = 0

    for idx, pdf_path in enumerate(cv_files, 1):
        res = extract_cv(pdf_path)
        status = "PASSED ✅" if res.is_valid else "FAILED ⚠️"
        if res.is_valid:
            passed_count += 1
            total_chars += res.char_count
            preview = truncate_text(res.clean_text, 45)
        else:
            preview = truncate_text(f"Lỗi: {res.error_message}", 45)

        rows.append([
            str(idx),
            truncate_text(pdf_path.name, 35),
            status,
            str(res.page_count),
            f"{res.char_count:,}" if res.is_valid else "0",
            preview,
        ])

    render_table(
        headers=headers,
        rows=rows,
        title=f"KẾT QUẢ KIỂM THỬ CHẶNG 1: INTAKE & TIỀN XỬ LÝ PDF ({passed_count}/{len(cv_files)} PASSED)",
        alignments=alignments,
    )
    print(f"📊 Tổng kết: {passed_count}/{len(cv_files)} CV đạt chuẩn | Tổng ký tự xử lý: {total_chars:,} ký tự\n")


if __name__ == "__main__":
    test_stage1_samples()
