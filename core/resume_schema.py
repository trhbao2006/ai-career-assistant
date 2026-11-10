import json
import re
from typing import Any, Dict, List, Optional
from core.ats_scorer import ATSScoreResult
from core.skills_extractor import SkillExtractionResult


def extract_candidate_name(contact_text: str) -> str:
    """
    Trích xuất tên ứng viên từ khối liên hệ hoặc đầu CV.
    Heuristic: Tìm dòng ngắn (2-5 từ), viết hoa hoặc Title Case, không chứa thông tin liên lạc/từ khóa kỹ thuật.
    Hỗ trợ cả các CV mẫu kiểm thử có placeholder dạng [HỌ VÀ TÊN], [FULL NAME].
    """
    if not contact_text:
        return ""

    # Nhận diện placeholder template kiểm thử
    placeholder_match = re.search(r"\[(HỌ VÀ TÊN|FULL NAME|YOUR NAME|TÊN ỨNG VIÊN|NAME)\]", contact_text, re.IGNORECASE)
    if placeholder_match:
        return placeholder_match.group(0)

    ignored_keywords = [
        "curriculum", "vitae", "resume", "cv", "email", "phone", "sđt",
        "github", "linkedin", "contact", "thông tin", "liên hệ", "address",
        "địa chỉ", "developer", "engineer", "backend", "fresher", "intern",
        "objective", "mục tiêu", "nam", "nữ", "sinh ngày", "dob", "nơi ở",
        "student", "sinh viên", "công ty", "vietnam", "việt nam"
    ]

    for line in contact_text.splitlines()[:6]:
        line_clean = line.strip()
        if not line_clean or len(line_clean) > 40:
            continue

        line_lower = line_clean.lower()
        if any(kw in line_lower for kw in ignored_keywords):
            continue
        if re.search(r"[@\d:/\\.]", line_clean):
            continue

        words = [w for w in line_clean.split() if w]
        if 2 <= len(words) <= 5:
            # Kiểm tra xem có phải tên (tất cả các từ viết hoa chữ đầu hoặc viết hoa toàn bộ)
            if all(w[0].isupper() for w in words):
                return line_clean

    return ""


def extract_contact_info(contact_text: str) -> Dict[str, Any]:
    """Trích xuất tên ứng viên, email, phone, link từ khối contact."""
    name = extract_candidate_name(contact_text)
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", contact_text)
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\b\d{9,11}\b", contact_text)
    
    links = []
    for link_pattern in [r"github\.com/[a-zA-Z0-9_-]+", r"linkedin\.com/in/[a-zA-Z0-9_-]+", r"https?://[^\s]+"]:
        matches = re.findall(link_pattern, contact_text, re.IGNORECASE)
        links.extend(matches)

    return {
        "name": name,
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0) if phone_match else "",
        "links": list(set(links)),
    }


def build_structured_resume(
    sections: Dict[str, str],
    skills_res: SkillExtractionResult,
    ats_res: Optional[ATSScoreResult] = None,
) -> Dict[str, Any]:
    """
    Chuẩn hóa dữ liệu bóc tách của CV theo phong cách JSON Resume Standard (jsonresume.org).
    """
    contact_text = sections.get("contact", "")
    info = extract_contact_info(contact_text)

    # Cấu trúc JSON Resume tiêu chuẩn
    resume_json: Dict[str, Any] = {
        "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
        "basics": {
            "name": info["name"],
            "summary": sections.get("summary", ""),
            "email": info["email"],
            "phone": info["phone"],
            "profiles": [{"network": "Web", "url": l} for l in info["links"]],
            "raw_contact": contact_text,
        },
        "education": sections.get("education", ""),
        "skills": {
            "explicit_skills": skills_res.explicit_skills,
            "implicit_skills": skills_res.implicit_skills,
            "all_found_skills": skills_res.all_found_skills,
        },
        "work": sections.get("experience", ""),
        "projects": sections.get("projects", ""),
        "others": sections.get("others", ""),
    }

    if ats_res:
        resume_json["ats_evaluation"] = {
            "total_score": ats_res.total_score,
            "match_level": ats_res.match_level,
            "archetype": ats_res.archetype,
            "breakdown": ats_res.breakdown,
            "missing_skills": ats_res.missing_skills,
            "unlisted_project_skills": ats_res.unlisted_project_skills,
            "actionable_feedback": ats_res.actionable_feedback,
        }

    return resume_json


def build_markdown_resume(
    sections: Dict[str, str],
    skills_res: SkillExtractionResult,
    missing_skills: Optional[Dict[str, List[str]]] = None,
) -> str:
    """
    Chuyển đổi dữ liệu CV từ dạng text phẳng thành văn bản Markdown có cấu trúc phân cấp chuẩn (#, ##, ###).
    Dùng để làm đầu vào chất lượng cao cho LLM Advisor và cho phép người dùng tải về file resume.md.
    """
    md_lines = []

    # 1. Header & Liên hệ
    name = extract_candidate_name(sections.get("contact", ""))
    title_header = f"# {name.upper()}" if name else "# SƠ YẾU LÝ LỊCH / CURRICULUM VITAE"
    md_lines.append(title_header)

    contact = sections.get("contact", "").strip()
    if contact:
        md_lines.append(f"_{contact.replace(chr(10), ' | ')}_\n")

    # 2. Tóm tắt bản thân
    summary = sections.get("summary", "").strip()
    if summary:
        md_lines.append("## Tóm tắt Mục tiêu Nghề nghiệp (Profile Summary)")
        md_lines.append(summary + "\n")

    # 3. Kỹ năng chuyên môn có cấu trúc
    md_lines.append("## Kỹ năng Chuyên môn (Technical Skills)")
    for category, skill_list in skills_res.all_found_skills.items():
        if skill_list:
            md_lines.append(f"- **{category.replace('_', ' ').title()}:** {', '.join(skill_list)}")

    if missing_skills:
        md_lines.append("\n### Lỗ hổng Kỹ năng Cốt lõi (Skill Gap cần bổ sung):")
        for cat, m_list in missing_skills.items():
            if m_list:
                md_lines.append(f"- **Thiếu hụt [{cat}]:** {', '.join(m_list)}")
    md_lines.append("")

    # 4. Dự án & Đồ án thực tế
    projects = sections.get("projects", "").strip()
    if projects:
        md_lines.append("## Dự án Kỹ thuật & Đồ án (Projects)")
        for line in projects.splitlines():
            line_str = line.strip()
            if line_str:
                if line_str.startswith("-") or line_str.startswith("•"):
                    md_lines.append(f"- {line_str.lstrip('-• ')}")
                else:
                    md_lines.append(f"\n### {line_str}")
        md_lines.append("")

    # 5. Kinh nghiệm làm việc
    experience = sections.get("experience", "").strip()
    if experience:
        md_lines.append("## Kinh nghiệm Làm việc (Experience)")
        for line in experience.splitlines():
            line_str = line.strip()
            if line_str:
                if line_str.startswith("-") or line_str.startswith("•"):
                    md_lines.append(f"- {line_str.lstrip('-• ')}")
                else:
                    md_lines.append(f"\n### {line_str}")
        md_lines.append("")

    # 6. Học vấn
    education = sections.get("education", "").strip()
    if education:
        md_lines.append("## Học vấn (Education)")
        md_lines.append(education + "\n")

    # 7. Khác (Chứng chỉ, giải thưởng)
    others = sections.get("others", "").strip()
    if others:
        md_lines.append("## Chứng chỉ & Hoạt động khác (Certifications & Others)")
        md_lines.append(others + "\n")

    return "\n".join(md_lines).strip()
