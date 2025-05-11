import json
import time
from datetime import datetime
from collections import defaultdict

def extract_vessel_routes():
    print("开始提取渔船航线数据...")
    start_time = time.time()
    
    try:
        # 读取JSON文件
        with open('MC2/mc2.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 创建渔船ID到渔船信息的映射
        vessel_info = {}
        for node in data.get('nodes', []):
            if node.get('type') == 'Entity.Vessel.FishingVessel':
                vessel_info[node.get('id')] = {
                    'company': node.get('company', '未知'),
                    'tonnage': node.get('tonnage', '未知'),
                    'length': node.get('length_overall', '未知'),
                    'flag_country': node.get('flag_country', '未知'),
                    'date_added': node.get('_date_added', '未知'),
                    'last_edited_date': node.get('_last_edited_date', '未知'),
                    'raw_source': node.get('_raw_source', '未知')
                }
        
        # 提取所有渔船定位事件
        vessel_routes = defaultdict(list)
        for link in data.get('links', []):
            if link.get('type') == 'Event.TransportEvent.TransponderPing':
                vessel_id = link.get('target')
                if vessel_id in vessel_info:
                    vessel_routes[vessel_id].append({
                        'time': link.get('time'),
                        'location': link.get('source'),
                        'dwell': link.get('dwell'),
                        'latitude': link.get('latitude', '未知'),
                        'longitude': link.get('longitude', '未知')
                    })
        
        # 按时间对每个渔船的航点进行排序
        for vessel_id in vessel_routes:
            vessel_routes[vessel_id].sort(key=lambda x: x['time'])
        
        # 保存到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'fishing_vessel_routes_{timestamp}.json'
        
        # 准备JSON输出数据
        output_data = {
            'total_fishing_vessels': len(vessel_routes),
            'fishing_vessels': []
        }
        
        for vessel_id, route in vessel_routes.items():
            vessel = vessel_info[vessel_id]
            vessel_data = {
                'vessel_id': vessel_id,
                'company': vessel['company'],
                'tonnage': vessel['tonnage'],
                'length': vessel['length'],
                'flag_country': vessel['flag_country'],
                'date_added': vessel['date_added'],
                'last_edited_date': vessel['last_edited_date'],
                'raw_source': vessel['raw_source'],
                'route_points': len(route),
                'route': route
            }
            output_data['fishing_vessels'].append(vessel_data)
        
        # 保存为JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n渔船航线信息已保存至 {output_file}")
        print(f"\n总共找到 {len(vessel_routes)} 艘渔船")
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
    
    elapsed_time = time.time() - start_time
    print(f"\n处理完成，耗时: {elapsed_time:.2f}秒")

if __name__ == "__main__":
    extract_vessel_routes()