# Task 5: ILP Optimization với BDD Constraints

## Mô tả

Task 5 thực hiện tối ưu hóa **maximize c^T M** với các ràng buộc từ BDD của Task 3.

## Công thức toán học

**Mục tiêu:** Maximize `c^T M = Σ(c_i × M_i)` với:
- `c`: Vector integer weights cho các places
- `M`: Marking vector (vector số token tại mỗi place)
- `M ∈ Reach(M₀)`: Marking phải là một trạng thái reachable từ initial marking M₀ (từ BDD Task 3)

## Implementation

### Hàm chính: `optimize_marking_ilp()`

**Vị trí:** `src/petrinet.py` (dòng 392-457)

**Tham số:**
- `bdd`: BDD manager từ Task 3 
- `visited_bdd`: BDD của tập reachable states từ Task 3 
- `cost_vector`: Dict `{place_id: integer_weight}` hoặc List `[weight1, weight2, ...]` theo thứ tự sorted places

**Trả về:**
- `(optimal_marking, optimal_value)`: 
  - `optimal_marking`: Marking tối ưu (dict) hoặc `None` nếu không có
  - `optimal_value`: Giá trị tối ưu c^T M hoặc `None` nếu không có

### Thuật toán

1. **Chuẩn hóa cost vector**: Chuyển về dạng dict `{place_id: integer_weight}`
2. **Enumerate reachable states**: Sử dụng `bdd.pick_iter()` để liệt kê tất cả reachable states từ BDD (chỉ đọc, không chỉnh sửa BDD)
3. **Tính toán objective**: Với mỗi state, tính `c^T M = Σ(c_i × M_i)`
4. **Tìm optimal**: So sánh và lưu marking có giá trị **max** (maximize)

## Kết quả

Khi chạy chương trình, Task 5 sẽ in ra:
- Số lượng reachable states đang xét
- Optimal marking (marking tối ưu maximize c^T M)
- Optimal value (giá trị c^T M tối ưu)
- "No optimal marking found (none)" nếu không có marking nào
- Thời gian thực thi (running time) và RAM sử dụng



