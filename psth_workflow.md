# NeuroPrime PSTH 分析工作流程图

## 步骤 1: 启动 NeuroPrime 应用程序

1. **运行应用程序**
   - 双击 `run_project.bat` 文件，或在终端中运行 `venv\Scripts\python.exe run.py`
   - 等待应用程序启动完成

2. **应用程序界面**
   - 顶部：RibbonBar 标签页（Data Loading, Spike Detection, Spike Sorting, etc.）
   - 左侧：Data Browser（数据浏览器）
   - 中间：Parameter Configuration（参数配置面板）
   - 右侧：Visualization（可视化区域）

## 步骤 2: 新建工程

1. **点击 "Data Loading" 标签页**
   - 位于 RibbonBar 左侧第一个标签页

2. **点击 "New Project" 按钮**
   - 位于 "Project" 组中
   - 按钮文本："New Project"

3. **创建工程对话框**
   - 输入工程名称（例如："Test Project"）
   - 选择工程保存路径
   - 点击 "OK" 按钮

## 步骤 3: 导入试验数据

1. **点击 "Import Trial Data" 按钮**
   - 位于 "Data Import" 组中
   - 按钮文本："Import Trial Data"

2. **选择数据文件**
   - 导航到包含 NEV 或 HDF5 文件的文件夹
   - 选择要导入的数据文件
   - 点击 "Open" 按钮

3. **数据导入进度**
   - 等待数据导入完成
   - 导入完成后，数据会显示在左侧 Data Browser 中

## 步骤 4: 选择 Spike 数据

1. **在 Data Browser 中展开数据结构**
   - 展开工程节点
   - 展开试验节点
   - 找到 "Spike Data" 节点

2. **双击 "Spike Data" 节点**
   - 数据会被添加到中间的 "Selected Data Items" 列表中

## 步骤 5: 选择 PSTH 分析

1. **点击 "Spike Analysis" 标签页**
   - 位于 RibbonBar 中间位置

2. **点击 "PSTH Analysis" 按钮**
   - 位于 "Analysis Method" 组中
   - 按钮文本："PSTH Analysis"

## 步骤 6: 配置 PSTH 参数

1. **在 Parameter Configuration 面板中设置参数**
   - **Pre-stimulus time (ms):** 刺激前时间，默认为 200 ms
   - **Post-stimulus time (ms):** 刺激后时间，默认为 1000 ms
   - **Bin size (ms):** 时间窗大小，默认为 10 ms
   - **Smoothing sigma (ms):** 高斯平滑系数，默认为 15 ms

2. **确认参数设置**
   - 检查所有参数是否正确
   - 可以根据需要调整参数值

## 步骤 7: 运行分析

1. **点击 "Run Analysis" 按钮**
   - 位于 "Actions" 组中
   - 按钮文本："▶ Run Analysis"

2. **分析进度**
   - 等待分析完成
   - 分析完成后，结果会显示在右侧 Visualization 区域

## 步骤 8: 查看 PSTH 结果

1. **在 Visualization 区域查看结果**
   - PSTH 图表显示在右侧面板中
   - X 轴：时间（相对于刺激开始）
   - Y 轴：发放率（Hz）
   - 红色虚线：刺激开始时间

2. **分析结果信息**
   - 基线发放率
   - 峰值发放率
   - 峰值时间
   - 响应调制
   - 试次数
   - 总 Spike 数

## 步骤 9: 导出 PSTH 数据

1. **运行 `extract_psth_data.py` 脚本**
   - 在终端中运行：`venv\Scripts\python.exe extract_psth_data.py`
   - 脚本会提取 PSTH 数据并保存为 `psth_data.csv` 文件

2. **查看导出的数据**
   - `psth_data.csv` 文件包含以下列：
     - `time_from_stimulus`: 相对于刺激的时间（秒）
     - `firing_rate`: 发放率（Hz）
     - `spike_counts`: Spike 计数

## 工作流程图

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ 1. 启动应用程序 │────>│ 2. 新建工程     │────>│ 3. 导入试验数据 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │                         │
                              ▼                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ 8. 查看 PSTH 结果 │<────│ 7. 运行分析     │<────│ 6. 配置 PSTH 参数 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              ^                         │
                              │                         │
                              └─────────────────────────┘
                                        │
                                        ▼
                              ┌─────────────────┐
                              │ 5. 选择 PSTH 分析 │
                              └─────────────────┘
                                        ^
                                        │
                              ┌─────────────────┐
                              │ 4. 选择 Spike 数据 │
                              └─────────────────┘
```

## 注意事项

1. **数据格式**
   - 支持 NEV 文件（Blackrock 格式）和 HDF5 文件
   - 确保数据包含 Spike 事件和试次信息

2. **时间对齐**
   - 如果多组数据需要时间对齐，点击 "Time Alignment" 按钮进行配置

3. **参数调整**
   - 根据数据特性调整 PSTH 参数以获得最佳结果
   - 时间窗大小和平滑系数会影响 PSTH 的平滑程度

4. **结果解释**
   - 基线发放率：刺激前的平均发放率
   - 峰值发放率：刺激后的最高发放率
   - 响应调制：(峰值发放率 - 基线发放率) / 基线发放率
   - 峰值时间：发放率达到峰值的时间点

5. **故障排除**
   - 如果 PSTH 分析失败，检查数据是否包含有效的事件时间
   - 确保 Spike 时间和试次时间使用相同的时间基准
   - 检查是否有足够的试次进行分析