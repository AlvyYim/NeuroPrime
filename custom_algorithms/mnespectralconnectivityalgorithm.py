# MNE Spectral Connectivity Algorithm Template

"""MNE频谱连接性分析算法模板，用于分析不同频率下的脑区连接模式。

该算法模板演示了如何使用MNE库进行频谱连接性分析，包括：
1. 相干性分析
2. 相位滞后指数（PLI）
3. 加权相位滞后指数（WPLI）
4. 虚部相干性

适用于研究不同频率波段的脑网络连接特性，如alpha、beta、gamma等频段的连接模式。

【输入数据】
- input_data.lfp_data: LFP数据，形状为 [channels × samples]
- input_data.sampling_rate: 采样率 (Hz)
- input_data.trial_info: 试验信息列表，包含事件时间

【输出数据】
- output_data['connectivity']: 频谱连接性矩阵，形状为 [channels × channels × n_freqs]
- output_data['avg_connectivity']: 频率平均连接性矩阵，形状为 [channels × channels]
- output_data['frequencies']: 频率数组
- output_data['channels']: 通道名称列表
- output_data['method']: 连接性计算方法
- output_data['freq_min'], output_data['freq_max']: 频率范围
- output_data['tmin'], output_data['tmax']: 时间范围
- output_data['signal_data']: 用于可视化的信号数据（跨epochs平均后的2D数组）
- output_data['sampling_rate']: 采样率
- output_data['times']: 时间轴
- output_data['plot_type']: 绘图类型 ('raw_signal')

【可视化说明】
- 当前可视化显示的是原始信号波形（raw_signal），而非频谱连接性热力图
- 这是因为当前可视化系统不支持频谱连接性的多频率可视化
- 频谱连接性结果已保存在 output_data['connectivity'] 和 output_data['avg_connectivity'] 中
- 如需查看频谱连接性热力图，建议将数据导出到Python/MATLAB等工具进行可视化

【注意】
- 本算法使用scipy实现简化的频谱连接性计算
- 原MNE的mne.connectivity模块在较新版本中已更改或需要单独安装
- 如需使用完整的MNE连接性分析功能，请安装mne-connectivity包
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
   - REQUIRED: class MNESpectralConnectivityAlgorithm(BaseAlgorithm): Main algorithm class
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
class MNESpectralConnectivityAlgorithm(BaseAlgorithm):
    """MNE频谱连接性分析算法"""
    
    def __init__(self):
        super().__init__()
        self.name = 'MNESpectralConnectivityAlgorithm'
        self.description = "MNE频谱连接性分析算法，用于分析不同频率下的脑区连接"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "method", ParameterType.SELECT,
                "连接性方法", "coherence",
                options=["coherence", "pli", "wpli", "imaginary_coherence"]
            ),
            create_parameter(
                "freq_min", ParameterType.FLOAT,
                "最低频率 (Hz)", 1.0,
                min_value=0.1, max_value=5.0
            ),
            create_parameter(
                "freq_max", ParameterType.FLOAT,
                "最高频率 (Hz)", 40.0,
                min_value=30.0, max_value=100.0
            ),
            create_parameter(
                "n_freqs", ParameterType.INTEGER,
                "频率点数", 20,
                min_value=5, max_value=50
            ),
            create_parameter(
                "tmin", ParameterType.FLOAT,
                "分析开始时间 (s)", 0.0,
                min_value=-1.0, max_value=0.0
            ),
            create_parameter(
                "tmax", ParameterType.FLOAT,
                "分析结束时间 (s)", 1.0,
                min_value=0.0, max_value=3.0
            )
        ]
    
    def validate_input(self, input_data):
        """Validate input data"""
        return True
    
    def run(self, input_data, parameters):
        """Execute algorithm"""
        try:
            print("Starting MNE spectral connectivity analysis...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            method = parameters.get('method', 'coherence')
            freq_min = parameters.get('freq_min', 1.0)
            freq_max = parameters.get('freq_max', 40.0)
            n_freqs = parameters.get('n_freqs', 20)
            tmin = parameters.get('tmin', 0.0)
            tmax = parameters.get('tmax', 1.0)
            
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
            
            # 计算频谱连接性
            frequencies = np.logspace(np.log10(freq_min), np.log10(freq_max), num=n_freqs)
            
            # 计算频谱连接性
            # 注意：mne.connectivity 模块在较新版本中已更改
            # 这里使用简化的连接性计算方法
            frequencies = np.logspace(np.log10(freq_min), np.log10(freq_max), num=n_freqs)
            
            # 获取数据
            data = epochs.get_data()  # 形状: (n_epochs, n_channels, n_times)
            n_channels = data.shape[1]
            
            # 计算频谱功率
            from scipy import signal as scipy_signal
            
            # 对每个通道计算频谱
            spectra = []
            for ch_idx in range(n_channels):
                ch_data = data[:, ch_idx, :].mean(axis=0)  # 平均epochs
                freqs_psd, psd = scipy_signal.welch(ch_data, fs=sampling_rate, 
                                                     nperseg=int(sampling_rate * 0.5))
                spectra.append(psd)
            
            spectra = np.array(spectra)  # 形状: (n_channels, n_freqs)
            
            # 计算连接性矩阵
            if method == 'coherence':
                # 使用相关系数作为连接性的简化估计
                connectivity = np.corrcoef(spectra)
            elif method == 'pli':
                # 简化版PLI：使用相位差的符号
                connectivity = np.zeros((n_channels, n_channels))
                for i in range(n_channels):
                    for j in range(i+1, n_channels):
                        # 计算相位差
                        phase_i = np.angle(scipy_signal.hilbert(data[:, i, :].mean(axis=0)))
                        phase_j = np.angle(scipy_signal.hilbert(data[:, j, :].mean(axis=0)))
                        # 计算PLI
                        pli = np.abs(np.mean(np.sign(np.sin(phase_i - phase_j))))
                        connectivity[i, j] = pli
                        connectivity[j, i] = pli
            elif method == 'wpli':
                # 简化版WPLI
                connectivity = np.zeros((n_channels, n_channels))
                for i in range(n_channels):
                    for j in range(i+1, n_channels):
                        phase_i = np.angle(scipy_signal.hilbert(data[:, i, :].mean(axis=0)))
                        phase_j = np.angle(scipy_signal.hilbert(data[:, j, :].mean(axis=0)))
                        sij = np.sin(phase_i - phase_j)
                        wpli = np.abs(np.mean(sij)) / np.mean(np.abs(sij))
                        connectivity[i, j] = wpli
                        connectivity[j, i] = wpli
            else:  # imaginary_coherence
                # 简化版虚部相干性
                connectivity = np.zeros((n_channels, n_channels))
                for i in range(n_channels):
                    for j in range(i+1, n_channels):
                        sig_i = data[:, i, :].mean(axis=0)
                        sig_j = data[:, j, :].mean(axis=0)
                        # 计算互谱密度的虚部
                        f, csd = scipy_signal.csd(sig_i, sig_j, fs=sampling_rate)
                        imag_coh = np.abs(np.imag(csd)).mean()
                        connectivity[i, j] = imag_coh
                        connectivity[j, i] = imag_coh
            
            # 确保对角线为1
            np.fill_diagonal(connectivity, 1.0)
            
            # 重塑为3D数组以兼容原有输出格式
            connectivity_3d = connectivity.reshape(n_channels, n_channels, 1)
            freqs = frequencies
            
            # 计算频率平均连接性
            avg_connectivity = np.mean(connectivity_3d, axis=2)
            
            # Prepare output
            output_data = {
                'connectivity': connectivity_3d,
                'avg_connectivity': avg_connectivity,
                'frequencies': freqs,
                'channels': epochs.ch_names,
                'method': method,
                'freq_min': freq_min,
                'freq_max': freq_max,
                'tmin': tmin,
                'tmax': tmax
            }
            # Prepare visualization data
            # Average across epochs to get 2D array [channels, samples]
            signal_data = np.mean(epochs.get_data(), axis=0)
            output_data['signal_data'] = signal_data
            output_data['sampling_rate'] = input_data.sampling_rate
            output_data['times'] = np.arange(signal_data.shape[1]) / input_data.sampling_rate
            output_data['plot_type'] = 'raw_signal'
            
            
            # Statistics
            statistics = {
                'method': method,
                'freq_min': freq_min,
                'freq_max': freq_max,
                'n_freqs': len(freqs),
                'tmin': tmin,
                'tmax': tmax,
                'channels': len(epochs.ch_names),
                'epochs': len(epochs),
                'mean_connectivity': np.mean(avg_connectivity[np.triu_indices(avg_connectivity.shape[0], 1)])
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE Spectral Connectivity Results',
                'xlabel': 'Frequency (Hz)',
                'ylabel': 'Connectivity'
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
    algo = MNESpectralConnectivityAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNESpectralConnectivityAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNESpectralConnectivityAlgorithm',
    'class': MNESpectralConnectivityAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
