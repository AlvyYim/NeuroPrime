"""
检查HDF5文件结构，验证Spike时间和试次时间的存储方式
"""

import h5py
import numpy as np
from pathlib import Path

def check_hdf5_structure(hdf5_path):
    """
    检查HDF5文件结构，验证Spike时间和试次时间的存储方式
    
    Args:
        hdf5_path: HDF5文件路径
    """
    print(f"\n=== 检查HDF5文件结构: {hdf5_path} ===")
    
    try:
        with h5py.File(str(hdf5_path), 'r') as f:
            # 打印文件结构
            print("\n文件结构:")
            def print_structure(name, obj):
                if isinstance(obj, h5py.Group):
                    print(f"Group: {name}")
                elif isinstance(obj, h5py.Dataset):
                    print(f"Dataset: {name}, shape: {obj.shape}, dtype: {obj.dtype}")
                    
                    # 打印前几个数据点
                    if obj.shape[0] > 0:
                        if obj.ndim == 1 and obj.shape[0] > 5:
                            print(f"  First 5 values: {obj[:5]}")
                        elif obj.ndim == 2 and obj.shape[0] > 0:
                            print(f"  First row: {obj[0, :5]}")
            
            f.visititems(print_structure)
            
            # 检查Spike时间
            if '/spikes/spike_times' in f:
                spike_times = f['/spikes/spike_times'][:]
                print(f"\nSpike时间信息:")
                print(f"  数量: {len(spike_times)}")
                print(f"  时间范围: {spike_times.min():.3f} - {spike_times.max():.3f} 秒")
                print(f"  前5个时间: {spike_times[:5]}")
                print(f"  后5个时间: {spike_times[-5:]}")
            
            # 检查试次信息
            if 'behavior/trials' in f:
                trials = f['behavior/trials'][:]
                print(f"\n试次信息:")
                print(f"  试次数: {len(trials)}")
                print(f"  字段: {trials.dtype.names}")
                
                if len(trials) > 0:
                    print(f"\n第一个试次:")
                    for field in trials.dtype.names:
                        print(f"  {field}: {trials[0][field]}")
                    
                    print(f"\n最后一个试次:")
                    for field in trials.dtype.names:
                        print(f"  {field}: {trials[-1][field]}")
                    
                    # 检查试次时间范围
                    if 'start_time' in trials.dtype.names:
                        start_times = trials['start_time']
                        end_times = trials['end_time'] if 'end_time' in trials.dtype.names else start_times + 1.0
                        print(f"\n试次时间范围:")
                        print(f"  开始时间: {start_times.min():.3f} - {start_times.max():.3f} 秒")
                        print(f"  结束时间: {end_times.min():.3f} - {end_times.max():.3f} 秒")
            
            # 检查metadata
            if 'metadata' in f:
                metadata = f['metadata']
                print(f"\nMetadata:")
                for key in metadata.keys():
                    if isinstance(metadata[key], h5py.Dataset):
                        value = metadata[key][()]
                        print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"检查HDF5文件失败: {e}")

if __name__ == '__main__':
    # 检查test2目录中的HDF5文件
    test2_hdf5 = "test2/data/processed/FC_Grating_012.h5"
    check_hdf5_structure(test2_hdf5)
