import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from config.backend import (
    COMPANY_ARCHETYPES,
    ARCHETYPE_CORE_SKILLS,
    ACTION_VERBS,
)
from core.skills_extractor import extract_skills


@dataclass
class ATSScoreResult:
    total_score: float                      # Tổng điểm thang 100
    match_level: str                        # Phân loại: Excellent / Good / Low Match
    archetype: str                          # Mô hình công ty mục tiêu
    breakdown: Dict[str, float]             # Điểm chi tiết từng trụ cột
    missing_skills: Dict[str, List[str]]    # Các kỹ năng quan trọng còn thiếu (Skill Gap)
    unlisted_Project_skills: List[str]      # Kỹ năng có làm trong đồ án nhưng quên ghi vào mục Skills (Implicit)
    actionable_feedback: List[str]          # Các lời khuyên sửa CV cụ thể


# Trụ cột 1: Độ hoàn thiện cấu trúc CV (Tối đa 20 điểm)
def score_section_completeness(sections: Dict[str, str]) -> Tuple[float, List[str]]:
    score = 0.0
    feedback = []

    if sections.get("contact", "").strip():
        score += 5.0
    else:
        feedback.append("Thiếu thông tin liên hệ (Email, SĐT) ở đầu CV.")

    if sections.get("education", "").strip():
        score += 5.0
    else:
        feedback.append("Thiếu mục Học vấn (Education).")

    if sections.get("skills", "").strip():
        score += 5.0
    else:
        feedback.append("Thiếu mục Kỹ năng (Skills) tách biệt — ATS sẽ khó quét từ khóa.")

    has_exp = bool(sections.get("experience", "").strip())
    has_proj = bool(sections.get("projects", "").strip())
    if has_exp or has_proj:
        score += 5.0
    else:
        feedback.append("Thiếu mục Kinh nghiệm (Experience) hoặc Dự án (Projects).")

    return score, feedback


# Trụ cột 2: Độ phủ Kỹ năng & Phân tích Skill Gap (Tối đa 40 điểm)
def score_skill_coverage(
    all_found_skills: Dict[str, List[str]],
    archetype: str = "product",
    jd_text: Optional[str] = None,
) -> Tuple[float, Dict[str, List[str]], List[str]]:
    archetype_key = archetype.lower()
    weights = COMPANY_ARCHETYPES.get(archetype_key, COMPANY_ARCHETYPES["product"])
    core_reqs = ARCHETYPE_CORE_SKILLS.get(archetype_key, ARCHETYPE_CORE_SKILLS["product"])

    # Nếu người dùng có upload thêm JD (học từ ý tưởng app.py nhưng dùng Regex chuẩn của Chặng 3)
    jd_skills = extract_skills(jd_text) if jd_text else {}

    score = 0.0
    missing_skills: Dict[str, List[str]] = {}
    feedback = []

    # Số lượng kỹ năng kỳ vọng đạt điểm tối đa ở mỗi nhóm đối với Fresher/Intern
    TARGET_COUNT = {
        "languages": 2,
        "frameworks": 2,
        "databases": 2,
        "devops_tools": 2,
        "concepts": 2,
    }

    for category, weight in weights.items():
        found_set = set(all_found_skills.get(category, []))

        # Xác định tập kỹ năng mục tiêu cần kiểm tra Skill Gap
        if jd_text and jd_skills.get(category):
            target_set = set(jd_skills[category])
            expected_num = len(target_set)
        else:
            target_set = set(core_reqs.get(category, []))
            expected_num = TARGET_COUNT.get(category, 2)

        # Tính Skill Gap bằng phép hiệu tập hợp (Set Difference)
        missing = sorted(list(target_set - found_set))
        if missing:
            missing_skills[category] = missing

        # Tính tỷ lệ phủ kỹ năng của nhóm này
        if expected_num > 0:
            ratio = min(len(found_set) / expected_num, 1.0)
        else:
            ratio = 1.0

        score += 40.0 * weight * ratio

        if ratio < 0.5:
            feedback.append(
                f"Nhóm kỹ năng [{category}] đang thiếu hụt cho hướng {archetype.title()} "
                f"(Mới có {len(found_set)}/{expected_num} kỹ năng kỳ vọng)."
            )

    return round(score, 1), missing_skills, feedback


