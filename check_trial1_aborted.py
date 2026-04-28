"""
检查试次1是否是abort的
"""

import h5py
from pathlib import Path

def check_trial1_aborted(hdf5_file):
    """
    检查试次1是否是abort的
    
    Args:
        hdf5_file: HDF5文件路径
    """
    try:
        with h5py.File(hdf5_file, 'r') as f:
            print(f"\n=== 检查文件: {hdf5_file} ===")
            
            # 检查试次信息
            if 'behavior' in f and 'trials' in f['behavior']:
                trials = f['behavior']['trials']
                print(f"试次数: {trials.shape[0]}")
                
                # 检查试次1的信息
                if trials.shape[0] > 0:
                    trial1 = trials[0]
                    print("\n试次1的信息:")
                    
                    # 打印试次1的所有属性
                    print(f"  trial_num: {trial1['trial_num']}")
                    print(f"  start_time: {trial1['start_time']:.3f}")
                    print(f"  end_time: {trial1['end_time']:.3f}")
                    print(f"  stim_cnd: {trial1['stim_cnd']}")
                    
                    # 检查aborted属性
                    if 'aborted' in trial1.dtype.names:
                        print(f"  aborted: {trial1['aborted']}")
                    else:
                        print("  aborted: 未找到此属性")
                        
                    # 检查其他可能的属性
                    print("\n试次1的所有属性:")
                    for name in trial1.dtype.names:
                        print(f"  {name}: {trial1[name]}")
                else:
                    print("没有试次数据")
            else:
                print("未找到behavior/trials")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    # 检查test2目录中的HDF5文件
    test2_h5 = Path("test2/data/processed/FC_Grating_012.h5")
    if test2_h5.exists():
        check_trial1_aborted(test2_h5)
    else:
        print(f"文件不存在: {test2_h5}")
