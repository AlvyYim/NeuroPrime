# MNE Source Localization Template

"""MNE源定位算法模板，用于估计脑电信号的神经源位置。

该算法模板演示了如何使用MNE库进行源定位分析，包括：
1. 数据预处理
2. 前向模型创建
3. 源估计

适用于研究脑功能活动的空间分布，如认知任务中的脑区激活。
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
   - REQUIRED: class MNESourceLocalizationAlgorithm(BaseAlgorithm): Main algorithm class
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
class MNESourceLocalizationAlgorithm(BaseAlgorithm):
    """MNE Source Localization algorithm implementation"""
    
    def __init__(self):
        super().__init__()
        self.name = 'MNESourceLocalizationAlgorithm'
        self.description = "MNE source localization algorithm"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "n_channels", ParameterType.INTEGER,
                "Number of channels", 10,
                min_value=1, max_value=100
            ),
            create_parameter(
                "duration", ParameterType.FLOAT,
                "Epoch duration (s)", 1.0,
                min_value=0.1, max_value=5.0
            )
        ]
    
    def validate_input(self, input_data):
        """Validate input data"""
        return True
    
    def run(self, input_data, parameters):
        """Execute algorithm"""
        try:
            print("Starting MNE source localization...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            n_channels = parameters.get('n_channels', 10)
            duration = parameters.get('duration', 1.0)
            
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
                ch_names = [f'ch{i}' for i in range(n_channels)]
                info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=['eeg']*n_channels)
                data = np.random.randn(n_channels, 10000) * 1e-6  # n_channels channels, 10000 samples
                raw = mne.io.RawArray(data, info)
            
            # Create epochs
            events = mne.make_fixed_length_events(raw, duration=duration)
            epochs = mne.Epochs(raw, events, tmin=-0.5, tmax=0.5, baseline=None, preload=True)
            
            # Create a simple forward model (requires a head model)
            print("Creating forward model...")
            # Note: This is a simplified example, real source localization requires proper head models
            
            # For demonstration purposes, create a simple source space
            # In real applications, you would use a proper head model
            print("Creating source space...")
            # Create a simple 3D source space with 9 sources (to fit in one 3x3 grid)
            n_sources = 9
            source_activations = np.random.randn(n_sources, epochs.get_data().shape[2]) * 1e-9
            
            # Prepare output
            output_data = {
                'message': 'Source localization completed',
                'epochs_shape': epochs.get_data().shape,
                'source_activations': source_activations
            }
            
            # Prepare visualization data with source localization results
            if input_data.lfp_data is not None:
                # Use source activations for visualization
                output_data['signal_data'] = source_activations
                output_data['sampling_rate'] = input_data.sampling_rate
                # Generate time axis
                times = np.arange(source_activations.shape[1]) / input_data.sampling_rate
                output_data['times'] = times
                output_data['plot_type'] = 'raw_signal'
            elif input_data.spike_times:
                # For spike data, use base class method
                vis_data = self.prepare_visualization_data(input_data)
                output_data.update(vis_data)
            
            # Statistics
            statistics = {
                'n_channels': n_channels,
                'duration': duration,
                'epochs_shape': epochs.get_data().shape
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE Source Localization Results',
                'xlabel': 'Time (s)',
                'ylabel': 'Channels'
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
    algo = MNESourceLocalizationAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNESourceLocalizationAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNESourceLocalizationAlgorithm',
    'class': MNESourceLocalizationAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
