# AI Career Assistant

> **Hệ thống Hybrid AI phân tích CV, định lượng điểm ATS, tư vấn nâng cấp kiến trúc đồ án và tối ưu hóa mô tả dự án chuẩn Google XYZ dành cho Backend Developer (Intern/Fresher).**

---

## 1. Giới thiệu Tổng quan

Trong thị trường tuyển dụng công nghệ hiện nay, hơn **70% CV của sinh viên IT bị loại ngay từ vòng lọc tự động (ATS - Applicant Tracking System)** do:
- Định dạng layout 2 cột phức tạp khiến máy quét đọc dính dòng ziczac.
- Mô tả dự án sơ sài, thiếu số liệu định lượng (Metrics), chỉ dừng lại ở CRUD cơ bản.
- Không đồng bộ giữa kỹ năng tự khai báo và kỹ năng thực chiến làm trong dự án.

**AI Career Assistant** được phát triển theo triết lý **Kiến trúc Hybrid (Kỹ thuật phần mềm truyền thống + Generative AI hiện đại)**:
- **Chặng 1–4 (Deterministic Core):** Sử dụng Rule-based, Heuristics, Regex Negative Lookaround và Lý thuyết tập hợp toán học để đảm bảo tính **tất định 100%, tốc độ phản hồi cực nhanh (< 50ms), tốn 0 đồng chi phí API** và có khả năng giải trình minh bạch từng tiêu chí điểm.
- **Tầng Chuẩn hóa Trung gian (IR Layer):** Đóng gói dữ liệu phi cấu trúc thành chuẩn quốc tế **JSON Resume (`jsonresume.org`)** và **Structured Markdown**.
- **Chặng 5 (Generative AI Engine):** Tận dụng **Google Gemini API** (`google-genai` SDK) kết hợp **Pydantic v2 Structured Outputs** để đóng vai một Principal Backend Architect: phân tích điểm nghẽn hiệu năng của đồ án hiện tại, hướng dẫn cấy ghép công nghệ thiếu (Redis, Docker, CI/CD, Unit Testing) và viết lại từng gạch đầu dòng dự án theo công thức Google XYZ.

---

## 2. Kiến trúc Hệ thống (Pipeline 5 Chặng)

