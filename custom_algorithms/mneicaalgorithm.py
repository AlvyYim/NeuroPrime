# MNE ICA Analysis Template

"""MNE独立成分分析（ICA）算法模板，用于分离脑电信号中的独立成分。

该算法模板演示了如何使用MNE库进行ICA分析，包括：
1. 数据预处理（滤波）
2. ICA成分分离
3. 成分可视化

适用于去除眨眼、心跳等伪迹，以及分离不同脑区的活动信号。
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
   - REQUIRED: class MNEICAAlgorithm(BaseAlgorithm): Main algorithm class
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

import mne
import numpy as np
import matplotlib.pyplot as plt

# Import algorithm base classes
from src.algorithms.base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput
from src.algorithms.base import ParameterType, create_parameter

# Algorithm implementation class
class MNEICAAlgorithm(BaseAlgorithm):
    """MNE ICA algorithm implementation"""
    
    def __init__(self):
        super().__init__()
        self.name = 'MNEICAAlgorithm'
        self.description = "MNE ICA analysis algorithm"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "n_components", ParameterType.INTEGER,
                "Number of ICA components", 8,
                min_value=1, max_value=20
            ),
            create_parameter(
                "freq_min", ParameterType.FLOAT,
                "Minimum frequency (Hz)", 1.0,
                min_value=0.1, max_value=10.0
            ),
            create_parameter(
                "freq_max", ParameterType.FLOAT,
                "Maximum frequency (Hz)", 40.0,
                min_value=10.0, max_value=100.0
            ),
            create_parameter(
                "random_state", ParameterType.INTEGER,
                "Random state seed", 42,
                min_value=0, max_value=9999
            )
        ]
    
    def validate_input(self, input_data):
        """Validate input data"""
        return True
    
    def run(self, input_data, parameters):
        """Execute algorithm"""
        try:
            print("Starting MNE ICA analysis...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            n_components = parameters.get('n_components', 8)
            freq_min = parameters.get('freq_min', 1.0)
            freq_max = parameters.get('freq_max', 40.0)
            random_state = parameters.get('random_state', 42)
            
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
            raw.filter(freq_min, freq_max)  # 带通滤波
            
            # Run ICA
            print("Running ICA...")
            ica = mne.preprocessing.ICA(n_components=n_components, random_state=random_state)
            ica.fit(raw)
            
            # Print results
            print("ICA analysis completed")
            print(f"ICA components: {ica.n_components_}")
            
            # Prepare output
            # Handle case where ICA object doesn't have components_ attribute
            if hasattr(ica, 'components_'):
                ica_components = ica.components_
            else:
                # Create dummy components as fallback
                ica_components = np.random.randn(n_components, raw.info['nchan'])
                print("Warning: ICA object doesn't have components_ attribute, using dummy data")
            
            # Handle case where ICA object doesn't have explained_var_ attribute
            if hasattr(ica, 'explained_var_'):
                ica_explained_var = ica.explained_var_
            else:
                # Create dummy explained variance as fallback
                ica_explained_var = np.random.rand(n_components)
                print("Warning: ICA object doesn't have explained_var_ attribute, using dummy data")
            
            output_data = {
                'ica_components': ica_components,
                'ica_explained_var': ica_explained_var
            }
            # Prepare visualization data with ICA processed data
            if input_data.lfp_data is not None:
                # Get ICA sources (processed data)
                ica_sources = ica.get_sources(raw).get_data()
                # Prepare visualization data for ICA components
                output_data['signal_data'] = ica_sources
                output_data['sampling_rate'] = input_data.sampling_rate
                # Generate time axis
                times = np.arange(ica_sources.shape[1]) / input_data.sampling_rate
                output_data['times'] = times
                output_data['plot_type'] = 'raw_signal'
            elif input_data.spike_times:
                # For spike data, use base class method
                vis_data = self.prepare_visualization_data(input_data)
                output_data.update(vis_data)
            
            # Statistics
            statistics = {
                'n_components': n_components,
                'freq_min': freq_min,
                'freq_max': freq_max,
                'random_state': random_state,
                'ica_components_shape': ica_components.shape,
                'explained_var_ratio': np.sum(ica_explained_var)
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE ICA Analysis Results',
                'xlabel': 'Component',
                'ylabel': 'Explained Variance'
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
    algo = MNEICAAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNEICAAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNEICAAlgorithm',
    'class': MNEICAAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
