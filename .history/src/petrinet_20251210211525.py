import xml.etree.ElementTree as ET
from collections import deque
from dd import autoref as _bdd
import os
import re
import subprocess

class Place:
    def __init__(self, id, initial_marking=0):
        self.id = id
        self.initial_marking = initial_marking
        self.name = ""
    def __repr__(self):
        return f"Place({self.id}, {self.initial_marking})"

class Transition:
    def __init__(self, id):
        self.id = id
    def __repr__(self):
        return f"Trans({self.id})"

class Arc:
    def __init__(self, source_id, target_id):
        self.source_id = source_id
        self.target_id = target_id

class PetriNet:
    def __init__(self):
        self.places = {}      
        self.transitions = {}
        self.arcs = []
        # Cache để tra cứu nhanh input/output của từng transition
        self.pre_set = {}  # Input places của transition: T -> {P}
        self.post_set = {} # Output places của transition: T -> {P}

    @staticmethod
    def natural_keys(text):
        match = re.search(r'_(\d+)$', text) # Tìm số ở cuối chuỗi
        if match:
            return (int(match.group(1)), text)
        return (float('inf'), text)

    def load_pnml(self, file_path):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 1. Đọc Places
            for p in root.findall(".//{*}place"):
                p_id = p.get('id')
                init_marking = 0
                name_tag = p.find(".//{*}name/{*}text")
                p_name = name_tag.text if name_tag is not None else p_id
                init_tag = p.find(".//{*}initialMarking")
                if init_tag is not None:
                    text_tag = init_tag.find(".//{*}text")
                    if text_tag is not None and text_tag.text:
                        init_marking = int(text_tag.text)
                new_place = Place(p_id, init_marking)
                new_place.name = p_name
                self.places[p_id] = new_place

            # 2. Đọc Transitions
            for t in root.findall(".//{*}transition"):
                t_id = t.get('id')
                self.transitions[t_id] = Transition(t_id)
                self.pre_set[t_id] = []
                self.post_set[t_id] = []

            # 3. Đọc Arcs và xây dựng cấu trúc đồ thị
            for a in root.findall(".//{*}arc"):
                source = a.get('source')
                target = a.get('target')
                self.arcs.append(Arc(source, target))
                
                # Map input/output cho dễ truy xuất khi chạy thuật toán
                if target in self.transitions: # Arc: Place -> Transition (Input)
                    self.pre_set[target].append(source)
                elif source in self.transitions: # Arc: Transition -> Place (Output)
                    self.post_set[source].append(target)

            print(f"ĐỌC FILE THÀNH CÔNG: {len(self.places)} places, {len(self.transitions)} transitions.")
            return True
        except Exception as e:
            print(f"Lỗi đọc file: {e}")
            return False

    # --- PHẦN LOGIC CỦA TASK 2 ---

    def get_current_marking_tuple(self, marking_dict):
        # Chuyển trạng thái về dạng Tuple (0, 1, 0...) để lưu vào set (hashable)
        # Sắp xếp theo ID để đảm bảo thứ tự nhất quán
        sorted_ids = sorted(self.places.keys())
        return tuple(marking_dict[pid] for pid in sorted_ids)

    def get_enabled_transitions(self, current_marking):
        enabled = []
        for t_id in self.transitions:
            # Một transition enable nếu TẤT CẢ nơi đầu vào đều có token > 0
            is_enabled = True
            for p_in in self.pre_set[t_id]:
                if current_marking[p_in] < 1:
                    is_enabled = False
                    break
            if is_enabled:
                enabled.append(t_id)
        return enabled

    def fire_transition(self, current_marking, t_id):
        # Tạo trạng thái mới (copy dict cũ)
        new_marking = current_marking.copy()
        
        # 1. Trừ token ở đầu vào
        for p_in in self.pre_set[t_id]:
            new_marking[p_in] -= 1
            
        # 2. Cộng token ở đầu ra
        for p_out in self.post_set[t_id]:
            new_marking[p_out] += 1
            
        return new_marking

    def run_reachability_bfs(self):
        print("\n--- BẮT ĐẦU DUYỆT TRẠNG THÁI (BFS) ---")
        
        # 1. Khởi tạo Marking ban đầu từ dữ liệu đã đọc
        initial_marking = {pid: p.initial_marking for pid, p in self.places.items()}
        
        # Queue chứa các Marking cần duyệt
        queue = deque([initial_marking])
        
        # Set chứa các Marking đã duyệt (dùng tuple để lưu trữ unique)
        visited = set()
        visited.add(self.get_current_marking_tuple(initial_marking))
        
        count = 0
        while queue:
            curr_m = queue.popleft()
            count += 1
            
            curr_tuple = self.get_current_marking_tuple(curr_m)
            # print(f"Marking {count}: {curr_tuple}") # Uncomment nếu muốn in từng bước

            # Tìm các transition bắn được từ trạng thái này
            enabled_trans = self.get_enabled_transitions(curr_m)
            
            for t_id in enabled_trans:
                next_m = self.fire_transition(curr_m, t_id)
                next_tuple = self.get_current_marking_tuple(next_m)
                
                if next_tuple not in visited:
                    visited.add(next_tuple)
                    queue.append(next_m)
        
        print(f"Reachable Markings: {len(visited)}")
        #print("Danh sách các trạng thái:", visited)
        return len(visited)
    # --- KẾT THÚC PHẦN LOGIC CỦA TASK 2 ---


    
    def run_reachability_bdd(self):
        # chỗ này gọi trình quản lí BDD nha
        bdd = _bdd.BDD()

        sorted_places = sorted(self.places.keys(), key=self.natural_keys)
        bdd_vars_curr = []
        rename_map = {} 
        for p_id in sorted_places:
            var_curr = f"{p_id}"
            var_next = f"{p_id}_prime"
            bdd.declare(var_curr, var_next)
            bdd_vars_curr.append(var_curr)
            rename_map[var_next] = var_curr

        init_parts = []
        for p_id in sorted_places:
            if self.places[p_id].initial_marking > 0:
                init_parts.append(f"{p_id}")
            else:
                init_parts.append(f"~ {p_id}")
        current_bdd = bdd.add_expr(" & ".join(init_parts))
        tr_list = []   
        for t_id in self.transitions:
            pre = bdd.true
            for p in self.pre_set[t_id]: pre &= bdd.var(p)
            post = bdd.true
            pre_nodes = set(self.pre_set[t_id])
            post_nodes = set(self.post_set[t_id])
            for p in pre_nodes:
                if p not in post_nodes: post &= ~bdd.var(f"{p}_prime")
            for p in post_nodes: post &= bdd.var(f"{p}_prime")
            frame = bdd.true
            affected = pre_nodes | post_nodes
            for p in sorted_places:
                if p not in affected:
                    p_c = bdd.var(p)
                    p_n = bdd.var(f"{p}_prime")
                    frame &= ((p_c & p_n) | (~p_c & ~p_n))
            tr_item = pre & post & frame
            tr_list.append(tr_item)
        
        visited_bdd = current_bdd
        step = 0
        
        while True:
            step += 1
            next_accumulated = bdd.false
            for tr_part in tr_list:
                temp = current_bdd & tr_part
                if temp != bdd.false:
                    small_next = bdd.exist(set(bdd_vars_curr), temp)
                    small_next = bdd.let(rename_map, small_next) 
                    next_accumulated |= small_next

            new_visited = visited_bdd | next_accumulated
            if new_visited == visited_bdd:
                break
            current_bdd = next_accumulated & ~visited_bdd
            visited_bdd = new_visited
        num_states = visited_bdd.count(len(sorted_places))
        return num_states, visited_bdd, bdd


        # if num_states <= 50:
        #     print(f"Danh sách trạng thái (BDD Decoded):")
        #     bdd_states = []
            
        #     for solution in bdd.pick_iter(visited_bdd, care_vars=bdd_vars_curr):
        #         # solution là dict: {'p1': True, 'p2': False, ...}
        #         # Ta cần chuyển nó về tuple: (1, 0, ...) cho giống BFS
        #         state_tuple = []
        #         for p_id in sorted_places:
        #             # Nếu biến p_id là True -> 1, False -> 0
        #             val = 1 if solution.get(p_id, False) else 0 
        #             state_tuple.append(val)
                
        #         bdd_states.append(tuple(state_tuple))
                
        #     print(set(bdd_states))
        # else:
        #     print(f"(Số lượng trạng thái quá lớn ({num_states}), không in ra nổi đâu)")
        # try:
        #     filename_png = "bdd_final.png"
        #     filename_dot = "bdd_manual.dot"
        #     print(f"\nĐang vẽ cây BDD .")

        #     def generate_dot_recursive(u, visited, lines):
        #         u_id = id(u)
        #         if u_id in visited: return
        #         visited.add(u_id)

        #         if u == bdd.true:
        #             lines.append(f'  "{u_id}" [label="REACHABLE", shape=box, style=filled, fillcolor=lightgreen, fontsize=12];')
        #             return
                
        #         if u == bdd.false:
        #             lines.append(f'  "{u_id}" [label="FALSE", shape=box, style=filled, fillcolor="#FFCCCC", fontcolor=red, fontsize=10];')
        #             return

        #         var_name = u.var if u.var else f"Node"
        #         lines.append(f'  "{u_id}" [label="{var_name}", shape=ellipse, style=filled, fillcolor=lightyellow];')

                
        #         low_child = u.low
        #         low_style = "style=dashed"
        #         if low_child == bdd.false:
        #              low_style += ', color="#FFaaaa"'
                
        #         lines.append(f'  "{u_id}" -> "{id(low_child)}" [{low_style}];')
        #         generate_dot_recursive(low_child, visited, lines)

        #         high_child = u.high
        #         high_style = "style=solid"
                
        #         is_negated = hasattr(high_child, 'negated') and high_child.negated
        #         is_dead_end = (high_child == bdd.false)

        #         if is_negated:
        #              high_style = 'style=dotted, color=red, fontcolor=red, label="not"'
        #         elif is_dead_end:
        #              high_style = 'color=red'

        #         lines.append(f'  "{u_id}" -> "{id(high_child)}" [{high_style}];')
        #         generate_dot_recursive(high_child, visited, lines)

        #     dot_lines = ["digraph BDD {", "rankdir=TB;", "node [fontname=\"Helvetica\"];"]
            
        #     root_node = visited_bdd
        #     dot_lines.append(f'  START [shape=doubleoctagon, style=filled, fillcolor=orange, label="START"];')
        #     dot_lines.append(f'  START -> "{id(root_node)}";')
            
        #     visited_set = set()
        #     generate_dot_recursive(root_node, visited_set, dot_lines)
        #     dot_lines.append("}")

        #     with open(filename_dot, "w") as f:
        #         f.write("\n".join(dot_lines))

        #     subprocess.run(["dot", "-Tpng", filename_dot, "-o", filename_png], check=True)
            
        #     print(f"Ảnh nằm đây nè: {os.path.abspath(filename_png)}")
        #     os.system(f"open {filename_png}")
            
        #     try: os.remove(filename_dot)
        #     except: pass

        # except Exception as e:
        #     print(f"Lỗi vẽ hình: {e}")
        # return num_states, visited_bdd, bdd

    # ======================================== PHẦN LOGIC CỦA TASK 4 (MỚI) ========================================================
    def check_deadlock_bdd(self, bdd, visited_bdd):
        """
        Task 4: Deadlock detection using Symbolic Logic.
        Deadlock = (Reachable States) AND (States where NO transition is enabled).
        """
        # 1. Khởi tạo danh sách các places đã sort để dùng cho care_vars và format output
        sorted_places = sorted(self.places.keys(), key=self.natural_keys)
        
        # 2. Xây dựng biểu thức logic cho "Tất cả transitions bị disabled"
        all_transitions_disabled_expr = bdd.true

        for t_id in self.transitions:

            t_is_enabled = bdd.true
            input_places = self.pre_set[t_id]
            
            for p_id in input_places:

                bdd_var_p = bdd.var(p_id)
                t_is_enabled = t_is_enabled & bdd_var_p

            t_is_disabled = ~t_is_enabled
            
            all_transitions_disabled_expr = all_transitions_disabled_expr & t_is_disabled

        # 3. Tìm Deadlock: Là trạng thái Reachable VÀ bị Disabled toàn bộ
        deadlock_set_bdd = visited_bdd & all_transitions_disabled_expr

        # 4. Kiểm tra kết quả
        if deadlock_set_bdd == bdd.false:
            return None # Không tìm thấy deadlock
        else:

            sample_solution = bdd.pick(deadlock_set_bdd, care_vars=sorted_places)
            
            marking_list = []
            for p_id in sorted_places:
                val = 1 if sample_solution.get(p_id, False) else 0
                marking_list.append(val)
            
            return tuple(marking_list)
        
    def export_graphviz(self):
        print("\n--- GRAPHVIZ CODE (Copy vào webgraphviz.com) ---")
        dot = ["digraph PetriNet {", "  rankdir=LR;", "  node [fontname=\"Helvetica\"];"]
        for p_id, p in self.places.items():
            lbl = f"{p.name}\\n({p.initial_marking})" if p.initial_marking else p.name
            dot.append(f'  "{p_id}" [shape=circle, label="{lbl}", style=filled, fillcolor=lightyellow];')
        for t_id in self.transitions.items():
            dot.append(f'  "{t_id[0]}" [shape=box, label="{t_id[0]}", style=filled, fillcolor=lightblue];')
        for a in self.arcs:
            dot.append(f'  "{a.source_id}" -> "{a.target_id}";')
        dot.append("}")
        print("\n".join(dot))
        print("-" * 50)

