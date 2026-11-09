from core.intake import extract_cv
from core.section_parser import parse_cv_sections, SECTION_NAMES
from tests.test_utils import get_test_cvs, render_table, truncate_text


def test_stage2_samples():
    cv_files = get_test_cvs()
    if not cv_files:
        print("❌ Không tìm thấy file PDF nào!")
        return

    headers = [
        "STT",
        "Tên File CV",
        "Contact",
        "Summary",
        "Edu",
        "Skills",
        "Exp",
        "Projects",
        "Others",
        "Đạt",
    ]
    alignments = ["center", "left", "center", "center", "center", "center", "center", "center", "center", "center"]
    rows = []

    section_stats = {sec: 0 for sec in SECTION_NAMES}

    for idx, pdf_path in enumerate(cv_files, 1):
        intake_res = extract_cv(pdf_path)
        if not intake_res.is_valid:
            continue

        sections = parse_cv_sections(intake_res.clean_text)

        row = [str(idx), truncate_text(pdf_path.name, 32)]
        found_count = 0

        for sec in SECTION_NAMES:
            text = sections.get(sec, "").strip()
            if text:
                found_count += 1
                section_stats[sec] += 1
                row.append(f"✅ {len(text)}")
            else:
                row.append("—")

        row.append(f"{found_count}/7")
        rows.append(row)

    render_table(
        headers=headers,
        rows=rows,
        title="KẾT QUẢ KIỂM THỬ CHẶNG 2: PHÂN TÁCH CẤU TRÚC 7 SECTIONS (FSM & CONDENSED)",
        alignments=alignments,
    )

    print("📊 Tần suất hiện diện các mục trên toàn bộ tập CV mẫu:")
    stats_str = " | ".join(f"{sec}: {count}/{len(cv_files)}" for sec, count in section_stats.items())
    print(f"   {stats_str}\n")


if __name__ == "__main__":
    test_stage2_samples()
