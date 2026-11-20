import json
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# Khởi tạo an toàn cho google-genai
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


# =====================================================================
# PYDANTIC SCHEMAS CHO CHẶNG 5: ĐÁNH GIÁ, CHẤM ĐIỂM, LÝ GIẢI & ĐỀ XUẤT
# =====================================================================

class QuickRecommendation(BaseModel):
    category: str = Field(
        description="Nhóm đề xuất: Kỹ năng / Kiến trúc đồ án / Số liệu đo lường / Trình bày"
    )
    action: str = Field(
        description="Hành động cụ thể, ngắn gọn ứng viên cần làm ngay để tăng điểm CV"
    )
    priority: str = Field(
        description="Mức độ ưu tiên: Cao / Trung bình / Khuyến khích"
    )


class ScoreReasoning(BaseModel):
    strengths: List[str] = Field(
        description="Danh sách các điểm sáng kỹ thuật nổi bật giúp ứng viên ghi điểm trong mắt nhà tuyển dụng"
    )
    weaknesses: List[str] = Field(
        description="Các lỗ hổng kỹ thuật, thiếu sót kiến trúc hoặc câu từ khiến CV bị trừ điểm"
    )
    detailed_explanation: str = Field(
        description="Lý giải toàn diện, thuyết phục vì sao CV đạt mức điểm này đối với vị trí Backend mục tiêu"
    )


class ArchitectureUpgradeItem(BaseModel):
    title: str = Field(
        description="Tên ngắn gọn của giải pháp nâng cấp kiến trúc (Ví dụ: Thêm Redis Caching theo mô hình Cache-Aside)"
    )
    target_project: str = Field(
        description="Tên đồ án cụ thể trong CV được áp dụng nâng cấp này"
    )
    addressed_skill_gaps: List[str] = Field(
        description="Danh sách các kỹ năng còn thiếu được bù đắp qua giải pháp này (Ví dụ: ['Redis', 'Performance Optimization'])"
    )
    problem_statement: str = Field(
        description="Vấn đề kỹ thuật, điểm nghẽn hiệu năng hoặc lỗ hổng kiến trúc trong đồ án hiện tại"
    )
    technical_solution: str = Field(
        description="Giải thích chi tiết kiến trúc đề xuất và nguyên lý hoạt động"
    )
    implementation_steps: List[str] = Field(
        description="Hướng dẫn các bước triển khai cụ thể từ cài đặt, viết code đến cấu hình"
    )
    expected_metrics_impact: str = Field(
        description="Chỉ số định lượng kỳ vọng đạt được (ms, %, req/s) để ứng viên bổ sung vào CV"
    )
    interview_talking_points: List[str] = Field(
        description="Các điểm kỹ thuật và trade-off then chốt cần trình bày khi nhà tuyển dụng hỏi về giải pháp này"
    )


class ProjectBulletRewrite(BaseModel):
    original_description: str = Field(
        description="Đoạn mô tả ban đầu trích xuất từ CV của ứng viên (hoặc tóm tắt ngắn)"
    )
    improved_bullet_point: str = Field(
        description="Dòng mô tả viết lại chuẩn ATS theo công thức Google XYZ (Action Verb + Kỹ thuật + Metrics)"
    )
    highlighted_skills: List[str] = Field(
        description="Các từ khóa kỹ thuật cốt lõi được lồng ghép nổi bật"
    )
    why_it_is_better: str = Field(
        description="Giải thích ngắn gọn vì sao cách viết mới vượt trội hơn về tính thuyết phục"
    )


class ArchitectureAdviceResult(BaseModel):
    overall_score: float = Field(
        description="Điểm số đánh giá tổng hợp của CV trên thang 100 (kết hợp tiêu chuẩn ATS và chuyên môn Senior Tech Lead)"
    )
    match_level: str = Field(
        description="Xếp loại mức độ sẵn sàng ứng tuyển: 'Excellent Match', 'Good Match', 'Potential Match', hoặc 'Low Match'"
    )
    verdict_summary: str = Field(
        description="Nhận định cô đọng 1-2 câu về hồ sơ của ứng viên đối với vị trí Backend mục tiêu"
    )
    score_reasoning: ScoreReasoning = Field(
        description="Phân tích và lý giải chi tiết vì sao có kết quả điểm như vậy (điểm mạnh, điểm trừ, giải thích)"
    )
    short_recommendations: List[QuickRecommendation] = Field(
        description="Danh sách các đề xuất hành động ngắn gọn, đúng trọng tâm để ứng viên cải thiện điểm số ngay"
    )
    upgrades: List[ArchitectureUpgradeItem] = Field(
        description="Danh sách các giải pháp nâng cấp kiến trúc cụ thể nhằm lấp đầy Skill Gap"
    )
    rewritten_project_bullets: List[ProjectBulletRewrite] = Field(
        description="Danh sách các gạch đầu dòng mô tả dự án được viết lại chuẩn chỉnh theo công thức Google XYZ"
    )

    @property
    def overall_assessment(self) -> str:
        """Tương thích ngược với định dạng cũ."""
        return self.verdict_summary


