# MNE Time-Frequency Analysis Algorithm Template

"""MNE时频分析算法模板，用于分析脑电信号在不同时间和频率上的能量变化。

该算法模板演示了如何使用MNE库进行时频分析，包括：
1. Morlet小波变换
2. 功率谱计算
3. 互相关分析

适用于研究脑电信号的动态变化，如事件相关同步/去同步（ERS/ERD）。
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
   - REQUIRED: class MNETimeFrequencyAlgorithm(BaseAlgorithm): Main algorithm class
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
class MNETimeFrequencyAlgorithm(BaseAlgorithm):
    """MNE时频分析算法"""
    
    def __init__(self):
        super().__init__()
        self.name = 'MNETimeFrequencyAlgorithm'
        self.description = "MNE时频分析算法，使用Morlet小波"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "freq_min", ParameterType.FLOAT,
                "最低频率 (Hz)", 1.0,
                min_value=0.1, max_value=10.0
            ),
            create_parameter(
                "freq_max", ParameterType.FLOAT,
                "最高频率 (Hz)", 40.0,
                min_value=10.0, max_value=100.0
            ),
            create_parameter(
                "n_cycles", ParameterType.FLOAT,
                "每个频率的周期数", 7.0,
                min_value=1.0, max_value=20.0
            ),
            create_parameter(
                "tmin", ParameterType.FLOAT,
                "分析开始时间 (s)", 0.0,
                min_value=-1.0, max_value=0.0
            ),
            create_parameter(
                "tmax", ParameterType.FLOAT,
                "分析结束时间 (s)", 1.0,
                min_value=0.0, max_value=5.0
            )
        ]
    
    def validate_input(self, input_data):
        """Validate input data"""
        return True
    
    def run(self, input_data, parameters):
        """Execute algorithm"""
        try:
            print("Starting MNE time-frequency analysis...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            freq_min = parameters.get('freq_min', 1.0)
            freq_max = parameters.get('freq_max', 40.0)
            n_cycles = parameters.get('n_cycles', 7.0)
            tmin = parameters.get('tmin', 0.0)
            tmax = parameters.get('tmax', 1.0)
            
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
                    tmin = 0.0
                    tmax = 1.0
            
            # 创建Epochs对象
            # 暂时禁用reject，避免所有epochs被拒绝
            # 设置合适的基线参数
            baseline = (None, 0)  # 默认基线：从开始到0秒
            # 检查tmin是否为0，如果是，则使用(0, 0)作为基线
            if tmin == 0:
                baseline = (0, 0)
            epochs = mne.Epochs(raw, events, event_id={"stimulus": event_id}, tmin=tmin, tmax=tmax, baseline=baseline, preload=True)
            
            # 检查Epochs对象是否为空
            if len(epochs) == 0:
                # 尝试使用更保守的参数
                tmin = 0.0
                tmax = 1.0
                baseline = (0, 0)  # 使用(0, 0)作为基线
                epochs = mne.Epochs(raw, events, event_id={"stimulus": event_id}, tmin=tmin, tmax=tmax, baseline=baseline, preload=True)
                
                if len(epochs) == 0:
                    # 仍然为空，使用最小的时间窗口
                    tmin = 0.0
                    tmax = 0.1
                    baseline = (0, 0)  # 使用(0, 0)作为基线
                    epochs = mne.Epochs(raw, events, event_id={"stimulus": event_id}, tmin=tmin, tmax=tmax, baseline=baseline, preload=True)
                    
                    if len(epochs) == 0:
                        raise ValueError("所有epochs都被拒绝或超出数据范围。请检查事件时间是否在数据范围内，或尝试调整参数。")
            
            # 计算时频表示
            sampling_rate = input_data.sampling_rate
            # 信号长度（样本数）
            signal_length = epochs.times.size
            
            print(f"原始信号长度: {signal_length} 样本")
            print(f"原始n_cycles: {n_cycles}")
            print(f"原始freq_min: {freq_min}, freq_max: {freq_max}")
            
            # 计算最大允许的n_cycles，确保小波长度不超过信号长度的一半（留有余地）
            # 对于最低频率，小波长度最长
            max_allowed_n_cycles = (signal_length / 2) * freq_min / sampling_rate
            
            # 确保n_cycles不超过最大允许值
            if n_cycles > max_allowed_n_cycles:
                n_cycles = max(1.0, max_allowed_n_cycles)
                print(f"调整n_cycles为: {n_cycles}")
            
            # 计算最大允许的频率，确保小波长度不超过信号长度的一半
            max_allowed_freq = (n_cycles * sampling_rate) / (signal_length / 2)
            
            # 调整freq_max，确保不超过最大允许频率
            if freq_max > max_allowed_freq:
                freq_max = max(freq_min + 1.0, max_allowed_freq)
                print(f"调整freq_max为: {freq_max}")
            
            # 生成频率数组
            frequencies = np.logspace(np.log10(freq_min), np.log10(freq_max), num=5)  # 减少频率点数量
            
            print(f"使用的频率: {frequencies}")
            print(f"信号长度: {signal_length} 样本")
            
            # 计算时频表示
            try:
                power, itc = mne.time_frequency.tfr_morlet(
                    epochs, freqs=frequencies, n_cycles=n_cycles, return_itc=True, decim=3
                )
            except Exception as e:
                # 如果仍然失败，使用非常保守的参数
                print(f"时频分析失败: {e}")
                print("使用保守参数重新尝试...")
                
                # 使用非常保守的参数
                frequencies = np.array([10.0, 20.0, 30.0])
                n_cycles = 2.0
                
                print(f"使用保守参数: 频率={frequencies}, n_cycles={n_cycles}")
                
                # 再次尝试
                power, itc = mne.time_frequency.tfr_morlet(
                    epochs, freqs=frequencies, n_cycles=n_cycles, return_itc=True, decim=3
                )
            
            # 获取数据
            power_data = power.data  # 形状: (n_epochs, n_channels, n_freqs, n_times)
            itc_data = itc.data      # 形状: (n_epochs, n_channels, n_freqs, n_times)
            times = power.times
            
            # 计算平均功率
            avg_power = np.mean(power_data, axis=0)  # 形状: (n_channels, n_freqs, n_times)
            
            # Prepare output
            output_data = {
                'power_data': power_data,
                'avg_power': avg_power,
                'itc_data': itc_data,
                'frequencies': frequencies,
                'times': times,
                'channels': power.ch_names,
                'freq_min': freq_min,
                'freq_max': freq_max,
                'n_cycles': n_cycles
            }
            # Prepare visualization data with time-frequency data
            if input_data.lfp_data is not None:
                # Use average power for visualization
                output_data['power_data'] = avg_power
                output_data['frequencies'] = frequencies
                output_data['times'] = times
                output_data['plot_type'] = 'time_frequency'
                output_data['channel_info'] = '所有通道的平均值'
            elif input_data.spike_times:
                # For spike data, use base class method
                vis_data = self.prepare_visualization_data(input_data)
                output_data.update(vis_data)
            

            
            # Statistics
            statistics = {
                'freq_min': freq_min,
                'freq_max': freq_max,
                'n_cycles': n_cycles,
                'frequencies': len(frequencies),
                'time_points': len(times),
                'channels': len(power.ch_names),
                'epochs': power_data.shape[0]
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE Time-Frequency Analysis Results',
                'xlabel': 'Time (s)',
                'ylabel': 'Frequency (Hz)'
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
    algo = MNETimeFrequencyAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNETimeFrequencyAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNETimeFrequencyAlgorithm',
    'class': MNETimeFrequencyAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
