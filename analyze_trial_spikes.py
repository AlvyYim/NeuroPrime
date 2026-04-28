"""
分析每个试次的开始时间、结束时间，以及每个试次刺激出现前后的Spike数
"""

import numpy as np
from src.parsers.nev_parser import parse_nev

def analyze_trial_spikes(nev_file):
    """
    分析每个试次的开始时间、结束时间，以及每个试次刺激出现前后的Spike数
    
    Args:
        nev_file: NEV文件路径
    """
    print(f"\n=== 分析试次Spike分布: {nev_file} ===")
    
    # 解析NEV文件
    result = parse_nev(nev_file)
    
    if not result:
        print("解析失败")
        return
    
    # 提取Spike时间和试次信息
    spike_events = result['spike_events']
    trials = result['trials']
    
    if not spike_events or not trials:
        print("没有Spike事件或试次信息")
        return
    
    # 提取Spike时间
    spike_times = np.array([e.timestamp for e in spike_events])
    
    print(f"\n共 {len(trials)} 个试次，{len(spike_events)} 个Spike事件")
    print("\n试次分析结果:")
    print("-" * 80)
    print(f"{'试次':<5} {'开始时间':<12} {'结束时间':<12} {'刺激前Spike':<12} {'刺激后Spike':<12} {'总Spike':<10}")
    print("-" * 80)
    
    # 分析每个试次
    for trial in trials:
        trial_num = trial.trial_num
        start_time = trial.start_time
        end_time = trial.end_time
        
        # 计算刺激前Spike数（开始时间前200ms）
        pre_stim_start = start_time - 0.2  # 200ms
        pre_stim_end = start_time
        pre_stim_spikes = len(spike_times[(spike_times >= pre_stim_start) & (spike_times < pre_stim_end)])
        
        # 计算刺激后Spike数（开始时间后1000ms）
        post_stim_start = start_time
        post_stim_end = start_time + 1.0  # 1000ms
        post_stim_spikes = len(spike_times[(spike_times >= post_stim_start) & (spike_times < post_stim_end)])
        
        # 计算试次期间的总Spike数
        trial_spikes = len(spike_times[(spike_times >= start_time) & (spike_times < end_time)])
        
        print(f"{trial_num:<5} {start_time:<12.3f} {end_time:<12.3f} {pre_stim_spikes:<12} {post_stim_spikes:<12} {trial_spikes:<10}")
    
    print("-" * 80)
    
    # 计算总体统计
    total_pre_stim = 0
    total_post_stim = 0
    total_trial_spikes = 0
    
    for trial in trials:
        start_time = trial.start_time
        end_time = trial.end_time
        
        # 计算刺激前Spike数
        pre_stim_start = start_time - 0.2
        pre_stim_end = start_time
        pre_stim_spikes = len(spike_times[(spike_times >= pre_stim_start) & (spike_times < pre_stim_end)])
        total_pre_stim += pre_stim_spikes
        
        # 计算刺激后Spike数
        post_stim_start = start_time
        post_stim_end = start_time + 1.0
        post_stim_spikes = len(spike_times[(spike_times >= post_stim_start) & (spike_times < post_stim_end)])
        total_post_stim += post_stim_spikes
        
        # 计算试次期间的总Spike数
        trial_spikes = len(spike_times[(spike_times >= start_time) & (spike_times < end_time)])
        total_trial_spikes += trial_spikes
    
    print(f"\n总体统计:")
    print(f"刺激前总Spike数: {total_pre_stim}")
    print(f"刺激后总Spike数: {total_post_stim}")
    print(f"试次期间总Spike数: {total_trial_spikes}")
    print(f"刺激前/刺激后比例: {total_pre_stim / total_post_stim:.2f}")

if __name__ == '__main__':
    # 分析test2目录中的NEV文件
    test2_nev = "test2/data/raw/FC_Grating_012.nev"
    analyze_trial_spikes(test2_nev)
