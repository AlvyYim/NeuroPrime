# MNE Power Spectrum Analysis Algorithm Template

"""MNE功率谱分析算法模板，用于分析脑电信号的频率成分和能量分布。

该算法模板演示了如何使用MNE库进行功率谱分析，包括：
1. 快速傅里叶变换（FFT）
2. 不同窗口函数的应用
3. 功率谱密度计算
4. 平均方法选择

适用于研究脑电信号的频率特性，如不同频段的能量分布。
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
   - REQUIRED: class MNEPowerSpectrumAlgorithm(BaseAlgorithm): Main algorithm class
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
class MNEPowerSpectrumAlgorithm(BaseAlgorithm):
    """MNE功率谱分析算法"""
    
    def __init__(self):
        super().__init__()
        self.name = 'MNEPowerSpectrumAlgorithm'
        self.description = "MNE功率谱密度分析算法"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "fmin", ParameterType.FLOAT,
                "最低频率 (Hz)", 0.1,
                min_value=0.01, max_value=1.0
            ),
            create_parameter(
                "fmax", ParameterType.FLOAT,
                "最高频率 (Hz)", 100.0,
                min_value=50.0, max_value=500.0
            ),
            create_parameter(
                "n_fft", ParameterType.INTEGER,
                "FFT点数", 2048,
                min_value=1024, max_value=8192
            ),
            create_parameter(
                "window", ParameterType.SELECT,
                "窗口类型", "hamming",
                options=["hamming", "hann", "blackman"]
            ),
            create_parameter(
                "averaging", ParameterType.SELECT,
                "平均方法", "mean",
                options=["mean", "median"]
            )
        ]
    
    def validate_input(self, input_data):
        """Validate input data"""
        return True
    
    def run(self, input_data, parameters):
        """Execute algorithm"""
        try:
            print("Starting MNE power spectrum analysis...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            fmin = parameters.get('fmin', 0.1)
            fmax = parameters.get('fmax', 100.0)
            n_fft = parameters.get('n_fft', 2048)
            window = parameters.get('window', 'hamming')
            averaging = parameters.get('averaging', 'mean')
            
            # Get input data
            lfp_data = input_data.lfp_data
            sampling_rate = input_data.sampling_rate
            
            # 转换数据格式
            raw = hdf5_to_mne(input_data)
            
            # 计算功率谱密度
            spectrum = raw.compute_psd(fmin=fmin, fmax=fmax, n_fft=n_fft, window=window)
            freqs = spectrum.freqs
            psd = spectrum.get_data()  # 形状: (n_channels, n_freqs)
            
            # 应用平均方法
            if averaging == 'mean':
                avg_psd = np.mean(psd, axis=0)
            else:  # median
                avg_psd = np.median(psd, axis=0)
            
            # Prepare output
            output_data = {
                'psd': psd,
                'avg_psd': avg_psd,
                'frequencies': freqs,
                'channels': raw.ch_names,
                'fmin': fmin,
                'fmax': fmax,
                'n_fft': n_fft,
                'window': window,
                'averaging': averaging
            }
            # Prepare visualization data for power spectrum
            if input_data.lfp_data is not None:
                # Use power spectrum data for visualization
                output_data['power'] = psd
                output_data['freqs'] = freqs
                output_data['plot_type'] = 'power_spectrum'
            elif input_data.spike_times:
                # For spike data, use base class method
                vis_data = self.prepare_visualization_data(input_data)
                output_data.update(vis_data)
            

            
            # Statistics
            statistics = {
                'fmin': fmin,
                'fmax': fmax,
                'n_fft': n_fft,
                'window': window,
                'averaging': averaging,
                'frequencies': len(freqs),
                'channels': len(raw.ch_names)
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE Power Spectrum Analysis Results',
                'xlabel': 'Frequency (Hz)',
                'ylabel': 'Power Spectral Density (V²/Hz)'
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
    algo = MNEPowerSpectrumAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNEPowerSpectrumAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNEPowerSpectrumAlgorithm',
    'class': MNEPowerSpectrumAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
