# Railway_trace

基于 Python + Folium 开发的 高铁 / 普速铁路轨迹可视化工具 ，支持批量导入 GeoJSON 铁路线路文件，自动生成可交互的 HTML 铁路地图，支持线路分类、起点 / 终点标记、自定义列车信息、线路宽度调节、多图层切换。

### ✨ 功能特性

- 支持 LineString / MultiLineString 格式的 GeoJSON 铁路轨迹解析
- 自动区分 高铁（蓝色） 和 普速（黑色） 线路
- 自定义 起点（绿色） 、 终点（红色）标记，支持显示：车号、路局、乘坐区间
- 配置自动保存， 重复运行无需重复输入
- 内置 4 种地图底图自由切换：
  - CartoDB Positron（简洁浅色）
  - CartoDB Voyager（标准）
  - CartoDB Dark Matter（深色）
  - OpenStreetMap（开源街道图）
- 滑块 实时调节线路宽度
- 图层控制器，可单独显示 / 隐藏高铁 / 普速线路

### **📁 项目结构**

```plaintext
train/                # 存放所有 .geojson 铁路轨迹文件（必须放在此目录）
line_config.json      # 自动生成的配置文件（保存线路类型、标记信息）
railway_trace_map.html # 最终生成的地图文件
railway_trace.py      # 主程序
count.py              # 统计信息程序
统计信息.txt		      # 统计信息
README.md             # 说明文档
```

### **🚀 快速开始**

1. **安装依赖**

```bash
pip install folium
```

2. **准备轨迹文件**

在项目根目录创建 train 文件夹

将所有 .geojson 铁路轨迹文件 放入该文件夹

铁路轨迹网站: [https://signal.eu.org/osm](https://signal.eu.org/osm)或[https://brouter.de/brouter-web/#map=19/31.91916/118.71480/standard&profile=rail](https://brouter.de/brouter-web/#map=19/31.91916/118.71480/standard&profile=rail)

3. **运行程序**

```bash
python railway_trace.py
```

4. **首次运行配置**

程序会自动遍历所有 GeoJSON 文件，逐条线路要求你输入：

```plain
线路类型： 1=高铁 / 0=普速
是否添加起点： 1=是 / 0=否
是否添加终点： 1=是 / 0=否
如需标记，继续输入：
	车号（如 G1 (北京南 - 上海虹桥)）
	路局（如 上海局）
	乘坐区间（多段用顿号(、)分隔）
```

配置会自动保存到 line_config.json ， 再次运行直接读取配置，无需重复输入 。

5. **查看结果**

运行完成后，会在根目录生成：

```
railway_trace_map.html
```

用浏览器打开即可查看完整铁路轨迹地图。

### 📌 使用说明

- 地图操作
  - 滚轮 ：缩放地图
  - 拖拽 ：平移地图
  - 右上角图层按钮 ：切换底图、显示 / 隐藏高铁 / 普速线路
  - 右下角滑块 ：调整线路宽度（2-8px）
  - 点击起点 / 终点标记 ：查看列车详细信息

- 配置文件说明


```json
"线路文件名.geojson": {
  "1": {
    "line_value": 1,        // 1=高铁 0=普速
    "start_flag": 1,        // 1=显示起点 0=隐藏
    "end_flag": 1,          // 1=显示终点 0=隐藏
    "train_number": "G1",   // 车号
    "train_service": "上海局", // 路局
    "start_to_end": ["区间1","区间2"] // 乘坐区间列表
  }
}
```

​	重新配置：如需重新输入所有配置， 直接删除 line_config.json 后重新运行程序即可。

- 统计信息

​	统计信息可显示：起点数据、终点数据、路局数据、车型数据（仅统计start_flag=1）

### 🛠️ 常见问题

1. 没有解析到任何线路

​	检查 train 文件夹是否存在

​	检查文件是否为 .geojson 后缀（小写也支持）

​	确认 GeoJSON 包含 LineString 或 MultiLineString 类型数据

2. 中文乱码

​	程序已内置 UTF-8 编码，正常使用不会出现乱码。

3. 地图打开空白

​	检查网络（底图需要联网加载，**！！！OpenStreetMap需要魔法**）

4. 使用 Chrome/Edge 等现代浏览器打开

### 📝 许可证

本项目开源免费，可自由使用、修改和分发。

### 🧩 完整命令总结

```bash
# 安装依赖
pip install folium

# 创建轨迹目录
mkdir train

# 放入 geojson 文件后运行
python railway_trace.py

# 打开生成的地图
start railway_trace_map.html
```

如果你觉得interesting，给我一个star⭐