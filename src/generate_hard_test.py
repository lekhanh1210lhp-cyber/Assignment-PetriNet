import os

def generate_parallel_pnml(num_processes=10, make_deadlock=True, filename="data/hard_deadlock.pnml"):
    """
    Sinh ra mạng Petri N luồng.
    - make_deadlock=False: Các luồng chạy vòng tròn mãi mãi (Live).
    - make_deadlock=True:  Các luồng chạy xong 1 vòng thì đi vào ngõ cụt (Dead).
    """
    status = "CÓ DEADLOCK" if make_deadlock else "KHÔNG DEADLOCK (Loop)"
    print(f"Đang tạo file '{filename}' ({status}) với {num_processes} luồng...")
    
    xml_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<pnml>',
        '  <net id="hard_net" type="http://www.pnml.org/version-2009/grammar/ptnet">',
        '    <page id="page1">'
    ]

    for i in range(num_processes):
        # 1. PLACES
        # Ready (Có token ban đầu)
        xml_content.append(f'      <place id="p_ready_{i}">')
        xml_content.append(f'        <name><text>Ready_{i}</text></name>')
        xml_content.append(f'        <initialMarking><text>1</text></initialMarking>')
        xml_content.append(f'      </place>')
        
        # Work (Đang xử lý)
        xml_content.append(f'      <place id="p_work_{i}">')
        xml_content.append(f'        <name><text>Work_{i}</text></name>')
        xml_content.append(f'        <initialMarking><text>0</text></initialMarking>')
        xml_content.append(f'      </place>')

        if make_deadlock:
            # Dead End (Nơi chôn token - Ngõ cụt)
            xml_content.append(f'      <place id="p_dead_{i}">')
            xml_content.append(f'        <name><text>DeadEnd_{i}</text></name>')
            xml_content.append(f'        <initialMarking><text>0</text></initialMarking>')
            xml_content.append(f'      </place>')

        # 2. TRANSITIONS
        xml_content.append(f'      <transition id="t_start_{i}">')
        xml_content.append(f'        <name><text>Start_{i}</text></name>')
        xml_content.append(f'      </transition>')
        
        xml_content.append(f'      <transition id="t_finish_{i}">')
        xml_content.append(f'        <name><text>Finish_{i}</text></name>')
        xml_content.append(f'      </transition>')

        # 3. ARCS
        # Luôn luôn: Ready -> Start -> Work
        xml_content.append(f'      <arc id="a_r2s_{i}" source="p_ready_{i}" target="t_start_{i}"/>')
        xml_content.append(f'      <arc id="a_s2w_{i}" source="t_start_{i}" target="p_work_{i}"/>')
        xml_content.append(f'      <arc id="a_w2f_{i}" source="p_work_{i}" target="t_finish_{i}"/>')

        # QUAN TRỌNG: Quyết định số phận token sau khi Finish
        if make_deadlock:
            # Work -> Finish -> DeadEnd (Không quay lại -> Kẹt luôn ở đây)
            xml_content.append(f'      <arc id="a_f2d_{i}" source="t_finish_{i}" target="p_dead_{i}"/>')
        else:
            # Work -> Finish -> Ready (Quay lại vòng lặp -> Chạy mãi mãi)
            xml_content.append(f'      <arc id="a_f2r_{i}" source="t_finish_{i}" target="p_ready_{i}"/>')

    xml_content.append('    </page>')
    xml_content.append('  </net>')
    xml_content.append('</pnml>')

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write("\n".join(xml_content))
    
    print(f"✅ Tạo xong! File lưu tại: {filename}")

if __name__ == "__main__":
    # Tạo file có deadlock với 10 luồng (Khoảng 3^10 trạng thái nếu tính cả dead places)
    generate_parallel_pnml(num_processes=12, make_deadlock=True, filename="data/hard_deadlock.pnml")