import sys
import os
import tracemalloc
import time

# Thiết lập màu sắc cho terminal để dễ nhìn
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

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
    file_path = os.path.join(root_dir, "data", "case_choice_deadlock.pnml")
    
    print("--- DEBUG INFO ---")
    print(f"Checking file at: {file_path}")
    
    if os.path.exists(file_path):
        print("-> FILE FOUND! Starting to parse...")
        if net.load_pnml(file_path):
            net.export_graphviz()
             # GỌI TASK 2 Ở ĐÂY
            print("\n>>> TASK 2: EXPLICIT REACHABILITY (BFS) <<<")
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
            
            # CẬP NHẬT: Nhận 3 giá trị (count, visited_bdd, bdd_manager)
            count_bdd, visited_bdd, bdd_manager = net.run_reachability_bdd()
            
            curr, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            time_bdd = time.time() - start
            mem_bdd = peak / 1024 / 1024
            
            print(f"--> States found: {count_bdd}")
            print(f"--> Time: {time_bdd:.6f} s")
            print(f"--> RAM (Peak): {mem_bdd:.6f} MB")

            # =========== TASK 4: DEADLOCK DETECTION ============
            print("\n>>> TASK 4: DEADLOCK DETECTION (ILP/BDD) <<<")
            tracemalloc.start()
            start = time.time()

            # Gọi hàm deadlock, truyền vào bdd manager và tập reachable states từ task 3
            deadlock_result = net.check_deadlock_bdd(bdd_manager, visited_bdd)

            curr, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            time_dl = time.time() - start
            mem_dl = peak / 1024 / 1024

            if deadlock_result:
                print(f"--> DEADLOCK DETECTED! Found one dead marking:")
                print(f"    {deadlock_result}")
            else:
                print("--> NO DEADLOCK FOUND (System is deadlock-free).")
            
            print(f"--> Time: {time_dl:.6f} s")

            
        except Exception as e:
            print(f"Lỗi BDD: {e}.")
    else:
        print("-> FILE NOT FOUND.")
        print(f"Current working dir: {os.getcwd()}")
        print("Please check if 'loop.pnml' is saved inside 'data' folder.")

if __name__ == "__main__":
    main()

