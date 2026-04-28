"""
分析时间对齐问题，检查PSTH分析中刺激前spike比刺激后多的原因
"""

import h5py
import numpy as np
from pathlib import Path

def analyze_time_alignment_issue(hdf5_file):
    """
    分析时间对齐问题，检查PSTH分析中刺激前spike比刺激后多的原因
    
    Args:
        hdf5_file: HDF5文件路径
    """
    try:
        with h5py.File(hdf5_file, 'r') as f:
            print(f"\n=== 分析文件: {hdf5_file} ===")
            
            # 检查Spike数据
            if 'spikes' in f:
                spikes = f['spikes']
                if 'spike_times' in spikes:
                    spike_times = spikes['spike_times'][:]
                    print(f"Spike总数: {len(spike_times)}")
                    print(f"Spike时间范围: {spike_times.min():.3f} - {spike_times.max():.3f}")
                else:
                    print("未找到spike_times")
                    return
            else:
                print("未找到spikes")
                return
            
            # 检查试次信息
            if 'behavior' in f and 'trials' in f['behavior']:
                trials = f['behavior']['trials']
                print(f"试次数: {trials.shape[0]}")
                
                # 分析每个试次的时间和Spike分布
                print("\n分析每个试次的时间和Spike分布:")
                
                for i in range(min(5, trials.shape[0])):
                    trial = trials[i]
                    start_time = trial['start_time']
                    end_time = trial['end_time']
                    
                    print(f"\n试次 {i+1}:")
                    print(f"  开始时间: {start_time:.3f}")
                    print(f"  结束时间: {end_time:.3f}")
                    
                    # 计算试次前的Spike数量（默认200ms）
                    pre_time = 0.2  # 200ms
                    post_time = 1.0  # 1000ms
                    
                    # 刺激前的Spike
                    pre_spikes = spike_times[(spike_times >= start_time - pre_time) & (spike_times < start_time)]
                    print(f"  刺激前Spike数量 (200ms): {len(pre_spikes)}")
                    
                    # 刺激后的Spike
                    post_spikes = spike_times[(spike_times >= start_time) & (spike_times < start_time + post_time)]
                    print(f"  刺激后Spike数量 (1000ms): {len(post_spikes)}")
                    
                    # 计算比例
                    if len(post_spikes) > 0:
                        ratio = len(pre_spikes) / len(post_spikes)
                        print(f"  刺激前/刺激后Spike比例: {ratio:.2f}")
                    else:
                        print(f"  刺激后无Spike")
            else:
                print("未找到behavior/trials")
                return
            
            # 检查元数据
            if 'metadata' in f:
                metadata = f['metadata']
                print("\n元数据:")
                print(f"  采样率: {metadata.attrs.get('sampling_rate', 'N/A')}")
                print(f"  记录时长: {metadata.attrs.get('duration', 'N/A')}")
                print(f"  通道数: {metadata.attrs.get('num_channels', 'N/A')}")
                
                if 'source_files' in metadata:
                    source_files = metadata['source_files']
                    print("  源文件:")
                    for key in source_files.attrs:
                        print(f"    {key}: {source_files.attrs[key]}")
            
    except Exception as e:
        print(f"错误: {e}")

def analyze_spike_distribution(hdf5_file):
    """
    分析Spike在整个时间范围内的分布
    
    Args:
        hdf5_file: HDF5文件路径
    """
    try:
        with h5py.File(hdf5_file, 'r') as f:
            print(f"\n=== 分析Spike分布: {hdf5_file} ===")
            
            # 检查Spike数据
            if 'spikes' in f:
                spikes = f['spikes']
                if 'spike_times' in spikes:
                    spike_times = spikes['spike_times'][:]
                    
                    # 计算Spike在时间上的分布
                    print(f"Spike总数: {len(spike_times)}")
                    print(f"Spike时间范围: {spike_times.min():.3f} - {spike_times.max():.3f}")
                    
                    # 按1秒间隔统计Spike数量
                    bin_size = 1.0
                    bins = np.arange(spike_times.min(), spike_times.max() + bin_size, bin_size)
                    counts, _ = np.histogram(spike_times, bins=bins)
                    
                    print("\nSpike时间分布（每1秒）:")
                    for i, count in enumerate(counts[:10]):  # 只显示前10秒
                        print(f"  {bins[i]:.1f}-{bins[i+1]:.1f}s: {count} spikes")
                    
                    # 检查是否有试次信息
                    if 'behavior' in f and 'trials' in f['behavior']:
                        trials = f['behavior']['trials']
                        trial_starts = [trial['start_time'] for trial in trials if not trial.get('aborted', False)]
                        
                        print("\n试次开始时间:")
                        for i, start_time in enumerate(trial_starts[:5]):
                            print(f"  试次 {i+1}: {start_time:.3f}s")
                            
                            # 检查试次开始时间前后的Spike分布
                            pre_spikes = spike_times[(spike_times >= start_time - 0.5) & (spike_times < start_time)]
                            post_spikes = spike_times[(spike_times >= start_time) & (spike_times < start_time + 0.5)]
                            print(f"    试次前0.5秒: {len(pre_spikes)} spikes")
                            print(f"    试次后0.5秒: {len(post_spikes)} spikes")
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    # 分析test2目录中的HDF5文件
    test2_h5 = Path("test2/data/processed/FC_Grating_012.h5")
    if test2_h5.exists():
        analyze_time_alignment_issue(test2_h5)
        analyze_spike_distribution(test2_h5)
    else:
        print(f"文件不存在: {test2_h5}")
