# 数据预处理层设计文档

## 1. 设计目标

为NeuroPrime软件设计一个统一的数据预处理层，解决以下问题：

1. **多组数据统一管理**：避免每个算法重复实现数据加载和合并逻辑
2. **数据变化检测**：确保用户添加新数据后能正确加载
3. **时间对齐兼容**：与现有的`TimeAlignmentConfig`系统兼容
4. **保持架构解耦**：数据加载、算法调度、绘图保持独立

## 2. 当前架构分析

### 2.1 数据流

```
用户选择数据 → ParameterPanel → MainWindow._on_run_analysis → 
_run_analysis_async → 算法特定数据准备 → Algorithm.run() → 
VisualizationArea.display_xxx()
```

### 2.2 存在的问题

1. **索引对应问题**：`data_list`和`data_items`通过索引对应，如果某些项加载失败会导致错位
2. **重复代码**：每个算法（PSTH、Raster、TuningCurve、ROC等）都重复实现了多试验数据合并逻辑
3. **无缓存机制**：每次运行都重新加载数据，即使数据选择没有变化

## 3. 数据预处理层架构

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     DataPreprocessor                            │
│                     (数据预处理层)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  DataCache   │    │ DataLoader   │    │DataValidator │      │
│  │  (数据缓存)   │    │  (数据加载)   │    │  (数据验证)  │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │MultiTrial    │    │TimeAlignment │    │InputBuilder  │      │
│  │  Merger      │    │  Handler     │    │ (输入构建)   │      │
│  │(多试验合并)  │    │ (时间对齐)   │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AlgorithmInput (标准接口)                     │
│  - lfp_data: 合并后的LFP数据                                     │
│  - spike_times: 合并后的Spike时间（带trial_source标记）          │
│  - trial_info: 合并后的试次信息（带trial_source标记）            │
│  - metadata: 包含数据来源、时间偏移等信息                        │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 核心组件

#### 3.2.1 DataCache (数据缓存)

```python
@dataclass
class DataCacheEntry:
    data: np.ndarray
    trial_name: str
    data_id: str
    data_type: str
    load_time: float

class DataCache:
    def get(self, unique_id: str) -> Optional[DataCacheEntry]
    def put(self, unique_id: str, entry: DataCacheEntry)
    def invalidate(self, unique_id: str)
    def clear(self)
```

**功能**：
- 根据数据项ID缓存加载的数据
- 支持缓存过期机制
- 检测数据选择变化，避免重复加载

#### 3.2.2 DataLoader (数据加载)

```python
class DataLoader:
    def load(self, item: Dict, time_config: Optional[TimeAlignmentConfig]) -> Optional[np.ndarray]
```

**功能**：
- 从HDF5文件加载数据
- 应用时间对齐配置
- 处理不同数据类型（spike、lfp、behavior）

#### 3.2.3 MultiTrialMerger (多试验合并)

```python
class MultiTrialMerger:
    def merge_spike_data(self, spike_items: List[Dict], 
                        time_config: Optional[TimeAlignmentConfig]) -> Tuple[np.ndarray, Dict]
    def merge_trial_info(self, trial_names: Set[str], 
                        time_offsets: Dict[str, float]) -> List[Dict]
```

**功能**：
- 合并多个试验的Spike数据（应用时间偏移）
- 合并试次信息（添加trial_source标记）
- 计算各试验的时间偏移量

#### 3.2.4 TimeAlignmentHandler (时间对齐处理)

```python
class TimeAlignmentHandler:
    def apply(self, data: np.ndarray, 
             aligned_window: Tuple[float, float],
             sampling_rate: float) -> np.ndarray
```

**功能**：
- 与现有的`TimeAlignmentConfig`兼容
- 在数据加载后应用时间截取
- 支持不同数据类型的对齐策略

#### 3.2.5 InputBuilder (输入构建)

```python
class InputBuilder:
    def build(self, 
             spike_data: Optional[np.ndarray],
             lfp_data: Optional[np.ndarray],
             trial_info: Optional[List[Dict]],
             metadata: Dict) -> AlgorithmInput
```

**功能**：
- 构建标准的`AlgorithmInput`对象
- 设置采样率、通道数等元数据
- 添加时间范围信息

