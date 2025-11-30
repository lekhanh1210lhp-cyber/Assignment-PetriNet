### Tóm tắt thay đổi TỪ SAU PHIÊN BẢN TASK 3
1.  **`petrinet.py`**:
    * Hàm `run_reachability_bdd` giờ trả về thêm biến `bdd` (BDD Manager).
    * Thêm hàm `check_deadlock_bdd` sử dụng tư duy tổ hợp logic (tương đương với ILP constraint trên biến boolean) để tạo công thức "Dead" và giao với tập Reachable.
2.  **`main.py`**:
    * Cập nhật dòng gọi hàm `run_reachability_bdd` để hứng 3 biến.
    * Thêm block thực thi Task 4, gọi `check_deadlock_bdd` và in kết quả/thời gian.

Code này đảm bảo chạy mượt trên nền tảng sẵn có của nhóm bạn mà không cần cài thêm thư viện lạ (ILP solver ngoài) vì logic 1-safe Petri net cho phép dùng BDD để giải quyết vấn đề ràng buộc này một cách chính xác nhất.