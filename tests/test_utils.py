import sys
from pathlib import Path
from typing import Any, List, Optional

# Cấu hình UTF-8 cho terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def get_test_cvs() -> List[Path]:
    """Tìm tất cả các file PDF kiểm thử có trong tests/."""
    search_dirs = [Path("tests/CV Test"), Path("tests/backend"), Path("tests")]
    pdfs = []
    for d in search_dirs:
        if d.exists():
            pdfs.extend(sorted(list(d.glob("*.pdf"))))
    
    seen = set()
    unique = []
    for p in pdfs:
        # Bỏ qua các file CV RAG
        if "rag" in p.name.lower():
            continue
        if p.name not in seen:
            seen.add(p.name)
            unique.append(p)
    return unique


def truncate_text(text: str, max_len: int) -> str:
    """Cắt ngắn chuỗi văn bản nếu vượt quá độ dài."""
    if not text:
        return ""
    text_clean = " ".join(str(text).split())
    if len(text_clean) <= max_len:
        return text_clean
    return text_clean[: max_len - 3] + "..."


def render_table(
    headers: List[str],
    rows: List[List[Any]],
    title: Optional[str] = None,
    alignments: Optional[List[str]] = None,
) -> None:
    """
    In bảng ASCII chuẩn đẹp mắt, căn chỉnh lề tự động hoặc theo cấu hình.
    alignments: danh sách 'left', 'center', 'right' cho từng cột.
    """
    if not headers or not rows:
        print("(Bảng rỗng hoặc không có dữ liệu)")
        return

    num_cols = len(headers)
    if not alignments:
        alignments = ["left"] * num_cols

    # Tính độ rộng cột tự động
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            if idx < num_cols:
                cell_str = str(cell)
                if len(cell_str) > col_widths[idx]:
                    col_widths[idx] = len(cell_str)

    # Thêm padding
    col_widths = [max(w + 2, 6) for w in col_widths]

    def format_row(values: List[Any], fill_char: str = " ") -> str:
        parts = []
        for i, val in enumerate(values):
            w = col_widths[i]
            align = alignments[i] if i < len(alignments) else "left"
            s = str(val)
            if align == "center":
                parts.append(s.center(w, fill_char))
            elif align == "right":
                parts.append(s.rjust(w, fill_char))
            else:
                parts.append(s.ljust(w, fill_char))
        return "│" + "│".join(parts) + "│"

    border_top = "┌" + "┬".join("─" * w for w in col_widths) + "┐"
    border_mid = "├" + "┼".join("─" * w for w in col_widths) + "┤"
    border_bot = "└" + "┴".join("─" * w for w in col_widths) + "┘"

    total_width = len(border_top)

    if title:
        print("\n" + "=" * total_width)
        print(f" {title} ".center(total_width))
        print("=" * total_width)

    print(border_top)
    print(format_row(headers))
    print(border_mid)
    for r in rows:
        print(format_row(r))
    print(border_bot)
