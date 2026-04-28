# MNE Effective Connectivity Algorithm Template

"""MNE有效连接性分析算法模板，用于分析不同脑区之间的方向性连接。

该算法模板演示了如何使用MNE库进行有效连接性分析，包括：
1. 格兰杰因果关系分析
2. 直接传递函数（DTF）
3. 部分有向相干性（PDC）

适用于研究脑网络的方向性信息流动，如信息处理的因果关系。

【输入数据】
- input_data.lfp_data: LFP数据，形状为 [channels × samples]
- input_data.sampling_rate: 采样率 (Hz)
- input_data.trial_info: 试验信息列表，包含事件时间

【输出数据】
- output_data['connectivity_matrix']: 有效连接性矩阵，形状为 [channels × channels]
- output_data['channels']: 通道名称列表
- output_data['method']: 连接性计算方法
- output_data['fmin'], output_data['fmax']: 频率范围
- output_data['n_lags']: 滞后阶数
- output_data['tmin'], output_data['tmax']: 时间范围
- output_data['signal_data']: 用于可视化的信号数据（跨epochs平均后的2D数组）
- output_data['sampling_rate']: 采样率
- output_data['times']: 时间轴
- output_data['plot_type']: 绘图类型 ('raw_signal')

【可视化说明】
- 当前可视化显示的是原始信号波形（raw_signal），而非有效连接性热力图
- 这是因为当前可视化系统不支持连接矩阵的热力图可视化
- 有效连接性结果已保存在 output_data['connectivity_matrix'] 中
- 如需查看连接性热力图，建议将数据导出到Python/MATLAB等工具进行可视化

【注意】
- 本算法使用numpy和scipy实现简化的有效连接性计算
- 原statsmodels库的格兰杰因果检验和AR模型需要单独安装
- 如需使用完整的statsmodels功能，请安装statsmodels包
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
   - REQUIRED: class MNEEffectiveConnectivityAlgorithm(BaseAlgorithm): Main algorithm class
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
class MNEEffectiveConnectivityAlgorithm(BaseAlgorithm):
    """MNE有效连接性分析算法"""
    
    def __init__(self):
        super().__init__()
        self.name = 'MNEEffectiveConnectivityAlgorithm'
        self.description = "MNE有效连接性分析算法，用于分析不同脑区之间的方向性连接"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "method", ParameterType.SELECT,
                "连接性方法", "granger",
                options=["granger", "dtf", "pdcm"]
            ),
            create_parameter(
                "fmin", ParameterType.FLOAT,
                "最低频率 (Hz)", 8.0,
                min_value=0.1, max_value=30.0
            ),
            create_parameter(
                "fmax", ParameterType.FLOAT,
                "最高频率 (Hz)", 12.0,
                min_value=5.0, max_value=50.0
            ),
            create_parameter(
                "n_lags", ParameterType.INTEGER,
                "滞后阶数", 5,
                min_value=1, max_value=20
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
            print("Starting MNE effective connectivity analysis...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            method = parameters.get('method', 'granger')
            fmin = parameters.get('fmin', 8.0)
            fmax = parameters.get('fmax', 12.0)
            n_lags = parameters.get('n_lags', 5)
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
            
            # 过滤到指定频率范围
            epochs.filter(fmin, fmax, fir_design='firwin')
            
            # 计算有效连接性
            data = epochs.get_data()  # 形状: (n_epochs, n_channels, n_times)
            n_epochs, n_channels, n_times = data.shape
            
            # 对每个epoch计算有效连接性
            connectivity = np.zeros((n_channels, n_channels))
            
            for epoch in data:
                if method == 'granger':
                    # 计算格兰杰因果关系（简化版）
                    # 使用互相关和偏相关系数作为替代
                    for i in range(n_channels):
                        for j in range(n_channels):
                            if i != j:
                                # 计算互相关
                                x = epoch[i, :]
                                y = epoch[j, :]
                                # 标准化
                                x_norm = (x - np.mean(x)) / (np.std(x) + 1e-10)
                                y_norm = (y - np.mean(y)) / (np.std(y) + 1e-10)
                                # 计算滞后互相关
                                max_corr = 0
                                for lag in range(1, n_lags + 1):
                                    if lag < len(x):
                                        corr = np.corrcoef(x_norm[:-lag], y_norm[lag:])[0, 1]
                                        max_corr = max(max_corr, abs(corr))
                                connectivity[i, j] += max_corr
                elif method == 'dtf':
                    # 计算直接传递函数（简化版）
                    # 使用自回归系数的估计
                    from scipy.linalg import lstsq
                    for i in range(n_channels):
                        for j in range(n_channels):
                            if i != j:
                                x = epoch[i, :]
                                y = epoch[j, :]
                                # 构建滞后矩阵
                                n_samples = len(x)
                                if n_samples > n_lags:
                                    X_lag = np.zeros((n_samples - n_lags, n_lags))
                                    for lag in range(n_lags):
                                        X_lag[:, lag] = y[lag:n_samples - n_lags + lag]
                                    # 最小二乘估计
                                    coeffs, _, _, _ = lstsq(X_lag, x[n_lags:])
                                    connectivity[i, j] += np.sum(np.abs(coeffs))
                else:  # pdcm
                    # 计算部分有向相干性（简化版）
                    # 使用频率域的相位差
                    from scipy.signal import welch, csd
                    for i in range(n_channels):
                        for j in range(n_channels):
                            if i != j:
                                f, Pxx = welch(epoch[i, :], sampling_rate)
                                f, Pyy = welch(epoch[j, :], sampling_rate)
                                f, Pxy = csd(epoch[i, :], epoch[j, :], sampling_rate)
                                # 计算相干性
                                coherence = np.abs(Pxy) ** 2 / (Pxx * Pyy + 1e-10)
                                connectivity[i, j] += np.mean(coherence)
            
            # 平均所有epoch的结果
            connectivity /= n_epochs
            
            # 归一化到0-1范围
            if connectivity.max() > 0:
                connectivity = connectivity / connectivity.max()
            
            # Prepare output
            output_data = {
                'connectivity_matrix': connectivity,
                'channels': epochs.ch_names,
                'method': method,
                'fmin': fmin,
                'fmax': fmax,
                'n_lags': n_lags,
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
                'fmin': fmin,
                'fmax': fmax,
                'n_lags': n_lags,
                'tmin': tmin,
                'tmax': tmax,
                'channels': len(epochs.ch_names),
                'epochs': len(epochs),
                'mean_connectivity': np.mean(connectivity)
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE Effective Connectivity Results',
                'xlabel': 'Source Channel',
                'ylabel': 'Target Channel'
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
    algo = MNEEffectiveConnectivityAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNEEffectiveConnectivityAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNEEffectiveConnectivityAlgorithm',
    'class': MNEEffectiveConnectivityAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
