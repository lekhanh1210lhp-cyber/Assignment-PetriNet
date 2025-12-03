# Task 5: ILP Optimization với BDD Constraints

## Mô tả

Task 5 thực hiện tối ưu hóa **maximize c^T M** (tích vô hướng của cost vector và marking vector) với các ràng buộc từ BDD của Task 3.

**Lưu ý quan trọng:** Task 5 chỉ sử dụng BDD từ Task 3, không chỉnh sửa Task 3 hay ảnh hưởng đến các task khác.

## Công thức toán học

**Mục tiêu:** Maximize `c^T M = Σ(c_i × M_i)` với:
- `c`: Vector integer weights cho các places
- `M`: Marking vector (vector số token tại mỗi place)
- `M ∈ Reach(M₀)`: Marking phải là một trạng thái reachable từ initial marking M₀ (từ BDD Task 3)

## Implementation

### Hàm chính: `optimize_marking_ilp()`

**Vị trí:** `src/petrinet.py` (dòng 392-457)

**Tham số:**
- `bdd`: BDD manager từ Task 3 (chỉ đọc, không chỉnh sửa)
- `visited_bdd`: BDD của tập reachable states từ Task 3 (chỉ đọc, không chỉnh sửa)
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

### Ưu điểm

- **Sử dụng BDD constraints**: Chỉ xét các trạng thái reachable từ Task 3, đảm bảo tính đúng đắn
- **Không ảnh hưởng Task 3**: Chỉ đọc BDD, không chỉnh sửa
- **Hiệu quả với 1-safe nets**: Vì mỗi place chỉ có 0 hoặc 1 token, enumeration nhanh
- **Integer weights**: Hỗ trợ cost vector là integer weights

## Cách sử dụng

### Trong `main.py`

```python
# Định nghĩa cost vector (integer weights)
cost_vector = {p_id: 1 for p_id in net.places.keys()}  # Default: weight = 1 cho mỗi place
# Hoặc custom:
# cost_vector = {'p1': 2, 'p2': 1, 'p3': 3}  # Custom integer weights

# Tối ưu: maximize c^T M với M ∈ Reach(M₀)
optimal_marking, optimal_value = net.optimize_marking_ilp(
    bdd_manager, visited_bdd, cost_vector
)
```

### Ví dụ với `case_choice_deadlock.pnml`

Petri net có 3 places: `p1`, `p2`, `p3`

**Reachable states** (từ Task 3):
- `{p1: 1, p2: 0, p3: 0}` - Initial state
- `{p1: 0, p2: 1, p3: 0}` - After t1
- `{p1: 0, p2: 0, p3: 1}` - After t2 (deadlock)

**Với cost vector `{p1: 1, p2: 1, p3: 1}`:**
- Maximize: State có nhiều token nhất (tổng số token lớn nhất)

**Với cost vector `{p1: 2, p2: 1, p3: 3}`:**
- Maximize: State có giá trị `2×M[p1] + 1×M[p2] + 3×M[p3]` lớn nhất

## Kết quả

Khi chạy chương trình, Task 5 sẽ in ra:
- Số lượng reachable states đang xét
- Optimal marking (marking tối ưu maximize c^T M)
- Optimal value (giá trị c^T M tối ưu)
- "No optimal marking found (none)" nếu không có marking nào
- Thời gian thực thi (running time) và RAM sử dụng

## Lưu ý

- **Task 5 chỉ sử dụng BDD từ Task 3, không chỉnh sửa Task 3 hay ảnh hưởng các task khác**
- Task 5 phụ thuộc vào Task 3 (cần BDD manager và visited_bdd)
- Phù hợp với 1-safe Petri nets (mỗi place chỉ có 0 hoặc 1 token)
- Với nets lớn có nhiều reachable states, enumeration có thể chậm hơn
- Cost vector phải là integer weights

