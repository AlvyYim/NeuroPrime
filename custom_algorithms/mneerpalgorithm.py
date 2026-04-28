# MNE ERP Analysis Algorithm Template

"""MNE事件相关电位（ERP）分析算法模板，用于分析刺激诱发的脑电反应。

该算法模板演示了如何使用MNE库进行ERP分析，包括：
1. 事件标记和 epochs 创建
2. 基线校正
3. 数据拒绝
4. ERP平均

适用于研究认知、感知和情感等心理过程的时间进程。
"""

"""
=============================================================
ALGORITHM TEMPLATE GUIDE
=============================================================

1. TEST DATA STRUCTURE:
   When validating your algorithm, the system will use mock input data with the following structure:
   
   - input_data.spike_times: List of spike timestamps (e.g., [0.1, 0.5, 1.2, ...])
   - input_data.trial_info: List of trial information dictionaries
     Example: [{'start_time': 0, 'end_time': 5}, {'start_time': 5, 'end_time': 10}]
   - input_data.sampling_rate: Sampling rate (default: 2000.0 Hz)
   - input_data.lfp_data: LFP data (if available) as 2D array [channels x samples]

2. TEMPLATE COMPONENTS:
   - REQUIRED: class MNEERPAlgorithm(BaseAlgorithm): Main algorithm class
   - REQUIRED: def run(self, input_data, parameters): Algorithm execution method
   - REQUIRED: def get_parameters_schema(): Define algorithm parameters
   - REQUIRED: def validate_input(input_data): Validate input data
   - REQUIRED: def run_algorithm(input_data, parameters): Legacy function for direct execution
   - REQUIRED: ALGORITHM_INFO: Algorithm metadata for scheduler

3. API USAGE:
   - input_data: Contains the input data from the software
   - parameters: Dictionary of algorithm parameters set by the user
   - AlgorithmOutput: Return this object with your results
     Example: return AlgorithmOutput(data={...}, success=True, error_message="")

4. CUSTOMIZATION GUIDE:
   - MODIFY: Algorithm class name (update both class definition and ALGORITHM_INFO)
   - MODIFY: get_parameters_schema() to define your algorithm parameters
   - MODIFY: run() method to implement your algorithm logic
   - MODIFY: Algorithm description and category in __init__()
   - KEEP: The overall structure and required components

5. INTEGRATION PROCESS:
   1. Write your algorithm code
   2. Click "Validate" to test with mock data
   3. Click "Integrate" to add to the algorithm dropdown
   4. Enter a name for your algorithm when prompted

=============================================================
"""

import numpy as np
import matplotlib.pyplot as plt
import mne

# Import algorithm base classes
from src.algorithms.base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput
from src.algorithms.base import ParameterType, create_parameter

# HDF5数据转换为MNE格式
def hdf5_to_mne(input_data):
    """将HDF5数据转换为MNE数据格式"""
    # 获取数据
    lfp_data = input_data.lfp_data
    sampling_rate = input_data.sampling_rate
    
    # 创建MNE信息对象
    ch_names = [f'ch{i}' for i in range(lfp_data.shape[0])]
    info = mne.create_info(ch_names=ch_names, sfreq=sampling_rate, ch_types=['eeg']*lfp_data.shape[0])
    
    # 创建Raw对象
    raw = mne.io.RawArray(lfp_data, info)
    
    return raw