```
[File PDF CV ứng viên]
          │
          ▼
┌────────────────────────────────────────────────────────────────────────┐
│ CHẶNG 1: INTAKE & LAYOUT PARSER (core/intake.py)                       │
│ • Phân tách 2 cột theo tọa độ khối (split_x = 0.38 * width)            │
│ • Chuẩn hóa Unicode NFKC, gỡ ligature (fi, fl) & dọn icon TopCV        │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ clean_text (Text sạch, đúng thứ tự)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ CHẶNG 2: SECTION PARSER FSM (core/section_parser.py)                   │
│ • Kỹ thuật Condensed Normalization: Xóa sạch khoảng trắng dãn chữ      │
│ • Máy trạng thái (FSM) phân tách chính xác 7 vùng thông tin            │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ sections: Dict[str, str]
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ CHẶNG 3: SKILLS EXTRACTOR (core/skills_extractor.py)                   │
│ • Taxonomy 3 tầng với 38 kỹ năng Backend cốt lõi                       │
│ • Pre-compiled Negative Lookaround Regex (an toàn với C++, C#, .NET)   │
│ • Phân định 2 tầng: Explicit Skills vs. Implicit Skills (kỹ năng ẩn)   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ SkillExtractionResult
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ CHẶNG 4: ATS SCORER & SKILL GAP (core/ats_scorer.py)                   │
│ • Chấm điểm định lượng 100đ qua 4 trụ cột có khả năng giải trình       │
│ • Phân tích Skill Gap đa mô hình: Product / Outsourcing / Startup / JD │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ ATSScoreResult
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ TẦNG CHUẨN HÓA TRUNG GIAN (core/resume_schema.py)                      │
│ • build_structured_resume() -> Xuất chuẩn mở JSON Resume (.json)       │
│ • build_markdown_resume()   -> Xuất chuẩn Structured Markdown (.md)    │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Structured Markdown + missing_skills
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ CHẶNG 5: LLM ADVISOR (core/llm_advisor.py)                             │
│ • Gemini Live API + Pydantic Structured Outputs (Auto-Fallback an toàn)│
│ • 1. Tư vấn Nâng cấp Kiến trúc Đồ án (Redis, Docker, Indexing, Test)   │
│ • 2. Viết lại Mô tả Dự án Before vs. After (Google XYZ Formula)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Các Điểm Sáng Kỹ Thuật Từng Chặng

### 🔹 Chặng 1: Intake & Tiền xử lý PDF Chống vỡ Layout (`core/intake.py`)
- **Thuật toán chia 2 cột tọa độ:** Đọc danh sách block văn bản từ `pymupdf`, phân chia tại tọa độ $x = 38\%$ chiều rộng trang. Sắp xếp độc lập cột trái và cột phải theo trục dọc $y_0$, đọc trọn vẹn cột trái rồi mới sang cột phải $\rightarrow$ *Triệt tiêu 100% lỗi đọc ziczac làm dính dòng ngang trên CV TopCV/Canva.*
- **Chuẩn hóa chuỗi đa tầng:** Ép kiểu Unicode NFKC, xóa bỏ ký tự ẩn (`\u200b`, `\xa0`), chuyển đổi mã icon font đặc thù của TopCV (`\uf095`, `\uf133`, `\uf3c5`) thành bullet `-`.
- **Hàng rào bảo vệ (Guardrails):** Chặn file ngoài khoảng $1 - 5$ trang hoặc $< 100$ ký tự (loại trừ PDF ảnh scan).

### 🔹 Chặng 2: Bóc tách Cấu trúc CV FSM (`core/section_parser.py`)
- **Kỹ thuật Condensed Normalization:** TopCV thường chèn khoảng trắng ngẫu nhiên vào tiêu đề (như `"HỌ C  V Ấ N"`, `"KỸ   N Ă NG"`). Hệ thống xóa sạch toàn bộ `\s\-_:•.()[]|/` và chuyển về chữ thường $\rightarrow$ tự động quy về dạng nén duy nhất (`"họcvấn"`, `"kỹnăng"`), trị dứt điểm lỗi vỡ font.
- **Bộ lọc Heuristics 4 tầng:** Lọc theo độ dài $\le 50$ ký tự, chặn câu văn có dấu chấm kết thúc `.` để tránh bắt nhầm câu văn thường thành tiêu đề.
- **Máy trạng thái hữu hạn (FSM):** Bóc tách CV thành 7 vùng ngữ nghĩa chuẩn: `contact`, `summary`, `education`, `skills`, `experience`, `projects`, `others`.

### 🔹 Chặng 3: Trích xuất Kỹ năng Chuyên sâu (`core/skills_extractor.py`)
- **Taxonomy Backend 3 tầng (`config/backend.py`):** Phân loại 38 kỹ năng Backend vào 5 nhóm: `languages`, `frameworks`, `databases`, `devops_tools`, `concepts`.
- **Pre-compiled Negative Lookaround Regex:**
  - Ký tự biên đặc biệt: Bắt chuẩn xác `.NET`, `C++`, `C#` bằng pattern `(?<![a-zA-Z0-9_]){escaped}(?![a-zA-Z0-9_+#])` mà không bị lỗi boundary `\b`.
  - Khử trùng lặp chuỗi con: Bắt `Java` mà không bắt nhầm `JavaScript` bằng pattern `\bjava\b(?!\s*script)`.
- **Phân định 2 tầng Explicit vs. Implicit Skills:**
  - *Explicit Skills:* Kỹ năng khai báo ở mục Kỹ năng.
  - *Implicit Skills:* Kỹ năng thực chiến có dùng trong Dự án/Kinh nghiệm nhưng **quên liệt kê** ở mục Kỹ năng $\rightarrow$ Cảnh báo để ứng viên tránh mất điểm ATS oan.

### 🔹 Chặng 4: Chấm điểm ATS Định lượng 4 Trụ cột (`core/ats_scorer.py`)
Định lượng khách quan trên thang điểm 100:
1. **Section Completeness (20đ):** Đủ 4 mục nền tảng Contact, Education, Skills, Exp/Projects.
2. **Skill Coverage & Skill Gap (40đ):** Chấm theo trọng số 3 mô hình (`Product`, `Outsourcing`, `Startup`) hoặc so khớp trực tiếp với JD tải lên. Ứng viên Fresher chỉ cần vững 1 ngôn ngữ cốt lõi là không bị trừ điểm.
3. **Impact & Metrics (25đ):** Quét số liệu đo lường kết quả (`%`, `ms`, `req/ngày`, `users`, `x`) và mật độ động từ hành động kỹ thuật (`ACTION_VERBS` Anh/Việt).
4. **Presentation & Consistency (15đ):** Quét link GitHub/LinkedIn/GitLab (ở cả Contact và Projects); trừ điểm nếu để kỹ năng thực tế bị bỏ quên ngoài mục Skills.

