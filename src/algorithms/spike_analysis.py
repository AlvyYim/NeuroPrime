"""
Spike Analysis Algorithms - Spike分析算法

提供PSTH、栅格图、调谐曲线等Spike分析功能
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
    刺激后时间直方图（PSTH）分析算法
    
    计算Spike在刺激事件周围的时间分布。
    
    可设置参数:
    - pre_time: 刺激前时间（ms）
    - post_time: 刺激后时间（ms）
    - bin_size: 时间窗大小（ms）
    - smoothing_sigma: 高斯平滑系数（ms）
    """
    
    def __init__(self):
        super().__init__()
        self.name = "PSTHAnalysis"
        self.description = "刺激后时间直方图（PSTH）分析"
        self.category = "Spike"
        self.version = "1.0"
        self.required_data_types = ['spike', 'behavior']
        self.data_requirements_description = "需要Spike数据和行为数据（试次信息）"
    
    def get_parameters_schema(self):
        return [
            create_parameter(
                "pre_time", ParameterType.FLOAT,
                "刺激前时间（ms）", 200.0,
                min_value=50.0, max_value=1000.0
            ),
            create_parameter(
                "post_time", ParameterType.FLOAT,
                "刺激后时间（ms）", 1000.0,
                min_value=100.0, max_value=2000.0
            ),
            create_parameter(
                "bin_size", ParameterType.FLOAT,
                "时间窗大小（ms）", 10.0,
                min_value=1.0, max_value=100.0
            ),
            create_parameter(
                "smoothing_sigma", ParameterType.FLOAT,
                "高斯平滑系数（ms）", 20.0,
                min_value=0.0, max_value=100.0
            ),
            create_parameter(
                "event_type", ParameterType.STRING,
                "事件类型", "stimulus_onset"
            )
        ]
    
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        return (input_data.spike_times is not None and 
                input_data.trial_info is not None and
                len(input_data.spike_times) > 0)
    
    def run(self, input_data: AlgorithmInput, parameters: Dict) -> AlgorithmOutput:
        import time
        start_time = time.time()
        
        try:
            spike_times = input_data.spike_times
            trial_info = input_data.trial_info
            
            # 提取参数
            pre_time = parameters.get("pre_time", 200.0) / 1000.0  # 转换为秒
            post_time = parameters.get("post_time", 500.0) / 1000.0
            bin_size = parameters.get("bin_size", 10.0) / 1000.0
            smoothing_sigma = parameters.get("smoothing_sigma", 20.0) / 1000.0
            
            # 获取事件时间
            event_times = []
            for trial in trial_info:
                if 'start_time' in trial and not trial.get('aborted', False):
                    event_times.append(trial['start_time'])
            
            if not event_times:
                return AlgorithmOutput(
                    success=False,
                    error_message="No valid event times found in trial info"
                )
            
            event_times = np.array(event_times)
            
            # 创建时间窗
            bins = np.arange(-pre_time, post_time + bin_size, bin_size)
            bin_centers = (bins[:-1] + bins[1:]) / 2
            
            # 计算PSTH
            psth_counts = np.zeros(len(bins) - 1)
            
            for event_time in event_times:
                # 对齐Spike时间
                aligned_spikes = spike_times - event_time
                
                # 筛选在时间窗内的Spike
                mask = (aligned_spikes >= -pre_time) & (aligned_spikes <= post_time)
                valid_spikes = aligned_spikes[mask]
                
                # 统计
                counts, _ = np.histogram(valid_spikes, bins=bins)
                psth_counts += counts
            
            # 转换为发放率（Hz）
            psth_rate = psth_counts / (len(event_times) * bin_size)
            
            # 应用平滑
            if smoothing_sigma > 0:
                sigma_samples = smoothing_sigma / bin_size
                psth_rate = gaussian_filter1d(psth_rate, sigma=sigma_samples)
            
            # 计算基线发放率（刺激前）
            baseline_mask = bin_centers < 0
            if np.any(baseline_mask):
                baseline_rate = np.mean(psth_rate[baseline_mask])
                baseline_std = np.std(psth_rate[baseline_mask])
            else:
                baseline_rate = 0
                baseline_std = 0
            
            # 计算响应峰值
            response_mask = bin_centers > 0
            if np.any(response_mask):
                peak_rate = np.max(psth_rate[response_mask])
                peak_time = bin_centers[response_mask][np.argmax(psth_rate[response_mask])]
            else:
                peak_rate = 0
                peak_time = 0
            
            execution_time = time.time() - start_time
            
            # 准备输出
            output = AlgorithmOutput(
                data={
                    'bin_centers': bin_centers,
                    'psth_rate': psth_rate,
                    'psth_counts': psth_counts
                },
                statistics={
                    'baseline_rate': float(baseline_rate),
                    'baseline_std': float(baseline_std),
                    'peak_rate': float(peak_rate),
                    'peak_time': float(peak_time),
                    'response_modulation': float((peak_rate - baseline_rate) / (baseline_rate + 1e-10)),
                    'n_trials': len(event_times),
                    'n_spikes_total': int(np.sum(psth_counts))
                },
                plot_config={
                    'type': 'psth',
                    'title': 'Peri-Stimulus Time Histogram (PSTH)',
                    'xlabel': 'Time from stimulus (s)',
                    'ylabel': 'Firing rate (Hz)',
                    'vline': 0  # 刺激 onset
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
            return AlgorithmOutput(
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )


class RasterPlotAnalysis(BaseAlgorithm):
    """
    栅格图分析算法
    
    生成Spike在试次中的时间分布栅格图。
    
    可设置参数:
    - pre_time: 刺激前时间（ms）
    - post_time: 刺激后时间（ms）
    - sort_by: 排序方式（time/response）
    """
    
    def __init__(self):
        super().__init__()
        self.name = "RasterPlotAnalysis"
        self.description = "栅格图分析"
        self.category = "Spike"
        self.version = "1.0"
        self.required_data_types = ['spike', 'behavior']
        self.data_requirements_description = "需要Spike数据和行为数据（试次信息）"
    
    def get_parameters_schema(self):
        return [
            create_parameter(
                "pre_time", ParameterType.FLOAT,
                "刺激前时间（ms）", 200.0,
                min_value=50.0, max_value=1000.0
            ),
            create_parameter(
                "post_time", ParameterType.FLOAT,
                "刺激后时间（ms）", 500.0,
                min_value=100.0, max_value=2000.0
            ),
            create_parameter(
                "sort_by", ParameterType.SELECT,
                "排序方式", "time",
                options=["time", "response"]
            ),
            create_parameter(
                "show_baseline", ParameterType.BOOLEAN,
                "显示基线期", True
            )
        ]
    
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        return (input_data.spike_times is not None and 
                input_data.trial_info is not None and
                len(input_data.spike_times) > 0)
    
    def run(self, input_data: AlgorithmInput, parameters: Dict) -> AlgorithmOutput:
        import time
        start_time = time.time()
        
        try:
            spike_times = input_data.spike_times
            trial_info = input_data.trial_info
            
            # 提取参数
            pre_time = parameters.get("pre_time", 200.0) / 1000.0
            post_time = parameters.get("post_time", 500.0) / 1000.0
            sort_by = parameters.get("sort_by", "time")
            show_baseline = parameters.get("show_baseline", True)
            
            # 获取事件时间、刺激条件和试次来源
            event_times = []
            stim_conditions = []
            trial_sources = []  # 记录试次来源（试验名称）
            
            for trial in trial_info:
                if 'start_time' in trial and not trial.get('aborted', False):
                    event_times.append(trial['start_time'])
                    # 获取刺激条件，默认为0
                    stim_cnd = trial.get('stim_cnd', 0)
                    stim_conditions.append(stim_cnd)
                    # 获取试次来源，用于区分不同试验的数据
                    trial_source = trial.get('trial_source', 'unknown')
                    trial_sources.append(trial_source)
            
            if not event_times:
                return AlgorithmOutput(
                    success=False,
                    error_message="No valid event times found in trial info"
                )
            
            event_times = np.array(event_times)
            stim_conditions = np.array(stim_conditions)
            trial_sources = np.array(trial_sources)
            
            # 获取唯一的刺激条件
            unique_conditions = np.unique(stim_conditions)
            
            # 获取唯一的试次来源
            unique_sources = np.unique(trial_sources)
            
            # 为每个试次收集Spike时间
            trial_spikes = []
            trial_responses = []
            
            for i, event_time in enumerate(event_times):
                # 对齐Spike时间
                aligned_spikes = spike_times - event_time
                
                # 筛选在时间窗内的Spike
                mask = (aligned_spikes >= -pre_time) & (aligned_spikes <= post_time)
                valid_spikes = aligned_spikes[mask]
                
                # 转换为Python列表以便序列化
                trial_spikes.append(valid_spikes.tolist() if hasattr(valid_spikes, 'tolist') else list(valid_spikes))
                
                # 计算响应（刺激后的Spike数量）
                response_mask = aligned_spikes > 0
                trial_responses.append(int(np.sum(response_mask)))
            
            # 按刺激条件分组，同时保留试次来源信息
            condition_rasters = {}
            for condition in unique_conditions:
                condition_mask = stim_conditions == condition
                condition_indices = np.where(condition_mask)[0]
                
                # 获取该条件下的试次spike数据
                condition_trial_spikes = [trial_spikes[i] for i in condition_indices]
                condition_responses = [trial_responses[i] for i in condition_indices]
                condition_trial_sources = [trial_sources[i] for i in condition_indices]
                
                # 排序试次
                if sort_by == "response":
                    sort_indices = np.argsort(condition_responses)[::-1]
                else:
                    sort_indices = np.arange(len(condition_trial_spikes))
                
                # 重新排序
                sorted_spikes = [condition_trial_spikes[i] for i in sort_indices]
                sorted_sources = [condition_trial_sources[i] for i in sort_indices]
                
                condition_rasters[int(condition)] = {
                    'trial_spikes': sorted_spikes,
                    'trial_sources': sorted_sources,  # 添加试次来源信息
                    'n_trials': len(sorted_spikes),
                    'mean_response': float(np.mean(condition_responses)) if condition_responses else 0.0
                }
            
            execution_time = time.time() - start_time
            
            # 准备输出 - 包含所有条件的栅格图数据
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
    调谐曲线分析算法
    
    分析神经元对不同刺激条件的调谐特性。
    
    可设置参数:
    - pre_time: 刺激前基线时间（ms）
    - post_time: 刺激后响应时间（ms）
    - metric: 响应指标（rate/count）
    """
    
    def __init__(self):
        super().__init__()
        self.name = "TuningCurveAnalysis"
        self.description = "调谐曲线分析"
        self.category = "Spike"
        self.version = "1.0"
        self.required_data_types = ['spike', 'behavior']
        self.data_requirements_description = "需要Spike数据和行为数据（试次信息）"
    
    def get_parameters_schema(self):
        return [
            create_parameter(
                "pre_time", ParameterType.FLOAT,
                "刺激前基线时间（ms）", 200.0,
                min_value=50.0, max_value=1000.0
            ),
            create_parameter(
                "post_time", ParameterType.FLOAT,
                "刺激后响应时间（ms）", 500.0,
                min_value=100.0, max_value=2000.0
            ),
            create_parameter(
                "metric", ParameterType.SELECT,
                "响应指标", "rate",
                options=["rate", "count"]
            ),
            create_parameter(
                "stim_condition_key", ParameterType.STRING,
                "刺激条件字段名", "stim_cnd"
            )
        ]
    
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        return (input_data.spike_times is not None and 
                input_data.trial_info is not None and
                len(input_data.spike_times) > 0)
    
    def run(self, input_data: AlgorithmInput, parameters: Dict) -> AlgorithmOutput:
        import time
        start_time = time.time()
        
        try:
            spike_times = input_data.spike_times
            trial_info = input_data.trial_info
            
            # 提取参数
            pre_time = parameters.get("pre_time", 200.0) / 1000.0
            post_time = parameters.get("post_time", 500.0) / 1000.0
            metric = parameters.get("metric", "rate")
            stim_condition_key = parameters.get("stim_condition_key", "stim_cnd")
            
            # 按试验分组（如果trial_info中有trial_source字段）
            trial_sources = {}
            for trial in trial_info:
                source = trial.get('trial_source', 'default')
                if source not in trial_sources:
                    trial_sources[source] = []
                trial_sources[source].append(trial)
            
            # 如果没有多个试验，使用默认分组
            if len(trial_sources) <= 1:
                trial_sources = {'all': trial_info}
            
            # 为每个试验计算调谐曲线
            trial_curves = {}
            all_conditions = set()
            
            for trial_name, trials in trial_sources.items():
                conditions = []
                responses = []
                
                for trial in trials:
                    if 'start_time' not in trial or trial.get('aborted', False):
                        continue
                    
                    event_time = trial['start_time']
                    stim_condition = trial.get(stim_condition_key, 0)
                    
                    # 对齐Spike时间
                    aligned_spikes = spike_times - event_time
                    
                    # 计算基线期Spike数量
                    baseline_mask = (aligned_spikes >= -pre_time) & (aligned_spikes < 0)
                    n_baseline = np.sum(baseline_mask)
                    
                    # 计算响应期Spike数量
                    response_mask = (aligned_spikes >= 0) & (aligned_spikes <= post_time)
                    n_response = np.sum(response_mask)
                    
                    # 计算净响应
                    if metric == "rate":
                        baseline_rate = n_baseline / pre_time
                        response_rate = n_response / post_time
                        net_response = response_rate - baseline_rate
                    else:  # count
                        net_response = n_response - n_baseline
                    
                    conditions.append(stim_condition)
                    responses.append(net_response)
                    all_conditions.add(stim_condition)
                
                if conditions:
                    trial_curves[trial_name] = {
                        'conditions': np.array(conditions),
                        'responses': np.array(responses)
                    }
            
            if not trial_curves:
                return AlgorithmOutput(
                    success=False,
                    error_message="No valid trials found"
                )
            
            # 获取所有唯一的刺激条件（排序）
            unique_conditions = np.array(sorted(all_conditions))
            
            # 为每个试验计算每个条件的平均响应
            trial_mean_responses = {}
            for trial_name, data in trial_curves.items():
                mean_responses = []
                for condition in unique_conditions:
                    mask = data['conditions'] == condition
                    if np.any(mask):
                        mean_responses.append(np.mean(data['responses'][mask]))
                    else:
                        mean_responses.append(np.nan)  # 该试验没有这个条件
                trial_mean_responses[trial_name] = np.array(mean_responses)
            
            # 计算所有试验合并的平均响应
            all_conditions_list = []
            all_responses_list = []
            for data in trial_curves.values():
                all_conditions_list.extend(data['conditions'].tolist())
                all_responses_list.extend(data['responses'].tolist())
            
            all_conditions_arr = np.array(all_conditions_list)
            all_responses_arr = np.array(all_responses_list)
            
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
            
            # 计算调谐指数
            if len(mean_responses) > 1:
                tuning_index = (np.max(mean_responses) - np.min(mean_responses)) / (
                    np.max(mean_responses) + np.min(mean_responses) + 1e-10
                )
                preferred_condition = unique_conditions[np.argmax(mean_responses)]
            else:
                tuning_index = 0
                preferred_condition = unique_conditions[0] if len(unique_conditions) > 0 else 0
            
            execution_time = time.time() - start_time
            
            # 准备输出 - 包含每个试验的调谐曲线
            output = AlgorithmOutput(
                data={
                    'conditions': unique_conditions,
                    'mean_responses': mean_responses,
                    'std_responses': std_responses,
                    'sem_responses': sem_responses,
                    'trial_curves': trial_mean_responses  # 每个试验的调谐曲线
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
    # 测试代码
    print("=== Testing Spike Analysis Algorithms ===\n")
    
    # 创建模拟数据
    np.random.seed(42)
    
    # 模拟Spike时间（10秒，平均20Hz）
    duration = 10.0
    spike_rate = 20.0
    n_spikes = int(duration * spike_rate)
    spike_times = np.sort(np.random.uniform(0, duration, n_spikes))
    
    # 模拟试次信息（5个试次，间隔2秒）
    trial_info = []
    for i in range(5):
        trial_info.append({
            'trial_num': i + 1,
            'start_time': i * 2.0 + 0.5,
            'stim_cnd': i % 3  # 3种刺激条件
        })
    
    input_data = AlgorithmInput(
        spike_times=spike_times,
        trial_info=trial_info
    )
    
    # 测试PSTH分析
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
    
    # 测试栅格图分析
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
    
    # 测试调谐曲线分析
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
    
    print("\n✅ Spike analysis tests completed!")
