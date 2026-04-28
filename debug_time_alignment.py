"""
调试时间对齐问题，验证Spike时间和试次时间的对齐情况
"""

import numpy as np
from src.parsers.nev_parser import parse_nev

def debug_time_alignment(nev_file):
    """
    调试时间对齐问题，验证Spike时间和试次时间的对齐情况
    
    Args:
        nev_file: NEV文件路径
    """
    print(f"\n=== 调试时间对齐: {nev_file} ===")
    
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
    
    # 检查所有试次的TTL时间
    print("\n试次TTL时间:")
    print("-" * 50)
    print(f"{'试次':<5} {'TTL时间':<12} {'开始时间':<12} {'结束时间':<12}")
    print("-" * 50)
    
    ttl_times = []
    for trial in trials:
        ttl_time = trial.ttl_time if trial.ttl_time else 0.0
        ttl_times.append(ttl_time)
        print(f"{trial.trial_num:<5} {ttl_time:<12.3f} {trial.start_time:<12.3f} {trial.end_time:<12.3f}")
    
    print("-" * 50)
    
    # 检查所有试次的TTL时间是否相同
    ttl_times = np.array(ttl_times)
    unique_ttl_times = np.unique(ttl_times)
    print(f"\n唯一的TTL时间: {unique_ttl_times}")
    print(f"所有试次的TTL时间是否相同: {len(unique_ttl_times) == 1}")
    
    # 分析Spike时间分布
    print(f"\nSpike时间范围: {spike_times.min():.3f} - {spike_times.max():.3f} 秒")
    
    # 分析每个试次的时间范围
    trial_start_times = np.array([t.start_time for t in trials])
    trial_end_times = np.array([t.end_time for t in trials])
    print(f"试次时间范围: {trial_start_times.min():.3f} - {trial_end_times.max():.3f} 秒")
    
    # 检查Spike时间是否在试次时间范围内
    spike_in_trial = 0
    for spike_time in spike_times:
        for trial in trials:
            if trial.start_time <= spike_time <= trial.end_time:
                spike_in_trial += 1
                break
    
    print(f"\n在试次时间范围内的Spike数量: {spike_in_trial}")
    print(f"在试次时间范围外的Spike数量: {len(spike_events) - spike_in_trial}")
    print(f"Spike在试次时间范围内的比例: {spike_in_trial / len(spike_events):.2f}")
    
    # 分析前几个试次的Spike分布
    print("\n前5个试次的Spike分布:")
    print("-" * 80)
    print(f"{'试次':<5} {'开始时间':<12} {'结束时间':<12} {'试次内Spike数':<15} {'刺激前Spike数':<15} {'刺激后Spike数':<15}")
    print("-" * 80)
    
    for trial in trials[:5]:
        trial_start = trial.start_time
        trial_end = trial.end_time
        
        # 试次内Spike数
        trial_spikes = len(spike_times[(spike_times >= trial_start) & (spike_times <= trial_end)])
        
        # 刺激前Spike数（开始时间前200ms）
        pre_stim_start = trial_start - 0.2
        pre_stim_end = trial_start
        pre_stim_spikes = len(spike_times[(spike_times >= pre_stim_start) & (spike_times < pre_stim_end)])
        
        # 刺激后Spike数（开始时间后1000ms）
        post_stim_start = trial_start
        post_stim_end = trial_start + 1.0
        post_stim_spikes = len(spike_times[(spike_times >= post_stim_start) & (spike_times < post_stim_end)])
        
        print(f"{trial.trial_num:<5} {trial_start:<12.3f} {trial_end:<12.3f} {trial_spikes:<15} {pre_stim_spikes:<15} {post_stim_spikes:<15}")
    
    print("-" * 80)

if __name__ == '__main__':
    # 分析test2目录中的NEV文件
    test2_nev = "test2/data/raw/FC_Grating_012.nev"
    debug_time_alignment(test2_nev)