### 🔹 Tầng Chuẩn hóa Trung gian (`core/resume_schema.py`)
- **JSON Resume Standard:** Tự động chuyển đổi dữ liệu phân tích sang schema chuẩn mở quốc tế `jsonresume.org`.
- **Structured Markdown:** Sinh ra văn bản Markdown có phân cấp rõ ràng (`#`, `##`, `###`, bullets `-`) phục vụ làm đầu vào tối ưu cho LLM và cho phép người dùng tải về file `resume.md`.

### 🔹 Chặng 5: Generative AI Advisor (`core/llm_advisor.py`)
- Tích hợp **Google GenAI SDK** (`google-genai`) với cơ chế **Pydantic Structured Outputs** nghiêm ngặt:
  1. **Tư vấn Nâng cấp Kiến trúc Đồ án:** Hướng dẫn tích hợp trực tiếp công nghệ thiếu (`Redis Cache-Aside`, `Docker Multi-stage`, `CI/CD Actions`, `Unit Testing`) vào chính đồ án đang có kèm cam kết số liệu đo lường kỳ vọng (Metrics).
  2. **Bộ công cụ Viết lại Dự án (Before vs. After):** Viết lại mô tả theo công thức Google XYZ (*"Đạt được [X], đo lường bằng [Y], thông qua việc làm [Z]"*) kết hợp Action Verbs mạnh mẽ sẵn sàng copy vào CV.
  3. **Deterministic Fallback Engine:** Tự động chuyển sang chế độ offline thông minh khi không có API key hoặc mất mạng.

---

## 4. Tech Stack

- **Ngôn ngữ:** Python 3.10+ (Đã kiểm thử tương thích hoàn toàn trên Python 3.14).
- **PDF & Text Extraction:** PyMuPDF (`pymupdf` >= 1.28.2).
- **Data Validation & Schemas:** Pydantic v2 (`pydantic` >= 2.14).
- **Generative AI:** Google GenAI SDK (`google-genai` >= 2.31.0) kết hợp Gemini Flash Models.
- **Regular Expressions & Algorithms:** Python Built-in `re`, `unicodedata`, Finite State Machine (FSM), Set Theory.
- **Testing & Tooling:** Bảng báo cáo ASCII tùy biến (`tests/test_utils.py`), PowerShell/Bash automation.

---

## 5. Cấu trúc Thư mục Dự án

```text
AI-Career-Assistant/
├── config/
│   └── backend.py              # Taxonomy 38 kỹ năng Backend, trọng số Archetypes & Action Verbs
├── core/
│   ├── intake.py               # Chặng 1: Bóc tách PDF 2 cột, làm sạch Unicode & icon
│   ├── section_parser.py       # Chặng 2: Máy trạng thái FSM bóc tách 7 sections (Condensed)
│   ├── skills_extractor.py     # Chặng 3: Regex Negative Lookaround, Explicit vs Implicit
│   ├── ats_scorer.py           # Chặng 4: Bộ chấm điểm ATS định lượng 4 trụ cột & Skill Gap
│   ├── resume_schema.py        # Tầng trung gian: Chuẩn hóa JSON Resume & Structured Markdown
│   └── llm_advisor.py          # Chặng 5: Gemini API tư vấn kiến trúc & Viết lại CV (Google XYZ)
├── tests/
│   ├── test_utils.py           # Tiện ích tự động quét CV và xuất bảng báo cáo ASCII
│   ├── test_intake.py          # Kiểm thử Chặng 1
│   ├── test_section_parser.py  # Kiểm thử Chặng 2
│   ├── test_skills_extractor.py# Kiểm thử Chặng 3
│   ├── test_ats_scorer.py      # Kiểm thử Chặng 4 (Đa mô hình & Custom JD)
│   ├── test_resume_schema.py   # Kiểm thử Tầng chuẩn hóa JSON Resume & Markdown
│   ├── test_llm_advisor.py     # Kiểm thử Chặng 5 (Trích xuất chi tiết Before vs. After)
│   └── CV Test/                # Thư mục chứa các CV PDF thực tế phục vụ kiểm thử
├── .gitignore
├── requirements.txt
├── README.md                   # Tài liệu hướng dẫn và kiến trúc dự án
└── CONTEXT.md                  # Bản tóm tắt trạng thái kỹ thuật và nhật ký kiến trúc
```

---

## ⚡ 6. Hướng dẫn Cài đặt & Chạy Thử nghiệm

