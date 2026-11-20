import sys
import time
from pathlib import Path

# Cấu hình UTF-8 cho console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from core.intake import extract_cv
from core.section_parser import parse_cv_sections
from core.skills_extractor import analyze_cv_skills
from core.ats_scorer import evaluate_cv_ats
from core.resume_schema import build_markdown_resume
from core.llm_advisor import LLMAdvisor
from tests.test_utils import get_test_cvs


def run_single_cv_test(cv_index: int = 0):
    cv_files = get_test_cvs()
    if not cv_files:
        print(" Không tìm thấy file PDF nào trong thư mục tests!")
        return

    # Lấy file CV theo index chỉ định (mặc định là file đầu tiên: index 0)
    target_idx = max(0, min(cv_index, len(cv_files) - 1))
    target_file = cv_files[target_idx]

    print(f"\n Đang chạy kiểm thử phân tích cho: {target_file.name}")
    print(f" Đang xử lý bóc tách và gọi AI Advisor (khoảng 3-5 giây)...", flush=True)

    t0 = time.time()

    # 1. Bóc tách & Chuẩn hóa
    intake = extract_cv(target_file)
    if not intake.is_valid:
        print(f" File CV không hợp lệ: {intake.error_message}")
        return

    sections = parse_cv_sections(intake.clean_text)
    skills = analyze_cv_skills(sections)
    ats_res = evaluate_cv_ats(
        sections=sections,
        all_found_skills=skills.all_found_skills,
        explicit_skills=skills.explicit_skills,
        implicit_skills=skills.implicit_skills,
        archetype="product",
    )

    # 2. Tầng trung gian & LLM Advisor
    md_content = build_markdown_resume(sections, skills, ats_res.missing_skills)
    advisor = LLMAdvisor()
    advice = advisor.suggest_architecture_upgrades(
        projects_text=sections.get("projects", "") or sections.get("experience", ""),
        missing_skills=ats_res.missing_skills,
        all_found_skills=skills.all_found_skills,
        archetype="product",
        structured_markdown=md_content,
        ats_score_result=ats_res,
    )

    elapsed = time.time() - t0
    mode = "Gemini Live API (Online) 🌐" if advisor.is_connected else "Deterministic Engine (Offline) 🛡️"

    # =========================================================================
    # IN KẾT QUẢ ĐẦY ĐỦ NHƯNG NGẮN GỌN
    # =========================================================================
    sep = "═" * 88
    sub_sep = "─" * 88

    print("\n" + sep)
    print(f"       BÁO CÁO PHÂN TÍCH & ĐÁNH GIÁ CV: {target_file.name}")
    print(f"       Chế độ: {mode} | Thời gian xử lý: {elapsed:.1f}s")
    print(sep)

    # 1. ĐIỂM SỐ & XẾP LOẠI
    bd = ats_res.breakdown
    print("\n 1. ĐIỂM SỐ & XẾP LOẠI TỔNG THỂ:")
    print(f"   • Điểm ATS Định lượng : {ats_res.total_score:.1f} / 100 đ")
    print(f"     └─ Chi tiết: Cấu trúc {bd['section_completeness']:.1f}/20 | Kỹ năng {bd['skill_coverage']:.1f}/40 | Chiều sâu {bd['impact_and_metrics']:.1f}/25 | Trình bày {bd['presentation_and_links']:.1f}/15")
    print(f"   • Điểm AI Cố vấn      : {advice.overall_score:.1f} / 100 đ")
    print(f"   • Xếp loại mức độ     : {advice.match_level.upper()} ")
    print(f"   • Đánh giá của AI     : {advice.verdict_summary}")

    # 2. ĐIỂM SÁNG KỸ THUẬT (STRENGTHS)
    print("\n" + sub_sep)
    print(" 2. ĐIỂM SÁNG GHI ĐIỂM (STRENGTHS):")
    if advice.score_reasoning.strengths:
        for idx, s in enumerate(advice.score_reasoning.strengths, 1):
            print(f"   [+] {s}")
    else:
        print("   • Chưa có điểm sáng nổi bật.")

    # 3. ĐIỂM TRỪ / LỖ HỔNG (WEAKNESSES)
    print("\n" + sub_sep)
    print(" 3. ĐIỂM TRỪ CẦN KHẮC PHỤC (WEAKNESSES):")
    if advice.score_reasoning.weaknesses:
        for idx, w in enumerate(advice.score_reasoning.weaknesses, 1):
            print(f"   [-] {w}")
    else:
        print("   • Không phát hiện lỗ hổng lớn.")

    # 4. ĐỀ XUẤT HÀNH ĐỘNG NGẮN GỌN (QUICK ACTIONS)
    print("\n" + sub_sep)
    print(" 4. ĐỀ XUẤT HÀNH ĐỘNG NGẮN GỌN ĐỂ TĂNG ĐIỂM NGAY:")
    recs = advice.short_recommendations if hasattr(advice, "short_recommendations") else getattr(advice, "short_recommedations", [])
    if recs:
        for idx, r in enumerate(recs, 1):
            print(f"   [{idx}] [{r.category.upper()}] (Ưu tiên: {r.priority}): {r.action}")
    else:
        print("   • Hồ sơ đã tối ưu rất tốt.")

    # 5. VIẾT LẠI MÔ TẢ DỰ ÁN GOOGLE XYZ (MẪU TIÊU BIỂU)
    print("\n" + sub_sep)
    print(" 5. MÔ TẢ DỰ ÁN VIẾT LẠI CHUẨN GOOGLE XYZ (MẪU TIÊU BIỂU):")
    if advice.rewritten_project_bullets:
        bullet = advice.rewritten_project_bullets[0]
        print(f"    [Gốc]: \"{bullet.original_description}\"")
        print(f"    [Sửa]: \"{bullet.improved_bullet_point}\"")
        print(f"    [Từ khóa]: {', '.join(bullet.highlighted_skills)}")
        print(f"    [Lý do vượt trội]: {bullet.why_it_is_better}")
    else:
        print("   • Chưa có dòng mô tả cần viết lại.")

    # 6. ĐỀ XUẤT NÂNG CẤP KIẾN TRÚC
    print("\n" + sub_sep)
    print("🛠️ 6. ĐỀ XUẤT NÂNG CẤP KIẾN TRÚC ĐỒ ÁN:")
    if advice.upgrades:
        up = advice.upgrades[0]
        print(f"   • Giải pháp: {up.title}")
        print(f"   • Đồ án áp dụng: {up.target_project} (Bù đắp: {', '.join(up.addressed_skill_gaps)})")
        print(f"   • Tác động định lượng: {up.expected_metrics_impact}")
        print(f"   • Câu hỏi phỏng vấn cần chuẩn bị: {up.interview_talking_points[0] if up.interview_talking_points else 'Giải thích mô hình.'}")
    print(sep + "\n")


if __name__ == "__main__":
    idx = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 0
    run_single_cv_test(idx)