# Trụ cột 3: Tác động định lượng (Metrics) & Động từ hành động (Tối đa 25 điểm)
def score_impact_and_metrics(sections: Dict[str, str]) -> Tuple[float, List[str]]:
    score = 0.0
    feedback = []

    exp_proj_text = f"{sections.get('experience', '')}\n{sections.get('projects', '')}".strip()
    if not exp_proj_text:
        return 0.0, ["Không có nội dung Dự án/Kinh nghiệm để chấm mức độ tác động (Impact)."]

    # uét số liệu đo lường kết quả (Tối đa 15 điểm)
    # Bắt: 30%, 200ms, 900ms -> 250ms, 10.000 request/ngày, 500+ users, 2x...
    metrics_pattern = re.compile(
        r"(\d+([.,]\d+)?\s*(%|ms|s|giây|request|req|rps|tps|users|người dùng|x\b)|giảm\s+\d+|tăng\s+\d+|rút ngắn)",
        re.IGNORECASE,
    )
    matches = metrics_pattern.findall(exp_proj_text)
    metric_count = len(matches)

    if metric_count >= 3:
        score += 15.0
    elif metric_count >= 1:
        score += 8.0
        feedback.append(
            f"Đã có {metric_count} số liệu định lượng trong dự án, nhưng nên bổ sung thêm (ít nhất 3 chỉ số như %, ms, lượng request)."
        )
    else:
        feedback.append(
            "Mô tả dự án hoàn toàn thiếu số liệu định lượng (%, ms, số lượng request/users) chứng minh kết quả."
        )

    # 2. Quét Động từ hành động mạnh - Action Verbs (Tối đa 10 điểm)
    text_lower = exp_proj_text.lower()
    matched_verbs = [v for v in ACTION_VERBS if v in text_lower]

    if len(matched_verbs) >= 4:
        score += 10.0
    elif len(matched_verbs) >= 2:
        score += 5.0
        feedback.append("Nên sử dụng đa dạng hơn các động từ hành động mạnh (Thiết kế, Tối ưu, Triển khai, Optimized, Built...).")
    else:
        feedback.append("Cách viết mô tả dự án còn thụ động, thiếu các động từ hành động kỹ thuật (Action Verbs).")

    return score, feedback


# Trụ cột 4: Trình bày, Liên kết & Tính nhất quán kỹ năng (Tối đa 15 điểm)
def score_presentation_and_consistency(
    sections: Dict[str, str],
    explicit_skills: Dict[str, List[str]],
    implicit_skills: Dict[str, List[str]],
) -> Tuple[float, List[str], List[str]]:
    score = 0.0
    feedback = []

    full_contact = f"{sections.get('contact', '')}\n{sections.get('summary', '')}"

    # 1. Kiểm tra link GitHub / Portfolio / LinkedIn (5 điểm)
    has_profile_link = bool(
        re.search(r"(github\.com|gitlab\.com|linkedin\.com)", full_contact, re.IGNORECASE)
    )
    if has_profile_link:
        score += 5.0
    else:
        feedback.append("Nên bổ sung link GitHub hoặc LinkedIn vào phần thông tin liên hệ để nhà tuyển dụng kiểm chứng code.")

    # 2. Tính nhất quán giữa mục Skills (Explicit) và Projects (Implicit) (10 điểm)
    unlisted = []
    for cat, sk_list in implicit_skills.items():
        unlisted.extend(sk_list)

    explicit_total = sum(len(v) for v in explicit_skills.values())

    if explicit_total > 0 and len(unlisted) == 0:
        score += 10.0
    elif explicit_total > 0 and len(unlisted) > 0:
        score += 6.0
        feedback.append(
            f"Phát hiện {len(unlisted)} kỹ năng bạn có dùng trong Dự án nhưng quên liệt kê ở mục Kỹ năng: {', '.join(unlisted[:5])}."
        )
    else:
        score += 2.0
        feedback.append("Toàn bộ kỹ năng đang nằm rải rác trong bài viết, cần gom lên mục Kỹ năng (Skills).")

    return score, unlisted, feedback


# Hàm điều phối chính (Main Orchestrator)
def evaluate_cv_ats(
    sections: Dict[str, str],
    all_found_skills: Dict[str, List[str]],
    explicit_skills: Dict[str, List[str]],
    implicit_skills: Dict[str, List[str]],
    archetype: str = "product",
    jd_text: Optional[str] = None,
) -> ATSScoreResult:
    s_struct, fb_struct = score_section_completeness(sections)
    s_skill, missing_skills, fb_skill = score_skill_coverage(all_found_skills, archetype, jd_text)
    s_impact, fb_impact = score_impact_and_metrics(sections)
    s_pres, unlisted_skills, fb_pres = score_presentation_and_consistency(
        sections, explicit_skills, implicit_skills
    )

    total_score = round(s_struct + s_skill + s_impact + s_pres, 1)

    # Phân hạng ngưỡng đánh giá (học từ cấu trúc phân loại của app.py)
    if total_score >= 80:
        match_level = "Excellent Match"
    elif total_score >= 60:
        match_level = "Good Match"
    else:
        match_level = "Low Match"

    all_feedback = fb_struct + fb_skill + fb_impact + fb_pres

    return ATSScoreResult(
        total_score=total_score,
        match_level=match_level,
        archetype=archetype,
        breakdown={
            "section_completeness": s_struct,     # /20
            "skill_coverage": s_skill,            # /40
            "impact_and_metrics": s_impact,       # /25
            "presentation_and_links": s_pres,     # /15
        },
        missing_skills=missing_skills,
        unlisted_Project_skills=unlisted_skills,
        actionable_feedback=all_feedback,
    )