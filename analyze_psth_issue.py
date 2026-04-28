"""
分析PSTH分析中刺激前spike比刺激后多的原因
"""

import h5py
import numpy as np
from pathlib import Path

def analyze_hdf5_data(hdf5_file):
    """
    分析HDF5文件中的数据，包括试次信息和Spike数据
    
    Args:
        hdf5_file: HDF5文件路径
    """
    try:
        with h5py.File(hdf5_file, 'r') as f:
            print(f"\n=== 分析文件: {hdf5_file} ===")
            
            # 检查试次信息
            if 'behavior' in f and 'trials' in f['behavior']:
                trials = f['behavior']['trials']
                print(f"试次数: {trials.shape[0]}")
                
                # 打印前几个试次的信息
                print("\n前5个试次的信息:")
                for i in range(min(5, trials.shape[0])):
                    trial = trials[i]
                    print(f"试次 {i+1}: start_time={trial['start_time']:.3f}, end_time={trial['end_time']:.3f}, stim_cnd={trial['stim_cnd']}, aborted={trial['aborted']}")
            
            # 检查Spike数据
            if 'spikes' in f:
                spikes = f['spikes']
                if 'spike_times' in spikes:
                    spike_times = spikes['spike_times'][:]
                    print(f"\nSpike总数: {len(spike_times)}")
                    print(f"Spike时间范围: {spike_times.min():.3f} - {spike_times.max():.3f}")
                
                if 'spike_elec_ids' in spikes:
                    spike_elec_ids = spikes['spike_elec_ids'][:]
                    unique_elec_ids = np.unique(spike_elec_ids)
                    print(f"Spike通道数: {len(unique_elec_ids)}")
            
            # 检查元数据
            if 'metadata' in f:
                metadata = f['metadata']
                print(f"\n元数据:")
                print(f"采样率: {metadata.attrs.get('sampling_rate', 'N/A')}")
                print(f"记录时长: {metadata.attrs.get('duration', 'N/A')}")
                print(f"通道数: {metadata.attrs.get('num_channels', 'N/A')}")
                
                if 'source_files' in metadata:
                    source_files = metadata['source_files']
                    print("源文件:")
                    for key in source_files.attrs:
                        print(f"  {key}: {source_files.attrs[key]}")
            
    except Exception as e:
        print(f"错误: {e}")

def analyze_time_alignment():
    """
    分析时间对齐的操作流程
    """
    print("\n=== 时间对齐操作流程 ===")
    print("1. 时间对齐的目的: 确保不同数据类型（如LFP、Spike、行为数据）之间的时间戳一致")
    print("2. 时间对齐的操作步骤:")
    print("   a. 提取各数据类型的时间戳")
    print("   b. 确定一个参考时间点（通常是第一个刺激事件）")
    print("   c. 计算各数据类型相对于参考时间点的偏移量")
    print("   d. 应用偏移量调整所有时间戳")
    print("3. 可能的时间对齐错误:")
    print("   a. 参考时间点选择错误")
    print("   b. 偏移量计算错误")
    print("   c. 不同数据类型的时间基准不一致")
    print("4. 检查时间对齐的方法:")
    print("   a. 比较刺激事件前后的Spike分布")
    print("   b. 检查试次开始时间与Spike时间的关系")
    print("   c. 验证不同数据类型之间的时间一致性")

if __name__ == "__main__":
    # 分析test2目录中的HDF5文件
    test2_h5 = Path("test2/data/processed/FC_Grating_012.h5")
    if test2_h5.exists():
        analyze_hdf5_data(test2_h5)
    
    # 分析时间对齐操作
    analyze_time_alignment()
