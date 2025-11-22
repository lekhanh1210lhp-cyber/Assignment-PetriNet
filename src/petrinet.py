import xml.etree.ElementTree as ET
from collections import deque

class Place:
    def __init__(self, id, initial_marking=0):
        self.id = id
        self.initial_marking = initial_marking
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
                init_tag = p.find(".//{*}initialMarking")
                if init_tag is not None:
                    text_tag = init_tag.find(".//{*}text")
                    if text_tag is not None and text_tag.text:
                        init_marking = int(text_tag.text)
                self.places[p_id] = Place(p_id, init_marking)

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