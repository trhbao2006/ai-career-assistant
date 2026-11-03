import json
import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

# Khởi tạo an toàn cho google-genai
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


# =====================================================================
# PYDANTIC SCHEMAS CHO CHẶNG 5: ARCHITECTURE ADVICE & CV REWRITE
# =====================================================================

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
    overall_assessment: str = Field(
        description="Đánh giá tổng quan hiện trạng kiến trúc các đồ án trong CV của ứng viên"
    )
    upgrades: List[ArchitectureUpgradeItem] = Field(
        description="Danh sách các giải pháp nâng cấp kiến trúc cụ thể nhằm lấp đầy Skill Gap"
    )
    rewritten_project_bullets: List[ProjectBulletRewrite] = Field(
        description="Danh sách các gạch đầu dòng mô tả dự án được viết lại chuẩn chỉnh để ứng viên copy thẳng vào CV"
    )


# SYSTEM PROMPT CHO GEMINI
SYSTEM_PROMPT_ARCH_ADVISOR = """
Bạn là một Principal Backend Architect và Tech Lead dày dặn kinh nghiệm, chuyên hướng dẫn các kỹ sư Backend Intern/Fresher nâng cấp đồ án cá nhân để vượt qua các kỳ tuyển dụng khắt khe.
Nhiệm vụ của bạn là phân tích nội dung các dự án trong CV của ứng viên, đối chiếu với danh sách các kỹ năng còn thiếu (Skill Gap) và mô hình công ty mục tiêu để đưa ra các đề xuất nâng cấp kiến trúc THỰC CHIẾN và KHẢ THI.

Nguyên tắc tư vấn:
1. KHÔNG yêu cầu ứng viên làm lại đồ án mới từ đầu. Hãy hướng dẫn cách tích hợp công nghệ mới (Redis, Docker, CI/CD, Message Queue, Indexing, Unit Testing...) trực tiếp vào đồ án hiện có.
2. Mỗi đề xuất phải gắn liền với bài toán thực tế (hiệu năng, nghẽn I/O, độ sẵn sàng, tính mở rộng), có các bước triển khai chi tiết và chỉ số định lượng (Metrics) rõ ràng.
3. Viết lại các dòng mô tả dự án (Before vs. After) chuẩn công thức Google XYZ: "Đạt được [X], đo lường bằng [Y], thông qua việc làm [Z]" kết hợp Action Verbs mạnh mẽ để ứng viên đưa thẳng vào CV.
""".strip()


# =====================================================================
# LỚP ĐIỀU PHỐI LLM ADVISOR
# =====================================================================

class LLMAdvisor:
    """
    Module Cố vấn Kiến trúc & Tối ưu Đồ án Backend sử dụng Gemini API kết hợp Pydantic Structured Outputs.
    Tự động hỗ trợ Fallback chất lượng cao khi không có API Key hoặc chạy offline.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-flash-lite-latest",
    ):
        # 1. Đọc key từ tham số, biến môi trường hoặc file .env
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
    ) -> ArchitectureAdviceResult:
        """
        Phân tích đồ án trong CV và đưa ra giải pháp nâng cấp kiến trúc kèm các bullet points viết lại.
        Hỗ trợ đầu vào Structured Markdown để LLM hiểu cấu trúc phân cấp sâu sắc hơn.
        """
        if self.client:
            try:
                # Sử dụng nội dung Markdown có cấu trúc nếu có, giúp LLM hiểu phân cấp đề mục
                content_block = (
                    f"### CẤU TRÚC CHI TIẾT ĐỒ ÁN (MARKDOWN FORMAT):\n{structured_markdown}"
                    if structured_markdown
                    else f"### NỘI DUNG DỰ ÁN TRONG CV:\n{projects_text if projects_text.strip() else '(Ứng viên chưa mô tả chi tiết)'}"
                )

                prompt = f"""
# THÔNG TIN PHÂN TÍCH ỨNG VIÊN & ĐỒ ÁN HIỆN TẠI
- **Mô hình công ty mục tiêu:** {archetype.upper()}
- **Kỹ năng hiện có:** {json.dumps(all_found_skills, ensure_ascii=False)}
- **Lỗ hổng kỹ năng cốt lõi (Skill Gap):** {json.dumps(missing_skills, ensure_ascii=False)}

{content_block}

