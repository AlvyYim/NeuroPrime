# NeuroPrime API 文档

## 目录
1. [算法基类](#算法基类)
2. [数据类](#数据类)
3. [算法实现](#算法实现)
4. [工程管理](#工程管理)
5. [数据解析](#数据解析)
6. [HDF5操作](#hdf5操作)

## 算法基类

### BaseAlgorithm

所有分析算法的抽象基类。

```python
from algorithms.base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput

class MyAlgorithm(BaseAlgorithm):
    def __init__(self):
        super().__init__()
        self.name = "MyAlgorithm"
        self.description = "My custom algorithm"
        self.category = "Custom"
    
    def get_parameters_schema(self):
        # 返回参数定义列表
        pass
    
    def validate_input(self, input_data):
        # 验证输入数据
        pass
    
    def run(self, input_data, parameters):
        # 执行算法
        pass
```

#### 方法

##### `get_parameters_schema()`

获取算法参数模式定义。

**返回**：
- `List[AlgorithmParameter]`：参数定义列表

**示例**：
```python
def get_parameters_schema(self):
    return [
        create_parameter(
            "threshold", ParameterType.FLOAT,
            "Detection threshold", 4.0,
            min_value=1.0, max_value=10.0
        ),
        create_parameter(
            "window_size", ParameterType.INTEGER,
            "Window size", 50,
            min_value=10, max_value=200
        )
    ]
```

##### `validate_input(input_data)`

验证输入数据是否符合要求。

**参数**：
- `input_data` (AlgorithmInput)：算法输入数据

**返回**：
- `bool`：True if valid

**示例**：
```python
def validate_input(self, input_data):
    return (input_data.lfp_data is not None and 
            input_data.sampling_rate > 0)
```

##### `run(input_data, parameters)`

执行算法。

**参数**：
- `input_data` (AlgorithmInput)：算法输入数据
- `parameters` (Dict[str, Any])：算法参数

**返回**：
- `AlgorithmOutput`：算法输出结果

**示例**：
```python
def run(self, input_data, parameters):
    import time
    start_time = time.time()
    
    # 算法逻辑
    result_data = self._process_data(input_data, parameters)
    
    execution_time = time.time() - start_time
    
    return AlgorithmOutput(
        data={'result': result_data},
        statistics={'mean': np.mean(result_data)},
        execution_time=execution_time,
        success=True
    )
```

##### `get_default_parameters()`

获取默认参数值。

**返回**：
- `Dict[str, Any]`：参数名 -> 默认值的字典

##### `validate_parameters(parameters)`

验证参数值。

**参数**：
- `parameters` (Dict[str, Any])：参数字典

**返回**：
- `tuple`：(is_valid, error_messages)

##### `get_info()`

获取算法信息。

**返回**：
- `Dict[str, Any]`：算法信息字典

## 数据类

### AlgorithmInput

算法输入数据类。

```python
from algorithms.base import AlgorithmInput

input_data = AlgorithmInput(
    lfp_data=lfp_array,           # LFP数据 [通道数 × 样本数]
    spike_times=spike_times,      # Spike时间戳
    spike_waveforms=waveforms,    # Spike波形
    sampling_rate=20000.0,        # 采样率 (Hz)
    trial_info=trial_list,        # 试次信息
    events=event_list             # 事件列表
)
```

#### 属性

| 属性 | 类型 | 描述 |
|------|------|------|
| `lfp_data` | np.ndarray | LFP信号数据 [通道数 × 样本数] |
| `spike_times` | np.ndarray | Spike时间戳数组 |
| `spike_waveforms` | np.ndarray | Spike波形数组 |
| `spike_elec_ids` | np.ndarray | Spike电极ID |
| `trial_info` | List[Dict] | 试次信息列表 |
| `events` | List[Dict] | 事件列表 |
| `sampling_rate` | float | 采样率 (Hz) |
| `duration` | float | 记录时长 (秒) |
| `num_channels` | int | 通道数量 |
| `time_range` | tuple | 时间范围 (start, end) |
| `trial_indices` | List[int] | 试次索引列表 |
| `extra_data` | Dict[str, Any] | 额外数据 |

### AlgorithmOutput

算法输出数据类。

```python
from algorithms.base import AlgorithmOutput

output = AlgorithmOutput(
    data={'spike_times': times, 'labels': labels},
    statistics={'total_spikes': 1000, 'firing_rate': 10.5},
    plot_config={'type': 'raster', 'title': 'Spike Raster'},
    execution_time=1.5,
    success=True
)
```

#### 属性

| 属性 | 类型 | 描述 |
|------|------|------|
| `data` | Dict[str, np.ndarray] | 分析结果数据 |
| `statistics` | Dict[str, float] | 统计信息 |
| `plot_config` | Dict[str, Any] | 图表配置 |
| `export_data` | Dict[str, np.ndarray] | 导出数据 |
| `metadata` | Dict[str, Any] | 元数据 |
| `execution_time` | float | 执行时间 (秒) |
| `success` | bool | 执行是否成功 |
| `error_message` | str | 错误信息 |

### AlgorithmParameter

算法参数定义类。

```python
from algorithms.base import AlgorithmParameter, ParameterType

param = AlgorithmParameter(
    name="threshold",
    param_type=ParameterType.FLOAT,
    description="Detection threshold",
    default_value=4.0,
    min_value=1.0,
    max_value=10.0,
    required=True
)
```

#### 属性

| 属性 | 类型 | 描述 |
|------|------|------|
| `name` | str | 参数名 |
| `param_type` | ParameterType | 参数类型 |
| `description` | str | 参数描述 |
| `default_value` | Any | 默认值 |
| `min_value` | float | 最小值（可选） |
| `max_value` | float | 最大值（可选） |
| `options` | List[str] | 选项列表（SELECT类型） |
| `required` | bool | 是否必需 |

#### ParameterType 枚举

- `INTEGER`：整数
- `FLOAT`：浮点数
- `STRING`：字符串
- `BOOLEAN`：布尔值
- `SELECT`：选择项
- `RANGE`：范围

## 算法实现

### Spike检测

#### SpikeDetectionThreshold

基于阈值的Spike检测算法。

```python
from algorithms.spike_detection import SpikeDetectionThreshold

detector = SpikeDetectionThreshold()

# 配置参数
params = {
    'threshold_factor': 4.5,      # 阈值系数
    'threshold_type': 'both',      # 阈值类型
    'window_ms': 1.0,             # 检测窗口 (ms)
    'refractory_ms': 1.0,         # 不应期 (ms)
    'filter_low': 300.0,          # 高通截止频率 (Hz)
    'filter_high': 3000.0,        # 低通截止频率 (Hz)
    'use_filter': True            # 是否使用滤波
}

# 运行检测
output = detector.run(input_data, params)

# 获取结果
spike_times = output.data['spike_times']
spike_channels = output.data['spike_channels']
spike_waveforms = output.data['spike_waveforms']
```

### Spike排序

#### SpikeSortingPCA

基于PCA和K-Means的Spike排序算法。

```python
from algorithms.spike_detection import SpikeSortingPCA

sorter = SpikeSortingPCA()

# 配置参数
params = {
    'n_components': 3,            # PCA主成分数量
    'n_clusters': 3,              # 聚类数量
    'max_iterations': 100,        # 最大迭代次数
    'random_state': 42            # 随机种子
}

# 准备输入
input_data = AlgorithmInput(spike_waveforms=waveforms)

# 运行排序
output = sorter.run(input_data, params)

# 获取结果
labels = output.data['labels']
features = output.data['features']
cluster_centers = output.data['cluster_centers']
```

### LFP分析

#### LFPPowerSpectrum

功率谱分析算法。

```python
from algorithms.lfp_analysis import LFPPowerSpectrum

analyzer = LFPPowerSpectrum()

# 配置参数
params = {
    'freq_range': [1, 100],       # 频率范围 (Hz)
    'window_size': 1024,          # 窗口大小
    'overlap': 0.5                # 重叠率
}

# 运行分析
output = analyzer.run(input_data, params)

# 获取结果
frequencies = output.data['frequencies']
psd = output.data['psd']
```

#### LFPSpectrogram

时频分析算法。

```python
from algorithms.lfp_analysis import LFPSpectrogram

analyzer = LFPSpectrogram()

# 配置参数
params = {
    'window_size': 256,           # STFT窗口大小
    'overlap': 128,               # 重叠样本数
    'freq_range': [1, 100]        # 频率范围
}

# 运行分析
output = analyzer.run(input_data, params)

# 获取结果
times = output.data['times']
frequencies = output.data['frequencies']
spectrogram = output.data['spectrogram']
```

### 行为分析

#### PSTHAnalysis

刺激后时间直方图分析。

```python
from algorithms.behavior_analysis import PSTHAnalysis

analyzer = PSTHAnalysis()

# 配置参数
params = {
    'time_window': [-0.5, 1.0],   # 时间窗口 (s)
    'bin_size': 0.01,             # 分箱大小 (s)
    'event_type': 'stimulus'      # 事件类型
}

# 运行分析
output = analyzer.run(input_data, params)

# 获取结果
time_bins = output.data['time_bins']
firing_rate = output.data['firing_rate']
```

### 解码分析

#### LDADecoder

线性判别分析解码算法。

```python
from algorithms.decoding import LDADecoder

decoder = LDADecoder()

# 配置参数
params = {
    'solver': 'svd',              # LDA求解器
    'shrinkage': 'auto',          # 收缩参数
    'n_components': 2,            # 降维维度
    'cv_folds': 5,                # 交叉验证折数
    'test_size': 0.2              # 测试集比例
}

# 准备输入
input_data = AlgorithmInput(
    extra_data={
        'neural_data': neural_data,   # [n_trials, n_features]
        'labels': labels               # [n_trials]
    }
)

# 运行解码
output = decoder.run(input_data, params)

# 获取结果
predictions = output.data['predictions']
accuracy = output.statistics['accuracy']
```

## 工程管理

### ProjectManager

工程管理器类。

```python
from project.project_manager import ProjectManager, TrialInfo

# 创建管理器
manager = ProjectManager()

# 创建工程
success = manager.create_project(
    project_path="/path/to/project",
    name="MyProject",
    description="A test project"
)

# 打开工程
success = manager.open_project("/path/to/project")

# 添加试验
trial_info = TrialInfo(
    name="Trial_001",
    experiment_name="Experiment_1",
    creation_time="2026-04-08T12:00:00",
    hdf5_file="Trial_001.h5",
    duration=100.0,
    num_channels=64,
    sampling_rate=20000.0
)
manager.add_trial(trial_info)

# 获取试验列表
trials = manager.get_all_trials()

# 保存工程
manager.save_project()

# 关闭工程
manager.close_project()
```

#### 方法

##### `create_project(project_path, name, description="")`

创建新工程。

**参数**：
- `project_path` (str)：工程路径
- `name` (str)：工程名称
- `description` (str)：工程描述

**返回**：
- `bool`：True if successful

##### `open_project(project_path)`

打开已有工程。

**参数**：
- `project_path` (str)：工程路径

**返回**：
- `bool`：True if successful

##### `add_trial(trial_info)`

添加试验到工程。

**参数**：
- `trial_info` (TrialInfo)：试验信息

**返回**：
- `bool`：True if successful

##### `remove_trial(trial_name)`

从工程中删除试验。

**参数**：
- `trial_name` (str)：试验名称

**返回**：
- `bool`：True if successful

##### `get_trial(trial_name)`

获取试验信息。

**参数**：
- `trial_name` (str)：试验名称

**返回**：
- `TrialInfo`：试验信息，未找到返回None

##### `get_all_trials()`

获取所有试验列表。

**返回**：
- `List[TrialInfo]`：试验信息列表

##### `save_project()`

保存工程配置。

**返回**：
- `bool`：True if successful

##### `close_project()`

关闭当前工程。

##### `is_project_opened()`

检查是否有工程已打开。

**返回**：
- `bool`：True if a project is opened

## 数据解析

### NS3Parser

NS3文件解析器。

```python
from parsers.ns3_parser import NS3Parser, parse_ns3

# 方法1: 使用解析器类
parser = NS3Parser("path/to/file.ns3")
if parser.parse():
    # 获取解析结果
    basic_header = parser.basic_header
    extended_headers = parser.extended_headers
    raw_data = parser.raw_data
    physical_data = parser.get_physical_data()
    channel_info = parser.get_channel_info()
    sampling_rate = parser.get_sampling_rate()
    duration = parser.get_duration()

# 方法2: 使用便捷函数
result = parse_ns3("path/to/file.ns3")
if result:
    basic_header = result['basic_header']
    raw_data = result['raw_data']
    physical_data = result['physical_data']
```

#### 属性

| 属性 | 类型 | 描述 |
|------|------|------|
| `basic_header` | NS3BasicHeader | 基本头信息 |
| `extended_headers` | List[NS3ExtendedHeader] | 扩展头信息列表 |
| `data_packets` | List[NS3DataPacket] | 数据包列表 |
| `raw_data` | np.ndarray | 原始数据 [通道数 × 样本数] |

#### 方法

##### `parse()`

解析NS3文件。

**返回**：
- `bool`：True if successful

##### `get_physical_data()`

获取物理值数据 (uV)。

**返回**：
- `np.ndarray`：物理值数据 [通道数 × 样本数]

##### `get_conversion_factors()`

获取数字值到物理值的转换因子。

**返回**：
- `np.ndarray`：转换因子数组 [通道数]

##### `get_channel_info()`

获取通道信息。

**返回**：
- `List[Dict]`：通道信息列表

##### `get_sampling_rate()`

获取采样率。

**返回**：
- `float`：采样率 (Hz)

##### `get_duration()`

获取记录时长。

**返回**：
- `float`：时长 (秒)

### NEVParser

NEV文件解析器。

```python
from parsers.nev_parser import NEVParser, parse_nev

# 解析NEV文件
result = parse_nev("path/to/file.nev")
if result:
    spike_times = result['spike_times']
    spike_waveforms = result['spike_waveforms']
    spike_elec_ids = result['spike_elec_ids']
```

### MBMParser

MBM文件解析器。

```python
from parsers.mbm_parser import parse_mbm

# 解析MBM文件
result = parse_mbm("path/to/file.mbm")
if result:
    for event in result:
        print(f"Event: {event['type']}, Time: {event['time']}")
```

## HDF5操作

### HDF5Writer

HDF5文件写入器。

```python
from data.hdf5_writer import (
    convert_ns3_to_hdf5,
    convert_nev_to_hdf5,
    create_hdf5_structure
)

# 转换NS3到HDF5
convert_ns3_to_hdf5(
    ns3_file="path/to/file.ns3",
    hdf5_file="path/to/output.h5",
    experiment_name="Experiment 1",
    trial_name="Trial_001"
)

# 添加NEV数据到HDF5
convert_nev_to_hdf5(
    nev_file="path/to/file.nev",
    hdf5_file="path/to/output.h5"
)
```

### HDF5Reader

HDF5文件读取器。

```python
from data.hdf5_reader import HDF5Reader

# 创建读取器
reader = HDF5Reader("path/to/file.h5")

# 读取信号数据
lfp_data = reader.read_signal_data(channel=0)

# 读取Spike数据
spike_times = reader.read_spike_times()
spike_waveforms = reader.read_spike_waveforms()

# 读取行为数据
trial_info = reader.read_trial_info()
events = reader.read_events()

# 获取元数据
metadata = reader.read_metadata()
```

#### 方法

##### `read_signal_data(channel=None, time_range=None)`

读取信号数据。

**参数**：
- `channel` (int)：通道索引，None表示所有通道
- `time_range` (tuple)：时间范围 (start, end) in seconds

**返回**：
- `np.ndarray`：信号数据

##### `read_spike_times()`

读取Spike时间戳。

**返回**：
- `np.ndarray`：Spike时间戳数组

##### `read_spike_waveforms()`

读取Spike波形。

**返回**：
- `np.ndarray`：Spike波形数组

##### `read_trial_info()`

读取试次信息。

**返回**：
- `List[Dict]`：试次信息列表

##### `read_events()`

读取事件数据。

**返回**：
- `List[Dict]`：事件列表

##### `read_metadata()`

读取元数据。

**返回**：
- `Dict`：元数据字典

## 工具函数

### create_parameter

创建算法参数的便捷函数。

```python
from algorithms.base import create_parameter, ParameterType

param = create_parameter(
    name="threshold",
    param_type=ParameterType.FLOAT,
    description="Detection threshold",
    default_value=4.0,
    min_value=1.0,
    max_value=10.0,
    required=True
)
```

## 示例代码

### 完整分析流程

```python
import numpy as np
from algorithms.base import AlgorithmInput
from algorithms.spike_detection import SpikeDetectionThreshold, SpikeSortingPCA
from project.project_manager import ProjectManager

# 1. 创建工程
manager = ProjectManager()
manager.create_project("/path/to/project", "MyProject")

# 2. 加载数据
from parsers.ns3_parser import parse_ns3
result = parse_ns3("path/to/data.ns3")
lfp_data = result['raw_data']
sampling_rate = result['sampling_rate']

# 3. Spike检测
detector = SpikeDetectionThreshold()
input_data = AlgorithmInput(
    lfp_data=lfp_data,
    sampling_rate=sampling_rate
)
params = detector.get_default_parameters()
output = detector.run(input_data, params)

spike_times = output.data['spike_times']
spike_waveforms = output.data['spike_waveforms']

print(f"Detected {len(spike_times)} spikes")

# 4. Spike排序
if len(spike_waveforms) > 0:
    sorter = SpikeSortingPCA()
    sort_input = AlgorithmInput(spike_waveforms=spike_waveforms)
    sort_params = {'n_clusters': 3}
    sort_output = sorter.run(sort_input, sort_params)
    
    labels = sort_output.data['labels']
    print(f"Sorted into {len(np.unique(labels))} clusters")

# 5. 保存结果
manager.save_project()
manager.close_project()
```

## 注意事项

1. **内存管理**：处理大数据时注意内存使用，可以分块处理
2. **错误处理**：始终检查返回值和success标志
3. **参数验证**：使用validate_parameters验证参数
4. **输入验证**：使用validate_input验证输入数据
5. **资源释放**：使用close_project释放资源

## 版本信息

- **API版本**：1.0.0
- **Python版本**：3.10+
- **最后更新**：2026-04-08
