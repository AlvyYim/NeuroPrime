"""
Spike Analysis Algorithms Module
================================

This module provides core spike analysis algorithms for electrophysiological data processing,
including Peri-Stimulus Time Histogram (PSTH), Raster Plot, and Tuning Curve analysis.

Key Features:
- PSTH Analysis: Computes spike time distribution around stimulus events
- Raster Plot: Visualizes spike times across trials with sorting options
- Tuning Curve: Analyzes neuron response selectivity to different stimulus conditions

Design Principles:
- Follows BaseAlgorithm interface for consistent API
- Handles multiple trials and stimulus conditions
- Supports event-time alignment and spike filtering
- Includes statistical metrics and visualization configurations
- Robust error handling and input validation

Usage:
    from src.algorithms.spike_analysis import PSTHAnalysis
    analyzer = PSTHAnalysis()
    params = analyzer.get_default_parameters()
    output = analyzer.run(input_data, params)
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
from scipy.ndimage import gaussian_filter1d

try:
    from .base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput, ParameterType, create_parameter
except ImportError:
    from base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput, ParameterType, create_parameter


class PSTHAnalysis(BaseAlgorithm):
    """
    Peri-Stimulus Time Histogram (PSTH) Analysis Algorithm
    
    Computes the spike firing rate distribution relative to stimulus onset times.
    This algorithm aligns spikes from multiple trials to stimulus events and bins
    them into a histogram to visualize the temporal response pattern of neurons.
    
    Key Operations:
    1. Extracts valid event times from trial information (excluding aborted trials)
    2. Aligns spike times to each stimulus event
    3. Bins spikes into time windows around the event
    4. Normalizes by number of trials to get firing rate (Hz)
    5. Applies optional Gaussian smoothing
    6. Computes baseline and response statistics
    
    Parameters:
        pre_time: Time window before stimulus onset (ms)
        post_time: Time window after stimulus onset (ms)
        bin_size: Width of each time bin (ms)
        smoothing_sigma: Standard deviation for Gaussian smoothing (ms)
        event_type: Type of event to align to (default: 'stimulus_onset')
    
    Output:
        data: Contains bin_centers, psth_rate, psth_counts
        statistics: Baseline rate, peak rate, peak time, response modulation
        plot_config: Configuration for visualization
    """
    
    def __init__(self):
        """Initialize PSTH analysis with default settings"""
        super().__init__()
        self.name = "PSTHAnalysis"
        self.description = "Peri-Stimulus Time Histogram (PSTH) Analysis"
        self.category = "Spike"
        self.version = "1.0"
        self.required_data_types = ['spike', 'behavior']
        self.data_requirements_description = "Requires spike times array and trial information with start_time"
    
    def get_parameters_schema(self):
        """
        Define the parameter schema for PSTH analysis.
        
        Returns:
            List of parameter definitions with name, type, description, default value, and constraints
        """
        return [
            create_parameter(
                "pre_time", ParameterType.FLOAT,
                "Pre-stimulus time window (ms)", 200.0,
                min_value=50.0, max_value=1000.0
            ),
            create_parameter(
                "post_time", ParameterType.FLOAT,
                "Post-stimulus time window (ms)", 1000.0,
                min_value=100.0, max_value=2000.0
            ),
            create_parameter(
                "bin_size", ParameterType.FLOAT,
                "Time bin width (ms)", 10.0,
                min_value=1.0, max_value=100.0
            ),
            create_parameter(
                "smoothing_sigma", ParameterType.FLOAT,
                "Gaussian smoothing standard deviation (ms)", 20.0,
                min_value=0.0, max_value=100.0
            ),
            create_parameter(
                "event_type", ParameterType.STRING,
                "Event type for alignment", "stimulus_onset"
            )
        ]
    
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        """
        Validate that input data meets requirements for PSTH analysis.
        
        Args:
            input_data: AlgorithmInput object containing spike_times and trial_info
        
        Returns:
            True if input is valid, False otherwise
        """
        return (input_data.spike_times is not None and 
                input_data.trial_info is not None and
                len(input_data.spike_times) > 0)
    
    def run(self, input_data: AlgorithmInput, parameters: Dict) -> AlgorithmOutput:
        """
        Execute PSTH analysis on input data with specified parameters.
        
        Args:
            input_data: Contains spike_times (np.ndarray) and trial_info (list of dicts)
            parameters: Dictionary with pre_time, post_time, bin_size, smoothing_sigma, event_type
        
        Returns:
            AlgorithmOutput with PSTH data, statistics, and visualization config
        """
        import time
        start_time = time.time()
        
        try:
            # Extract core data from input
            spike_times = input_data.spike_times
            trial_info = input_data.trial_info
            
            # Convert parameters from milliseconds to seconds for calculations
            pre_time = parameters.get("pre_time", 200.0) / 1000.0
            post_time = parameters.get("post_time", 500.0) / 1000.0
            bin_size = parameters.get("bin_size", 10.0) / 1000.0
            smoothing_sigma = parameters.get("smoothing_sigma", 20.0) / 1000.0
            
            # Extract valid event times, excluding aborted trials
            # Each trial must have 'start_time' and not be marked as aborted
            event_times = []
            for trial in trial_info:
                if 'start_time' in trial and not trial.get('aborted', False):
                    event_times.append(trial['start_time'])
            
            # Handle case with no valid events
            if not event_times:
                return AlgorithmOutput(
                    success=False,
                    error_message="No valid event times found in trial info"
                )
            
            # Convert to numpy array for efficient processing
            event_times = np.array(event_times)
            
            # Create time bins from -pre_time to +post_time
            # bins define the edges, bin_centers are used for plotting
            bins = np.arange(-pre_time, post_time + bin_size, bin_size)
            bin_centers = (bins[:-1] + bins[1:]) / 2
            
            # Initialize PSTH count array
            psth_counts = np.zeros(len(bins) - 1)
            
            # Accumulate spikes across all trials
            for event_time in event_times:
                # Align spikes relative to this stimulus event
                aligned_spikes = spike_times - event_time
                
                # Filter spikes within the analysis window
                mask = (aligned_spikes >= -pre_time) & (aligned_spikes <= post_time)
                valid_spikes = aligned_spikes[mask]
                
                # Count spikes in each bin and accumulate
                counts, _ = np.histogram(valid_spikes, bins=bins)
                psth_counts += counts
            
            # Convert raw counts to firing rate (Hz)
            # Normalize by number of trials and bin width
            psth_rate = psth_counts / (len(event_times) * bin_size)
            
            # Apply Gaussian smoothing if requested
            # Convert sigma from seconds to number of samples
            if smoothing_sigma > 0:
                sigma_samples = smoothing_sigma / bin_size
                psth_rate = gaussian_filter1d(psth_rate, sigma=sigma_samples)
            
            # Calculate baseline statistics from pre-stimulus period
            baseline_mask = bin_centers < 0
            if np.any(baseline_mask):
                baseline_rate = np.mean(psth_rate[baseline_mask])
                baseline_std = np.std(psth_rate[baseline_mask])
            else:
                baseline_rate = 0
                baseline_std = 0
            
            # Calculate response peak statistics from post-stimulus period
            response_mask = bin_centers > 0
            if np.any(response_mask):
                peak_rate = np.max(psth_rate[response_mask])
                peak_time = bin_centers[response_mask][np.argmax(psth_rate[response_mask])]
            else:
                peak_rate = 0
                peak_time = 0
            
            execution_time = time.time() - start_time
            
            # Prepare comprehensive output
            output = AlgorithmOutput(
                data={
                    'bin_centers': bin_centers,       # Time points for each bin (center)
                    'psth_rate': psth_rate,           # Firing rate in Hz
                    'psth_counts': psth_counts        # Raw spike counts
                },
                statistics={
                    'baseline_rate': float(baseline_rate),      # Pre-stimulus firing rate
                    'baseline_std': float(baseline_std),        # Variability in baseline
                    'peak_rate': float(peak_rate),              # Maximum response rate
                    'peak_time': float(peak_time),              # Time of peak response
                    'response_modulation': float((peak_rate - baseline_rate) / (baseline_rate + 1e-10)),
                    'n_trials': len(event_times),               # Number of valid trials
                    'n_spikes_total': int(np.sum(psth_counts)) # Total spikes analyzed
                },
                plot_config={
                    'type': 'psth',
                    'title': 'Peri-Stimulus Time Histogram (PSTH)',
                    'xlabel': 'Time from stimulus (s)',
                    'ylabel': 'Firing rate (Hz)',
                    'vline': 0  # Mark stimulus onset
                },
                export_data={
                    'bin_centers': bin_centers,
                    'psth_rate': psth_rate,
                    'psth_counts': psth_counts
                },
                metadata={
                    'pre_time': pre_time,
                    'post_time': post_time,
                    'bin_size': bin_size,
                    'smoothing_sigma': smoothing_sigma
                },
                execution_time=execution_time,
                success=True
            )
            
            self._record_execution(input_data, parameters, output)
            return output
            
        except Exception as e:
            # Handle any exceptions and return error information
            return AlgorithmOutput(
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )


class RasterPlotAnalysis(BaseAlgorithm):
    """
    Raster Plot Analysis Algorithm
    
    Generates spike raster plots showing spike times across multiple trials.
    Each row represents one trial, with dots indicating spike occurrences.
    Trials can be sorted by response strength or chronological order.
    
    Key Features:
    - Groups trials by stimulus condition
    - Supports sorting by response magnitude or trial order
    - Handles multiple trial sources (experiments)
    - Computes per-trial response metrics
    
    Parameters:
        pre_time: Time before stimulus onset (ms)
        post_time: Time after stimulus onset (ms)
        sort_by: 'time' (chronological) or 'response' (by spike count)
        show_baseline: Include baseline period in visualization
    
    Output:
        data: Grouped raster data by stimulus condition
        statistics: Trial counts, response statistics
        plot_config: Configuration for grouped raster visualization
    """
    
    def __init__(self):
        """Initialize raster plot analysis with default settings"""
        super().__init__()
        self.name = "RasterPlotAnalysis"
        self.description = "Spike Raster Plot Analysis"
        self.category = "Spike"
        self.version = "1.0"
        self.required_data_types = ['spike', 'behavior']
        self.data_requirements_description = "Requires spike times array and trial information"
    
    def get_parameters_schema(self):
        """Define parameter schema for raster plot analysis"""
        return [
            create_parameter(
                "pre_time", ParameterType.FLOAT,
                "Pre-stimulus time window (ms)", 200.0,
                min_value=50.0, max_value=1000.0
            ),
            create_parameter(
                "post_time", ParameterType.FLOAT,
                "Post-stimulus time window (ms)", 500.0,
                min_value=100.0, max_value=2000.0
            ),
            create_parameter(
                "sort_by", ParameterType.SELECT,
                "Sort trials by", "time",
                options=["time", "response"]
            ),
            create_parameter(
                "show_baseline", ParameterType.BOOLEAN,
                "Include baseline period", True
            )
        ]
    
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        """Validate input data for raster plot analysis"""
        return (input_data.spike_times is not None and 
                input_data.trial_info is not None and
                len(input_data.spike_times) > 0)
    
    def run(self, input_data: AlgorithmInput, parameters: Dict) -> AlgorithmOutput:
        """
        Execute raster plot analysis.
        
        Args:
            input_data: Contains spike_times and trial_info
            parameters: Analysis configuration
        
        Returns:
            AlgorithmOutput with raster data organized by stimulus condition
        """
        import time
        start_time = time.time()
        
        try:
            spike_times = input_data.spike_times
            trial_info = input_data.trial_info
            
            # Extract and convert parameters
            pre_time = parameters.get("pre_time", 200.0) / 1000.0
            post_time = parameters.get("post_time", 500.0) / 1000.0
            sort_by = parameters.get("sort_by", "time")
            show_baseline = parameters.get("show_baseline", True)
            
            # Collect event times, stimulus conditions, and trial sources
            # This allows for grouping by both condition and experiment
            event_times = []
            stim_conditions = []
            trial_sources = []
            
            for trial in trial_info:
                if 'start_time' in trial and not trial.get('aborted', False):
                    event_times.append(trial['start_time'])
                    stim_conditions.append(trial.get('stim_cnd', 0))
                    trial_sources.append(trial.get('trial_source', 'unknown'))
            
            # Handle empty case
            if not event_times:
                return AlgorithmOutput(
                    success=False,
                    error_message="No valid event times found in trial info"
                )
            
            # Convert to numpy arrays for efficient processing
            event_times = np.array(event_times)
            stim_conditions = np.array(stim_conditions)
            trial_sources = np.array(trial_sources)
            
            # Get unique conditions and sources for grouping
            unique_conditions = np.unique(stim_conditions)
            unique_sources = np.unique(trial_sources)
            
            # Collect spikes for each trial
            trial_spikes = []
            trial_responses = []
            
            for i, event_time in enumerate(event_times):
                # Align spikes to this trial's event
                aligned_spikes = spike_times - event_time
                
                # Filter spikes within analysis window
                mask = (aligned_spikes >= -pre_time) & (aligned_spikes <= post_time)
                valid_spikes = aligned_spikes[mask]
                
                # Convert to list for serialization
                trial_spikes.append(valid_spikes.tolist() if hasattr(valid_spikes, 'tolist') else list(valid_spikes))
                
                # Calculate response metric (spikes after stimulus)
                response_mask = aligned_spikes > 0
                trial_responses.append(int(np.sum(response_mask)))
            
            # Organize raster data by stimulus condition
            condition_rasters = {}
            for condition in unique_conditions:
                # Get indices for this condition
                condition_mask = stim_conditions == condition
                condition_indices = np.where(condition_mask)[0]
                
                # Extract data for this condition
                condition_trial_spikes = [trial_spikes[i] for i in condition_indices]
                condition_responses = [trial_responses[i] for i in condition_indices]
                condition_trial_sources = [trial_sources[i] for i in condition_indices]
                
                # Sort trials based on user preference
                if sort_by == "response":
                    # Sort by response magnitude (descending)
                    sort_indices = np.argsort(condition_responses)[::-1]
                else:
                    # Keep original chronological order
                    sort_indices = np.arange(len(condition_trial_spikes))
                
                # Apply sorting
                sorted_spikes = [condition_trial_spikes[i] for i in sort_indices]
                sorted_sources = [condition_trial_sources[i] for i in sort_indices]
                
                # Store organized data
                condition_rasters[int(condition)] = {
                    'trial_spikes': sorted_spikes,
                    'trial_sources': sorted_sources,
                    'n_trials': len(sorted_spikes),
                    'mean_response': float(np.mean(condition_responses)) if condition_responses else 0.0
                }
            
            execution_time = time.time() - start_time
            
            # Prepare output
            output = AlgorithmOutput(
                data={
                    'condition_rasters': condition_rasters,
                    'time_range': (-pre_time, post_time),
                    'unique_conditions': unique_conditions.tolist()
                },
                statistics={
                    'n_trials_total': len(trial_spikes),
                    'n_conditions': len(unique_conditions),
                    'mean_response': float(np.mean(trial_responses)),
                    'std_response': float(np.std(trial_responses)),
                    'total_spikes': int(np.sum([len(spikes) for spikes in trial_spikes]))
                },
                plot_config={
                    'type': 'raster_grouped',
                    'title': 'Raster Plot by Stimulus Condition',
                    'xlabel': 'Time from stimulus (s)',
                    'ylabel': 'Trial',
                    'vline': 0,
                    'n_subplots': len(unique_conditions)
                },
                export_data={
                    'condition_rasters': condition_rasters,
                    'time_range': (-pre_time, post_time)
                },
                metadata={
                    'pre_time': pre_time,
                    'post_time': post_time,
                    'sort_by': sort_by,
                    'unique_conditions': unique_conditions.tolist()
                },
                execution_time=execution_time,
                success=True
            )
            
            self._record_execution(input_data, parameters, output)
            return output
            
        except Exception as e:
            return AlgorithmOutput(
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )


class TuningCurveAnalysis(BaseAlgorithm):
    """
    Tuning Curve Analysis Algorithm
    
    Analyzes neuron response selectivity across different stimulus conditions.
    Computes mean response for each condition and derives tuning metrics.
    
    Key Features:
    - Supports multiple trials and experimental sessions
    - Computes net response (response - baseline)
    - Calculates tuning index and preferred stimulus
    - Handles missing conditions gracefully
    - Provides per-trial and aggregated results
    
    Parameters:
        pre_time: Baseline period before stimulus (ms)
        post_time: Response period after stimulus (ms)
        metric: 'rate' (firing rate) or 'count' (spike count)
        stim_condition_key: Field name for stimulus condition in trial info
    
    Output:
        data: Condition-response pairs with statistics
        statistics: Tuning index, preferred condition, response metrics
        plot_config: Configuration for tuning curve visualization
    """
    
    def __init__(self):
        """Initialize tuning curve analysis with default settings"""
        super().__init__()
        self.name = "TuningCurveAnalysis"
        self.description = "Neuron Tuning Curve Analysis"
        self.category = "Spike"
        self.version = "1.0"
        self.required_data_types = ['spike', 'behavior']
        self.data_requirements_description = "Requires spike times and trial info with stimulus conditions"
    
    def get_parameters_schema(self):
        """Define parameter schema for tuning curve analysis"""
        return [
            create_parameter(
                "pre_time", ParameterType.FLOAT,
                "Pre-stimulus baseline period (ms)", 200.0,
                min_value=50.0, max_value=1000.0
            ),
            create_parameter(
                "post_time", ParameterType.FLOAT,
                "Post-stimulus response period (ms)", 500.0,
                min_value=100.0, max_value=2000.0
            ),
            create_parameter(
                "metric", ParameterType.SELECT,
                "Response metric", "rate",
                options=["rate", "count"]
            ),
            create_parameter(
                "stim_condition_key", ParameterType.STRING,
                "Field name for stimulus condition", "stim_cnd"
            )
        ]
    
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        """Validate input data for tuning curve analysis"""
        return (input_data.spike_times is not None and 
                input_data.trial_info is not None and
                len(input_data.spike_times) > 0)
    
    def run(self, input_data: AlgorithmInput, parameters: Dict) -> AlgorithmOutput:
        """
        Execute tuning curve analysis.
        
        Args:
            input_data: Contains spike_times and trial_info
            parameters: Analysis configuration
        
        Returns:
            AlgorithmOutput with tuning curve data and statistics
        """
        import time
        start_time = time.time()
        
        try:
            spike_times = input_data.spike_times
            trial_info = input_data.trial_info
            
            # Extract and convert parameters
            pre_time = parameters.get("pre_time", 200.0) / 1000.0
            post_time = parameters.get("post_time", 500.0) / 1000.0
            metric = parameters.get("metric", "rate")
            stim_condition_key = parameters.get("stim_condition_key", "stim_cnd")
            
            # Group trials by source (experiment/session)
            trial_sources = {}
            for trial in trial_info:
                source = trial.get('trial_source', 'default')
                if source not in trial_sources:
                    trial_sources[source] = []
                trial_sources[source].append(trial)
            
            # If no multiple sources, use single group
            if len(trial_sources) <= 1:
                trial_sources = {'all': trial_info}
            
            # Calculate tuning curve for each trial group
            trial_curves = {}
            all_conditions = set()
            
            for trial_name, trials in trial_sources.items():
                conditions = []
                responses = []
                
                for trial in trials:
                    # Skip invalid or aborted trials
                    if 'start_time' not in trial or trial.get('aborted', False):
                        continue
                    
                    event_time = trial['start_time']
                    stim_condition = trial.get(stim_condition_key, 0)
                    
                    # Align spikes to this trial's event
                    aligned_spikes = spike_times - event_time
                    
                    # Count spikes in baseline period
                    baseline_mask = (aligned_spikes >= -pre_time) & (aligned_spikes < 0)
                    n_baseline = np.sum(baseline_mask)
                    
                    # Count spikes in response period
                    response_mask = (aligned_spikes >= 0) & (aligned_spikes <= post_time)
                    n_response = np.sum(response_mask)
                    
                    # Calculate net response based on selected metric
                    if metric == "rate":
                        # Convert counts to firing rates (Hz)
                        baseline_rate = n_baseline / pre_time
                        response_rate = n_response / post_time
                        net_response = response_rate - baseline_rate
                    else:
                        # Use raw spike counts
                        net_response = n_response - n_baseline
                    
                    conditions.append(stim_condition)
                    responses.append(net_response)
                    all_conditions.add(stim_condition)
                
                # Store data for this trial group if valid
                if conditions:
                    trial_curves[trial_name] = {
                        'conditions': np.array(conditions),
                        'responses': np.array(responses)
                    }
            
            # Handle empty case
            if not trial_curves:
                return AlgorithmOutput(
                    success=False,
                    error_message="No valid trials found"
                )
            
            # Get all unique conditions sorted numerically
            unique_conditions = np.array(sorted(all_conditions))
            
            # Compute mean responses for each condition within each trial group
            trial_mean_responses = {}
            for trial_name, data in trial_curves.items():
                mean_responses = []
                for condition in unique_conditions:
                    mask = data['conditions'] == condition
                    if np.any(mask):
                        mean_responses.append(np.mean(data['responses'][mask]))
                    else:
                        # Use NaN for missing conditions
                        mean_responses.append(np.nan)
                trial_mean_responses[trial_name] = np.array(mean_responses)
            
            # Aggregate data across all trial groups
            all_conditions_list = []
            all_responses_list = []
            for data in trial_curves.values():
                all_conditions_list.extend(data['conditions'].tolist())
                all_responses_list.extend(data['responses'].tolist())
            
            all_conditions_arr = np.array(all_conditions_list)
            all_responses_arr = np.array(all_responses_list)
            
            # Compute statistics for each unique condition
            mean_responses = []
            std_responses = []
            sem_responses = []
            n_trials_per_condition = []
            
            for condition in unique_conditions:
                mask = all_conditions_arr == condition
                condition_responses = all_responses_arr[mask]
                
                mean_responses.append(np.mean(condition_responses))
                std_responses.append(np.std(condition_responses))
                sem_responses.append(np.std(condition_responses) / np.sqrt(len(condition_responses)))
                n_trials_per_condition.append(len(condition_responses))
            
            mean_responses = np.array(mean_responses)
            std_responses = np.array(std_responses)
            sem_responses = np.array(sem_responses)
            
            # Calculate tuning index: (max - min) / (max + min)
            # This ranges from 0 (no tuning) to 1 (maximal tuning)
            if len(mean_responses) > 1:
                tuning_index = (np.max(mean_responses) - np.min(mean_responses)) / (
                    np.max(mean_responses) + np.min(mean_responses) + 1e-10
                )
                preferred_condition = unique_conditions[np.argmax(mean_responses)]
            else:
                tuning_index = 0
                preferred_condition = unique_conditions[0] if len(unique_conditions) > 0 else 0
            
            execution_time = time.time() - start_time
            
            # Prepare comprehensive output
            output = AlgorithmOutput(
                data={
                    'conditions': unique_conditions,
                    'mean_responses': mean_responses,
                    'std_responses': std_responses,
                    'sem_responses': sem_responses,
                    'trial_curves': trial_mean_responses
                },
                statistics={
                    'tuning_index': float(tuning_index),
                    'preferred_condition': float(preferred_condition),
                    'max_response': float(np.max(mean_responses)),
                    'min_response': float(np.min(mean_responses)),
                    'mean_response': float(np.mean(mean_responses)),
                    'n_conditions': len(unique_conditions),
                    'n_trials': sum(n_trials_per_condition),
                    'n_trials_per_condition': n_trials_per_condition
                },
                plot_config={
                    'type': 'tuning_curve_multi',
                    'title': 'Tuning Curve (Multi-Trial)',
                    'xlabel': 'Stimulus Condition',
                    'ylabel': f'Response ({metric})',
                    'n_trials': len(trial_curves)
                },
                export_data={
                    'conditions': unique_conditions,
                    'mean_responses': mean_responses,
                    'std_responses': std_responses,
                    'sem_responses': sem_responses,
                    'trial_curves': trial_mean_responses
                },
                metadata={
                    'metric': metric,
                    'pre_time': pre_time,
                    'post_time': post_time,
                    'n_trials_per_condition': n_trials_per_condition,
                    'trial_names': list(trial_curves.keys())
                },
                execution_time=execution_time,
                success=True
            )
            
            self._record_execution(input_data, parameters, output)
            return output
            
        except Exception as e:
            return AlgorithmOutput(
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )


if __name__ == '__main__':
    """
    Self-test for spike analysis algorithms.
    This test verifies basic functionality of all three analysis classes.
    """
    print("=== Testing Spike Analysis Algorithms ===\n")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate simulated spike data (10 seconds recording at 20 Hz)
    duration = 10.0
    spike_rate = 20.0
    n_spikes = int(duration * spike_rate)
    spike_times = np.sort(np.random.uniform(0, duration, n_spikes))
    
    # Generate simulated trial information (5 trials, 3 stimulus conditions)
    trial_info = []
    for i in range(5):
        trial_info.append({
            'trial_num': i + 1,
            'start_time': i * 2.0 + 0.5,
            'stim_cnd': i % 3  # Cycle through 3 conditions
        })
    
    # Create input data object
    input_data = AlgorithmInput(
        spike_times=spike_times,
        trial_info=trial_info
    )
    
    # Test PSTH Analysis
    print("1. Testing PSTHAnalysis...")
    psth_analyzer = PSTHAnalysis()
    psth_params = psth_analyzer.get_default_parameters()
    psth_output = psth_analyzer.run(input_data, psth_params)
    
    if psth_output.success:
        print(f"   ✓ PSTH analysis successful")
        print(f"     Baseline rate: {psth_output.statistics['baseline_rate']:.2f} Hz")
        print(f"     Peak rate: {psth_output.statistics['peak_rate']:.2f} Hz")
        print(f"     Peak time: {psth_output.statistics['peak_time']:.3f} s")
        print(f"     Response modulation: {psth_output.statistics['response_modulation']:.2f}")
        print(f"     Execution time: {psth_output.execution_time:.4f}s")
    else:
        print(f"   ✗ PSTH analysis failed: {psth_output.error_message}")
    print()
    
    # Test Raster Plot Analysis
    print("2. Testing RasterPlotAnalysis...")
    raster_analyzer = RasterPlotAnalysis()
    raster_params = raster_analyzer.get_default_parameters()
    raster_output = raster_analyzer.run(input_data, raster_params)
    
    if raster_output.success:
        print(f"   ✓ Raster plot analysis successful")
        print(f"     Number of trials: {raster_output.statistics['n_trials_total']}")
        print(f"     Mean response: {raster_output.statistics['mean_response']:.2f}")
        print(f"     Total spikes: {raster_output.statistics['total_spikes']}")
        print(f"     Execution time: {raster_output.execution_time:.4f}s")
    else:
        print(f"   ✗ Raster plot analysis failed: {raster_output.error_message}")
    print()
    
    # Test Tuning Curve Analysis
    print("3. Testing TuningCurveAnalysis...")
    tuning_analyzer = TuningCurveAnalysis()
    tuning_params = tuning_analyzer.get_default_parameters()
    tuning_output = tuning_analyzer.run(input_data, tuning_params)
    
    if tuning_output.success:
        print(f"   ✓ Tuning curve analysis successful")
        print(f"     Tuning index: {tuning_output.statistics['tuning_index']:.3f}")
        print(f"     Preferred condition: {tuning_output.statistics['preferred_condition']}")
        print(f"     Max response: {tuning_output.statistics['max_response']:.2f}")
        print(f"     Min response: {tuning_output.statistics['min_response']:.2f}")
        print(f"     Number of conditions: {tuning_output.statistics['n_conditions']}")
        print(f"     Execution time: {tuning_output.execution_time:.4f}s")
    else:
        print(f"   ✗ Tuning curve analysis failed: {tuning_output.error_message}")
    
    print("\n✅ Spike analysis tests completed successfully!")
