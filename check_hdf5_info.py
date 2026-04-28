"""
检查HDF5文件中的trial数量和channel数量
"""

import h5py
import numpy as np
from pathlib import Path

def check_hdf5_info(hdf5_file):
    """
    检查HDF5文件中的trial数量和channel数量
    
    Args:
        hdf5_file: HDF5文件路径
    """
    try:
        with h5py.File(hdf5_file, 'r') as f:
            print(f"\n=== 检查文件: {hdf5_file} ===")
            
            # 检查元数据
            if 'metadata' in f:
                metadata = f['metadata']
                num_channels = metadata.attrs.get('num_channels', 'N/A')
                print(f"通道数: {num_channels}")
            else:
                print("通道数: N/A (未找到metadata)")
            
            # 检查行为数据中的trial数量
            if 'behavior' in f and 'trials' in f['behavior']:
                trials = f['behavior']['trials']
                num_trials = trials.shape[0]
                print(f"试次数: {num_trials}")
            else:
                print("试次数: N/A (未找到behavior/trials)")
            
            # 检查spike数据
            if 'spikes' in f:
                spikes = f['spikes']
                if 'spike_elec_ids' in spikes:
                    spike_elec_ids = spikes['spike_elec_ids'][:]
                    unique_elec_ids = np.unique(spike_elec_ids)
                    print(f"Spike通道数: {len(unique_elec_ids)}")
                else:
                    print("Spike通道数: N/A (未找到spike_elec_ids)")
            else:
                print("Spike通道数: N/A (未找到spikes)")
                
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    # 检查test1目录中的HDF5文件
    test1_dir = Path("test1/data/processed")
    if test1_dir.exists():
        print("=== 检查test1目录中的HDF5文件 ===")
        h5_files = list(test1_dir.glob("*.h5"))
        for h5_file in h5_files[:5]:  # 只检查前5个文件
            check_hdf5_info(h5_file)
    
    # 检查test2目录中的HDF5文件
    test2_dir = Path("test2/data/processed")
    if test2_dir.exists():
        print("\n=== 检查test2目录中的HDF5文件 ===")
        h5_files = list(test2_dir.glob("*.h5"))
        for h5_file in h5_files:
            check_hdf5_info(h5_file)
