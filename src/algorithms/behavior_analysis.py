"""
Behavior Analysis Algorithms - 行为分析算法

提供ROC分析功能
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats


try:
    from .base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput, ParameterType, create_parameter
except ImportError:
    from base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput, ParameterType, create_parameter


class ROCAnalysis(BaseAlgorithm):
    """
    ROC（Receiver Operating Characteristic）分析算法
    
    评估神经元对不同刺激条件的区分能力。
    
    可设置参数:
    - pre_time: 基线时间（ms）
    - post_time: 响应时间（ms）
    - positive_class: 正类标签（默认为1）
    """
    
    def __init__(self):
        super().__init__()
        self.name = "ROCAnalysis"
        self.description = "ROC曲线分析（评估神经元区分能力）"
        self.category = "Behavior"
        self.version = "1.0"
        self.required_data_types = ['spike', 'behavior']
        self.data_requirements_description = "需要Spike数据和行为数据（试次信息）"
    
    def get_parameters_schema(self):
        return [
            create_parameter(
                "pre_time", ParameterType.FLOAT,
                "基线时间（ms）", 200.0,
                min_value=50.0, max_value=1000.0
            ),
            create_parameter(
                "post_time", ParameterType.FLOAT,
                "响应时间（ms）", 500.0,
                min_value=100.0, max_value=2000.0
            ),
            create_parameter(
                "positive_class", ParameterType.INTEGER,
                "正类标签", 1,
                min_value=0, max_value=10
            ),
        ]
    
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        """验证输入数据"""
        if input_data.spike_times is None or len(input_data.spike_times) == 0:
            return False
        if input_data.trial_info is None or len(input_data.trial_info) == 0:
            return False
        return True
    
    def run(self, input_data: AlgorithmInput, parameters: Dict) -> AlgorithmOutput:
        """执行ROC分析 - 支持多试验数据对比"""
        import time
        start_time = time.time()
        
        try:
            # 检查输入数据
            if input_data.spike_times is None or len(input_data.spike_times) == 0:
                return AlgorithmOutput(
                    success=False,
                    error_message="No spike times provided"
                )
            
            if input_data.trial_info is None or len(input_data.trial_info) == 0:
                return AlgorithmOutput(
                    success=False,
                    error_message="No trial info provided"
                )
            
            spike_times = input_data.spike_times
            trial_info = input_data.trial_info
            
            # 提取参数
            pre_time = parameters.get("pre_time", 200.0) / 1000.0
            post_time = parameters.get("post_time", 500.0) / 1000.0
            positive_class = parameters.get("positive_class", 1)
            
            # 按试验来源分组
            trial_sources = {}
            for trial in trial_info:
                source = trial.get('trial_source', 'unknown')
                if source not in trial_sources:
                    trial_sources[source] = []
                trial_sources[source].append(trial)
            
            # 为每个试验来源计算ROC曲线
            roc_curves = {}
            roc_errors = {}  # 初始化错误记录字典
            
            for source, trials in trial_sources.items():
                y_true = []
                y_score = []
                
                for trial in trials:
                    if 'start_time' not in trial or trial.get('aborted', False):
                        continue
                    
                    event_time = trial['start_time']
                    stim_cnd = trial.get('stim_cnd', 0)
                    
                    # 对齐Spike时间
                    aligned_spikes = spike_times - event_time
                    
                    # 计算响应时间窗内的发放率
                    response_mask = (aligned_spikes >= 0) & (aligned_spikes <= post_time)
                    n_response_spikes = np.sum(response_mask)
                    response_rate = n_response_spikes / post_time
                    
                    # 二分类标签
                    label = 1 if stim_cnd == positive_class else 0
                    
                    y_true.append(label)
                    y_score.append(response_rate)
                
                # 检查是否有足够的数据
                if len(y_true) < 2:
                    roc_errors[source] = f"试次数不足 ({len(y_true)})"
                    print(f"[DEBUG] {source}: 试次数不足 ({len(y_true)})")
                    continue
                
                unique_classes = len(set(y_true))
                if unique_classes < 2:
                    class_dist = {c: y_true.count(c) for c in set(y_true)}
                    roc_errors[source] = f"只有一类数据 {class_dist}"
                    print(f"[DEBUG] {source}: 只有一类数据 {class_dist}")
                    continue
                
                # 检查y_score是否有足够的差异
                unique_scores = len(set(y_score))
                if unique_scores < 2:
                    roc_errors[source] = f"所有试次的响应率相同 ({y_score[0]:.4f})"
                    print(f"[DEBUG] {source}: 所有试次的响应率相同 ({y_score[0]:.4f})")
                    continue
                
                try:
                    from sklearn.metrics import roc_curve, roc_auc_score
                    
                    # 调试输出
                    print(f"[DEBUG] Calculating ROC for {source}:")
                    print(f"  y_true (n={len(y_true)}): {y_true}")
                    print(f"  y_score (n={len(y_score)}): {[round(s, 4) for s in y_score]}")
                    print(f"  unique_classes: {unique_classes}, unique_scores: {unique_scores}")
                    
                    fpr, tpr, thresholds = roc_curve(y_true, y_score)
                    auc_value = roc_auc_score(y_true, y_score)
                    
                    print(f"[DEBUG] ROC calculation successful: AUC={auc_value:.4f}")
                    
                    roc_curves[source] = {
                        'fpr': fpr,
                        'tpr': tpr,
                        'auc': auc_value,
                        'n_trials': len(y_true),
                        'n_positive': int(np.sum(y_true)),
                        'n_negative': len(y_true) - int(np.sum(y_true))
                    }
                except Exception as e:
                    import traceback
                    error_msg = f"ROC计算失败: {str(e)}"
                    print(f"[DEBUG] {error_msg}")
                    print(f"[DEBUG] Traceback: {traceback.format_exc()}")
                    roc_errors[source] = error_msg
                    continue
            
            if not roc_curves:
                # 检查是否有试验数据
                if not trial_sources:
                    return AlgorithmOutput(
                        success=False,
                        error_message="No trial data available"
                    )
                
                # 使用roc_errors字典中的错误信息
                error_details = []
                for source in trial_sources.keys():
                    if source in roc_errors:
                        error_details.append(f"{source}: {roc_errors[source]}")
                    else:
                        # 如果没有错误记录，重新分析
                        trials = trial_sources[source]
                        y_true = [1 if trial.get('stim_cnd', 0) == positive_class else 0 for trial in trials]
                        unique_classes = len(set(y_true))
                        n_trials = len(trials)
                        error_details.append(f"{source}: 未知问题 (试次{n_trials}, 类别{unique_classes})")
                
                if not error_details:
                    error_details.append("未知错误：无法计算ROC曲线")
                
                error_msg = "无法计算ROC曲线。原因:\n" + "\n".join(error_details)
                error_msg += f"\n\n提示: 当前正类标签={positive_class}，请检查数据是否包含该标签"
                
                return AlgorithmOutput(
                    success=False,
                    error_message=error_msg
                )
            
            # 如果只有一个试验来源，使用传统格式
            if len(roc_curves) == 1:
                source = list(roc_curves.keys())[0]
                curve_data = roc_curves[source]
                fpr = curve_data['fpr']
                tpr = curve_data['tpr']
                auc_value = curve_data['auc']
            else:
                # 多个试验来源，使用新格式
                fpr = None
                tpr = None
                auc_value = None
            
            # 准备输出数据
            if len(roc_curves) == 1:
                # 单个试验来源
                source = list(roc_curves.keys())[0]
                curve_data = roc_curves[source]
                fpr = curve_data['fpr']
                tpr = curve_data['tpr']
                thresholds = np.array([])  # 简化处理
                auc_value = curve_data['auc']
                
                # 计算最佳阈值
                j_scores = tpr - fpr
                best_idx = np.argmax(j_scores)
                best_threshold = 0
                best_fpr = fpr[best_idx] if best_idx < len(fpr) else 0
                best_tpr = tpr[best_idx] if best_idx < len(tpr) else 0
                
                output_data = {
                    'fpr': fpr,
                    'tpr': tpr,
                    'auc': auc_value,
                    'roc_curves': roc_curves
                }
                
                output_statistics = {
                    'auc': float(auc_value),
                    'best_threshold': float(best_threshold),
                    'best_fpr': float(best_fpr),
                    'best_tpr': float(best_tpr),
                    'n_trials': curve_data['n_trials'],
                    'n_positive': curve_data['n_positive'],
                    'n_negative': curve_data['n_negative']
                }
                
                plot_title = f'ROC Curve (AUC={auc_value:.3f})'
            else:
                # 多个试验来源
                output_data = {
                    'roc_curves': roc_curves
                }
                
                # 计算平均AUC
                avg_auc = np.mean([c['auc'] for c in roc_curves.values()])
                total_trials = sum([c['n_trials'] for c in roc_curves.values()])
                total_positive = sum([c['n_positive'] for c in roc_curves.values()])
                total_negative = sum([c['n_negative'] for c in roc_curves.values()])
                
                output_statistics = {
                    'avg_auc': float(avg_auc),
                    'n_trials': total_trials,
                    'n_positive': total_positive,
                    'n_negative': total_negative,
                    'n_sources': len(roc_curves)
                }
                
                plot_title = f'ROC Curves Comparison ({len(roc_curves)} sources, avg AUC={avg_auc:.3f})'
            
            execution_time = time.time() - start_time
            
            # 准备输出
            output = AlgorithmOutput(
                data=output_data,
                statistics=output_statistics,
                plot_config={
                    'type': 'roc_curve',
                    'title': plot_title,
                    'xlabel': 'False Positive Rate',
                    'ylabel': 'True Positive Rate'
                },
                export_data=output_data,
                metadata={
                    'positive_class': positive_class,
                    'pre_time': pre_time,
                    'post_time': post_time,
                    'roc_curves': roc_curves
                },
                execution_time=execution_time,
                success=True
            )
            
            self._record_execution(input_data, parameters, output)
            return output
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return AlgorithmOutput(
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )


if __name__ == '__main__':
    # 测试代码
    print("=== Testing Behavior Analysis Algorithms ===\n")
    
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
            'stim_cnd': i % 2  # 2种刺激条件，用于ROC分析
        })
    
    input_data = AlgorithmInput(
        spike_times=spike_times,
        trial_info=trial_info
    )
    
    # 测试ROC分析
    print("1. Testing ROCAnalysis...")
    roc_analyzer = ROCAnalysis()
    
    roc_params = roc_analyzer.get_default_parameters()
    
    roc_output = roc_analyzer.run(input_data, roc_params)
    
    if roc_output.success:
        print(f"   ✓ ROC analysis successful")
        if 'auc' in roc_output.statistics:
            print(f"     AUC: {roc_output.statistics['auc']:.3f}")
        elif 'avg_auc' in roc_output.statistics:
            print(f"     Average AUC: {roc_output.statistics['avg_auc']:.3f}")
        print(f"     Number of trials: {roc_output.statistics.get('n_trials', 0)}")
        print(f"     Execution time: {roc_output.execution_time:.4f}s")
    else:
        print(f"   ✗ ROC analysis failed: {roc_output.error_message}")
    
    print("\n✅ Behavior analysis tests completed!")
