import os
import time

try:
    import pytest
    skip_live_llm = pytest.mark.skipif(
        os.getenv("RUN_LIVE_LLM_TEST") != "true",
        reason="Bỏ qua gọi live Gemini API khi chạy pytest hàng loạt. Chạy riêng bằng: python -m tests.test_llm_advisor"
    )
except ImportError:
    def skip_live_llm(func):
        return func

from core.intake import extract_cv
from core.section_parser import parse_cv_sections
from core.skills_extractor import analyze_cv_skills
from core.ats_scorer import evaluate_cv_ats
from core.resume_schema import build_markdown_resume
from core.llm_advisor import LLMAdvisor
from tests.test_utils import get_test_cvs, render_table, truncate_text


@skip_live_llm
def test_stage5_samples():
    cv_files = get_test_cvs()
    if not cv_files:
        print("❌ Không tìm thấy file PDF nào!")
        return

    advisor = LLMAdvisor()
    mode = "Gemini Live API (Online) 🌐" if advisor.is_connected else "Deterministic Fallback Engine (Offline) 🛡️"

    print(f"\n🚀 Khởi chạy Kiểm thử Chặng 5: Đánh giá, Chấm điểm, Lý giải & Đề xuất Nâng cấp")
    print(f"📡 Chế độ hoạt động: {mode}")
    print(f"📂 Đang phân tích lần lượt {len(cv_files)} CV mẫu (ước tính ~3-5s mỗi file)...\n", flush=True)

    # =========================================================================
    # PHẦN 1: BẢNG TỔNG HỢP KIỂM THỬ TRÊN TOÀN BỘ CV
    # =========================================================================
    headers_summary = [
        "STT",
        "Tên File CV",
        "Điểm AI",
        "Xếp loại",
        "Điểm sáng chính (Strengths)",
        "Điểm trừ chính (Weaknesses)",
        "Đề xuất",
        "Chế độ",
    ]
    alignments_summary = ["center", "left", "center", "center", "left", "left", "center", "center"]
    rows_summary = []

    featured_advice = None
    featured_file = ""

    for idx, pdf_path in enumerate(cv_files, 1):
        t0 = time.time()
        print(f"   ⏳ [{idx}/{len(cv_files)}] Phân tích: {pdf_path.name[:28]}...", end=" ", flush=True)

        intake = extract_cv(pdf_path)
        if not intake.is_valid:
            print("⚠️ (Bỏ qua - file không hợp lệ)", flush=True)
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

        md_content = build_markdown_resume(sections, skills, ats_res.missing_skills)

        advice = advisor.suggest_architecture_upgrades(
            projects_text=sections.get("projects", "") or sections.get("experience", ""),
            missing_skills=ats_res.missing_skills,
            all_found_skills=skills.all_found_skills,
            archetype="product",
            structured_markdown=md_content,
            ats_score_result=ats_res,
        )

        elapsed = time.time() - t0
        print(f"✅ Xong ({elapsed:.1f}s)", flush=True)

        str_preview = truncate_text(advice.score_reasoning.strengths[0], 30) if advice.score_reasoning.strengths else "—"
        weak_preview = truncate_text(advice.score_reasoning.weaknesses[0], 30) if advice.score_reasoning.weaknesses else "—"

        rows_summary.append([
            str(idx),
            truncate_text(pdf_path.name, 26),
            f"{advice.overall_score:.1f} đ",
            advice.match_level,
            str_preview,
            weak_preview,
            f"{len(advice.short_recommedations if hasattr(advice, 'short_recommedations') else advice.short_recommendations)} mục",
            "Gemini" if advisor.is_connected else "Fallback",
        ])

        if not featured_advice and advice.overall_score >= 80:
            featured_advice = advice
            featured_file = pdf_path.name

    # In Bảng ma trận tổng hợp
    render_table(
        headers=headers_summary,
        rows=rows_summary,
        title=f"KẾT QUẢ KIỂM THỬ CHẶNG 5: ĐÁNH GIÁ & CHẤM ĐIỂM TOÀN BỘ {len(cv_files)} CV ({mode})",
        alignments=alignments_summary,
    )

    # Nếu chưa chọn được file tiêu biểu thì lấy file đầu tiên
    if not featured_advice and cv_files:
        intake = extract_cv(cv_files[0])
        sections = parse_cv_sections(intake.clean_text)
        skills = analyze_cv_skills(sections)
        ats_res = evaluate_cv_ats(sections, skills.all_found_skills, skills.explicit_skills, skills.implicit_skills, "product")
        md_content = build_markdown_resume(sections, skills, ats_res.missing_skills)
        featured_advice = advisor.suggest_architecture_upgrades(
            sections.get("projects", ""), ats_res.missing_skills, skills.all_found_skills, "product", md_content, ats_res
        )
        featured_file = cv_files[0].name

    # =========================================================================
    # PHẦN 2: CHI TIẾT ĐÁNH GIÁ, CHẤM ĐIỂM & LÝ GIẢI NGUYÊN NHÂN ĐIỂM SỐ
    # =========================================================================
    print("\n" + "=" * 95)
    print(f"  CHI TIẾT ĐẦY ĐỦ: ĐÁNH GIÁ, CHẤM ĐIỂM & LÝ GIẢI NGUYÊN NHÂN (File: {featured_file})  ")
    print("=" * 95)

    print(f"\n📊 ĐIỂM SỐ ĐÁNH GIÁ TỔNG HỢP: {featured_advice.overall_score:.1f} / 100 điểm")
    print(f"🎯 XẾP LOẠI MỨC ĐỘ PHÙ HỢP : {featured_advice.match_level}")
    print(f"💬 NHẬN ĐỊNH CỦA CHUYÊN GIA : {featured_advice.verdict_summary}\n")

    print("┌─────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("│ LÝ GIẢI VÌ SAO CÓ KẾT QUẢ ĐIỂM NHƯ VẬY (SCORE REASONING):                                   │")
    print("└─────────────────────────────────────────────────────────────────────────────────────────────┘")
    print("  🌟 ĐIỂM MẠNH GIÚP CV GHI ĐIỂM:")
    for s in featured_advice.score_reasoning.strengths:
        print(f"     + {s}")

    print("\n  ⚠️ ĐIỂM THIẾU SÓT / LỖ HỔNG KHIẾN BỊ MẤT ĐIỂM:")
    for w in featured_advice.score_reasoning.weaknesses:
        print(f"     - {w}")

    print(f"\n  🔍 LÝ GIẢI CHI TIẾT TỪ TECH LEAD:\n     {featured_advice.score_reasoning.detailed_explanation}\n")

    # =========================================================================
    # PHẦN 3: CÁC ĐỀ XUẤT HÀNH ĐỘNG NGẮN GỌN ĐỂ TĂNG ĐIỂM (QUICK RECOMMENDATIONS)
    # =========================================================================
    print("┌─────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("│ CÁC ĐỀ XUẤT BỔ SUNG NGẮN GỌN ĐỂ CẢI THIỆN ĐIỂM SỐ NGAY:                                     │")
    print("└─────────────────────────────────────────────────────────────────────────────────────────────┘")
    for idx, rec in enumerate(featured_advice.short_recommendations, 1):
        print(f"  [{idx}] [{rec.category.upper()}] (Ưu tiên: {rec.priority}):")
        print(f"      👉 {rec.action}")
    print()

    # =========================================================================
    # PHẦN 4: ĐOẠN TRÍCH ĐẦY ĐỦ CÁC DÒNG MÔ TẢ CV VIẾT LẠI (BEFORE vs. AFTER)
    # =========================================================================
    print("=" * 95)
    print(f"  CHI TIẾT: CÁC DÒNG MÔ TẢ DỰ ÁN VIẾT LẠI CHUẨN GOOGLE XYZ (File: {featured_file})  ")
    print("=" * 95)

    for idx, bullet in enumerate(featured_advice.rewritten_project_bullets, 1):
        print(f"\n┌─────────────────────────────────────────────────────────────────────────────────────────────┐")
        print(f"│ MẪU SỐ {idx}: SO SÁNH TRỰC DIỆN BEFORE vs. AFTER                                            │")
        print(f"└─────────────────────────────────────────────────────────────────────────────────────────────┘")
        print(f"  🔴 [TRƯỚC - CV GỐC]:")
        print(f"     \"{bullet.original_description}\"\n")
        print(f"  🟢 [SAU - VIẾT LẠI CHUẨN ATS (GOOGLE XYZ)]:")
        print(f"     \"{bullet.improved_bullet_point}\"\n")
        print(f"  🔑 [TỪ KHÓA KỸ THUẬT LỒNG GHÉP]: {', '.join(bullet.highlighted_skills)}")
        print(f"  💡 [VÌ SAO CÁCH VIẾT NÀY VƯỢT TRỘI]:\n     {bullet.why_it_is_better}")
        print("─" * 95)

    # =========================================================================
    # PHẦN 5: ĐỀ XUẤT NÂNG CẤP KIẾN TRÚC & CÂU HỎI PHỎNG VẤN
    # =========================================================================
    print("\n" + "=" * 95)
    print(f"  CHI TIẾT: CÁC GIẢI PHÁP NÂNG CẤP KIẾN TRÚC ĐỒ ÁN THỰC CHIẾN (File: {featured_file})   ")
    print("=" * 95)

    for idx, up in enumerate(featured_advice.upgrades, 1):
        print(f"┌─────────────────────────────────────────────────────────────────────────────────────────────┐")
        print(f"│ GIẢI PHÁP #{idx}: {up.title.upper()} ")
        print(f"└─────────────────────────────────────────────────────────────────────────────────────────────┘")
        print(f"  🎯 Đồ án áp dụng    : {up.target_project}")
        print(f"  🛠️  Công nghệ bổ sung : {', '.join(up.addressed_skill_gaps)}")
        print(f"\n  ⚠️  Điểm nghẽn hiệu năng (Problem Statement):")
        print(f"     {up.problem_statement}")
        print(f"\n  💡 Giải pháp kỹ thuật (Technical Solution):")
        print(f"     {up.technical_solution}")
        print(f"\n  📋 Hướng dẫn triển khai từng bước:")
        for step_idx, step in enumerate(up.implementation_steps, 1):
            print(f"     {step_idx}. {step}")
        print(f"\n  📈 Chỉ số định lượng kỳ vọng (Metrics Impact):")
        print(f"     👉 {up.expected_metrics_impact}")
        print(f"\n  🗣️  Điểm then chốt cần chuẩn bị khi phỏng vấn:")
        for pt in up.interview_talking_points:
            print(f"     • {pt}")
        print("\n" + "─" * 95 + "\n")


if __name__ == "__main__":
    test_stage5_samples()
