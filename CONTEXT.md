# AI Career Assistant — Project Architecture & Status

Bản tóm tắt toàn bộ kiến trúc, quyết định kỹ thuật và trạng thái mã nguồn hiện tại của dự án **AI Career Assistant**.

---

## 1. Tổng quan & Định hướng Kiến trúc
- **Mục tiêu**: Hệ thống phân tích CV, tính điểm ATS, chỉ ra lỗ hổng kỹ năng (Skill Gap), tư vấn nâng cấp kiến trúc đồ án và viết lại mô tả dự án chuẩn ATS (Before vs. After theo chuẩn Google XYZ) cho sinh viên ứng tuyển vị trí **Backend Developer (Intern/Fresher)**.
- **Quyết định phạm vi (Scope Decision)**: Tập trung sâu vào giải bài toán CV & Đồ án thực chiến (đã loại bỏ phần Mock Interview để tối ưu hóa trải nghiệm người dùng và tính tập trung của sản phẩm).
- **Phương pháp tiếp cận**: **Hybrid (Rule-based + Generative AI)**:
  - **Chặng 1–4**: Dùng Rule-based / Heuristics / Regex để đảm bảo tính tất định (Deterministic), tốc độ cực nhanh (< 50ms) và giải trình được (Explainability).
  - **Chặng 5**: Tích hợp Google Gemini API (`google-genai` SDK) kết hợp Pydantic Schemas (Structured Outputs) để tư vấn nâng cấp kiến trúc và viết lại mô tả dự án.
- **Đối tượng phân tích**: Đánh giá theo 3 mô hình công ty (`Product`, `Outsourcing`, `Startup`) hoặc đối chiếu trực tiếp với văn bản Job Description (JD) tải lên.

---

## 2. Cấu trúc Thư mục & Trạng thái các Module

### `config/backend.py` (Đã mở rộng toàn diện & Tối ưu)
- `backend_skills_taxonomy` (alias `backend_skills_tamoxy`): Từ điển phân loại kỹ năng Backend mở rộng gồm 9 nhóm chuyên môn (`languages`, `frameworks`, `databases`, `devops_tools`, `cloud`, `messaging`, `observability`, `security`, `concepts`).
- Đã bổ sung đầy đủ: PHP/Laravel, Go Web Frameworks (Gin/Echo/Fiber), Ruby on Rails, Kotlin, Rust, Hibernate/JPA, MyBatis, Oracle, MariaDB, Firebase/Supabase, Payment Gateways (VNPAY/MoMo/ZaloPay), Database Design & Optimization.
- Đã làm sạch các alias dễ gây nhiễu/bắt nhầm (`aws lambda`, `solid principles`, `server log`).
- `COMPANY_ARCHETYPES`: Bảng trọng số chấm điểm đa mô hình (Product, Outsourcing, Startup) với 9 nhóm kỹ năng (tổng trọng số chuẩn hóa = 1.0 kèm assertion).
- `ARCHETYPE_CORE_SKILLS`: Danh sách kỹ năng cốt lõi cho từng archetype.
- `ACTION_VERBS`: Danh sách động từ hành động kỹ thuật mở rộng song ngữ Anh - Việt.

### `core/intake.py` (Chặng 1 — Hoàn thành & Tối ưu)
- Sử dụng `pymupdf` đọc PDF theo khối tọa độ (`page.get_text("blocks")`).
- **Adaptive Column Detection (`is_two_column_layout`)**: Nhận diện động CV 1 cột (đọc tuần tự tự nhiên) vs CV 2 cột (TopCV, Canva).
- **Full-width Header Preservation**: Tự động nhận diện và bảo toàn khối Header/Banner trải rộng toàn trang ở đầu CV trước khi phân chia cột, chống lỗi đảo lộn tên và thông tin liên hệ.
- Chuẩn hóa Unicode NFKC, xóa ký tự ẩn, chuyển đổi icon TopCV/Canva thành bullet `-`.
- Guardrails: Giới hạn 1–5 trang, tối thiểu 100 ký tự.

### `core/section_parser.py` (Chặng 2 — Hoàn thành & Tối ưu)
- Máy trạng thái hữu hạn (FSM) phân tách CV thành 7 nhóm: `contact`, `summary`, `education`, `skills`, `experience`, `projects`, `others`.
- Kỹ thuật **Condensed Normalization**: Xóa toàn bộ khoảng trắng và dấu câu trang trí trước khi so khớp từ khóa, xử lý triệt để lỗi kerning dãn chữ / vỡ font tiếng Việt của TopCV.
- **False Positive Guard**: Bộ lọc thông minh chặn bắt nhầm câu văn nội dung thành đề mục (chặn các liên từ/giới từ thông thường `STOP_WORDS_IN_HEADER`, giới hạn số từ $\le 6$, chặn dấu phẩy `,` và câu có dấu chấm kết thúc).
- Khớp chính xác từ khóa hoặc chỉ cho phép hậu tố số/La Mã hợp lệ (`duan1`, `projects i`).

### `core/skills_extractor.py` (Chặng 3 — Hoàn thành)
- Pre-compiled Regex Negative Lookaround an toàn cho các từ khóa đặc biệt (`C++`, `C#`, `.NET`, `Java` không trùng `JavaScript`).
- Phân loại rõ ràng **Explicit Skills** (khai báo ở mục Skills), **Implicit Skills** (ẩn trong Projects/Experience nhưng quên ghi ở Skills) và **All Found Skills**.

