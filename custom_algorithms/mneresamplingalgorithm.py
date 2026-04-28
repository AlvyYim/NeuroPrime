# MNE Resampling Algorithm Template

"""MNE重采样算法模板，用于改变脑电信号的采样率。

该算法模板演示了如何使用MNE库进行信号重采样，包括：
1. 降低采样率（下采样）
2. 提高采样率（上采样）
3. 重采样前的抗混叠滤波

适用于数据压缩、降低计算复杂度，以及不同采样率数据的统一处理。
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
   - REQUIRED: class MNEResamplingAlgorithm(BaseAlgorithm): Main algorithm class
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
class MNEResamplingAlgorithm(BaseAlgorithm):
    """MNE重采样算法"""
    
    def __init__(self):
        super().__init__()
        self.name = 'MNEResamplingAlgorithm'
        self.description = "MNE重采样算法，用于改变数据采样率"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "new_sampling_rate", ParameterType.FLOAT,
                "新采样率 (Hz)", 1000.0,
                min_value=1.0, max_value=10000.0
            ),
            create_parameter(
                "n_jobs", ParameterType.INTEGER,
                "并行处理任务数", 1,
                min_value=1, max_value=8
            ),
            create_parameter(
                "filter_before", ParameterType.BOOLEAN,
                "重采样前滤波", True
            )
        ]
    
    def validate_input(self, input_data):
        """Validate input data"""
        return True
    
    def run(self, input_data, parameters):
        """Execute algorithm"""
        try:
            print("Starting MNE resampling analysis...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            new_sampling_rate = parameters.get('new_sampling_rate', 1000.0)
            n_jobs = parameters.get('n_jobs', 1)
            filter_before = parameters.get('filter_before', True)
            
            # Get input data
            lfp_data = input_data.lfp_data
            original_sampling_rate = input_data.sampling_rate
            
            # 转换数据格式
            raw = hdf5_to_mne(input_data)
            
            # 应用重采样
            resampled_raw = raw.resample(sfreq=new_sampling_rate, n_jobs=n_jobs)
            
            # 获取重采样后的数据
            resampled_data = resampled_raw.get_data()
            
            # 计算原始数据和重采样数据的功率谱
            from scipy.signal import welch
            f_original, Pxx_original = welch(lfp_data[0, :], original_sampling_rate, nperseg=1024)
            f_resampled, Pxx_resampled = welch(resampled_data[0, :], new_sampling_rate, nperseg=1024)
            
            # Prepare output
            output_data = {
                'resampled_data': resampled_data,
                'original_data': lfp_data,
                'original_sampling_rate': original_sampling_rate,
                'new_sampling_rate': new_sampling_rate,
                'frequencies_original': f_original,
                'psd_original': Pxx_original,
                'frequencies_resampled': f_resampled,
                'psd_resampled': Pxx_resampled
            }
            # Prepare visualization data with resampled data
            if input_data.lfp_data is not None:
                # Use resampled data for visualization
                output_data['signal_data'] = resampled_data
                output_data['sampling_rate'] = new_sampling_rate
                # Generate time axis
                times = np.arange(resampled_data.shape[1]) / new_sampling_rate
                output_data['times'] = times
                output_data['plot_type'] = 'raw_signal'
            elif input_data.spike_times:
                # For spike data, use base class method
                vis_data = self.prepare_visualization_data(input_data)
                output_data.update(vis_data)
            

            
            # Statistics
            statistics = {
                'original_sampling_rate': original_sampling_rate,
                'new_sampling_rate': new_sampling_rate,
                'original_samples': lfp_data.shape[1],
                'resampled_samples': resampled_data.shape[1],
                'channels': resampled_data.shape[0],
                'filter_before': filter_before,
                'n_jobs': n_jobs
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE Resampling Results',
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
    algo = MNEResamplingAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNEResamplingAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNEResamplingAlgorithm',
    'class': MNEResamplingAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
