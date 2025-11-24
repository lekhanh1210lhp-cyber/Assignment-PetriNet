Petri Net Reachability & Deadlock Analysis Tool
Bài tập lớn môn Mô hình hóa Toán học (Mathematical Modeling). Chương trình thực hiện phân tích mạng Petri (Petri Net Analysis) thông qua việc duyệt không gian trạng thái bằng hai phương pháp: Duyệt tường minh (Explicit BFS) và Tính toán ký hiệu (Symbolic BDD).

📋 Tính năng chính
PNML Parser (Task 1):

Đọc và phân tích file chuẩn .pnml (Petri Net Markup Language).

Hỗ trợ đọc Places, Transitions, Arcs và Initial Marking.

Explicit Reachability Analysis (Task 2):

Sử dụng thuật toán Breadth-First Search (BFS).

Lưu trữ trạng thái dưới dạng Tuple trong Hash Set.

Phù hợp với các mạng nhỏ để kiểm chứng kết quả.

Symbolic Reachability Analysis (Task 3):

Sử dụng Binary Decision Diagrams (BDD) thông qua thư viện dd.

Mã hóa trạng thái (Encoding) và Quan hệ chuyển đổi (Transition Relation).

Tính toán tập trạng thái đến được (Reachable Set) bằng phương pháp lặp điểm bất động (Fixed-point iteration).

Tự động trực quan hóa: Xuất ảnh cây BDD (.png) thể hiện cấu trúc không gian trạng thái.

Deadlock Detection (Task 4):

Phát hiện trạng thái chết (Deadlock) dựa trên các phép toán logic trên BDD.

Công thức: Deadlock = Reachable_Set AND (NOT Enabled_T1) AND (NOT Enabled_T2)...

🛠 Yêu cầu cài đặt (Prerequisites)
Để chạy được dự án, máy tính cần cài đặt:

1. Python & Thư viện

Python 3.8+

Thư viện dd (Dùng cho BDD):

Bash
pip install dd
2. Graphviz (Bắt buộc để xuất ảnh PNG)

Chương trình sử dụng Graphviz để vẽ cây BDD.

MacOS:

Bash
brew install graphviz
Windows: Tải bộ cài từ graphviz.org và thêm vào PATH.

Linux (Ubuntu/Debian):

Bash
sudo apt-get install graphviz
🚀 Hướng dẫn sử dụng
1. Cấu trúc thư mục

Plaintext
Project_Root/
├── data/
│   ├── loop.pnml           # File test đơn giản
│   └── matrix_test.pnml    # File test song song (Concurrency)
├── src/
│   ├── main.py             # File chạy chính
│   └── petrinet.py         # Class xử lý logic (BFS, BDD, Deadlock)
└── README.md
2. Chạy chương trình

Mở Terminal tại thư mục gốc và chạy lệnh:

Bash
python3 src/main.py
3. Thay đổi File Input

Để đổi file test (ví dụ từ loop.pnml sang matrix_test.pnml), hãy mở file src/main.py và sửa dòng:

Python
# Dòng khoảng 15
file_path = os.path.join(root_dir, "data", "matrix_test.pnml")
📊 Giải thích thuật toán (Technical Highlights)
Phương pháp Explicit (BFS)

Cách làm: Bắt đầu từ trạng thái đầu, lần lượt bắn các transition khả dụng để sinh ra trạng thái mới. Lưu tất cả vào một hàng đợi (Queue).

Ưu điểm: Dễ cài đặt, dễ hiểu.

Nhược điểm: Dễ gặp lỗi tràn bộ nhớ (State Space Explosion) với các mạng lớn hoặc song song.

* **Mã hóa (Encoding):**
    Mỗi Place $P_i$ được gán 2 biến Boolean:
    * $p_i$: Biến trạng thái hiện tại (Current state).
    * $p_i'$: Biến trạng thái tương lai (Next state).

* **Luật chuyển đổi (Transition Relation - TR):**
    Hệ thống chuyển đổi được xây dựng bằng cách hợp (OR) logic của tất cả các transition:
    $$TR = \bigvee_{t \in T} (Pre_t \wedge Post_t \wedge Frame_t)$$
    * **Pre:** Điều kiện kích hoạt (Input places có token).
    * **Post:** Trạng thái sau khi bắn (Input mất, Output có).
    * **Frame Condition:** Điều kiện bất biến, đảm bảo các Place không tham gia vào transition sẽ giữ nguyên giá trị ($p \leftrightarrow p'$).

* **Image Computation (Tính toán ảnh):**
    Tìm tập trạng thái tiếp theo ($Next$) từ tập hiện tại ($Current$) bằng phép toán `Relational Product` (kết hợp AND và Existential Quantification):
    $$Next(X') = \exists X . (Current(X) \wedge TR(X, X'))$$

🖼 Kết quả minh họa
Khi chạy thành công, chương trình sẽ:

In ra số lượng trạng thái tìm thấy bởi cả 2 cách (để so sánh tính đúng đắn).

In ra thời gian chạy và dung lượng RAM tiêu thụ.

Tạo ra file ảnh bdd_final_result.png tại thư mục gốc.
