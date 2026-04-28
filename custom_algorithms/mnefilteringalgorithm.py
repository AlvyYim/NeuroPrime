# MNE Filtering Algorithm Template

"""MNE滤波算法模板，用于对脑电信号进行频率滤波。

该算法模板演示了如何使用MNE库进行信号滤波，包括：
1. 低通滤波
2. 高通滤波
3. 带通滤波
4. 陷波滤波

适用于去除噪声、伪迹，以及提取特定频率范围内的脑电信号。
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
   - REQUIRED: class MNEFilteringAlgorithm(BaseAlgorithm): Main algorithm class
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
class MNEFilteringAlgorithm(BaseAlgorithm):
    """MNE滤波算法"""
    
    def __init__(self):
        super().__init__()
        self.name = 'MNEFilteringAlgorithm'
        self.description = "MNE滤波算法，支持带通、高通、低通滤波"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "filter_type", ParameterType.SELECT,
                "滤波类型", "bandpass",
                options=["bandpass", "highpass", "lowpass"]
            ),
            create_parameter(
                "l_freq", ParameterType.FLOAT,
                "低频截止 (Hz)", 0.1,
                min_value=0.0, max_value=100.0
            ),
            create_parameter(
                "h_freq", ParameterType.FLOAT,
                "高频截止 (Hz)", 40.0,
                min_value=0.1, max_value=1000.0
            ),
            create_parameter(
                "filter_method", ParameterType.SELECT,
                "滤波方法", "fir",
                options=["fir", "iir"]
            ),
            create_parameter(
                "fir_window", ParameterType.SELECT,
                "FIR窗口类型", "hamming",
                options=["hamming", "hann", "blackman"]
            )
        ]
    
    def validate_input(self, input_data):
        """Validate input data"""
        return True
    
    def run(self, input_data, parameters):
        """Execute algorithm"""
        try:
            print("Starting MNE filtering analysis...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            filter_type = parameters.get('filter_type', 'bandpass')
            l_freq = parameters.get('l_freq', 0.1)
            h_freq = parameters.get('h_freq', 40.0)
            filter_method = parameters.get('filter_method', 'fir')
            fir_window = parameters.get('fir_window', 'hamming')
            
            # Get input data
            lfp_data = input_data.lfp_data
            sampling_rate = input_data.sampling_rate
            
            # 转换数据格式
            raw = hdf5_to_mne(input_data)
            
            # 应用滤波
            if filter_type == 'bandpass':
                filtered_raw = raw.filter(l_freq=l_freq, h_freq=h_freq, method=filter_method, fir_window=fir_window)
            elif filter_type == 'highpass':
                filtered_raw = raw.filter(l_freq=l_freq, h_freq=None, method=filter_method, fir_window=fir_window)
            else:  # lowpass
                filtered_raw = raw.filter(l_freq=None, h_freq=h_freq, method=filter_method, fir_window=fir_window)
            
            # 获取滤波后的数据
            filtered_data = filtered_raw.get_data()
            
            # 计算原始数据和滤波后数据的功率谱
            from scipy.signal import welch
            f, Pxx_original = welch(lfp_data[0, :], sampling_rate, nperseg=1024)
            f, Pxx_filtered = welch(filtered_data[0, :], sampling_rate, nperseg=1024)
            
            # Prepare output
            output_data = {
                'filtered_data': filtered_data,
                'original_data': lfp_data,
                'frequencies': f,
                'psd_original': Pxx_original,
                'psd_filtered': Pxx_filtered,
                'filter_type': filter_type,
                'l_freq': l_freq,
                'h_freq': h_freq
            }
            # Prepare visualization data with filtered data
            if input_data.lfp_data is not None:
                # Use filtered data for visualization
                output_data['signal_data'] = filtered_data
                output_data['sampling_rate'] = input_data.sampling_rate
                # Generate time axis
                times = np.arange(filtered_data.shape[1]) / input_data.sampling_rate
                output_data['times'] = times
                output_data['plot_type'] = 'raw_signal'
            elif input_data.spike_times:
                # For spike data, use base class method
                vis_data = self.prepare_visualization_data(input_data)
                output_data.update(vis_data)
            

            
            # Statistics
            statistics = {
                'filter_type': filter_type,
                'l_freq': l_freq,
                'h_freq': h_freq,
                'filter_method': filter_method,
                'fir_window': fir_window,
                'channels': filtered_data.shape[0],
                'samples': filtered_data.shape[1]
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE Filtering Results',
                'xlabel': 'Frequency (Hz)',
                'ylabel': 'Power Spectral Density'
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
    algo = MNEFilteringAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNEFilteringAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNEFilteringAlgorithm',
    'class': MNEFilteringAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
