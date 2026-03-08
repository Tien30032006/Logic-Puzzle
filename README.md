# AI-Search-Logic-Puzzle

**Bài tập lớn 1 - Môn Nhập môn Trí tuệ Nhân tạo**
Bài tập lớn này xây dựng hệ thống Trí tuệ Nhân tạo để tự động giải quyết các bài toán Logic Puzzles (Nonogram và Chess Puzzles). Hệ thống áp dụng và so sánh hiệu năng giữa các chiến lược Tìm kiếm mù (Blind Search: DFS, BrFS) và Tìm kiếm có thông tin (Heuristic Search).

## 📂 Cấu trúc thư mục (Project Structure)

Bài tập lớn được tổ chức theo cấu trúc chuẩn như sau:

```text
AI-SEARCH-LOGIC-PUZZLE/
├── docs/                   # Chứa tài liệu báo cáo và slide thuyết trình
│   ├── BaoCao_BTL1.pdf
│   └── Slides_BTL1.pdf
├── input/                  # Chứa dữ liệu đầu vào (Testcases) dạng JSON/Text
│   ├── chess_puzzles_in.txt
│   └── nonogram_in.txt
├── output/                 # Chứa các file kết quả xuất ra (nếu có)
├── src/                    # Chứa mã nguồn chính (Source code)
│   ├── benchmark.py        # Script chạy đánh giá hiệu năng (Time & Memory) và vẽ đồ thị
│   ├── chess_puzzles.py    # Chương trình giải bài toán Chess Puzzles
│   └── nonogram.py         # Chương trình giải bài toán Nonogram 
├── .gitignore              # Cấu hình bỏ qua các file rác khi push lên Git
├── README.md               # Tài liệu hướng dẫn sử dụng đồ án
└── requirements.txt        # Danh sách các thư viện cần cài đặt
```

## 🚀 Hướng dẫn Cài đặt (Installation)

**Bước 1:** Clone repository này về máy hoặc giải nén thư mục đồ án. Mở Terminal/Command Prompt tại thư mục gốc của đồ án.

**Bước 2:** Cài đặt các thư viện Python cần thiết bằng lệnh:

```bash
pip install -r requirements.txt
```

*(Các thư viện chính bao gồm: `customtkinter` để vẽ giao diện, `matplotlib` và `numpy` để vẽ đồ thị so sánh).*

## 🎮 Hướng dẫn Sử dụng (Usage)

Tất cả các lệnh dưới đây được chạy từ thư mục gốc của project.

**1. Chạy giao diện giải Nonogram:**
Chương trình cung cấp giao diện trực quan trực tiếp theo dõi từng bước duyệt của AI.

```bash
python src/nonogram.py
```

**2. Chạy bài toán Chess Puzzles:**

```bash
python src/chess_puzzles.py
```

**3. Chạy Đánh giá Hiệu năng (Benchmark & Biểu đồ):**
Script này sẽ chạy ngầm các thuật toán qua các testcases, sau đó xuất ra biểu đồ Line Chart so sánh Thời gian (Time) và Bộ nhớ (RAM) tiêu thụ.

```bash
python src/benchmark.py
```
