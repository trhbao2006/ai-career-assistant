# AI Career Assistant — Project Architecture & Status

Bản tóm tắt toàn bộ kiến trúc, quyết định kỹ thuật và trạng thái mã nguồn hiện tại của dự án **AI Career Assistant**.

---

## 1. Tổng quan & Định hướng Kiến trúc
- **Mục tiêu**: Hệ thống phân tích CV, tính điểm ATS, chỉ ra lỗ hổng kỹ năng (Skill Gap), tư vấn nâng cấp kiến trúc đồ án và viết lại mô tả dự án chuẩn ATS (Before vs. After theo chuẩn Google XYZ) cho sinh viên/ứng viên.
- **Mở rộng phạm vi (Scope Expansion)**:
  - **Hướng 1 (Lõi)**: Trợ lý CV theo nhóm ngành (**Kinh tế, Y tế, Giáo dục, IT**), kết hợp bộ nhận diện ngành và taxonomy kỹ năng trích từ dữ liệu thực tế.
  - **Hướng 3 (Mở rộng)**: Tư vấn chuyển ngành sang vị trí công nghệ ít code / IT-lite (Business Analyst, Data Analyst, QA/QC Tester...).
- **Phương pháp tiếp cận**: **Hybrid (Rule-based + Generative AI + Data-Driven Benchmark)**:
  - **Chặng 1–4**: Dùng Rule-based / Heuristics / Regex để đảm bảo tính tất định (Deterministic), tốc độ cực nhanh (< 50ms) và giải trình được (Explainability).
  - **Tầng dữ liệu chuẩn đối sánh (`dataset/`, không đưa lên GitHub)**: Đã hợp nhất & làm sạch từ 4 dataset gốc thành 3 nhóm phục vụ 3 vai trò riêng biệt (xem `dataset/README.md` và `dataset/dataset_manifest.json`).
  - **Chặng 5**: Tích hợp Google Gemini API (`google-genai` SDK) kết hợp Pydantic Schemas (Structured Outputs) để tư vấn nâng cấp kiến trúc (cho IT) hoặc Tái cấu trúc kinh nghiệm (Re-framing Experience) & đề xuất đồ án nghiệp vụ thay thế (cho người chuyển ngành / IT-lite).
- **Đối tượng phân tích**: Đánh giá theo đa mô hình công ty (`Product`, `Outsourcing`, `Startup`) hoặc đối chiếu trực tiếp với văn bản Job Description (JD) tải lên.

---

## 2. Cấu trúc Thư mục & Trạng thái các Module

### `dataset/` (Thư mục dữ liệu hợp nhất cục bộ — nằm trong `.gitignore`)
- `1_domain_resumes/`: `2.481` CV tiếng Anh (24 ngành → 5 nhóm: Kinh tế 700, Y tế 232, IT 120, Giáo dục 102, Khác 1.327), đã bỏ placeholder và cắt tiêu đề lộ nhãn (`text_no_title`).
- `2_vn_real_pdfs/`: `934` PDF CV Việt Nam thật (515 `it_domain`, 419 `non_it_domain`, khử trùng MD5 0% chồng chéo, lọc bỏ PDF scan & >5 trang) + `vn_resumes_index.csv` đã ẩn danh PII cơ bản.
- `3_ats_fit_benchmark/`: `6.228` cặp train + `1.759` cặp test CV–JD (nhãn `No Fit` / `Potential Fit` / `Good Fit`), đã loại mâu thuẫn nhãn và khôi phục xuống dòng sau heading.

### `config/taxonomies/backend.py` (Đã module hóa)
- `backend_skills_taxonomy`: Từ điển phân loại kỹ năng Backend mở rộng gồm 9 nhóm chuyên môn.
- `COMPANY_ARCHETYPES`: Bảng trọng số chấm điểm đa mô hình (Product, Outsourcing, Startup).
- `ARCHETYPE_CORE_SKILLS`: Danh sách kỹ năng cốt lõi cho từng archetype.
- `ACTION_VERBS`: Danh sách động từ hành động kỹ thuật mở rộng song ngữ Anh - Việt.