# SYSTEM PROMPT CHO GEMINI
SYSTEM_PROMPT_CAREER_ADVISOR = """
Bạn là một Senior Tech Lead và Principal Backend Architect chuyên tuyển dụng và phát triển kỹ sư Backend Intern/Fresher.
Nhiệm vụ của bạn là đánh giá toàn diện hồ sơ CV của ứng viên:

1. CHẤM ĐIỂM & XẾP LOẠI (Thang 100):
   - Đưa ra điểm số tổng hợp khách quan và xếp loại (Excellent Match >= 80, Good Match >= 65, Potential Match >= 50, Low Match < 50).
   - Tham khảo điểm số định lượng từ ATS Scorer (nếu có) kết hợp với đánh giá chiều sâu về chất lượng đồ án và tiềm năng kỹ thuật.

2. LÝ GIẢI NGUYÊN NHÂN ĐIỂM SỐ (Minh bạch & Thuyết phục):
   - Chỉ rõ những Điểm mạnh vượt trội (Strengths) giúp ứng viên ghi điểm.
   - Chỉ rõ các Điểm yếu, lỗ hổng kiến trúc hoặc thiếu sót kỹ năng (Weaknesses) khiến ứng viên bị trừ điểm.
   - Viết phần giải thích chi tiết (detailed_explanation) mạch lạc, khách quan.

3. ĐỀ XUẤT NGẮN GỌN BỔ SUNG (Actionable):
   - Đưa ra 3 đến 4 đề xuất hành động ngắn gọn, súc tích (Làm gì, thuộc nhóm nào, mức ưu tiên) để ứng viên có thể sửa đổi và kéo điểm lên ngay.

4. NÂNG CẤP KIẾN TRÚC & VIẾT LẠI MÔ TẢ (Google XYZ):
   - Hướng dẫn cấy ghép công nghệ thiếu (Redis, Docker, CI/CD, Testing...) trực tiếp vào đồ án hiện có, không yêu cầu làm lại từ đầu.
   - Viết lại các dòng mô tả dự án theo công thức Google XYZ: "Đạt được [X], đo lường bằng [Y], thông qua việc làm [Z]" kết hợp Action Verbs mạnh mẽ.
""".strip()


# =====================================================================
# LỚP ĐIỀU PHỐI LLM ADVISOR
# =====================================================================

class LLMAdvisor:
    """
    Module Cố vấn Nghề nghiệp & Kiến trúc Backend sử dụng Gemini API kết hợp Pydantic Structured Outputs.
    Đánh giá toàn diện: Chấm điểm, Lý giải nguyên nhân, Đề xuất ngắn gọn, Nâng cấp đồ án & Viết lại CV.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-flash-lite-latest",
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            env_path = os.path.join(os.getcwd(), ".env")
            if os.path.exists(env_path):
                try:
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            clean_line = line.strip()
                            if clean_line.startswith("GEMINI_API_KEY="):
                                self.api_key = clean_line.split("=", 1)[1].strip().strip('"').strip("'")
                                break
                except Exception:
                    pass

        self.model_name = model_name
        self.client = None

        if self.api_key and GENAI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    @property
    def is_connected(self) -> bool:
        """Kiểm tra Gemini Client đã được khởi tạo thành công hay chưa."""
        return self.client is not None

    def suggest_architecture_upgrades(
        self,
        projects_text: str,
        missing_skills: Dict[str, List[str]],
        all_found_skills: Dict[str, List[str]],
        archetype: str = "product",
        structured_markdown: Optional[str] = None,
        ats_score_result: Optional[Any] = None,
    ) -> ArchitectureAdviceResult:
        """
        Đánh giá toàn diện CV: Chấm điểm, Lý giải nguyên nhân điểm số, Đề xuất ngắn gọn,
        Tư vấn nâng cấp kiến trúc và Viết lại mô tả dự án theo chuẩn Google XYZ.
        """
        if self.client:
            try:
                content_block = (
                    f"### CẤU TRÚC CHI TIẾT CV (MARKDOWN FORMAT):\n{structured_markdown}"
                    if structured_markdown
                    else f"### NỘI DUNG DỰ ÁN TRONG CV:\n{projects_text if projects_text.strip() else '(Ứng viên chưa mô tả chi tiết)'}"
                )

                ats_context = ""
                if ats_score_result:
                    ats_context = f"""
