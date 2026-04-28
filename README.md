# NeuroPrime - 猕猴脑电生理数据分析平台

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

NeuroPrime是一款基于PyQt6的专业电生理数据分析软件，专门用于分析猕猴脑电信号数据。支持完整的分析流程，包括数据加载、预处理、Spike检测与排序、LFP分析、行为对齐、解码分析等功能。

## 功能特性

### 核心功能
- **工程管理**：创建、打开、保存工程，管理多个试验数据
- **数据加载**：支持Blackrock NeuroPort系统的NS3、NEV、MBM文件格式
- **数据转换**：自动将原始数据转换为HDF5标准格式
- **时间对齐**：支持多数据项的时间对齐配置

### 分析模块
- **Spike检测**：基于阈值的Spike检测算法
- **Spike排序**：PCA+KMeans、GMM等聚类算法
- **LFP分析**：功率谱分析、时频分析、滤波分析
- **行为分析**：PSTH分析、栅格图、调谐曲线、ROC分析
- **解码分析**：LDA、SVM、随机森林等机器学习算法

### 可视化
- **多标签页显示**：支持同时显示多个图表
- **专业图表**：栅格图、PSTH、调谐曲线、功率谱密度图等
- **交互操作**：缩放、平移、区域选取
- **导出功能**：支持PNG、PDF、SVG格式导出

## 系统要求

- **操作系统**：Windows 10/11, macOS 10.14+, Linux
- **Python版本**：3.10或更高
- **内存**：建议8GB以上
- **磁盘空间**：根据数据量而定，建议预留10GB以上

## 安装指南

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/neuroprime.git
cd neuroprime
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行程序

```bash
python -m src.ui.main_window
```

或者

```bash
python run.py
```

## 快速开始

### 1. 创建新工程

1. 启动NeuroPrime
2. 点击"文件" -> "新建工程" 或按 `Ctrl+N`
3. 输入工程名称和路径
4. 点击"确定"创建工程

### 2. 导入数据

1. 点击"数据加载"标签页
2. 点击"导入试验"按钮
3. 选择NS3文件（NEV和MBM文件会自动检测）
4. 输入试验名称
5. 点击"导入"开始处理

### 3. 运行分析

1. 在左侧导航栏选择要分析的试验
2. 在参数面板选择算法
3. 配置算法参数
4. 选择要分析的数据项
5. 点击"运行分析"

### 4. 查看结果

分析结果将自动显示在右侧可视化区域，支持：
- 多标签页切换
- 图表缩放和平移
- 导出为图片

## 项目结构

```
NeuroPrime/
├── src/                    # 源代码目录
│   ├── algorithms/         # 分析算法
│   │   ├── base.py         # 算法基类
│   │   ├── spike_detection.py
│   │   ├── spike_sorting.py
│   │   ├── lfp_analysis.py
│   │   ├── behavior_analysis.py
│   │   ├── decoding.py
│   │   └── scheduler.py    # 算法调度器
│   ├── data/               # 数据处理
│   │   ├── hdf5_reader.py
│   │   └── hdf5_writer.py
│   ├── parsers/            # 数据解析器
│   │   ├── ns3_parser.py   # NS3文件解析
│   │   ├── nev_parser.py   # NEV文件解析
│   │   └── mbm_parser.py   # MBM文件解析
│   ├── project/            # 工程管理
│   │   ├── project_manager.py
│   │   └── data_enumerator.py
│   ├── ui/                 # 用户界面
│   │   ├── main_window.py  # 主窗口
│   │   ├── ribbon_bar.py   # 工具栏
│   │   ├── navigator.py    # 导航栏
│   │   ├── parameter_panel.py
│   │   ├── visualization_area.py
│   │   └── dialogs/        # 对话框
│   │       ├── new_project_dialog.py
│   │       ├── import_dialog.py
│   │       └── time_alignment_dialog.py
│   └── visualization/      # 可视化
│       ├── data_interface.py
│       └── time_alignment.py
├── tests/                  # 测试代码
├── Document/               # 文档
├── coco1227rawdata/        # 示例数据
├── requirements.txt        # 依赖列表
├── README.md              # 本文件
└── LICENSE                # 许可证
```

