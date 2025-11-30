import sys
import os
import tracemalloc
import time
# 1. Setup đường dẫn để import được petrinet từ cùng thư mục src
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from petrinet import PetriNet

def main():
    net = PetriNet()
    
    # 2. Tự động tìm về thư mục gốc (PetriNetAssignment) từ thư mục src
    # current_dir đang là .../PetriNetAssignment/src
    # lùi lại 1 cấp để ra .../PetriNetAssignment
    root_dir = os.path.dirname(current_dir) 
    
    # 3. Tạo đường dẫn tuyệt đối tới file data
    file_path = os.path.join(root_dir, "data", "loop.pnml")
    
    print("--- DEBUG INFO ---")
    print(f"Checking file at: {file_path}")
    
    if os.path.exists(file_path):
        print("-> FILE FOUND! Starting to parse...")
        if net.load_pnml(file_path):
            net.export_graphviz()
             # GỌI TASK 2 Ở ĐÂY
            tracemalloc.start()
            start = time.time()
            net.run_reachability_bfs()
            curr, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            time_bfs = time.time() - start
            mem_bfs = peak / 1024 / 1024
            print(f"--> Time: {time_bfs:.6f} s")
            print(f"--> RAM (Peak): {mem_bfs:.6f} MB")

            print("\n>>> TASK 3: SYMBOLIC BDD <<<")
        try:
            tracemalloc.start()
            start = time.time()
            
            # Nhận 2 giá trị trả về: Số lượng & Object BDD
            count_bdd, bdd_obj = net.run_reachability_bdd()
            
            curr, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            time_bdd = time.time() - start
            mem_bdd = peak / 1024 / 1024
            
            print(f"--> States found: {count_bdd}")
            print(f"--> Time: {time_bdd:.6f} s")
            print(f"--> RAM (Peak): {mem_bdd:.6f} MB")
            
        except Exception as e:
            print(f"Lỗi BDD: {e}.")
    else:
        print("-> FILE NOT FOUND.")
        print(f"Current working dir: {os.getcwd()}")
        print("Please check if 'loop.pnml' is saved inside 'data' folder.")

if __name__ == "__main__":
    main()