### KẾT QUẢ PHÂN TÍCH ĐỊNH LƯỢNG TỪ ATS SCORER:
- **Điểm ATS tham chiếu:** {getattr(ats_score_result, 'total_score', 'N/A')} / 100
- **Phân loại:** {getattr(ats_score_result, 'match_level', 'N/A')}
- **Chi tiết từng trụ cột:** {json.dumps(getattr(ats_score_result, 'breakdown', {}), ensure_ascii=False)}
- **Lời khuyên từ hệ thống:** {json.dumps(getattr(ats_score_result, 'actionable_feedback', []), ensure_ascii=False)}
"""

                prompt = f"""
# THÔNG TIN PHÂN TÍCH ỨNG VIÊN & ĐỒ ÁN
- **Mô hình công ty mục tiêu:** {archetype.upper()}
- **Kỹ năng đã nhận diện:** {json.dumps(all_found_skills, ensure_ascii=False)}
- **Lỗ hổng kỹ năng cốt lõi (Skill Gap):** {json.dumps(missing_skills, ensure_ascii=False)}
{ats_context}

{content_block}

# YÊU CẦU ĐẦU RA (THEO SCHEMA JSON ĐÃ ĐỊNH NGHĨA):
1. **overall_score & match_level:** Chấm điểm tổng hợp (thang 100) và xếp loại mức độ sẵn sàng ứng tuyển.
2. **verdict_summary:** Đưa ra nhận xét tổng quát ngắn gọn (1-2 câu).
3. **score_reasoning:** Lý giải rõ ràng vì sao có kết quả điểm như vậy:
   - strengths: Những điểm sáng lớn nhất giúp CV ghi điểm.
   - weaknesses: Những thiếu sót, lỗ hổng khiến CV bị trừ điểm.
   - detailed_explanation: Giải thích chi tiết, thuyết phục về mức điểm.