# YÊU CẦU ĐẦU RA:
1. Đưa ra 2 đến 3 giải pháp nâng cấp kiến trúc cụ thể nhằm tích hợp trực tiếp các công nghệ thiếu vào đồ án hiện tại.
2. Viết lại 2 đến 3 dòng mô tả dự án theo chuẩn công thức Google XYZ (Action Verb + Công nghệ + Metrics) để ứng viên copy vào CV.
""".strip()

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT_ARCH_ADVISOR,
                        response_mime_type="application/json",
                        response_schema=ArchitectureAdviceResult,
                        temperature=0.3,
                    ),
                )
                if response.parsed:
                    return response.parsed
            except Exception:
                # Dự phòng tự động chuyển sang các model khả dụng khác nếu model chính gặp lỗi
                for fb_model in ["gemini-flash-latest", "gemini-3.8-flash"]:
                    try:
                        response = self.client.models.generate_content(
                            model=fb_model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=SYSTEM_PROMPT_ARCH_ADVISOR,
                                response_mime_type="application/json",
                                response_schema=ArchitectureAdviceResult,
                                temperature=0.3,
                            ),
                        )
                        if response.parsed:
                            return response.parsed
                    except Exception:
                        continue

        # Fallback Offline chất lượng cao dựa trên missing_skills và rule-based template
        return self._fallback_architecture_advice(projects_text, missing_skills, archetype)

    def _fallback_architecture_advice(
        self,
        projects_text: str,
        missing_skills: Dict[str, List[str]],
        archetype: str,
    ) -> ArchitectureAdviceResult:
        """Tạo gợi ý nâng cấp kiến trúc offline khi không có API key."""
        upgrades = []

        # 1. Nếu thiếu Redis hoặc Caching
        missing_dbs = missing_skills.get("databases", [])
        if "Redis" in missing_dbs or any("redis" in s.lower() for s in missing_dbs) or not missing_skills:
            upgrades.append(
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
                )
            )

        # 2. Nếu thiếu Docker / CI-CD
        missing_devops = missing_skills.get("devops_tools", [])
        if "Docker" in missing_devops or "CI/CD" in missing_devops or len(upgrades) < 2:
            upgrades.append(
                ArchitectureUpgradeItem(
                    title="Đóng gói Docker Multi-stage & Tự động hóa CI/CD Pipeline",
                    target_project="Dự án Backend API",
                    addressed_skill_gaps=["Docker", "CI/CD", "DevOps"],
                    problem_statement="Quy trình triển khai thủ công, môi trường phát triển cục bộ không nhất quán với môi trường server dẫn đến lỗi 'chạy được trên máy em nhưng lỗi trên production'.",
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
                )
            )

        # 3. Nếu thiếu Unit Testing
        missing_concepts = missing_skills.get("concepts", [])
        if "Unit Testing" in missing_concepts or len(upgrades) < 3:
            upgrades.append(
                ArchitectureUpgradeItem(
                    title="Bổ sung tầng Unit Testing & Mocking cho Business Logic",
                    target_project="Tầng Service của ứng dụng",
                    addressed_skill_gaps=["Unit Testing", "Clean Architecture"],
                    problem_statement="Ứng dụng thiếu kiểm thử tự động, dẫn đến nguy cơ hồi quy (regression bugs) mỗi khi bổ sung tính năng hoặc tái cấu trúc code.",
                    technical_solution="Áp dụng kiểm thử đơn vị độc lập cho toàn bộ các hàm nghiệp vụ trọng yếu (tính tiền, xác thực, trừ hàng tồn kho), sử dụng Mocking để cô lập Database.",
                    implementation_steps=[
                        "Cài đặt test framework (pytest cho Python / Jest cho Node.js / JUnit cho Java).",
                        "Áp dụng Dependency Injection hoặc Mock library để giả lập phản hồi của Database Repository.",
                        "Viết test cases bao phủ cả kịch bản thành công (Happy Path) lẫn các trường hợp biên và ngoại lệ (Edge Cases/Exceptions).",
                    ],
                    expected_metrics_impact="Đạt độ bao phủ kiểm thử (Code Coverage) trên 80% cho tầng Service nghiệp vụ cốt lõi.",
                    interview_talking_points=[
                        "Phân biệt Unit Test, Integration Test và E2E Test (Mô hình Kim tự tháp Test).",
                        "Nguyên tắc viết test F.I.R.S.T và cách mock external services hiệu quả.",
                    ],
                )
            )

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
            ProjectBulletRewrite(
                original_description="Viết code xử lý đơn hàng và thanh toán giỏ hàng.",
                improved_bullet_point="Xây dựng module thanh toán và trừ kho an toàn với Unit Testing đạt 80% Code Coverage, áp dụng Idempotency Key xử lý hơn 1,000 giao dịch thử nghiệm không xảy ra trùng lặp.",
                highlighted_skills=["Unit Testing", "Code Coverage", "Idempotency", "Data Consistency"],
                why_it_is_better="Chứng minh khả năng bảo vệ dữ liệu tài chính trong hệ thống Backend thực tế qua kiểm thử và tính bình luân (Idempotency).",
            ),
        ]

        return ArchitectureAdviceResult(
            overall_assessment=f"Đồ án hiện tại của bạn đã có khung sườn backend cơ bản nhưng còn mang tính chất nguyên khối (Monolith) đơn giản, thiếu các thành phần đảm bảo độ tin cậy và hiệu năng cao chuẩn {archetype.title()}. Các giải pháp dưới đây sẽ giúp bạn tích hợp công nghệ còn thiếu vào ngay đồ án hiện tại.",
            upgrades=upgrades,
            rewritten_project_bullets=rewritten_bullets,
        )
