# Custom Algorithm Script Template

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
   - REQUIRED: class CustomAlgorithm(BaseAlgorithm): Main algorithm class
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

# Import algorithm base classes
from src.algorithms.base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput
from src.algorithms.base import ParameterType, create_parameter

# Algorithm implementation class
class CustomAlgorithm(BaseAlgorithm):
    """Custom algorithm implementation"""
    
    def __init__(self):
        super().__init__()
        self.name = 'ViewLFPData'
        self.description = "Custom algorithm template"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "threshold", ParameterType.FLOAT,
                "Detection threshold", 3.0,
                min_value=0.1, max_value=10.0
            )
        ]
    
    def validate_input(self, input_data):
        """Validate input data"""
        return True
    
    def run(self, input_data, parameters):
        """Execute algorithm"""
        try:
            print("Starting algorithm execution...")
            
            # Get input data
            spike_times = input_data.spike_times if input_data.spike_times is not None else []
            
            # Example: Count spikes
            spike_count = len(spike_times)
            print(f"Detected {spike_count} spikes")
            
            # Example: Use parameters
            threshold = parameters.get('threshold', 3.0)
            print(f"Using threshold: {threshold}")
            
            # Simulate algorithm output
            output_data = {
                'spike_count': spike_count,
                'threshold_used': threshold
            }
            # Auto visualization based on input data type
            if input_data.lfp_data is not None:
                # Prepare visualization data for Raw Signal Plot
                output_data['signal_data'] = input_data.lfp_data
                output_data['sampling_rate'] = input_data.sampling_rate
                # Generate time axis
                import numpy as np
                times = np.arange(input_data.lfp_data.shape[1]) / input_data.sampling_rate
                output_data['times'] = times
                output_data['plot_type'] = 'raw_signal'
            elif input_data.spike_times:
                # Prepare visualization data for Spike Raster Plot
                output_data['spike_times'] = input_data.spike_times
                output_data['trial_info'] = input_data.trial_info
                output_data['plot_type'] = 'spike_raster'
            

            
            # Return result
            return AlgorithmOutput(
                data=output_data,
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
    algo = CustomAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = CustomAlgorithm()
ALGORITHM_INFO = {
    'name': 'ViewLFPData',
    'class': CustomAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
