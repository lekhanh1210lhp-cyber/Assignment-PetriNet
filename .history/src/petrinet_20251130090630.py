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
        
        print(f"KẾT QUẢ: Tổng số trạng thái tìm thấy (Reachable Markings): {len(visited)}")
        print("Danh sách các trạng thái:", visited)
        return len(visited)
    # --- KẾT THÚC PHẦN LOGIC CỦA TASK 2 ---
    def run_reachability_bdd(self):
        # chỗ này gọi trình quản lí BDD nha
        bdd = _bdd.BDD()
        # khúc này là sắp xếp các place theo ID để ko lỗi BDD. Dùng py nó có hàm sorted sẵn, dùng mấy ngôn ngữ khác chắc t chết
        sorted_places = sorted(self.places.keys())
        
        # 1. Khai báo biến
        # bdd_vars_curr sẽ lưu các trạng thái hiện tại
        bdd_vars_curr = []
        # rename_map để ánh xạ biến prime về biến current. Kỉu p' -> p
        rename_map = {} 
        # vòng lặp này để khai báo biến cho BDD gòm cả trạng thái hiện tại và trạng thái kế tiếp. Current và prime
        for p_id in sorted_places:
            var_curr = f"{p_id}"
            var_next = f"{p_id}_prime"
            #declare biến cho BDD
            bdd.declare(var_curr, var_next)
            # append biến current vào list
            bdd_vars_curr.append(var_curr)
            # ánh xạ biến next về current. Để sau này khi replod thì nó chuyển từ prime về lại current r làm típ mấy cái vòng lặp sau
            rename_map[var_next] = var_curr

        # 2. Mã hóa trạng thái đầu
        # Tạo biểu thức BDD cho trạng thái ban đầu
        init_parts = []
        # vòng lặp tạo predicate cho initial marking nè. Vd kỉu initial có token ở p1 với p2 trong số 8 place thì sẽ là p1 & p2 & ~p3 & ~p4 & ... kỉu kỉu z
        for p_id in sorted_places:
            if self.places[p_id].initial_marking > 0:
                init_parts.append(f"{p_id}")
            else:
                init_parts.append(f"~ {p_id}")
        # dùng & để nối các predicate lại. VD như trên thì sẽ là p1 & p2 & ~p3 & ~p4 & ...
        current_bdd = bdd.add_expr(" & ".join(init_parts))

        # 3. Xây dựng Transition Relation (TR). Khó vloz
        # global_tr sẽ lưu trữ toàn bộ transition relation, nên nó false ban đầu để đỡ OR dính nó vào
        global_tr = bdd.false
        # vòng lặp qua từng transition để tạo predicate cho từng transition
        for t_id in self.transitions:
            # Pre-condition
            # pre phải khai báo true trc tại lát sau mình AND mấy cái đkien vào
            pre = bdd.true
            # vòng lặp qua các place đầu vào của transition hiện tại để tạo điều kiện pre. Vd như p1 & p2 & .... &= là phép AND nha
            for p in self.pre_set[t_id]: pre &= bdd.var(p)
            
            # Post-condition
            # tương tự khai báo post true trc
            post = bdd.true
            # # vòng lặp đầu lặp qua các place vào (pre_set) để biến nó sang dạng not prime (mất token). Vd T1 có token ở p1 thì sau khi bắn token sẽ thành ~p1' trong post condition
            # for p in self.pre_set[t_id]: post &= ~bdd.var(f"{p}_prime")
            # # vòng lặp hai sẽ duyệt qa các place đầu ra (post_set) để biến nó sang dạng prime. VD P1 T1 P2 thì sau khi bắn token sẽ thành p2' trong post condition
            # for p in self.post_set[t_id]: post &= bdd.var(f"{p}_prime")

            pre_nodes = set(self.pre_set[t_id])
            post_nodes = set(self.post_set[t_id])

            # Nếu place nằm trong pre nhưng KHÔNG nằm trong post -> Mất token
            for p in pre_nodes:
                if p not in post_nodes: 
                    post &= ~bdd.var(f"{p}_prime")

            # Nếu place nằm trong post -> Có token (bất kể trước đó có hay không)
            for p in post_nodes: 
                post &= bdd.var(f"{p}_prime")
            
            # Frame Condition. Frame để đảm bảo các place ko có đụng chạm j đến transition này thì sẽ khôm bị j hết. Kiểu nếu P1 T1 P2 thì P3, P4,... sẽ <-> P3', P4',..
            frame = bdd.true
            # affected là tập các place tham gia dô transition này ở cả hai đầu pre và post. Dấu | là phép hợp Union á
            affected = set(self.pre_set[t_id]) | set(self.post_set[t_id])
            # loop này lập qua tất cả place sorted, nếu nó ko affected thì tạo điều kiện để p <-> p'
            for p in sorted_places:
                if p not in affected:
                    p_c = bdd.var(p)
                    p_n = bdd.var(f"{p}_prime")
                    # (p and p') or (not p and not p') -> p <-> p'
                    frame &= ((p_c & p_n) | (~p_c & ~p_n))
            # ta sẽ có đc predicate cho transition hiện tại sẽ là phép and của (pre & post & frame). Và vì có nhiều Transition nên ta sẽ dùng |= để OR nó vào global_tr
            global_tr |= (pre & post & frame)

        # 4. Vòng lặp tìm kiếm
        # current_bdd là trạng thái hiện tại, visited_bdd là tập trạng thái đã thăm
        visited_bdd = current_bdd
        # vòng lặp này để duyệt tất cả trạng thái reachable
        while True:
            # 1. Tính giao (AND) giữa trạng thái hiện tại và luật chuyển
            temp_transition = current_bdd & global_tr
            # 2. Dùng exist để loại bỏ các biến cũ
            next_bdd = bdd.exist(set(bdd_vars_curr), temp_transition)
            next_bdd = bdd.let(rename_map, next_bdd)
            new_visited = visited_bdd | next_bdd
            
            if new_visited == visited_bdd:
                break
            current_bdd = next_bdd
            visited_bdd = new_visited

        num_states = visited_bdd.count(len(sorted_places))

        # QUAN TRỌNG: Trả về cả biến 'bdd' manager để dùng cho Task 4 (TheHoang thêm vào sau AnhKhoa done task3)
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
        # return num_states, visited_bdd

    # --- PHẦN LOGIC CỦA TASK 4 (MỚI) ---
    def check_deadlock_bdd(self, bdd, visited_bdd):
        """
        Task 4: Deadlock detection using Symbolic Logic (equivalent to ILP constraints).
        Deadlock = (Reachable States) AND (States where NO transition is enabled).
        """
        print("Đang kiểm tra Deadlock...")
        sorted_places = sorted(self.places.keys())

        # 1. Xây dựng công thức DEAD (Không transition nào bắn được)
        # Mặc định dead_logic là True, sau đó AND với điều kiện "disabled" của từng transition
        dead_logic = bdd.true
        
        for t_id in self.transitions:
            # Transition t bị disable nếu tồn tại ít nhất 1 place đầu vào p mà không có token (~p)
            # Logic: t_disabled = (NOT p1) OR (NOT p2) OR ...
            
            # Nếu transition không có đầu vào (source transition), nó luôn bắn được -> ko bao giờ deadlock
            if not self.pre_set[t_id]:
                dead_logic = bdd.false
                break

            t_disabled = bdd.false
            for p_in in self.pre_set[t_id]:
                # Add điều kiện: Place này không có token
                t_disabled |= ~bdd.var(p_in)
            
            # Hệ thống chỉ chết khi TẤT CẢ các transition đều bị disable
            dead_logic &= t_disabled

        # 2. Tìm Deadlock = Reachable INTERSECTION Dead
        deadlock_set = visited_bdd & dead_logic

        # 3. Kiểm tra kết quả
        if deadlock_set == bdd.false:
            return None
        else:
            # Pick one deadlock state to report
            satisfying_models = list(bdd.pick_iter(deadlock_set, care_vars=sorted_places))
            if satisfying_models:
                # Lấy mẫu đầu tiên tìm thấy
                model = satisfying_models[0]
                # Convert về dạng dễ đọc
                result_marking = {}
                for p_id in sorted_places:
                    # Nếu biến p_id là True -> 1, False -> 0
                    val = 1 if model.get(p_id, False) else 0
                    result_marking[p_id] = val
                return result_marking
            return None
        
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