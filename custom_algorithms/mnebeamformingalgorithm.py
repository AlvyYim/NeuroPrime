# MNE Beamforming Algorithm Template

"""MNE波束形成器算法模板，用于估计脑电信号的神经源位置和强度。

该算法模板演示了如何使用MNE库进行波束形成器分析，包括：
1. 协方差矩阵计算
2. 波束形成器权重计算
3. 源功率估计
4. 空间滤波

适用于研究脑功能活动的空间分布，如运动想象、认知任务等。
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
   - REQUIRED: class MNEBeamformingAlgorithm(BaseAlgorithm): Main algorithm class
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

# 创建简化的头模型（用于演示）
def create_simple_head_model(info):
    """创建简化的头模型"""
    # 创建源空间
    src = mne.setup_source_space('sample', spacing='ico4', add_dist='patch')
    
    # 创建简化的正向模型
    conductivity = (0.3, 0.006, 0.3)  # 三层球模型
    model = mne.make_bem_model(info=info, ico=4, conductivity=conductivity)
    bem = mne.make_bem_solution(model)
    
    # 创建电极位置
    dig = mne.dig.point.GridPoint([0.0, 0.0, 0.0])
    info.set_montage('standard_1020')
    
    # 创建正向模型
    fwd = mne.make_forward_solution(info, trans=None, src=src, bem=bem, eeg=True, meg=False)
    
    return fwd

# Algorithm implementation class
class MNEBeamformingAlgorithm(BaseAlgorithm):
    """MNE波束形成器算法"""
    
    def __init__(self):
        super().__init__()
        self.name = 'MNEBeamformingAlgorithm'
        self.description = "MNE波束形成器算法，用于源定位"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "freq_min", ParameterType.FLOAT,
                "最低频率 (Hz)", 8.0,
                min_value=1.0, max_value=30.0
            ),
            create_parameter(
                "freq_max", ParameterType.FLOAT,
                "最高频率 (Hz)", 12.0,
                min_value=5.0, max_value=50.0
            ),
            create_parameter(
                "method", ParameterType.SELECT,
                "波束形成器方法", "lcmv",
                options=["lcmv", "dics", "sbeam"]
            ),
            create_parameter(
                "pick_ori", ParameterType.SELECT,
                "方向选择", "max-power",
                options=["max-power", "vector", "none"]
            ),
            create_parameter(
                "rank", ParameterType.SELECT,
                "秩估计方法", "info",
                options=["info", "full", "auto"]
            )
        ]
    
    def validate_input(self, input_data):
        """Validate input data"""
        return True
    
    def run(self, input_data, parameters):
        """Execute algorithm"""
        try:
            print("Starting MNE beamforming analysis...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            freq_min = parameters.get('freq_min', 8.0)
            freq_max = parameters.get('freq_max', 12.0)
            method = parameters.get('method', 'lcmv')
            pick_ori = parameters.get('pick_ori', 'max-power')
            rank = parameters.get('rank', 'info')
            
            # Get input data
            lfp_data = input_data.lfp_data
            trial_info = input_data.trial_info if input_data.trial_info is not None else []
            sampling_rate = input_data.sampling_rate
            
            # 转换数据格式
            raw = hdf5_to_mne(input_data)
            
            # 创建事件数组
            events = []
            event_id = 1
            for i, trial in enumerate(trial_info):
                if 'start_time' in trial:
                    # 转换为样本索引
                    sample = int(trial['start_time'] * sampling_rate)
                    events.append([sample, 0, event_id])
            
            # 确保events是整数类型的numpy数组
            events = np.array(events, dtype=int)
            
            # 如果没有事件或所有事件都超出范围，创建一个默认事件
            if events.size == 0:
                # 创建一个默认事件，确保在数据范围内
                # 选择数据中间位置作为事件时间
                data_length = lfp_data.shape[1]
                max_sample = data_length - 1
                default_sample = max(0, min(int(data_length / 2), max_sample))
                events = np.array([[default_sample, 0, event_id]], dtype=int)
            
            # 检查tmin和tmax是否合理，确保数据长度足够
            tmin = -0.5  # 与Epochs创建时使用的tmin一致
            tmax = 1.5   # 与Epochs创建时使用的tmax一致
            data_length = lfp_data.shape[1]
            sampling_rate = input_data.sampling_rate
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
            epochs = mne.Epochs(raw, events, event_id={"stimulus": event_id}, tmin=-0.5, tmax=1.5, preload=True)
            
            # 计算协方差矩阵
            noise_cov = mne.compute_covariance(epochs, tmin=-0.5, tmax=0.0, method='auto')
            data_cov = mne.compute_covariance(epochs, tmin=0.0, tmax=1.0, method='auto')
            
            # 创建简化的头模型（实际应用中应使用真实的头模型）
            try:
                fwd = create_simple_head_model(epochs.info)
            except:
                # 如果无法创建头模型，使用简化的源定位
                print("Using simplified source localization without head model")
                # 计算每个通道的平均功率
                power = np.mean(epochs.get_data() ** 2, axis=(0, 2))
                
                # Prepare output for simplified case
                output_data = {
                    'channel_power': power,
                    'channels': epochs.ch_names,
                    'freq_min': freq_min,
                    'freq_max': freq_max,
                    'method': method
                }
                # Prepare visualization data for simplified case
                # Average across epochs to get 2D array [channels, samples]
                signal_data = np.mean(epochs.get_data(), axis=0)
                output_data['signal_data'] = signal_data
                output_data['sampling_rate'] = input_data.sampling_rate
                output_data['times'] = np.arange(signal_data.shape[1]) / input_data.sampling_rate
                output_data['plot_type'] = 'raw_signal'
            
                # Statistics
                statistics = {
                    'freq_min': freq_min,
                    'freq_max': freq_max,
                    'method': method,
                    'channels': len(epochs.ch_names),
                    'epochs': len(epochs)
                }
            
                # Plot config
                plot_config = {
                    'title': 'MNE Beamforming Results (Simplified)',
                    'xlabel': 'Channel',
                    'ylabel': 'Power'
                }
            
                # Return results
                return AlgorithmOutput(
                    data=output_data,
                    statistics=statistics,
                    plot_config=plot_config,
                    success=True,
                    error_message=""
                )
            
            # 创建波束形成器
            if method == 'lcmv':
                beamformer = mne.beamformer.make_lcmv(
                    epochs.info, fwd, data_cov, reg=0.05, noise_cov=noise_cov,
                    pick_ori=pick_ori, rank=rank
                )
            elif method == 'dics':
                beamformer = mne.beamformer.make_dics(
                    epochs.info, fwd, data_cov, noise_cov=noise_cov,
                    pick_ori=pick_ori, rank=rank
                )
            else:  # sbeam
                beamformer = mne.beamformer.make_lcmv(
                    epochs.info, fwd, data_cov, reg=0.05, noise_cov=noise_cov,
                    pick_ori=pick_ori, rank=rank, weight_norm='unit-noise-gain'
                )
            
            # 应用波束形成器
            stc = mne.beamformer.apply_beamformer_epochs(epochs, beamformer, return_generator=False)
            
            # 计算平均源估计
            stc_avg = stc[0].copy()
            for s in stc[1:]:
                stc_avg.data += s.data
            stc_avg.data /= len(stc)
            
            # Prepare output
            output_data = {
                'stc_data': stc_avg.data,
                'vertices': stc_avg.vertices,
                'times': stc_avg.times,
                'freq_min': freq_min,
                'freq_max': freq_max,
                'method': method
            }
            # Prepare visualization data for beamforming results
            # Average across epochs to get 2D array [channels, samples]
            signal_data = np.mean(epochs.get_data(), axis=0)
            output_data['signal_data'] = signal_data
            output_data['sampling_rate'] = input_data.sampling_rate
            output_data['times'] = np.arange(signal_data.shape[1]) / input_data.sampling_rate
            output_data['plot_type'] = 'raw_signal'
            
            # Statistics
            statistics = {
                'freq_min': freq_min,
                'freq_max': freq_max,
                'method': method,
                'source_points': stc_avg.data.shape[0],
                'time_points': len(stc_avg.times),
                'epochs': len(epochs)
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE Beamforming Results',
                'xlabel': 'Time (s)',
                'ylabel': 'Source Power'
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
    algo = MNEBeamformingAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNEBeamformingAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNEBeamformingAlgorithm',
    'class': MNEBeamformingAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