### `core/intake.py` (Chặng 1 — Hoàn thành & Đã nghiệm thu trên Dataset 2.484 CV)
- Sử dụng `pymupdf` đọc PDF theo khối tọa độ (`page.get_text("blocks")`).
- **Adaptive Column Detection**: Nhận diện động CV 1 cột vs CV 2 cột.
- **Full-width Header Preservation**: Bảo toàn khối Header/Banner trải rộng toàn trang ở đầu CV.
- Chuẩn hóa Unicode NFKC, xóa ký tự ẩn, chuyển đổi icon thành bullet `-`.

### `core/section_parser.py` (Chặng 2 — Hoàn thành & Đã nghiệm thu trên Dataset 2.484 CV)
- Máy trạng thái hữu hạn (FSM) phân tách CV thành 7 nhóm: `contact`, `summary`, `education`, `skills`, `experience`, `projects`, `others`.
- Kỹ thuật **Condensed Normalization**: Xử lý triệt để lỗi kerning dãn chữ / vỡ font.
- **False Positive Guard**: Bộ lọc thông minh chặn bắt nhầm câu văn nội dung thành đề mục.

### `core/skills_extractor.py` (Chặng 3 — Hoàn thành)
- Pre-compiled Regex Negative Lookaround an toàn cho các từ khóa đặc biệt.
- Phân loại rõ ràng **Explicit Skills**, **Implicit Skills** và **All Found Skills**.

### `core/ats_scorer.py` (Chặng 4 — Hoàn thành & Chuẩn bị tích hợp Fallback)
- Chấm điểm định lượng thang 100 qua 4 trụ cột:
  1. **Section Completeness (20đ)**.
  2. **Skill Coverage & Skill Gap (40đ)** kèm cơ chế Anti-Keyword Stuffing.
  3. **Impact & Metrics (25đ)**.
  4. **Presentation & Consistency (15đ)**.

### `core/resume_schema.py` (Tầng Chuẩn hóa Trung gian — Hoàn thành)
- **Candidate Name Extraction**: Trích xuất họ tên ứng viên từ header/contact.
- **JSON Resume Standard**: Chuẩn hóa dữ liệu theo chuẩn `jsonresume.org`.
- **Structured Markdown**: Chuyển đổi CV sang văn bản Markdown sạch tối ưu làm context cho LLM.

### `core/llm_advisor.py` (Chặng 5 — Hoàn thành & Chuẩn bị mở rộng Transition Mode)
- Sử dụng Google GenAI SDK kết hợp Pydantic Schemas cho Structured Outputs:
  1. **Architecture Upgrade Advisor**: Đề xuất giải pháp kiến trúc kèm Metrics.
  2. **Before vs. After Project Rewrite**: Viết lại dòng mô tả dự án theo chuẩn Google XYZ.
  3. **Deterministic Fallback Engine**: Tự động chuyển sang chế độ offline khi không có API key.

---

## 3. Kế hoạch Hoàn thiện Chặng 6 & Đa ngành
1. **Module hóa Taxonomy**: Tách cấu hình kỹ năng thành các file theo vai trò (Backend, Business Analyst, Data Analyst, QA Tester).
2. **Fallback Projects trong Scorer**: Tự động tính điểm dự án từ `experience` khi không có section `projects`.
3. **Transition Mode trong LLM Advisor**: Tư vấn tái cấu trúc kinh nghiệm cũ (Re-framing) cho ứng viên trái ngành.
4. **`app.py`**: Xây dựng Dashboard Streamlit hoàn chỉnh (Upload CV $\rightarrow$ Radar Chart $\rightarrow$ Đề xuất kiến trúc / Viết lại dự án $\rightarrow$ Xuất báo cáo).
