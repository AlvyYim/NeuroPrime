# 多组数据处理框架问题记录

## 问题描述

当前NeuroPrime框架缺乏统一的多组数据处理机制，导致：

1. **代码重复严重**：每个支持多组数据的算法都在主窗口中重复实现数据合并逻辑
2. **维护困难**：修改数据合并逻辑需要修改多处代码
3. **容易出错**：不同算法的数据处理逻辑可能存在细微差异

## 当前状况

### 受影响的算法

以下算法都实现了自己的多组数据处理逻辑（代码重复）：

- [x] 调谐曲线分析 (TuningCurveAnalysis)
- [x] ROC分析 (ROCAnalysis)
- [x] PSTH分析 (PSTHAnalysis)
- [x] 栅格图分析 (RasterPlotAnalysis)

### 重复的代码模式

每个算法都包含以下重复逻辑：

```python
# 1. 收集Spike和行为数据项
spike_data_items = []
behavior_data_items = []
for idx, item in enumerate(data_items):
    if isinstance(item, dict):
        data_type = item.get('data_type', '')
        if data_type == 'spike' and idx < len(data_list):
            spike_data_items.append({...})
        elif data_type == 'behavior':
            behavior_data_items.append({...})

# 2. 为每个试验分配时间偏移量
all_spike_times = []
trial_time_offsets = {}
current_offset = 0.0
for spike_item in spike_data_items:
    trial_name = spike_item['trial_name']
    trial_time_offsets[trial_name] = current_offset
    # ... 合并Spike时间
    current_offset += max(spike_list) + 10.0

# 3. 从所有behavior数据加载trial信息
all_trial_info = []
for behav_item in behavior_data_items:
    trial_name = behav_item.get('trial_name', '')
    time_offset = trial_time_offsets.get(trial_name, 0.0)
    # ... 从HDF5加载trial信息并应用偏移
```

## 问题影响

### 短期影响
- 开发新算法时需要复制粘贴数据合并代码
- 容易遗漏某些数据处理步骤
- 调试困难（需要检查多处代码）

### 长期影响
- 代码维护成本高
- 新增功能时需要修改多处
- 不同算法的行为可能不一致

## 建议解决方案

### 方案B：添加数据预处理层（推荐）

创建统一的数据合并器：

```python
# src/data/data_merger.py

class DataMerger:
    """统一的多组数据合并器"""
    
    def __init__(self, project_manager):
        self.project_manager = project_manager
    
    def merge_multi_trial_data(self, data_items, data_list) -> Dict:
        """
        合并多试验数据
        
        Returns:
            {
                'spike_times': np.ndarray,  # 合并后的Spike时间
                'trial_info': List[Dict],   # 合并后的试次信息
                'trial_sources': Dict,       # 试验来源映射
                'time_offsets': Dict         # 时间偏移量映射
            }
        """
        # 统一实现数据合并逻辑
        ...
```

### 使用方式

在主窗口中统一调用：

```python
# 在主窗口中
from src.data.data_merger import DataMerger

class MainWindow:
    def __init__(self):
        self.data_merger = DataMerger(self.project_manager)
    
    def run_analysis(self, algorithm_name, data_items, data_list):
        # 所有算法共享数据合并逻辑
        merged_data = self.data_merger.merge_multi_trial_data(
            data_items, data_list
        )
        
        input_data = AlgorithmInput(
            spike_times=merged_data['spike_times'],
            trial_info=merged_data['trial_info']
        )
        
        # 运行算法
        output = algorithm.run(input_data, parameters)
```

## 优点

1. **代码复用**：所有算法共享数据合并逻辑
2. **易于维护**：修改只需改一处
3. **行为一致**：确保所有算法的数据处理行为相同
4. **降低Bug风险**：减少重复代码，降低出错概率

## 风险

⚠️ **可能引发新的Bug**：
- 重构过程中可能引入新的问题
- 需要全面测试所有受影响的算法
- 可能影响现有功能

## 决策

**暂时不实施**，原因：
1. 当前功能已经稳定
2. 重构风险较高
3. 需要充分测试时间

**未来考虑实施时机**：
- 添加新算法时
- 现有功能需要大幅修改时
- 有充足时间进行测试时

## 相关文件

- `src/ui/main_window.py` - 主窗口，包含重复的数据合并逻辑
- `src/algorithms/behavior_analysis.py` - 行为分析算法
- `src/data/` - 建议添加数据预处理层的位置

## 记录时间

2026-04-13

## 记录人

AI Assistant