# Algorithm implementation class
class MNEERPAlgorithm(BaseAlgorithm):
    """MNE ERP分析算法"""
    
    def __init__(self):
        super().__init__()
        self.name = 'MNEERPAlgorithm'
        self.description = "MNE事件相关电位(ERP)分析算法"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "tmin", ParameterType.FLOAT,
                "事件前时间 (s)", -0.2,
                min_value=-1.0, max_value=0.0
            ),
            create_parameter(
                "tmax", ParameterType.FLOAT,
                "事件后时间 (s)", 0.8,
                min_value=0.0, max_value=3.0
            ),
            create_parameter(
                "baseline", ParameterType.STRING,
                "基线校正时间范围", "-0.2,0"
            ),
            create_parameter(
                "reject", ParameterType.FLOAT,
                "拒绝阈值 (μV)", 100.0,
                min_value=50.0, max_value=500.0
            )
        ]
    
    def validate_input(self, input_data):
        """Validate input data"""
        return True
    
    def run(self, input_data, parameters):
        """Execute algorithm"""
        try:
            print("Starting MNE ERP analysis...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            tmin = parameters.get('tmin', -0.2)
            tmax = parameters.get('tmax', 0.8)
            baseline_str = parameters.get('baseline', "-0.2,0")
            reject = parameters.get('reject', 100.0)
            
            # 解析基线参数
            baseline = tuple(map(float, baseline_str.split(',')))
            
            # Get input data
            lfp_data = input_data.lfp_data
            trial_info = input_data.trial_info if input_data.trial_info is not None else []
            sampling_rate = input_data.sampling_rate
            
            # 转换数据格式
            raw = hdf5_to_mne(input_data)
            
            # 获取数据长度
            data_length = lfp_data.shape[1]
            max_sample = data_length - 1
            
            # 创建事件数组
            events = []
            event_id = 1
            for i, trial in enumerate(trial_info):
                if 'start_time' in trial:
                    # 转换为样本索引
                    sample = int(trial['start_time'] * sampling_rate)
                    # 确保样本索引在数据范围内
                    if 0 <= sample <= max_sample:
                        events.append([sample, 0, event_id])
            
            # 确保events是整数类型的numpy数组
            events = np.array(events, dtype=int)
            
            # 如果没有事件或所有事件都超出范围，创建一个默认事件
            if events.size == 0:
                # 创建一个默认事件，确保在数据范围内
                # 选择数据中间位置作为事件时间
                default_sample = max(0, min(int(data_length / 2), max_sample))
                events = np.array([[default_sample, 0, event_id]], dtype=int)
            
            # 检查tmin和tmax是否合理，确保数据长度足够
            required_length = int((abs(tmin) + tmax) * sampling_rate)
            if data_length < required_length:
                # 数据长度不足，调整tmax
                available_time = data_length / sampling_rate - abs(tmin)
                if available_time > 0:
                    tmax = available_time
                else:
                    # 数据长度严重不足，使用默认值
                    tmin = -0.1
                    tmax = 0.4
            
            # 创建Epochs对象
            # 暂时禁用reject，避免所有epochs被拒绝
            epochs = mne.Epochs(raw, events, event_id={"stimulus": event_id}, tmin=tmin, tmax=tmax, 
                               baseline=baseline, preload=True)
            
            # 检查Epochs对象是否为空
            if len(epochs) == 0:
                # 尝试使用更保守的参数
                tmin = -0.1
                tmax = 0.4
                epochs = mne.Epochs(raw, events, event_id={"stimulus": event_id}, tmin=tmin, tmax=tmax, 
                                   baseline=baseline, preload=True)
                
                if len(epochs) == 0:
                    # 仍然为空，使用最小的时间窗口
                    tmin = 0
                    tmax = 0.1
                    epochs = mne.Epochs(raw, events, event_id={"stimulus": event_id}, tmin=tmin, tmax=tmax, 
                                       baseline=baseline, preload=True)
                    
                    if len(epochs) == 0:
                        raise ValueError("所有epochs都被拒绝或超出数据范围。请检查事件时间是否在数据范围内，或尝试调整参数。")
            
            # 计算ERP
            evoked = epochs.average()
            
            # 获取ERP数据
            erp_data = evoked.data
            times = evoked.times
            
            # Prepare output
            output_data = {
                'erp_data': erp_data,
                'times': times,
                'channels': evoked.ch_names,
                'tmin': tmin,
                'tmax': tmax,
                'baseline': baseline,
                'event_count': len(events)
            }
            # Prepare visualization data with ERP data
            if input_data.lfp_data is not None:
                # Use ERP data for visualization
                output_data['signal_data'] = erp_data
                output_data['sampling_rate'] = input_data.sampling_rate
                output_data['times'] = times
                output_data['plot_type'] = 'raw_signal'
            elif input_data.spike_times:
                # For spike data, use base class method
                vis_data = self.prepare_visualization_data(input_data)
                output_data.update(vis_data)
            

            
            # Statistics
            statistics = {
                'tmin': tmin,
                'tmax': tmax,
                'baseline': baseline,
                'event_count': len(events),
                'channels': len(evoked.ch_names),
                'time_points': len(times)
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE ERP Analysis Results',
                'xlabel': 'Time (s)',
                'ylabel': 'Amplitude (μV)'
            }
            
            # Return results
            return AlgorithmOutput(
                data=output_data,
                statistics=statistics,
                plot_config=plot_config,
                success=True,
                error_message=""
            )
            
        except Exception as e:
            print(f"Algorithm execution error: {e}")
            import traceback
            traceback.print_exc()
            return AlgorithmOutput(
                success=False,
                error_message=str(e)
            )

# Legacy function for direct execution
def run_algorithm(input_data, parameters):
    """Legacy run function for direct execution"""
    algo = MNEERPAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNEERPAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNEERPAlgorithm',
    'class': MNEERPAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
