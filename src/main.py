import sys
import os

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
             # GỌI TASK 2 Ở ĐÂY
             net.run_reachability_bfs()
    else:
        print("-> FILE NOT FOUND.")
        print(f"Current working dir: {os.getcwd()}")
        print("Please check if 'loop.pnml' is saved inside 'data' folder.")

if __name__ == "__main__":
    main()