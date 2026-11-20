import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from config.taxonomies.backend import (
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
    unlisted_project_skills: List[str]      # Kỹ năng có làm trong đồ án nhưng quên ghi vào mục Skills (Implicit)
    actionable_feedback: List[str]          # Các lời khuyên sửa CV cụ thể

    @property
    def unlisted_Project_skills(self) -> List[str]:
        """Tương thích ngược với định dạng cũ."""
        return self.unlisted_project_skills


# =========================================================================
# DANH MỤC THUẬT NGỮ KỸ THUẬT BACKEND (CHỐNG CÂU VĂN SÁO RỖNG / BOILERPLATE)
# =========================================================================
BACKEND_TECHNICAL_TERMS = {
    "crud", "index", "indexing", "schema", "jwt", "token", "middleware",
    "caching", "cache", "migration", "migrations", "api", "apis", "endpoint",
    "endpoints", "restful", "rest", "rest api", "auth", "authentication",
    "authorization", "transaction", "transactions", "acid", "query", "queries",
    "orm", "async", "asynchronous", "webhook", "webhooks", "microservice",
    "microservices", "docker", "pipeline", "queue", "payload", "validation",
    "mvc", "clean architecture", "repository", "unit test", "websocket",
    "websockets", "cors", "session", "oauth", "oauth2", "redis", "sql",
    "nosql", "sharding", "replica", "replication", "kafka", "rabbitmq",
    "ci/cd", "ci-cd", "pagination", "rate limiting"
}


def extract_backend_terms(text: str) -> List[str]:
    """Trích xuất các thuật ngữ chuyên môn backend thực tế trong bài viết."""
    text_lower = text.lower()
    found = []
    for term in BACKEND_TECHNICAL_TERMS:
        escaped = re.escape(term)
        pattern = rf"(?<![a-zA-Z0-9_]){escaped}(?![a-zA-Z0-9_])"
        if re.search(pattern, text_lower):
            found.append(term)
    return found


# =========================================================================
# QUY TẮC NHẬN DIỆN VÀ XÁC THỰC PROFILE LINK (GITHUB / LINKEDIN)
# =========================================================================
PLACEHOLDER_URL_PATTERNS = [
    r"github\.com/(?:your-?username|your-?name|username|example|user|account|abc)\b",
    r"gitlab\.com/(?:your-?username|your-?name|username|example)\b",
    r"linkedin\.com/in/(?:your-?name|username|example|abc)\b",
]

ANONYMIZED_LINK_PATTERNS = [
    r"\[(?:github|portfolio|linkedin|link)[^\]]*\]",
    r"\b(?:your_github|link_github|your_linkedin)\b",
]


def check_profile_link(text: str) -> Tuple[float, Optional[str]]:
    """
    Kiểm tra và xác thực liên kết GitHub/GitLab/LinkedIn:
    - Nhận diện link thật, link placeholder, link ẩn danh, và link chết (404).
    Trả về: (điểm_số_tối_đa_5, feedback)
    """
    url_matches = re.findall(
        r"(?:https?://)?(?:www\.)?((?:github\.com|gitlab\.com|linkedin\.com)/[a-zA-Z0-9_\-\./]+)",
        text,
        re.IGNORECASE,
    )

    anon_matches = []
    for p in ANONYMIZED_LINK_PATTERNS:
        anon_matches.extend(re.findall(p, text, re.IGNORECASE))

    if not url_matches and not anon_matches:
        return 0.0, "Nên bổ sung link GitHub hoặc LinkedIn vào phần thông tin liên hệ để nhà tuyển dụng kiểm chứng code."

    if url_matches:
        for url in url_matches:
            is_placeholder = any(re.search(p, url, re.IGNORECASE) for p in PLACEHOLDER_URL_PATTERNS)
            if is_placeholder:
                return 2.5, f"Phát hiện đường dẫn dạng mẫu (placeholder): '{url}'. Vui lòng thay bằng liên kết thật của bạn để ghi điểm tối đa."

            full_url = url if url.startswith(("http://", "https://")) else f"https://{url}"
            try:
                req = urllib.request.Request(
                    full_url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                    method="HEAD",
                )
                with urllib.request.urlopen(req, timeout=1.2) as resp:
                    if resp.status == 200:
                        return 5.0, None
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return 1.0, f"Đường dẫn [{url}] trả về mã lỗi 404 (Link chết hoặc repository/profile đang ở chế độ Private). Hãy kiểm tra lại chế độ Public!"
                return 5.0, None
            except Exception:
                # Chế độ offline/timeout: chấp nhận định dạng hợp lệ
                return 5.0, None

        return 5.0, None

    if anon_matches:
        return 3.5, f"Nhận diện liên kết dạng ẩn danh trong CV mẫu: '{anon_matches[0]}'. Đừng quên điền link GitHub/LinkedIn thật khi gửi tuyển dụng."

    return 0.0, "Nên bổ sung link GitHub hoặc LinkedIn vào phần thông tin liên hệ."


# =========================================================================
# TRỤ CỘT 1: ĐỘ HOÀN THIỆN CẤU TRÚC CV (Tối đa 20 điểm)
# =========================================================================
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

    # Chấp nhận linh hoạt alias gộp Projects / Experience trên CV 1 trang
    has_exp = bool(sections.get("experience", "").strip())
    has_proj = bool(sections.get("projects", "").strip())
    if has_exp or has_proj:
        score += 5.0
    else:
        feedback.append("Thiếu mục Kinh nghiệm (Experience) hoặc Dự án (Projects).")

    return score, feedback


# =========================================================================
# TRỤ CỘT 2: ĐỘ PHỦ KỸ NĂNG & CHỐNG KEYWORD STUFFING (Tối đa 40 điểm)
# =========================================================================
def score_skill_coverage(
    all_found_skills: Dict[str, List[str]],
    archetype: str = "product",
    jd_text: Optional[str] = None,
    project_skills: Optional[Dict[str, List[str]]] = None,
) -> Tuple[float, Dict[str, List[str]], List[str]]:
    archetype_key = archetype.lower()
    weights = COMPANY_ARCHETYPES.get(archetype_key, COMPANY_ARCHETYPES["product"])
    core_reqs = ARCHETYPE_CORE_SKILLS.get(archetype_key, ARCHETYPE_CORE_SKILLS["product"])

    jd_skills = extract_skills(jd_text) if jd_text else {}
    jd_total_skills = sum(len(skills) for skills in jd_skills.values()) if jd_skills else 0
    use_jd_mode = bool(jd_text and jd_total_skills >= 2)

    score = 0.0
    missing_skills: Dict[str, List[str]] = {}
    feedback = []

    if jd_text and not use_jd_mode:
        feedback.append(
            f"Văn bản JD cung cấp chỉ nhận diện được {jd_total_skills} kỹ năng Backend cốt lõi. "
            f"Hệ thống tự động đối chiếu theo tiêu chuẩn mô hình {archetype.title()} để đảm bảo khách quan."
        )

    # Chỉ tiêu kỹ năng kỳ vọng đối với Fresher/Intern
    TARGET_COUNT = {
        "languages": 1,
        "frameworks": 2,
        "databases": 2,
        "devops_tools": 2,
        "concepts": 2,
        "cloud": 1,
        "messaging": 1,
        "observability": 1,
        "security": 1,
    }

    for category, weight in weights.items():
        found_set = set(all_found_skills.get(category, []))
        proj_set = set(project_skills.get(category, [])) if project_skills else None

        # CHỐNG KEYWORD STUFFING: Đối chiếu ngược với Đồ án/Kinh nghiệm
        if proj_set is not None and found_set:
            verified_skills = [s for s in found_set if s in proj_set]
            unverified_skills = [s for s in found_set if s not in proj_set]
            # Hạ trọng số kỹ năng không có trong dự án xuống 60%
            n_actual = len(verified_skills) + 0.6 * len(unverified_skills)

            if len(unverified_skills) >= 2:
                feedback.append(
                    f"Cảnh báo Keyword Stuffing ở nhóm [{category}]: Các kỹ năng [{', '.join(unverified_skills)}] "
                    f"chỉ được liệt kê ở mục Kỹ năng mà không xuất hiện trong mô tả Đồ án/Kinh nghiệm. "
                    f"Hãy đưa công nghệ này vào dự án thực tế để đạt điểm tối đa."
                )
        else:
            n_actual = float(len(found_set))

        # Xác định target_set và expected_num
        if use_jd_mode and jd_skills.get(category):
            target_set = set(jd_skills[category])
            expected_num = max(len(target_set), 1)
            missing = sorted(list(target_set - found_set))
            if missing:
                missing_skills[category] = missing
        else:
            target_set = set(core_reqs.get(category, []))
            if target_set:
                expected_num = min(len(target_set), TARGET_COUNT.get(category, 2))
                if category == "languages":
                    core_matched = found_set & target_set
                    if not core_matched:
                        missing_skills[category] = sorted(list(target_set))
                else:
                    missing = sorted(list(target_set - found_set))
                    if missing and len(found_set) < expected_num:
                        missing_skills[category] = missing
            else:
                expected_num = 0

        # Áp dụng công thức chuẩn hóa đề xuất:
        # Score_category = 40 * W_i * min(N_actual / max(N_expected, 1), 1.0)
        if expected_num > 0:
            ratio = min(n_actual / max(expected_num, 1), 1.0)
        else:
            # Danh mục không bắt buộc ở Archetype này: mặc định đạt 1.0
            ratio = 1.0

        score += 40.0 * weight * ratio

        if expected_num > 0 and ratio < 0.5:
            feedback.append(
                f"Nhóm kỹ năng [{category}] đang thiếu hụt cho hướng {archetype.title()} "
                f"(Mới có {len(found_set)}/{expected_num} kỹ năng kỳ vọng)."
            )

    return round(score, 1), missing_skills, feedback


# =========================================================================
# TRỤ CỘT 3: CHIỀU SÂU KỸ THUẬT, ACTION VERBS & SỐ LIỆU (Tối đa 25 điểm)
# =========================================================================
def score_impact_and_metrics(sections: Dict[str, str]) -> Tuple[float, List[str]]:
    score = 0.0
    feedback = []

    exp_proj_text = f"{sections.get('experience', '')}\n{sections.get('projects', '')}".strip()
    if not exp_proj_text:
        return 0.0, ["Mục Dự án/Kinh nghiệm chưa có nội dung. Đây là phần quan trọng nhất để nhà tuyển dụng đánh giá năng lực làm việc."]

    desc_lines = [line.strip() for line in exp_proj_text.splitlines() if len(line.strip()) > 15]
    char_len = len(exp_proj_text)
    backend_terms = extract_backend_terms(exp_proj_text)

    # 1. Đánh giá tính chi tiết & Chiều sâu kỹ thuật (Tối đa 10 điểm)
    # Chống câu văn dài dòng sáo rỗng: Bắt buộc phải chứa thuật ngữ chuyên môn Backend
    if (len(desc_lines) >= 4 or char_len >= 300) and len(backend_terms) >= 2:
        score += 10.0
    elif (len(desc_lines) >= 4 or char_len >= 300) and len(backend_terms) == 1:
        score += 8.5
        feedback.append(
            "Mô tả dự án có độ dài tốt nhưng nên bổ sung thêm các thuật ngữ kỹ thuật chuyên sâu (ví dụ: schema, JWT, caching, migration, middleware, transaction...)."
        )
    elif (len(desc_lines) >= 4 or char_len >= 300) and len(backend_terms) == 0:
        # Dài dòng nhưng không có thuật ngữ backend nào (câu văn sáo rỗng)
        score += 5.0
        feedback.append(
            "Cảnh báo nội dung sáo rỗng: Mô tả dự án có độ dài nhưng thiếu hoàn toàn các thuật ngữ chuyên môn Backend "
            "(như CRUD, RESTful API, Schema, Index, JWT, Middleware, Caching...). Cần tập trung vào giải pháp kỹ thuật thay vì mô tả chung chung."
        )
    elif (len(desc_lines) >= 2 or char_len >= 120) and len(backend_terms) >= 1:
        score += 7.0
        feedback.append("Nên mô tả chi tiết hơn về các tính năng kỹ thuật và bài toán backend trong đồ án (bổ sung thêm 2-3 gạch đầu dòng cụ thể).")
    elif len(desc_lines) >= 2 or char_len >= 120:
        score += 5.0
        feedback.append("Mô tả dự án còn ngắn và thiếu thuật ngữ kỹ thuật chuyên môn.")
    else:
        score += 3.0
        feedback.append("Nội dung mô tả đồ án còn khá ngắn và sơ sài, cần viết rõ các module/tính năng kỹ thuật bạn đã trực tiếp xây dựng.")

    # 2. Quét Động từ hành động mạnh - Action Verbs (Tối đa 8 điểm)
    text_lower = exp_proj_text.lower()
    matched_verbs = [v for v in ACTION_VERBS if v in text_lower]

    if len(matched_verbs) >= 3:
        score += 8.0
    elif len(matched_verbs) >= 1:
        score += 5.0
        feedback.append("Nên sử dụng thêm các động từ hành động kỹ thuật (Thiết kế, Tối ưu, Triển khai, Built, Optimized...) để lời văn chủ động và chuyên nghiệp hơn.")
    else:
        score += 2.0
        feedback.append("Cách viết mô tả dự án còn thụ động, nên mở đầu mỗi gạch đầu dòng bằng một động từ hành động kỹ thuật.")

    # 3. Quét số liệu đo lường & Tác động định lượng (Tối đa 7 điểm - Điểm cộng khuyến khích cho Fresher)
    metrics_pattern = re.compile(
        r"(\d+([.,]\d+)?\s*(%|ms|s|giây|request|req|rps|tps|users|người dùng|bản ghi|records|apis|endpoints|tables|x\b)|giảm\s+\d+|tăng\s+\d+|rút ngắn|tối ưu\s+\d+)",
        re.IGNORECASE,
    )
    matches = metrics_pattern.findall(exp_proj_text)
    metric_count = len(matches)

    if metric_count >= 2:
        score += 7.0
    elif metric_count == 1:
        score += 5.0
        feedback.append(f"Đã có {metric_count} số liệu trong dự án. Nếu bổ sung thêm 1-2 chỉ số nữa (ví dụ: lượng request, latency ms, số lượng API), CV sẽ nổi bật hơn.")
    else:
        # Điểm sàn nhân văn cho Fresher
        score += 2.0
        feedback.append("Đối với vị trí Fresher, nếu bổ sung được số liệu đo lường cụ thể (như số lượng API endpoints, thời gian phản hồi ms, hoặc số lượng người dùng thử nghiệm) thì CV của bạn sẽ vượt trội hơn hẳn so với ứng viên khác.")

    return round(score, 1), feedback


# =========================================================================
# TRỤ CỘT 4: TRÌNH BÀY, LIÊN KẾT & TÍNH NHẤT QUÁN (Tối đa 15 điểm)
# =========================================================================
def score_presentation_and_consistency(
    sections: Dict[str, str],
    explicit_skills: Dict[str, List[str]],
    implicit_skills: Dict[str, List[str]],
) -> Tuple[float, List[str], List[str]]:
    score = 0.0
    feedback = []

    search_text = f"{sections.get('contact', '')}\n{sections.get('summary', '')}\n{sections.get('projects', '')}"

    # 1. Kiểm tra & Xác thực link GitHub / Portfolio / LinkedIn (5 điểm)
    link_score, link_fb = check_profile_link(search_text)
    score += link_score
    if link_fb:
        feedback.append(link_fb)

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

    return round(score, 1), unlisted, feedback


# =========================================================================
# HÀM ĐIỀU PHỐI CHÍNH (MAIN ATS ORCHESTRATOR)
# =========================================================================
def evaluate_cv_ats(
    sections: Dict[str, str],
    all_found_skills: Dict[str, List[str]],
    explicit_skills: Dict[str, List[str]],
    implicit_skills: Dict[str, List[str]],
    archetype: str = "product",
    jd_text: Optional[str] = None,
    project_skills: Optional[Dict[str, List[str]]] = None,
) -> ATSScoreResult:
    # Nếu chưa truyền project_skills, tự động trích xuất từ projects và experience
    if project_skills is None:
        project_exp_text = f"{sections.get('projects', '')}\n{sections.get('experience', '')}".strip()
        project_skills = extract_skills(project_exp_text)

    s_struct, fb_struct = score_section_completeness(sections)
    s_skill, missing_skills, fb_skill = score_skill_coverage(
        all_found_skills=all_found_skills,
        archetype=archetype,
        jd_text=jd_text,
        project_skills=project_skills,
    )
    s_impact, fb_impact = score_impact_and_metrics(sections)
    s_pres, unlisted_skills, fb_pres = score_presentation_and_consistency(
        sections, explicit_skills, implicit_skills
    )

    total_score = round(s_struct + s_skill + s_impact + s_pres, 1)

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
        unlisted_project_skills=unlisted_skills,
        actionable_feedback=all_feedback,
    )
