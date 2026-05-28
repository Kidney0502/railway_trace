import json
import re
from collections import Counter
from datetime import datetime

def parse_train_type(train_info):
    """解析车型信息，提取完整型号"""
    pattern = r'(CRH?\d+[A-Za-z]+(?:-[A-Za-z0-9]+)?)\s*(重联)?'
    match = re.search(pattern, train_info, re.IGNORECASE)
    if match:
        # 返回完整型号（大写）
        return match.group(1).upper()
    return None

def classify_train_type(base_type):
    """分类车型：和谐号或复兴号"""
    if not base_type:
        return "未知"
    if base_type.startswith('CRH'):
        return "和谐号"
    elif base_type.startswith('CR'):
        return "复兴号"
    return "未知"

def main():
    # 读取配置文件
    config_path = r'.\line_config.json'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("错误：line_config.json 文件不存在")
        return
    except json.JSONDecodeError:
        print("错误：line_config.json 格式不正确")
        return
    
    # 统计变量
    train_types = Counter()  # 车型统计
    train_type_categories = Counter()  # 和谐号/复兴号分类统计
    start_points = Counter()  # 起点统计
    end_points = Counter()  # 终点统计
    
    # 遍历配置数据
    for file_key, lines in config.items():
        for line_key, data in lines.items():
            # 提取区间信息
            start_to_end = data.get('start_to_end', '')
            start_flag = data.get('start_flag', False)
            if not start_flag:
                continue
            
            # 处理列表或字符串
            if isinstance(start_to_end, list) and start_to_end:
                interval_list = start_to_end
            elif isinstance(start_to_end, str):
                interval_list = [start_to_end]
            else:
                interval_list = []
            
            # 遍历所有区间信息
            for interval_str in interval_list:
                # 解析车型
                base_type = parse_train_type(interval_str)
                if base_type:
                    train_types[base_type] += 1
                    category = classify_train_type(base_type)
                    train_type_categories[category] += 1
                
                # 提取起点和终点（从区间字符串中提取）
                # 格式如：2023-01-01 08:00-12:30 北京南-上海虹桥 (CR400BF-BZ)
                match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}-\d{2}:\d{2}\s+)?([\u4e00-\u9fa5]+[东|西|南|北|站]?)-([\u4e00-\u9fa5]+[东|西|南|北|站]?)', interval_str)
                if match:
                    start = match.group(2).strip()
                    end = match.group(3).strip()
                    start_points[start] += 1
                    end_points[end] += 1
    
    # 生成输出内容
    current_time = datetime.now().strftime(r"%Y-%m-%d %H:%M")
    output_lines = []
    output_lines.append("=" * 60)
    output_lines.append(f"                    统计报告_{current_time}")
    output_lines.append("=" * 60)
    
    def get_train_prefix(train_type):
        """提取车型前缀，如 CRH380A、CRH380B、CR400AF、CR400BF、CR300AF、CR300BF"""
        # 匹配特定的细分系列
        # CRH380A系列、CRH380B系列
        match = re.match(r'(CRH380[A-B])', train_type)
        if match:
            return match.group(1)
        # CR400AF系列、CR400BF系列
        match = re.match(r'(CR400[AB]F)', train_type)
        if match:
            return match.group(1)
        # CR300AF、CR300BF
        match = re.match(r'(CR300[AB]F)', train_type)
        if match:
            return match.group(1)
        # 其他车型返回粗粒度前缀
        match = re.match(r'(CRH?\d+)', train_type)
        if match:
            return match.group(1)
        return train_type
    
    # 车型统计 - 按分类分组
    output_lines.append("\n一、车型统计")
    output_lines.append("-" * 40)
    
    # 和谐号统计
    hexie_count = train_type_categories.get('和谐号', 0)
    output_lines.append(f"和谐号: {hexie_count} 次")
    if hexie_count > 0:
        hexie_types = [(t, c) for t, c in train_types.items() if t.startswith('CRH')]
        # 按前缀分组
        hexie_groups = {}
        for train_type, count in hexie_types:
            prefix = get_train_prefix(train_type)
            if prefix not in hexie_groups:
                hexie_groups[prefix] = []
            hexie_groups[prefix].append((train_type, count))
        
        # 按前缀名称排序
        sorted_groups = sorted(hexie_groups.items(), key=lambda x: x[0])
        for prefix, items in sorted_groups:
            # 计算组内总数
            total = sum(c for _, c in items)
            output_lines.append(f"  ├ {prefix}系列: {total} 次")
            for train_type, count in sorted(items, key=lambda x: x[0]):
                output_lines.append(f"  │   └ {train_type}: {count} 次")
    
    # 复兴号统计
    fuxing_count = train_type_categories.get('复兴号', 0)
    output_lines.append(f"\n复兴号: {fuxing_count} 次")
    if fuxing_count > 0:
        fuxing_types = [(t, c) for t, c in train_types.items() if t.startswith('CR') and not t.startswith('CRH')]
        # 按前缀分组
        fuxing_groups = {}
        for train_type, count in fuxing_types:
            prefix = get_train_prefix(train_type)
            if prefix not in fuxing_groups:
                fuxing_groups[prefix] = []
            fuxing_groups[prefix].append((train_type, count))
        
        # 按前缀名称排序
        sorted_groups = sorted(fuxing_groups.items(), key=lambda x: x[0])
        for prefix, items in sorted_groups:
            # 计算组内总数
            total = sum(c for _, c in items)
            output_lines.append(f"  ├ {prefix}系列: {total} 次")
            for train_type, count in sorted(items, key=lambda x: x[0]):
                output_lines.append(f"  │   └ {train_type}: {count} 次")
    
    # 起点统计
    output_lines.append("\n二、起点统计")
    output_lines.append("-" * 40)
    for station, count in start_points.most_common():
        output_lines.append(f"{station}: {count} 次")
    
    # 终点统计
    output_lines.append("\n三、终点统计")
    output_lines.append("-" * 40)
    for station, count in end_points.most_common():
        output_lines.append(f"{station}: {count} 次")
    
    # 输出到文件
    output_path = fr'.\统计报告.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"统计完成！报告已保存到: {output_path}")
    print(f"\n统计摘要:")
    print(f"- 和谐号: {train_type_categories.get('和谐号', 0)} 次")
    print(f"- 复兴号: {train_type_categories.get('复兴号', 0)} 次")
    print(f"- 总车型数: {len(train_types)} 种")
    print(f"- 起点数: {len(start_points)} 个")
    print(f"- 终点数: {len(end_points)} 个")

if __name__ == "__main__":
    main()