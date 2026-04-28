import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.data.hdf5_reader import HDF5Reader
import numpy as np

hdf5_file = r"c:\Users\Administrator\Desktop\new hope\code\NeuroPrime\test2\data\processed\FC_Grating_012.h5"

print("=" * 60)
print("HDF5 数据检查")
print("=" * 60)

with HDF5Reader(hdf5_file) as reader:
    print("\n【1. 元数据】")
    metadata = reader.get_metadata()
    print(f"   试验名称: {metadata.get('trial_name', 'Unknown')}")
    print(f"   采样率: {metadata.get('sampling_rate', 0)} Hz")
    print(f"   持续时间: {metadata.get('duration', 0)} 秒")
    print(f"   通道数: {metadata.get('num_channels', 0)}")

    print("\n【2. LFP数据】")
    if 'signals/lfp_data' in reader.file:
        lfp_shape = reader.file['signals/lfp_data'].shape
        print(f"   形状: {lfp_shape}")
        print(f"   维度: [通道数 × 样本数]")
        print(f"   通道数: {lfp_shape[0]}")
        print(f"   样本数: {lfp_shape[1]}")

    print("\n【3. Spike数据】")
    spike_times = reader.get_spike_times()
    print(f"   Spike总数: {len(spike_times)}")
    print(f"   时间范围: {spike_times.min():.3f} 秒 ~ {spike_times.max():.3f} 秒")
    print(f"   时间跨度: {spike_times.max() - spike_times.min():.3f} 秒")

    print("\n【4. 试次信息】")
    trials = reader.get_trials()
    print(f"   试次总数: {len(trials)}")

    if len(trials) > 0:
        print("\n   所有试次的start_time:")
        for i, trial in enumerate(trials):
            print(f"   试次{i+1}: start_time={trial['start_time']:.3f}s, "
                  f"end_time={trial['end_time']:.3f}s, "
                  f"stim_cnd={trial['stim_cnd']}, "
                  f"aborted={trial['aborted']}")

        print("\n   试次时间分析:")
        trial_start_times = [t['start_time'] for t in trials]
        print(f"   试次start_time范围: {min(trial_start_times):.3f}s ~ {max(trial_start_times):.3f}s")

        print("\n   每个试次后的Spike数量 (刺激后500ms内):")
        for i, trial in enumerate(trials[:10]):
            start = trial['start_time']
            end = start + 0.5
            count = np.sum((spike_times >= start) & (spike_times <= end))
            print(f"   试次{i+1}: {count} 个Spike")

print("\n" + "=" * 60)
input("\n按回车键退出...")