4. **short_recommendations:** Đưa ra 3-4 đề xuất hành động ngắn gọn, đúng trọng tâm để ứng viên tăng điểm ngay.
5. **upgrades:** Đưa ra 2-3 giải pháp nâng cấp kiến trúc thực chiến cho đồ án hiện có.
6. **rewritten_project_bullets:** Viết lại 2-3 dòng mô tả dự án theo chuẩn công thức Google XYZ (Action Verb + Công nghệ + Metrics).
""".strip()

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT_CAREER_ADVISOR,
                        response_mime_type="application/json",
                        response_schema=ArchitectureAdviceResult,
                        temperature=0.3,
                    ),
                )
                if response.parsed:
                    return response.parsed
            except Exception:
                for fb_model in ["gemini-flash-latest", "gemini-3.8-flash"]:
                    try:
                        response = self.client.models.generate_content(
                            model=fb_model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=SYSTEM_PROMPT_CAREER_ADVISOR,
                                response_mime_type="application/json",
                                response_schema=ArchitectureAdviceResult,
                                temperature=0.3,
                            ),
                        )
                        if response.parsed:
                            return response.parsed
                    except Exception:
                        continue

        # Fallback Offline thông minh
        return self._fallback_career_advice(
            projects_text, missing_skills, all_found_skills, archetype, ats_score_result
        )

    def _fallback_career_advice(
        self,
        projects_text: str,
        missing_skills: Dict[str, List[str]],
        all_found_skills: Dict[str, List[str]],
        archetype: str,
        ats_score_result: Optional[Any] = None,
    ) -> ArchitectureAdviceResult:
        """Tạo đánh giá, chấm điểm và lý giải offline khi không có API key."""
        base_score = getattr(ats_score_result, "total_score", 70.0) if ats_score_result else 70.0
        match_level = getattr(ats_score_result, "match_level", "Good Match") if ats_score_result else "Good Match"

        # 1. Tổng hợp điểm mạnh
        strengths = []
        languages = all_found_skills.get("languages", [])
        if languages:
            strengths.append(f"Nắm vững ngôn ngữ backend cốt lõi: {', '.join(languages[:3])}.")
        frameworks = all_found_skills.get("frameworks", [])
        if frameworks:
            strengths.append(f"Đã có kinh nghiệm làm việc với framework: {', '.join(frameworks[:2])}.")
        databases = all_found_skills.get("databases", [])
        if databases:
            strengths.append(f"Đã biết sử dụng cơ sở dữ liệu: {', '.join(databases[:2])}.")
        if not strengths:
            strengths.append("Hồ sơ đã có cấu trúc cơ bản và thể hiện được định hướng nghề nghiệp.")

        # 2. Tổng hợp điểm yếu / Lý do trừ điểm
        weaknesses = []
        missing_flat = [s for lst in missing_skills.values() for s in lst]
        if missing_flat:
            weaknesses.append(f"Còn thiếu hụt một số kỹ năng cốt lõi cho hướng {archetype.title()}: {', '.join(missing_flat[:4])}.")
        if "Redis" in missing_flat or "Caching" in missing_flat:
            weaknesses.append("Đồ án thiếu tầng bộ nhớ đệm (Caching/Redis), truy vấn đang phụ thuộc hoàn toàn vào Database.")
        if "Unit Testing" in missing_flat or "Testing" in missing_flat:
            weaknesses.append("Chưa thể hiện việc viết Unit Test tự động để bảo vệ tính toàn vẹn của mã nguồn.")
        if not weaknesses:
            weaknesses.append("Mô tả đồ án cần bổ sung thêm số liệu định lượng (metrics) để tăng sức thuyết phục.")

        # 3. Đề xuất ngắn gọn bổ sung
        short_recs = [
            QuickRecommendation(
                category="Kiến trúc đồ án",
                action="Tích hợp Redis Caching (Cache-Aside Pattern) cho các API truy vấn thường xuyên.",
                priority="Cao",
            ),
            QuickRecommendation(
                category="Số liệu đo lường",
                action="Bổ sung chỉ số đo lường cụ thể vào dự án (ví dụ: thời gian phản hồi ms, số lượng request/ngày).",
                priority="Cao",
            ),
            QuickRecommendation(
                category="Kỹ năng",
                action="Đóng gói ứng dụng bằng Docker Multi-stage và bổ sung file docker-compose.yml vào repo.",
                priority="Trung bình",
            ),
            QuickRecommendation(
                category="Trình bày",
                action="Đưa link GitHub/GitLab của dự án lên đầu CV để nhà tuyển dụng kiểm chứng mã nguồn.",
                priority="Khuyến khích",
            ),
        ]

        # 4. Giải pháp nâng cấp kiến trúc cụ thể
        upgrades = [
            ArchitectureUpgradeItem(
                title="Tích hợp Redis Caching theo mô hình Cache-Aside",
                target_project="Đồ án Web API / E-commerce chính trong CV",
                addressed_skill_gaps=["Redis", "Performance Optimization"],
                problem_statement="Các API truy vấn danh sách hoặc chi tiết sản phẩm gọi trực tiếp vào cơ sở dữ liệu quan hệ, gây thắt nút cổ chai (I/O Bottleneck) khi lưu lượng truy cập tăng cao.",
                technical_solution="Triển khai tầng đệm Redis Cache đặt trước Database. Áp dụng chiến lược Cache-Aside (Lazy Loading) kèm cơ chế TTL (Time-To-Live) 60s và chủ động xóa Cache (Cache Eviction) khi có cập nhật dữ liệu.",
                implementation_steps=[
                    "Cài đặt và chạy Redis Server qua Docker container.",
                    "Viết middleware/service đệm: kiểm tra key trên Redis trước, nếu Cache Hit thì trả về ngay; nếu Cache Miss thì truy vấn DB rồi set vào Redis.",
                    "Xử lý chống Cache Stampede và Cache Avalanche bằng cách thêm jitter ngẫu nhiên vào thời gian hết hạn (TTL).",
                    "Kiểm thử tải bằng k6 hoặc Apache Benchmark (ab) để đo đạc độ trễ.",
                ],
                expected_metrics_impact="Giảm thời gian phản hồi (p95 latency) từ 250ms xuống dưới 20ms, tăng năng lực xử lý (throughput) gấp 8 lần.",
                interview_talking_points=[
                    "Sự khác biệt giữa chiến lược Cache-Aside, Write-Through và Write-Behind.",
                    "Cách xử lý bài toán Cache Penetration, Cache Avalanche và Cache Stampede.",
                    "Chiến lược đồng bộ dữ liệu giữa Cache và Database để tránh dữ liệu cũ (Stale Data).",
                ],
            ),
            ArchitectureUpgradeItem(
                title="Đóng gói Docker Multi-stage & Tự động hóa CI/CD Pipeline",
                target_project="Dự án Backend API",
                addressed_skill_gaps=["Docker", "CI/CD", "DevOps"],
                problem_statement="Quy trình triển khai thủ công, môi trường phát triển cục bộ không nhất quán với server dẫn đến lỗi 'chạy được trên máy em nhưng lỗi trên server'.",
                technical_solution="Viết Dockerfile chuẩn Multi-stage build nhằm tối ưu hóa dung lượng image. Thiết lập GitHub Actions workflow tự động chạy linter, unit test và build image mỗi khi push code lên nhánh main.",
                implementation_steps=[
                    "Tạo Dockerfile gồm stage build (chứa dev dependencies/compiler) và stage runtime (chỉ chứa file build tối giản trên Alpine Linux).",
                    "Viết file docker-compose.yml kết nối đồng bộ Backend, Database và Cache trong mạng nội bộ cô lập.",
                    "Tạo workflow .github/workflows/ci.yml kích hoạt trên pull request: chạy test tự động và build kiểm tra Docker image.",
                ],
                expected_metrics_impact="Dung lượng Docker image giảm 65% (từ ~800MB xuống ~120MB), thời gian triển khai tự động hóa rút ngắn dưới 3 phút.",
                interview_talking_points=[
                    "Lợi ích của Docker Multi-stage build đối với bảo mật và dung lượng image.",
                    "Cách quản lý biến môi trường an toàn (Secrets/Env vars) trong CI/CD pipeline.",
                ],
            ),
        ]

        # 5. Dòng mô tả viết lại Google XYZ
        rewritten_bullets = [
            ProjectBulletRewrite(
                original_description="Xây dựng API quản lý sản phẩm và hỗ trợ tìm kiếm sản phẩm cho người dùng.",
                improved_bullet_point="Thiết kế và triển khai hệ thống RESTful API sản phẩm tích hợp tầng đệm Redis Cache (mô hình Cache-Aside), tối ưu hóa thời gian phản hồi (p95 latency) từ 250ms xuống dưới 20ms.",
                highlighted_skills=["RESTful API", "Redis", "Cache-Aside", "Latency Optimization"],
                why_it_is_better="Bổ sung Action Verb mạnh ('Thiết kế và triển khai'), công nghệ cụ thể ('Redis', 'Cache-Aside') và số liệu định lượng rõ ràng ('250ms -> 20ms').",
            ),
            ProjectBulletRewrite(
                original_description="Đóng gói dự án và deploy lên server cá nhân.",
                improved_bullet_point="Chuẩn hóa Dockerfile Multi-stage build và thiết lập CI/CD pipeline tự động với GitHub Actions, giúp giảm 65% dung lượng image và rút ngắn chu kỳ release dưới 3 phút.",
                highlighted_skills=["Docker", "Multi-stage build", "CI/CD", "GitHub Actions"],
                why_it_is_better="Thể hiện tư duy DevOps chuyên nghiệp thay vì deploy thủ công, có số liệu chứng minh hiệu quả giảm tải dung lượng image.",
            ),
        ]

        return ArchitectureAdviceResult(
            overall_score=base_score,
            match_level=match_level,
            verdict_summary=f"Hồ sơ của bạn đã có nền tảng tốt cho vị trí Backend {archetype.title()}, tuy nhiên cần lấp đầy một số khoảng trống kỹ thuật để đạt mức điểm xuất sắc.",
            score_reasoning=ScoreReasoning(
                strengths=strengths,
                weaknesses=weaknesses,
                detailed_explanation=f"CV đạt {base_score} điểm ({match_level}) do đã thể hiện tốt các kỹ năng nền tảng cơ bản, nhưng bị trừ điểm ở việc thiếu một số công nghệ thực chiến then chốt (như Caching/Redis hoặc Testing) và các dòng mô tả dự án còn thiếu số liệu đo lường kết quả.",
            ),
            short_recommendations=short_recs,
            upgrades=upgrades,
            rewritten_project_bullets=rewritten_bullets,
        )
