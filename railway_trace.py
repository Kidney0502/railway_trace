import os
import json
import folium
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CONFIG_FILE = 'line_config.json'


def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def extract_lines_from_geojson_simple(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    lines = []

    if data.get("type") == "FeatureCollection":
        for feature in data.get("features", []):
            geometry = feature.get("geometry", {})
            geom_type = geometry.get("type")

            if geom_type == "LineString":
                coords = geometry.get("coordinates", [])
                line = [(c[1], c[0]) for c in coords]  # 转换为 (lat, lon)
                if len(line) >= 2:
                    lines.append(line)

            elif geom_type == "MultiLineString":
                for segment in geometry.get("coordinates", []):
                    line = [(c[1], c[0]) for c in segment]
                    if len(line) >= 2:
                        lines.append(line)

    print(f"从 {os.path.basename(file_path)} 提取 LineString 数: {len(lines)}")
    return lines


def clean_filename(name):
    left = name.find('(')
    right = name.find(')', left)
    if left != -1 and right != -1:
        name = name[:left] + name[right + 1:]
    return name.replace('.geojson', '')


def create_base_map():
    m = folium.Map(location=[35, 105], zoom_start=4, tiles=None)
    folium.TileLayer('CartoDB positron', name='Positron').add_to(m)
    folium.TileLayer('CartoDB Voyager', name='Voyager').add_to(m)
    folium.TileLayer('cartodb dark_matter', name='Dark_matter').add_to(m)
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
    return m


def create_feature_groups():
    return {
        'blue': folium.FeatureGroup(name='高铁线路'),
        'black': folium.FeatureGroup(name='普速线路')
    }


def add_line_to_groups(line, file_name, groups, line_value, start_flag, train_service, end_flag, train_number='', start_to_end='', weight=4):
    color_map = {
        'black': '#000000',
        'blue': '#00008B',  # 深蓝色
    }

    group_name = 'blue' if line_value == 1 else 'black'
    group = groups[group_name]

    # 透明背景线（用于宽度调节）
    folium.PolyLine(
        line,
        color='black',
        weight=15,
        opacity=0,
        class_name="transparent-line",
        interactive=False
    ).add_to(group)

    # 实际彩色线
    folium.PolyLine(
        line,
        color=color_map[group_name],
        weight=weight,
        opacity=1,
        class_name="real-line",
        interactive=False
    ).add_to(group)

    # ====== 添加起点终点 ======
    if len(line) >= 2:
        if start_flag == 1:
            # 起点
            # 创建popup内容
            popup_content = f"<div style='white-space: nowrap;'>"
            if train_number:
                popup_content += f"车号: {train_number}<br>"
            if train_service:
                popup_content += f"路局: {train_service}<br>"
            if start_to_end:
                popup_content += f"区间: {start_to_end[0]}"
                for s in start_to_end[1:-1]:
                    popup_content += f",<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{s}"
                if len(start_to_end) > 1:
                    popup_content += f",<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{start_to_end[-1]}<br>"
            popup_content += f"</div>"

            # 自定义地图标记形状（空心圆+下方尖点）
            start_icon = folium.DivIcon(
                html=f"""
                <svg width="24" height="32" viewBox="0 0 24 32">
                    <circle cx="12" cy="10" r="8" fill="green" stroke="green" stroke-width="2"/>
                    <polygon points="12,28 4,10 20,10" fill="green" stroke="green" stroke-width="2"/>
                    <circle cx="12" cy="10" r="3" fill="white"/>
                </svg>
                """,
                icon_size=(24, 32),
                icon_anchor=(12, 28)  # 锚点在底部尖点
            )
            folium.Marker(
                location=line[0],
                icon=start_icon,
                popup=folium.Popup(popup_content, max_width=600),
                interactive=True
            ).add_to(group)

        if end_flag == 1:
            popup_content_end = f"<div style='white-space: nowrap;'>"
            if train_number:
                popup_content_end += f"车号: {train_number}<br>"
            if train_service:
                popup_content_end += f"路局: {str(train_service)}<br>"
            if start_to_end:
                popup_content_end += f"区间: {start_to_end[0]}"
                for s in start_to_end[1:-1]:
                    popup_content_end += f",<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{s}"
                if len(start_to_end) > 1:
                    popup_content_end += f",<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{start_to_end[-1]}<br>"
            popup_content_end += f"</div>"

            # 自定义地图标记形状（空心圆+下方尖点）
            end_icon = folium.DivIcon(
                html=f"""
                <svg width="24" height="32" viewBox="0 0 24 32">
                    <circle cx="12" cy="10" r="8" fill="red" stroke="red" stroke-width="2"/>
                    <polygon points="12,28 4,10 20,10" fill="red" stroke="red" stroke-width="2"/>
                    <circle cx="12" cy="10" r="3" fill="white"/>
                </svg>
                """,
                icon_size=(24, 32),
                icon_anchor=(12, 28)  # 锚点在底部尖点
            )
            folium.Marker(
                location=line[-1],
                icon=end_icon,
                popup=folium.Popup(popup_content_end, max_width=600),
                interactive=True
            ).add_to(group)


def add_slider_control(map_object):
    html = """
        <div style="position: absolute; bottom: 20px; right: 20px; z-index: 9999; background-color: white; padding: 10px; border-radius: 5px;">
            <label for="line-width-slider" style="font-size: 14px;">调整线路宽度:</label>
            <input type="range" id="line-width-slider" min="2" max="8" value="4" step="1" style="width: 200px;">
            <span id="line-width-value" style="font-size: 14px;">4</span> px
        </div>
        """
    map_object.get_root().html.add_child(folium.Element(html))

    js_script = """
        <script>
            const slider = document.getElementById('line-width-slider');
            const valueDisplay = document.getElementById('line-width-value');

            slider.oninput = function() {
                valueDisplay.textContent = slider.value;
                updateLineWidth(slider.value);
            }

            function updateLineWidth(weight) {
                const transparentLines = document.querySelectorAll('.transparent-line');
                transparentLines.forEach(line => {
                    line.setAttribute('stroke-width', 15);
                });

                const realLines = document.querySelectorAll('.real-line');
                realLines.forEach(line => {
                    line.setAttribute('stroke-width', weight);
                });
            }
        </script>
        """
    map_object.get_root().html.add_child(folium.Element(js_script))


def main():
    geojson_folder = r"./train/"
    output_html = r"./railway_trace_map.html"

    geojson_files = [
        os.path.join(geojson_folder, f)
        for f in os.listdir(geojson_folder)
        if f.lower().endswith('.geojson')
    ]

    all_lines = []
    geojson_line_map = {}

    for geojson_file in geojson_files:
        lines = extract_lines_from_geojson_simple(geojson_file)
        if lines:
            all_lines.extend(lines)
            geojson_line_map[geojson_file] = lines

    if not all_lines:
        print("没有解析到任何线路，程序终止。")
        return

    # ===== 自动计算地图中心 =====
    all_points = [pt for line in all_lines for pt in line]
    avg_lat = sum(p[0] for p in all_points) / len(all_points)
    avg_lon = sum(p[1] for p in all_points) / len(all_points)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=6, tiles=None)
    folium.TileLayer('CartoDB positron').add_to(m)
    folium.TileLayer('CartoDB Voyager').add_to(m)
    folium.TileLayer('cartodb dark_matter').add_to(m)
    folium.TileLayer('OpenStreetMap').add_to(m)

    groups = create_feature_groups()
    for group in groups.values():
        group.add_to(m)

    # ===== 加载配置 =====
    config = load_config()

    for geojson_file, lines in geojson_line_map.items():
        file_name = clean_filename(os.path.basename(geojson_file))
        file_key = os.path.basename(geojson_file)

        if file_key not in config:
            config[file_key] = {}

        for idx, line in enumerate(lines, start=1):
            line_key = str(idx)
            print(f"\n文件: {file_name}  第 {idx} 条线路")

            if line_key not in config[file_key]:
                line_value = int(input("线路类型（高铁1，普速0）: "))
                start_flag = int(input("是否添加起点(1/0): "))
                end_flag = int(input("是否添加终点(1/0): "))
                if start_flag or end_flag:
                    train_number = input("车号（如G1(北京南-上海虹桥)）: ")
                    train_service = input("路局（如上海局）: ")
                    start_to_end_input = input("乘坐区间（如2023-01-01 08:00-12:30 北京南-上海虹桥(CR400BF-BZ)，多个用顿号分隔）: ")
                    
                    start_to_end = [s.strip() for s in start_to_end_input.split('、')] if start_to_end_input else []
                else:
                    train_number = ''
                    train_service = ''
                    start_to_end = []

                config[file_key][line_key] = {
                    'line_value': line_value,
                    'start_flag': start_flag,
                    'end_flag': end_flag,
                    'train_number': train_number,
                    'train_service': train_service,
                    'start_to_end': start_to_end
                }
                save_config(config)
            else:
                line_value = config[file_key][line_key]['line_value']
                start_flag = config[file_key][line_key]['start_flag']
                end_flag = config[file_key][line_key]['end_flag']
                train_number = config[file_key][line_key].get('train_number', '')
                train_service = config[file_key][line_key].get('train_service', '')
                start_to_end = config[file_key][line_key].get('start_to_end', '')

                print(f"使用配置: 类型={line_value}, 起点={start_flag}, 终点={end_flag}, 车号={train_number}, 路局={train_service}, 区间={start_to_end}")

            add_line_to_groups(
                line,
                file_name,
                groups,
                line_value,
                start_flag,
                train_service,
                end_flag,
                train_number,
                start_to_end
            )

    add_slider_control(m)
    folium.LayerControl().add_to(m)

    os.makedirs(os.path.dirname(output_html), exist_ok=True)
    m.save(output_html)

    print(f"HTML 地图已保存为 {output_html}")


if __name__ == "__main__":
    main()