## 数据格式

### 支持的原始数据格式

- **.ns3**：连续宽频信号（LFP和Spike）
- **.nev**：Spike事件和波形数据
- **.mbm**：行为任务参数和事件

### 内部数据格式（HDF5）

```
/trial_name.h5
├── /signals
│   ├── /raw
│   │   ├── data          # [n_channels, n_samples]
│   │   ├── fs            # 采样率
│   │   └── channel_names
│   └── /lfp
├── /spikes
│   ├── times             # Spike时间戳
│   ├── waveforms         # Spike波形
│   ├── channels          # 通道信息
│   └── labels            # 聚类标签
└── /behavior
    ├── events            # 行为事件
    └── trials            # 试次信息
```

## 算法说明

### Spike检测
- **阈值检测**：基于标准差倍数的阈值检测
- 参数：阈值倍数（默认4.0）、检测通道、波形窗口

### Spike排序
- **PCA+KMeans**：主成分分析+K均值聚类
- **GMM**：高斯混合模型概率聚类
- 参数：聚类数量、特征维度

### LFP分析
- **功率谱分析**：Welch方法计算功率谱密度
- **时频分析**：STFT短时傅里叶变换
- **滤波分析**：自定义频段滤波

### 行为分析
- **PSTH**：刺激后时间直方图
- **栅格图**：Spike时间栅格图
- **调谐曲线**：刺激-响应调谐关系
- **ROC分析**：接收者操作特征曲线

### 解码分析
- **LDA**：线性判别分析
- **SVM**：支持向量机
- **随机森林**：随机森林分类器

## 开发指南

### 添加自定义算法

1. 继承`BaseAlgorithm`基类
2. 实现`run`方法
3. 定义`parameters_schema`参数模式
4. 注册到算法调度器

示例：

```python
from src.algorithms.base import BaseAlgorithm

class MyAlgorithm(BaseAlgorithm):
    name = "my_algorithm"
    description = "我的自定义算法"
    
    parameters_schema = {
        'threshold': {
            'type': 'float',
            'default': 4.0,
            'min': 1.0,
            'max': 10.0,
            'label': '阈值'
        }
    }
    
    def run(self, input_data):
        # 实现算法逻辑
        return output_data
```

### 运行测试

```bash
# 运行所有测试
python test_solo_coder.py

# 运行特定测试
python test_ui_components.py
```

## 常见问题

### Q: 导入数据时出现错误？
A: 请确保：
1. 数据文件完整且未损坏
2. 配套文件（.ns3, .nev, .mbm）名称一致
3. 磁盘空间充足

### Q: 如何批量导入数据？
A: 使用"批量导入"功能，选择包含数据文件的文件夹，系统会自动识别配套的试验文件。

### Q: 分析结果如何导出？
A: 在可视化区域点击"保存"按钮，支持PNG、PDF、SVG格式。

### Q: 如何添加自定义算法？
A: 参考"开发指南"中的"添加自定义算法"部分，实现算法接口并注册到调度器。

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目主页：https://github.com/yourusername/neuroprime
- 问题反馈：https://github.com/yourusername/neuroprime/issues
- 邮箱：your.email@example.com

## 致谢

感谢以下开源项目的支持：
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- [NumPy](https://numpy.org/)
- [SciPy](https://scipy.org/)
- [h5py](https://www.h5py.org/)
- [scikit-learn](https://scikit-learn.org/)

## 更新日志

### v1.0.0 (2026-04-08)
- 初始版本发布
- 实现核心功能：工程管理、数据导入、Spike检测与排序、LFP分析、行为分析、解码分析
- 支持NS3、NEV、MBM文件格式
- 提供完整的可视化功能

---

**注意**：本项目仍在积极开发中，API可能会发生变化。请关注更新日志获取最新信息。