### `core/ats_scorer.py` (Chặng 4 — Đã hoàn thành & Tối ưu)
- Chấm điểm định lượng thang 100 qua 4 trụ cột:
  1. **Section Completeness (20đ)**: 4 mục cơ bản contact, education, skills, exp/projects.
  2. **Skill Coverage & Skill Gap (40đ)**: Tính độ phủ theo trọng số archetype hoặc JD; logic thông minh cho nhóm ngôn ngữ (không ép buộc học cả 4 thứ tiếng nếu đã vững 1 ngôn ngữ cốt lõi). Xử lý an toàn Custom JD khi ít từ khóa nhận diện, tự động fallback về Archetype kèm cảnh báo minh bạch.
  3. **Impact & Metrics (25đ)**: Quét regex tìm số liệu định lượng (`%`, `ms`, `req/ngày`, `users`, `x`) và đếm `ACTION_VERBS`.
  4. **Presentation & Consistency (15đ)**: Quét link GitHub/GitLab/LinkedIn ở contact, summary và projects; trừ điểm nếu để kỹ năng thực tế bị trôi dạt (Implicit skills).
- Trả về DTO `ATSScoreResult` kèm phân hạng (`Excellent` / `Good` / `Low Match`) và `actionable_feedback`.

### `core/resume_schema.py` (Tầng Chuẩn hóa Trung gian — Hoàn thành & Tối ưu)
- **Candidate Name Extraction (`extract_candidate_name`)**: Trích xuất họ tên ứng viên từ header/contact (hỗ trợ cả các mẫu test có token `[HỌ VÀ TÊN]`, `[FULL NAME]`).
- **JSON Resume Standard (`build_structured_resume`)**: Chuẩn hóa toàn bộ dữ liệu bóc tách của CV theo schema chuẩn quốc tế `jsonresume.org` (basics kèm name, email, phone, links, education, skills, work, projects, ats_evaluation). Sẵn sàng serialize lưu SQLite ở Chặng 6 và cho phép tải về `resume.json`.
- **Structured Markdown (`build_markdown_resume`)**: Chuyển đổi CV sang văn bản Markdown sạch với cấu trúc phân cấp (#, ##, ###, bullets) có tên ứng viên ở tiêu đề, phục vụ làm đầu vào tối ưu cho LLM Advisor ở Chặng 5 và xuất file `resume.md`.

### `core/llm_advisor.py` (Chặng 5 — Đã hoàn thành & Tinh gọn)
- Sử dụng Google GenAI SDK (`from google import genai`) kết hợp Pydantic Schemas (`response_schema`) cho Structured Outputs:
  1. **Architecture Upgrade Advisor (`suggest_architecture_upgrades`)**: Nhận đầu vào là Structured Markdown và Skill Gap để gợi ý tích hợp trực tiếp Caching Redis, Docker Multi-stage, CI/CD, Unit Testing... kèm chỉ số định lượng (Metrics).
  2. **Before vs. After Project Rewrite (`ProjectBulletRewrite`)**: Viết lại mô tả dự án theo chuẩn công thức Google XYZ (Action Verb + Nhiệm vụ kỹ thuật + Số liệu đo lường) để ứng viên copy thẳng vào CV.
  3. **Deterministic Fallback Engine**: Tự động chuyển sang chế độ offline thông minh khi không có API key hoặc mất mạng.

### `tests/` (Bộ kiểm thử tự động & Báo cáo Bảng ASCII)
- `test_utils.py`: Tiện ích tự động quét tất cả file PDF trong `tests/CV Test/` hoặc `tests/` và render bảng ASCII đẹp mắt.
- `test_intake.py`: Bảng kiểm thử Chặng 1 (Trạng thái, Số trang, Số ký tự, Preview).
- `test_section_parser.py`: Bảng ma trận kiểm thử Chặng 2 (Tỷ lệ bóc tách 7 sections trên toàn bộ CV).
- `test_skills_extractor.py`: Bảng kiểm thử Chặng 3 (Thống kê 5 nhóm taxonomy, Explicit vs. Implicit skills).
- `test_ats_scorer.py`: Bảng điểm ATS 4 trụ cột và so sánh đa mô hình (Product, Outsourcing, Startup, Custom JD).
- `test_resume_schema.py`: Bảng kiểm thử Tầng trung gian (Email, Phone, Links, JSON Resume, Structured Markdown).
- `test_llm_advisor.py`: Bảng kiểm thử Chặng 5 (Đề xuất kiến trúc & So sánh Before vs. After theo chuẩn Google XYZ).
- Đã cấu hình UTF-8 console output chạy mượt mà trên Windows PowerShell/CMD.

---

## 3. Kế hoạch Chặng 6 (Đóng gói Sản phẩm End-to-End)
- **`core/database.py`**: Thiết kế cơ sở dữ liệu SQLite cục bộ để lưu trữ lịch sử các phiên phân tích CV, điểm số ATS và các đề xuất nâng cấp kiến trúc / viết lại dự án.
- **`app.py`**: Thiết kế giao diện trực quan bằng **Streamlit**:
  - Tab 1: Upload CV (PDF) + Chọn Archetype / Dán JD $\rightarrow$ Dashboard điểm ATS 4 trụ cột, biểu đồ radar / progress bars, Skill Gap.
  - Tab 2: Nâng cấp kiến trúc đồ án $\rightarrow$ Thẻ giải pháp nâng cấp cụ thể (Problem, Solution, Implementation, Metrics Impact).
  - Tab 3: Viết lại CV (Before vs. After) $\rightarrow$ Thẻ so sánh trực quan dòng mô tả cũ và dòng mô tả mới chuẩn ATS, có nút Copy nhanh 1-click.