### 1. Khởi tạo Môi trường
```bash
# Clone repository
git clone https://github.com/your-username/ai-career-assistant.git
cd ai-career-assistant

# Tạo và kích hoạt môi trường ảo
python -m venv venv
# Trên Windows:
.\venv\Scripts\activate
# Trên Linux/macOS:
source venv/bin/activate

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

### 2. Cấu hình Gemini API Key (Tùy chọn cho Chặng 5)
Hệ thống có thể chạy hoàn toàn **Offline (Fallback Engine)** mà không cần API Key. Để kích hoạt tính năng **Online với Gemini Live API**:
Tạo file `.env` tại thư mục gốc của dự án:
```env
GEMINI_API_KEY=AIzaSy_mã_key_của_bạn_từ_Google_AI_Studio
```

---

## 🧪 7. Chạy Bộ Kiểm thử Báo cáo (ASCII Dashboard)

Hệ thống được tích hợp bộ xuất bảng báo cáo trực quan. Bạn có thể chạy kiểm thử từng chặng hoặc chạy toàn bộ:

```powershell
# Kiểm thử Chặng 1: Bóc tách PDF & Tiền xử lý
python -m tests.test_intake

# Kiểm thử Chặng 2: Phân tách cấu trúc 7 Sections
python -m tests.test_section_parser

# Kiểm thử Chặng 3: Trích xuất kỹ năng & Kỹ năng ẩn
python -m tests.test_skills_extractor

# Kiểm thử Chặng 4: Bảng điểm ATS 4 Trụ cột & So sánh Đa mô hình
python -m tests.test_ats_scorer

# Kiểm thử Tầng chuẩn hóa: JSON Resume & Structured Markdown
python -m tests.test_resume_schema

# Kiểm thử Chặng 5: Đề xuất kiến trúc & Đoạn trích Before vs After (Google XYZ)
python -m tests.test_llm_advisor
```

### 📊 Minh họa Kết quả Bảng Điểm ATS (Chặng 4):
```text
┌──────┬──────────────────────────────────┬────────────────┬───────────────┬──────────────┬─────────────────┬───────────┬─────────────────┐
│ STT  │Tên File CV                       │ Cấu trúc (/20) │ Kỹ năng (/40) │ Impact (/25) │ Trình bày (/15) │  TỔNG ĐIỂM│     Xếp loại    │
├──────┼──────────────────────────────────┼────────────────┼───────────────┼──────────────┼─────────────────┼───────────┼─────────────────┤
│  1   │CV_backend_1.pdf                  │      20.0      │      40.0     │     18.0     │       6.0       │     84.0 đ│ Excellent Match │
│  2   │CV_backend_2.pdf                  │      15.0      │      35.0     │      0.0     │      10.0       │     60.0 đ│    Good Match   │
│  3   │CV_Backend_Developer.pdf          │      20.0      │      40.0     │     10.0     │       6.0       │     76.0 đ│    Good Match   │
│  4   │CV_Computer_Science_AI_Backen...  │      20.0      │      27.0     │     20.0     │      10.0       │     77.0 đ│    Good Match   │
│  5   │CV_Fullstack_Developer.pdf        │      15.0      │      37.0     │     10.0     │       6.0       │     68.0 đ│    Good Match   │
│  6   │CV_Fullstack_Web_Developer.pdf    │      15.0      │      33.0     │     25.0     │       6.0       │     79.0 đ│    Good Match   │
│  7   │CV_Java_Backend_Developer.pdf     │      20.0      │      37.0     │     10.0     │       6.0       │     73.0 đ│    Good Match   │
│  8   │CV_Software_Engineer_Java.pdf     │      20.0      │      36.0     │     10.0     │       6.0       │     72.0 đ│    Good Match   │
└──────┴──────────────────────────────────┴────────────────┴───────────────┴──────────────┴─────────────────┴───────────┴─────────────────┘
```

---

## 8. Kế hoạch Phát triển Tiếp theo (Chặng 6 & Mở rộng)

- [ ] **Giao diện Người dùng Web (Streamlit UI):**
  - Dashboard điểm số trực quan (đồng hồ đo điểm, biểu đồ radar kỹ năng).
  - Thẻ giải pháp nâng cấp kiến trúc với nút Copy mã nguồn mẫu.
  - Bộ so sánh Before vs. After từng dòng CV có nút Copy nhanh 1-click.
  - Nút xuất/tải về file `resume.json` và `resume.md`.
- [ ] **Cơ sở dữ liệu Lịch sử (SQLite):** Lưu trữ toàn bộ lịch sử các lần phân tích CV để ứng viên theo dõi tiến trình tăng điểm sau mỗi lần sửa đổi.
- [ ] **Mở rộng Đa ngành nghề (Multi-role Expansion):** Tách cấu hình `config/` để hỗ trợ thêm Frontend Developer, Data Engineer, DevOps Engineer, Mobile Developer.

---

## 9. Bản quyền & Đóng góp
Dự án được phát triển phục vụ mục đích học thuật, nghiên cứu và hỗ trợ cộng đồng sinh viên công nghệ thông tin. Mọi đóng góp (Pull Requests / Issues) đều được hoan nghênh!
