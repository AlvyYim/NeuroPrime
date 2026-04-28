"""
分析原始NEV文件，检查Spike数据和试次信息的实际情况
"""

import numpy as np
from pathlib import Path
from src.parsers.nev_parser import parse_nev

def analyze_nev_file(nev_file):
    """
    分析原始NEV文件，检查Spike数据和试次信息的实际情况
    
    Args:
        nev_file: NEV文件路径
    """
    print(f"\n=== 分析NEV文件: {nev_file} ===")
    
    # 解析NEV文件
    result = parse_nev(nev_file)
    
    if not result:
        print("解析失败")
        return
    
    # 检查基本信息
    basic_header = result['basic_header']
    print(f"\n=== 基本信息 ===")
    print(f"文件类型: {basic_header.file_type}")
    print(f"版本: {basic_header.version}")
    print(f"时钟频率: {basic_header.clock_fs} Hz")
    print(f"波形采样率: {basic_header.waveform_fs} Hz")
    
    # 检查Spike事件
    spike_events = result['spike_events']
    print(f"\n=== Spike事件 ===")
    print(f"总Spike事件数: {len(spike_events)}")
    
    if spike_events:
        # 提取Spike时间戳
        spike_times = np.array([e.timestamp for e in spike_events])
        print(f"Spike时间范围: {spike_times.min():.3f} - {spike_times.max():.3f} 秒")
        
        # 按1秒间隔统计Spike数量
        bin_size = 1.0
        bins = np.arange(spike_times.min(), spike_times.max() + bin_size, bin_size)
        counts, _ = np.histogram(spike_times, bins=bins)
        
        print("\nSpike时间分布（每1秒）:")
        for i, count in enumerate(counts[:20]):  # 只显示前20秒
            print(f"  {bins[i]:.1f}-{bins[i+1]:.1f}s: {count} spikes")
    
    # 检查数字事件
    digital_events = result['digital_events']
    print(f"\n=== 数字事件 ===")
    print(f"总数字事件数: {len(digital_events)}")
    
    # 统计事件类型
    event_types = {}
    for e in digital_events:
        if e.event_type not in event_types:
            event_types[e.event_type] = 0
        event_types[e.event_type] += 1
    
    print("\n事件类型统计:")
    for event_type, count in event_types.items():
        print(f"  {event_type}: {count}")
    
    # 检查试次信息
    trials = result['trials']
    print(f"\n=== 试次信息 ===")
    print(f"试次数: {len(trials)}")
    
    if trials:
        print("\n前5个试次的信息:")
        for i, trial in enumerate(trials[:5]):
            print(f"  试次 {trial.trial_num}:")
            print(f"    开始时间: {trial.start_time:.3f} 秒")
            print(f"    结束时间: {trial.end_time:.3f} 秒")
            print(f"    刺激条件: {trial.stim_cnd}")
            print(f"    中止时间: {trial.abort_time if trial.abort_time else 'None'}")
            print(f"    TTL时间: {trial.ttl_time if trial.ttl_time else 'None'}")
            
            # 计算试次期间的Spike数量
            if spike_events:
                trial_spikes = [e for e in spike_events if trial.start_time <= e.timestamp <= trial.end_time]
                print(f"    试次期间Spike数量: {len(trial_spikes)}")
    
    print("\n分析完成!")

if __name__ == '__main__':
    # 测试test2目录中的NEV文件
    test2_nev = Path("test2/data/raw/FC_Grating_012.nev")
    if test2_nev.exists():
        analyze_nev_file(str(test2_nev))
    else:
        # 尝试其他路径
        alternative_nev = Path("C:/Users/Administrator/Desktop/new hope/dataandcode/FC_Grating_012.nev")
        if alternative_nev.exists():
            analyze_nev_file(str(alternative_nev))
        else:
            print(f"NEV文件不存在: {test2_nev}")
