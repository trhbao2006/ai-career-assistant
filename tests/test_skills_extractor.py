from core.intake import extract_cv
from core.section_parser import parse_cv_sections
from core.skills_extractor import analyze_cv_skills
from tests.test_utils import get_test_cvs, render_table, truncate_text


def test_stage3_samples():
    cv_files = get_test_cvs()
    if not cv_files:
        print("❌ Không tìm thấy file PDF nào!")
        return

    # Bảng 1: Thống kê số lượng kỹ năng theo 9 nhóm taxonomy
    headers_stats = [
        "STT",
        "Tên File CV",
        "Lang",
        "Framework",
        "DB",
        "DevOps",
        "Cloud",
        "Msg",
        "Obs",
        "Sec",
        "Concepts",
        "Explicit",
        "Implicit 🔍",
        "Tổng",
    ]
    alignments_stats = [
        "center", "left", "center", "center", "center", "center",
        "center", "center", "center", "center", "center", "center",
        "center", "center"
    ]
    rows_stats = []

    # Bảng 2: Chi tiết các kỹ năng ẩn phát hiện trong dự án
    headers_implicit = ["STT", "Tên File CV", "Kỹ năng Khai báo (Explicit)", "Kỹ năng Ẩn trong Dự án (Implicit)"]
    alignments_implicit = ["center", "left", "left", "left"]
    rows_implicit = []

    total_explicit_all = 0
    total_implicit_all = 0

    for idx, pdf_path in enumerate(cv_files, 1):
        intake_res = extract_cv(pdf_path)
        if not intake_res.is_valid:
            continue

        sections = parse_cv_sections(intake_res.clean_text)
        res = analyze_cv_skills(sections)

        explicit_count = sum(len(v) for v in res.explicit_skills.values())
        implicit_count = sum(len(v) for v in res.implicit_skills.values())
        total_found = sum(len(v) for v in res.all_found_skills.values())

        total_explicit_all += explicit_count
        total_implicit_all += implicit_count

        rows_stats.append([
            str(idx),
            truncate_text(pdf_path.name, 26),
            str(len(res.all_found_skills.get("languages", []))),
            str(len(res.all_found_skills.get("frameworks", []))),
            str(len(res.all_found_skills.get("databases", []))),
            str(len(res.all_found_skills.get("devops_tools", []))),
            str(len(res.all_found_skills.get("cloud", []))),
            str(len(res.all_found_skills.get("messaging", []))),
            str(len(res.all_found_skills.get("observability", []))),
            str(len(res.all_found_skills.get("security", []))),
            str(len(res.all_found_skills.get("concepts", []))),
            str(explicit_count),
            f"🔍 {implicit_count}" if implicit_count > 0 else "0",
            str(total_found),
        ])

        # Chi tiết kỹ năng
        exp_flat = [s for lst in res.explicit_skills.values() for s in lst]
        imp_flat = [s for lst in res.implicit_skills.values() for s in lst]

        rows_implicit.append([
            str(idx),
            truncate_text(pdf_path.name, 26),
            truncate_text(", ".join(exp_flat), 45) if exp_flat else "(Không có mục Skills)",
            truncate_text(", ".join(imp_flat), 42) if imp_flat else "(Không có kỹ năng ẩn mới)",
        ])

    render_table(
        headers=headers_stats,
        rows=rows_stats,
        title="KẾT QUẢ KIỂM THỬ CHẶNG 3: BÓC TÁCH KỸ NĂNG THEO TAXONOMY (9 NHÓM MỞ RỘNG)",
        alignments=alignments_stats,
    )

    render_table(
        headers=headers_implicit,
        rows=rows_implicit,
        title="CHI TIẾT: KỸ NĂNG KHAI BÁO (EXPLICIT) vs KỸ NĂNG THỰC CHIẾN ẨN TRONG DỰ ÁN (IMPLICIT)",
        alignments=alignments_implicit,
    )

    avg_skills = round(total_explicit_all + total_implicit_all) / len(cv_files)
    print(f"📊 Tổng kết: Phát hiện trung bình {avg_skills:.1f} kỹ năng/CV")
    print(f"   (Tổng Explicit: {total_explicit_all} | Tổng Implicit phát hiện thêm từ dự án: {total_implicit_all})\n")


if __name__ == "__main__":
    test_stage3_samples()
