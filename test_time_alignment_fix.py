"""
测试时间对齐修复
"""

import h5py
import numpy as np
from pathlib import Path

def test_time_alignment_fix(hdf5_file):
    """
    测试时间对齐修复，检查PSTH分析中刺激前spike是否不再比刺激后的多
    
    Args:
        hdf5_file: HDF5文件路径
    """
    try:
        with h5py.File(hdf5_file, 'r') as f:
            print(f"\n=== 测试文件: {hdf5_file} ===")
            
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
    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    # 测试test2目录中的HDF5文件
    test2_h5 = Path("test2/data/processed/FC_Grating_012.h5")
    if test2_h5.exists():
        test_time_alignment_fix(test2_h5)
    else:
        print(f"文件不存在: {test2_h5}")
