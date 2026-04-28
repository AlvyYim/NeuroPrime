# MNE Bad Channel Detection Algorithm Template

"""MNE坏通道检测算法模板，用于识别和标记脑电信号中的坏通道。

该算法模板演示了如何使用MNE库进行坏通道检测，包括：
1. 基于通道间相关性的检测
2. 基于标准差的检测
3. 基于方差的检测

适用于数据预处理阶段，确保后续分析使用高质量的通道数据。
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
   - REQUIRED: class MNEBadChannelDetectionAlgorithm(BaseAlgorithm): Main algorithm class
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
class MNEBadChannelDetectionAlgorithm(BaseAlgorithm):
    """MNE坏通道检测算法"""
    
    def __init__(self):
        super().__init__()
        self.name = 'MNEBadChannelDetectionAlgorithm'
        self.description = "MNE坏通道检测算法，用于识别和标记坏通道"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "method", ParameterType.SELECT,
                "检测方法", "correlation",
                options=["correlation", "std", "variance"]
            ),
            create_parameter(
                "threshold", ParameterType.FLOAT,
                "阈值", 3.0,
                min_value=1.0, max_value=10.0
            ),
            create_parameter(
                "verbose", ParameterType.BOOLEAN,
                "详细输出", False
            )
        ]
    
    def validate_input(self, input_data):
        """Validate input data"""
        return True
    
    def run(self, input_data, parameters):
        """Execute algorithm"""
        try:
            print("Starting MNE bad channel detection...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            method = parameters.get('method', 'correlation')
            threshold = parameters.get('threshold', 3.0)
            verbose = parameters.get('verbose', False)
            
            # Get input data
            lfp_data = input_data.lfp_data
            sampling_rate = input_data.sampling_rate
            
            # 转换数据格式
            raw = hdf5_to_mne(input_data)
            
            # 检测坏通道
            if method == 'correlation':
                # 基于通道间相关性检测
                corr = np.corrcoef(lfp_data)
                mean_corr = np.mean(corr, axis=1)
                bad_channels = np.where(mean_corr < np.mean(mean_corr) - threshold * np.std(mean_corr))[0]
            elif method == 'std':
                # 基于标准差检测
                std = np.std(lfp_data, axis=1)
                bad_channels = np.where(std > np.mean(std) + threshold * np.std(std))[0]
            else:  # variance
                # 基于方差检测
                var = np.var(lfp_data, axis=1)
                bad_channels = np.where(var > np.mean(var) + threshold * np.std(var))[0]
            
            # 标记坏通道
            bad_channel_names = [raw.ch_names[ch] for ch in bad_channels]
            raw.info['bads'] = bad_channel_names
            
            # 检查是否有坏通道
            if len(bad_channels) == 0:
                # 没有坏通道，返回提示信息
                output_data = {
                    'message': '未检测到坏通道',
                    'method': method,
                    'threshold': threshold,
                    'total_channels': lfp_data.shape[0],
                    'bad_channel_count': 0
                }
                
                # 不绘制图像
                statistics = {
                    'method': method,
                    'threshold': threshold,
                    'total_channels': lfp_data.shape[0],
                    'bad_channel_count': 0,
                    'message': '未检测到坏通道'
                }
                
                plot_config = {
                    'title': 'MNE Bad Channel Detection Results',
                    'show_plot': False  # 不显示图像
                }
                
                return AlgorithmOutput(
                    data=output_data,
                    statistics=statistics,
                    plot_config=plot_config,
                    success=True,
                    error_message=""
                )
            
            # 计算通道统计信息
            channel_stats = []
            for i, ch_name in enumerate(raw.ch_names):
                if method == 'correlation':
                    value = mean_corr[i]
                elif method == 'std':
                    value = np.std(lfp_data[i, :])
                else:
                    value = np.var(lfp_data[i, :])
                
                channel_stats.append({
                    'channel': ch_name,
                    'value': value,
                    'is_bad': ch_name in bad_channel_names
                })
            
            # Prepare output
            output_data = {
                'bad_channels': bad_channel_names,
                'bad_channel_indices': bad_channels.tolist(),
                'channel_stats': channel_stats,
                'method': method,
                'threshold': threshold,
                'total_channels': lfp_data.shape[0],
                'bad_channel_count': len(bad_channels)
            }
            # Prepare visualization data with bad channels marked
            if input_data.lfp_data is not None:
                # Create a copy of the data
                marked_data = lfp_data.copy()
                # Mark bad channels by setting their values to NaN
                for ch in bad_channels:
                    marked_data[ch, :] = np.nan
                # Use marked data for visualization
                output_data['signal_data'] = marked_data
                output_data['sampling_rate'] = input_data.sampling_rate
                # Generate time axis
                times = np.arange(marked_data.shape[1]) / input_data.sampling_rate
                output_data['times'] = times
                output_data['plot_type'] = 'raw_signal'
            elif input_data.spike_times:
                # For spike data, use base class method
                vis_data = self.prepare_visualization_data(input_data)
                output_data.update(vis_data)
            

            
            # Statistics
            # 生成坏通道提示信息
            if len(bad_channels) > 0:
                bad_channel_indices_str = ', '.join(map(str, bad_channels))
                message = f'检测到 {len(bad_channels)} 个坏通道: {bad_channel_indices_str}'
            else:
                message = '未检测到坏通道'
            
            statistics = {
                'method': method,
                'threshold': threshold,
                'total_channels': lfp_data.shape[0],
                'bad_channel_count': len(bad_channels),
                'bad_channels': bad_channel_names,
                'message': message
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE Bad Channel Detection Results',
                'xlabel': 'Channel',
                'ylabel': f'{method.capitalize()} Value'
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
    algo = MNEBadChannelDetectionAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNEBadChannelDetectionAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNEBadChannelDetectionAlgorithm',
    'class': MNEBadChannelDetectionAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