## 4. 接口设计

### 4.1 主要接口

```python
class DataPreprocessor:
    def __init__(self, project_manager: ProjectManager)
    
    def prepare_input(self, 
                     data_items: List[Dict[str, Any]], 
                     algorithm_name: str,
                     time_alignment_config: Optional[TimeAlignmentConfig] = None
                     ) -> Tuple[AlgorithmInput, Dict[str, Any]]
    
    def clear_cache(self)
```

### 4.2 使用示例

```python
# 初始化预处理器
preprocessor = DataPreprocessor(project_manager)

# 准备输入数据
input_data, metadata = preprocessor.prepare_input(
    data_items=[
        {'id': 'spike_times', 'trial_name': 'FC_Grating_014', 'data_type': 'spike'},
        {'id': 'spike_times', 'trial_name': 'Fix_Grating_005', 'data_type': 'spike'},
        {'id': 'trials', 'trial_name': 'FC_Grating_014', 'data_type': 'behavior'},
    ],
    algorithm_name='ROCAnalysis',
    time_alignment_config=time_config  # 可选
)

# 运行算法
algorithm = scheduler.get_algorithm('ROCAnalysis')
output = algorithm.run(input_data, parameters)

# 显示结果
visualization_area.display_roc_curve(output.data, output.plot_config)
```

## 5. 与现有系统的集成

### 5.1 与TimeAlignmentConfig的集成

```python
# 在ParameterPanel中，用户配置时间对齐后
time_config = TimeAlignmentConfig()
time_config.add_data_item('FC_Grating_014/spike_times', (0.0, 100.0))
time_config.set_global_time_window(10.0, 50.0)

# 传递给预处理器
input_data, metadata = preprocessor.prepare_input(
    data_items=data_items,
    algorithm_name=algorithm_name,
    time_alignment_config=time_config
)
```

### 5.2 与Algorithm接口的兼容

预处理层的输出是标准的`AlgorithmInput`，与现有算法接口完全兼容：

```python
@dataclass
class AlgorithmInput:
    lfp_data: Optional[np.ndarray] = None
    spike_times: Optional[np.ndarray] = None
    spike_waveforms: Optional[np.ndarray] = None
    trial_info: Optional[List[Dict]] = None
    sampling_rate: float = 2000.0
    time_range: Optional[tuple] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)
```

## 6. 实现建议

### 6.1 渐进式重构

建议采用渐进式重构策略：

1. **第一阶段**：创建`DataPreprocessor`类，但不替换现有代码
2. **第二阶段**：选择一个算法（如ROCAnalysis）试用新接口
3. **第三阶段**：逐步迁移其他算法
4. **第四阶段**：移除旧的数据加载代码

### 6.2 向后兼容

在重构过程中保持向后兼容：

```python
# 在main_window.py中，可以支持两种模式
USE_NEW_PREPROCESSOR = True  # 特性开关

if USE_NEW_PREPROCESSOR:
    input_data, metadata = preprocessor.prepare_input(...)
else:
    # 保留旧的数据加载逻辑
    ...
```

### 6.3 错误处理

预处理层应该提供详细的错误信息：

```python
metadata = {
    'data_sources': {
        'FC_Grating_014/spike_times': {'loaded': True, 'n_points': 150496},
        'Fix_Grating_005/spike_times': {'loaded': False, 'error': 'File not found'}
    },
    'load_errors': ['Failed to load: Fix_Grating_005/spike_times'],
    'time_offsets': {'FC_Grating_014': 0.0, 'Fix_Grating_005': 110.5}
}
```

## 7. 文件位置

- 实现文件：`src/algorithms/data_preprocessor.py`
- 设计文档：`docs/data_preprocessor_design.md`

## 8. 总结

这个数据预处理层设计：

1. **保持架构解耦**：算法仍然通过标准的`AlgorithmInput`接口接收数据
2. **统一多组数据处理**：避免每个算法重复实现数据合并逻辑
3. **兼容时间对齐**：与现有的`TimeAlignmentConfig`系统无缝集成
4. **支持缓存机制**：避免重复加载相同的数据
5. **渐进式重构**：可以逐步迁移，不影响现有功能
