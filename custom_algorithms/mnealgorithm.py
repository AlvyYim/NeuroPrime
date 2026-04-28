# MNE Algorithm Script Template

# MNE基础算法模板，包含CSP分析和时频分析功能。
# 该算法模板演示了如何使用MNE库进行脑电信号处理，包括：
# 1. 数据预处理（滤波）
# 2. 共空间模式（CSP）分析
# 3. 时频分析（使用Morlet小波）
# 适用于运动想象、认知负荷等研究领域的信号处理。

import mne
import numpy as np
import matplotlib.pyplot as plt

# Import algorithm base classes
from src.algorithms.base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput
from src.algorithms.base import ParameterType, create_parameter

# Algorithm implementation class
class MNEAlgorithm(BaseAlgorithm):
    def __init__(self):
        super().__init__()
        self.name = 'MNEAlgorithm'
        self.description = "MNE algorithm template"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        return [
            create_parameter(
                "n_components", ParameterType.INTEGER,
                "Number of CSP components", 6,
                min_value=1, max_value=10
            ),
            create_parameter(
                "freq_min", ParameterType.FLOAT,
                "Minimum frequency (Hz)", 8.0,
                min_value=1.0, max_value=50.0
            ),
            create_parameter(
                "freq_max", ParameterType.FLOAT,
                "Maximum frequency (Hz)", 30.0,
                min_value=1.0, max_value=100.0
            ),
            create_parameter(
                "n_cycles", ParameterType.INTEGER,
                "Number of cycles for Morlet wavelet", 3,
                min_value=1, max_value=10
            )
        ]
    
    def validate_input(self, input_data):
        return True
    
    def run(self, input_data, parameters):
        try:
            print("Starting MNE algorithm execution...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            n_components = parameters.get('n_components', 6)
            freq_min = parameters.get('freq_min', 8.0)
            freq_max = parameters.get('freq_max', 30.0)
            n_cycles = parameters.get('n_cycles', 3)
            
            # Load data or create test data
            if input_data.lfp_data is not None:
                # Use input data
                lfp_data = input_data.lfp_data
                sampling_rate = input_data.sampling_rate
                ch_names = [f'ch{i}' for i in range(lfp_data.shape[0])]
                info = mne.create_info(ch_names=ch_names, sfreq=sampling_rate, ch_types=['eeg']*lfp_data.shape[0])
                raw = mne.io.RawArray(lfp_data, info)
            else:
                # Create test data
                print("Creating test data...")
                sfreq = 2000.0  # Sampling rate
                ch_names = [f'ch{i}' for i in range(10)]
                info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=['eeg']*10)
                data = np.random.randn(10, 10000) * 1e-6  # 10 channels, 10000 samples
                raw = mne.io.RawArray(data, info)
            
            # Preprocess data
            print("Preprocessing data...")
            raw.filter(freq_min, freq_max)
            
            # Example: CSP analysis
            print("Executing CSP analysis...")
            from mne.decoding import CSP
            
            # Create epochs
            events = mne.make_fixed_length_events(raw, duration=1.0)
            epochs = mne.Epochs(raw, events, tmin=-0.5, tmax=0.5, baseline=None, preload=True)
            
            # Create CSP
            csp = CSP(n_components=n_components, reg=None, log=True, norm_trace=False)
            X = epochs.get_data()
            y = epochs.events[:, -1] % 2  # Simple binary labels
            
            # Check if we have at least two classes
            if len(np.unique(y)) < 2:
                print("Warning: Only one class found, skipping CSP analysis")
                # Create dummy CSP results
                csp_patterns = np.random.randn(n_components, X.shape[1])
                csp_filters = np.random.randn(n_components, X.shape[1])
            else:
                # Fit CSP
                csp.fit(X, y)
                csp_patterns = csp.patterns_
                csp_filters = csp.filters_
            
            # Print results
            print("CSP analysis completed")
            print(f"CSP patterns shape: {csp_patterns.shape}")
            
            # Example: Time-frequency analysis
            print("Executing time-frequency analysis...")
            from mne.time_frequency import tfr_morlet
            
            # Calculate time-frequency map
            frequencies = np.arange(freq_min, freq_max, 2)  # Step 2Hz
            power = tfr_morlet(epochs, freqs=frequencies, n_cycles=n_cycles, return_itc=False)
            
            print("Time-frequency analysis completed")
            print(f"Time-frequency map shape: {power.data.shape}")
            
            # Prepare output
            output_data = {
                'csp_patterns': csp_patterns,
                'csp_filters': csp_filters,
                'power_data': power.data
            }
            # Prepare visualization data for Time-Frequency Plot
            output_data['frequencies'] = frequencies
            output_data['times'] = epochs.times
            output_data['plot_type'] = 'time_frequency'
            
            # Statistics
            statistics = {
                'n_components': n_components,
                'freq_min': freq_min,
                'freq_max': freq_max,
                'n_cycles': n_cycles,
                'csp_patterns_shape': csp_patterns.shape,
                'power_data_shape': power.data.shape
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE Algorithm Results',
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
    algo = MNEAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNEAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNEAlgorithm',
    'class': MNEAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
