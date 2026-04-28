"""
重新生成HDF5文件，应用修复后的时间对齐逻辑
"""

import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data.hdf5_writer import convert_ns3_to_hdf5, convert_nev_to_hdf5

def regenerate_hdf5(ns3_file, nev_file, hdf5_file):
    """
    重新生成HDF5文件，应用修复后的时间对齐逻辑
    
    Args:
        ns3_file: NS3文件路径
        nev_file: NEV文件路径
        hdf5_file: 输出HDF5文件路径
    """
    print(f"\n=== 重新生成HDF5文件 ===")
    print(f"NS3文件: {ns3_file}")
    print(f"NEV文件: {nev_file}")
    print(f"HDF5文件: {hdf5_file}")
    
    # 1. 转换NS3文件
    print("\n1. 转换NS3文件...")
    if not convert_ns3_to_hdf5(ns3_file, hdf5_file, experiment_name="Test Experiment"):
        print("NS3转换失败！")
        return False
    
    # 2. 添加NEV数据
    print("\n2. 添加NEV数据...")
    if not convert_nev_to_hdf5(nev_file, hdf5_file):
        print("NEV转换失败！")
        return False
    
    print("\n✅ HDF5文件重新生成成功！")
    return True

if __name__ == '__main__':
    # 测试文件路径
    test2_ns3 = "test2/data/raw/FC_Grating_012.ns3"
    test2_nev = "test2/data/raw/FC_Grating_012.nev"
    test2_hdf5 = "test2/data/processed/FC_Grating_012.h5"
    
    # 重新生成HDF5文件
    regenerate_hdf5(test2_ns3, test2_nev, test2_hdf5)