#--------------------------------------------------------------------------------------------------------------------------------
    def optimize_marking_ilp(self, bdd, visited_bdd, cost_vector):
        """
        Task 5: Maximize c^T M với BDD constraints.
        Tối ưu hóa linear objective function: maximize c^T M
        với M là marking thuộc Reach(M₀) (reachable markings từ BDD Task 3).
        
        Args:
            bdd: BDD manager từ Task 3 (không được chỉnh sửa)
            visited_bdd: BDD của tập reachable states từ Task 3 (không được chỉnh sửa)
            cost_vector: Dict {place_id: integer_weight} hoặc List [weight1, weight2, ...] 
                        theo thứ tự sorted places. c là vector integer weights cho places.
        
        Returns:
            (optimal_marking, optimal_value): 
                - optimal_marking: Marking tối ưu (dict {place_id: token_count}) hoặc None nếu không có
                - optimal_value: Giá trị tối ưu c^T M hoặc None nếu không có
        """
        print("Đang tối ưu maximize c^T M với BDD constraints...")
        
        # kiểm tra input hợp lệ
        if bdd is None or visited_bdd is None:
            print("--> Lỗi: BDD manager hoặc visited_bdd không hợp lệ!")
            return None, None
        
        # sorted_places = sorted(self.places.keys())
        sorted_places = sorted(self.places.keys(), key=self.natural_keys)
        # kiểm tra có places không
        if not sorted_places:
            print("--> Lỗi: Không có places nào trong Petri net!")
            return None, None
        
        # 1. chuẩn hóa cost_vector về dạng dict với error handling
        try:
            if isinstance(cost_vector, list):
                if len(cost_vector) != len(sorted_places):
                    raise ValueError(f"Cost vector length ({len(cost_vector)}) != number of places ({len(sorted_places)})")
                cost_dict = {}
                for i, p_id in enumerate(sorted_places):
                    try:
                        cost_dict[p_id] = int(cost_vector[i])
                    except (ValueError, TypeError):
                        raise ValueError(f"Cost value at index {i} must be an integer, got {type(cost_vector[i])}")
            elif isinstance(cost_vector, dict):
                cost_dict = {}
                for p_id in sorted_places:
                    try:
                        cost_dict[p_id] = int(cost_vector.get(p_id, 0))
                    except (ValueError, TypeError):
                        raise ValueError(f"Cost value for place '{p_id}' must be an integer, got {type(cost_vector.get(p_id))}")
            else:
                raise ValueError("cost_vector must be dict or list of integers")
        except ValueError as e:
            print(f"--> Lỗi: {e}")
            return None, None
        
        # 2. enumerate tất cả reachable states từ BDD (không chỉnh sửa BDD)
        optimal_marking = None
        optimal_value = float('-inf')  # Maximize nên bắt đầu từ -infinity
        
        # try:
        #     # kiểm tra visited_bdd có phải false không (không có reachable states)
        #     if visited_bdd == bdd.false:
        #         print("--> Không tìm thấy reachable state nào (visited_bdd is false)!")
        #         return None, None
            
        #     reachable_states = list(bdd.pick_iter(visited_bdd, care_vars=sorted_places))
        # except Exception as e:
        #     print(f"--> Lỗi khi enumerate reachable states từ BDD: {e}")
        #     return None, None
        
        # if not reachable_states:
        #     print("--> Không tìm thấy reachable state nào!")
        #     return None, None
        
        # print(f"--> Đang xét {len(reachable_states)} reachable states...")
        
        # # 3. tính c^T M cho mỗi state và tìm optimal (maximize)
        # for state_model in reachable_states:
        #     try:
        #         # convert BDD model về marking dict
        #         marking = {}
        #         objective_value = 0
                
        #         for p_id in sorted_places:
        #             # BDD model: True = 1, False = 0 (1-safe net)
        #             # state_model.get() có thể trả về true/false hoặc None
        #             token_count = 1 if state_model.get(p_id, False) else 0
        #             marking[p_id] = token_count
        #             objective_value += cost_dict[p_id] * token_count
                
        #         # update optimal (maximize)
        #         if objective_value > optimal_value:
        #             optimal_value = objective_value
        #             optimal_marking = marking
        #     except Exception as e:
        #         print(f"--> Cảnh báo: Lỗi khi xử lý state {state_model}: {e}")
        #         continue  # bỏ qua state này và tiếp tục
        
        # # kiểm tra kết quả cuối cùng
        # if optimal_marking is None:
        #     print("--> Không tìm thấy marking tối ưu (có thể do lỗi trong quá trình tính toán).")
        #     return None, None
        
        # return optimal_marking, optimal_value
        try:
            # pick_iter trả về một "vòi nước" (generator), ta hứng từng giọt
            iterator = bdd.pick_iter(visited_bdd, care_vars=sorted_places)
            
            count = 0
            for state_model in iterator:
                count += 1
                current_val = 0
                # Tính giá trị c^T * M cho trạng thái này
                for p_id in sorted_places:
                    # Nếu place có token (val=1) thì cộng cost
                    if state_model.get(p_id, False):
                        current_val += cost_dict.get(p_id, 0)
                
                # Cập nhật Max ngay lập tức
                if current_val > optimal_value:
                    optimal_value = current_val
                    # Lưu lại marking này (convert sang dict số 1/0)
                    optimal_marking = {p: (1 if state_model.get(p, False) else 0) for p in sorted_places}
            
            print(f"--> Đã duyệt qua {count} trạng thái.")

        except Exception as e:
            print(f"--> Lỗi khi duyệt BDD: {e}")
            return None, None

        if optimal_marking:
            return optimal_marking, optimal_value
        return None, None
