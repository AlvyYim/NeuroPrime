# EOG数据集成到HDF5文件的实现计划

## 1. 需求背景

当前NeuroPrime软件中的MNEICAArtifactRemovalAlgorithm算法在处理数据时，会尝试寻找EOG（眼电）通道来识别和去除眨眼伪迹。然而，目前的HDF5文件结构中没有包含EOG数据，导致算法在运行时会出现"No EOG channel(s) found"错误。

同时，我们发现在`coco1227rawdata`目录中存在`.eye`文件，这些是眼电数据文件，但尚未被加载到HDF5文件中。

## 2. 目标

将`.eye`数据集成到HDF5文件中，使MNEICAArtifactRemovalAlgorithm算法能够：
- 自动识别EOG通道
- 正确使用EOG数据进行伪迹去除
- 在没有EOG数据时仍能正常运行

## 3. 数据结构设计

### 3.1 HDF5文件结构调整

```
/ (根)
├── behavior/
│   ├── events
│   └── trials
├── metadata/
│   └── source_files
├── signals/
│   ├── channel_info  # 包含所有通道信息，包括EOG通道
│   ├── lfp_data      # 现有的LFP数据
│   └── eog_data      # 新增的EOG数据
└── spikes/
    ├── channel_info
    ├── spike_elec_ids
    ├── spike_times
    ├── spike_units
    └── spike_waveforms
```

### 3.2 通道信息结构

在`signals/channel_info`中添加EOG通道信息，确保每个通道包含：
- `channel_id`：通道ID
- `electrode_id`：电极ID
- `electrode_label`：电极标签
- `connector`：连接器
- `pin`：引脚
- `unit`：单位
- `conversion_factor`：转换因子
- `channel_type`：通道类型（'eeg'或'eog'）

## 4. 实现步骤

### 4.1 数据加载脚本

创建一个Python脚本来：
1. 读取`.eye`文件
2. 解析眼电数据
3. 将数据写入HDF5文件

```python
#!/usr/bin/env python3
# 读取.eye文件并写入HDF5

def load_eye_data(eye_file_path, hdf5_file_path):
    # 读取.eye文件
    # 解析数据
    # 写入HDF5文件
    pass
```

### 4.2 数据转换函数修改

修改`hdf5_to_mne`函数，使其能够：

```python
def hdf5_to_mne(input_data):
    """将HDF5数据转换为MNE数据格式"""
    # 获取LFP数据
    lfp_data = input_data.lfp_data
    sampling_rate = input_data.sampling_rate
    
    # 检查是否有EOG数据
    if hasattr(input_data, 'eog_data') and input_data.eog_data is not None:
        eog_data = input_data.eog_data
        # 合并LFP和EOG数据
        all_data = np.vstack([lfp_data, eog_data])
        # 创建通道名称和类型
        ch_names = [f'ch{i}' for i in range(lfp_data.shape[0])] + \
                   [f'eog{i}' for i in range(eog_data.shape[0])]
        ch_types = ['eeg'] * lfp_data.shape[0] + ['eog'] * eog_data.shape[0]
    else:
        all_data = lfp_data
        ch_names = [f'ch{i}' for i in range(lfp_data.shape[0])]
        ch_types = ['eeg'] * lfp_data.shape[0]
    
    # 创建MNE信息对象
    info = mne.create_info(ch_names=ch_names, sfreq=sampling_rate, ch_types=ch_types)
    
    # 创建Raw对象
    raw = mne.io.RawArray(all_data, info)
    
    return raw
```

### 4.3 算法适配

MNEICAArtifactRemovalAlgorithm算法已经具备处理EOG数据的能力：
- 当有EOG通道时，`ica.find_bads_eog()`会正常工作
- 当没有EOG通道时，算法会跳过EOG伪迹去除

无需对算法本身进行修改。

## 5. 测试计划

### 5.1 数据集成测试

1. **单元测试**：
   - 测试`.eye`文件读取功能
   - 测试HDF5文件写入功能
   - 测试数据转换功能

2. **集成测试**：
   - 测试完整的数据加载流程
   - 测试HDF5文件结构是否正确

### 5.2 算法功能测试

1. **有EOG数据的情况**：
   - 测试算法是否能正确识别EOG通道
   - 测试算法是否能正确去除眨眼伪迹
   - 测试结果是否符合预期

2. **无EOG数据的情况**：
   - 测试算法是否能正常运行
   - 测试算法是否能跳过EOG伪迹去除
   - 测试结果是否符合预期

## 6. 时间估计

| 任务 | 估计时间 |
|------|----------|
| 数据加载脚本开发 | 2小时 |
| 数据转换函数修改 | 1小时 |
| 数据集成测试 | 2小时 |
| 算法功能测试 | 2小时 |
| 文档更新 | 1小时 |
| **总计** | **8小时** |

## 7. 预期结果

完成本计划后，NeuroPrime软件将能够：
1. 从`.eye`文件中加载EOG数据到HDF5文件
2. 在MNEICAArtifactRemovalAlgorithm算法中正确使用EOG数据进行伪迹去除
3. 在没有EOG数据时仍能正常运行
4. 提供更准确的伪迹去除结果

## 8. 注意事项

1. **数据格式兼容性**：确保`.eye`文件的格式与解析脚本兼容
2. **通道同步**：确保EOG数据与LFP数据在时间上同步
3. **内存管理**：处理大型数据时注意内存使用
4. **错误处理**：添加适当的错误处理，确保数据加载过程稳定

## 9. 后续优化

1. **GUI支持**：在软件界面中添加EOG数据加载选项
2. **数据质量检查**：添加EOG数据质量检查功能
3. **多通道支持**：支持多个EOG通道的处理
4. **实时处理**：考虑添加实时EOG数据处理功能

---

*此文档为后续工作的参考，详细实现细节可能需要根据实际情况进行调整。*
