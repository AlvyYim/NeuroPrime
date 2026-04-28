#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PSTH分析修复是否有效
"""

import h5py
import numpy as np
from src.algorithms.spike_analysis import PSTHAnalysis
from src.algorithms.base import AlgorithmInput

def test_psth_fix(hdf5_file):
    """
    测试PSTH分析修复是否有效
    
    Args:
        hdf5_file: HDF5文件路径
    """
    print(f"\n=== 测试PSTH分析修复: {hdf5_file} ===")
    
    try:
        with h5py.File(hdf5_file, 'r') as f:
            # 加载Spike时间
            if 'spikes' in f and 'spike_times' in f['spikes']:
                spike_times = f['spikes']['spike_times'][:]
                print(f"Spike总数: {len(spike_times)}")
                print(f"Spike时间范围: {spike_times.min():.3f} - {spike_times.max():.3f} 秒")
            else:
                print("未找到Spike数据")
                return
            
            # 加载试次信息
            if 'behavior' in f and 'trials' in f['behavior']:
                trials = f['behavior']['trials'][:]
                print(f"试次数: {len(trials)}")
                
                # 转换试次信息为字典列表
                trial_info = []
                for i, trial in enumerate(trials):
                    trial_dict = {
                        'trial_num': int(trial['trial_num']) if 'trial_num' in trial.dtype.names else i + 1,
                        'start_time': float(trial['start_time']) if 'start_time' in trial.dtype.names else 0,
                        'end_time': float(trial['end_time']) if 'end_time' in trial.dtype.names else 0,
                        'stim_cnd': int(trial['stim_cnd']) if 'stim_cnd' in trial.dtype.names else 0,
                        'aborted': bool(trial['aborted']) if 'aborted' in trial.dtype.names else False
                    }
                    trial_info.append(trial_dict)
                
                print(f"第一个试次: start_time={trial_info[0]['start_time']:.3f}, end_time={trial_info[0]['end_time']:.3f}")
                print(f"最后一个试次: start_time={trial_info[-1]['start_time']:.3f}, end_time={trial_info[-1]['end_time']:.3f}")
            else:
                print("未找到试次信息")
                return
    except Exception as e:
        print(f"加载HDF5文件失败: {e}")
        return
    
    # 准备PSTH分析输入
    input_data = AlgorithmInput(
        spike_times=spike_times,
        trial_info=trial_info
    )
    
    # 运行PSTH分析
    psth_analyzer = PSTHAnalysis()
    params = psth_analyzer.get_default_parameters()
    
    print(f"\nPSTH分析参数:")
    print(f"  刺激前时间: {params['pre_time']} ms")
    print(f"  刺激后时间: {params['post_time']} ms")
    print(f"  时间窗大小: {params['bin_size']} ms")
    print(f"  高斯平滑系数: {params['smoothing_sigma']} ms")
    
    output = psth_analyzer.run(input_data, params)
    
    if output.success:
        print("\n=== PSTH分析结果 ===")
        print(f"基线发放率: {output.statistics['baseline_rate']:.2f} Hz")
        print(f"峰值发放率: {output.statistics['peak_rate']:.2f} Hz")
        print(f"峰值时间: {output.statistics['peak_time']:.3f} s")
        print(f"响应调制: {output.statistics['response_modulation']:.2f}")
        print(f"试次数: {output.statistics['n_trials']}")
        print(f"总Spike数: {output.statistics['n_spikes_total']}")
        
        # 分析刺激前和刺激后的Spike分布
        bin_centers = output.data['bin_centers']
        psth_counts = output.data['psth_counts']
        
        pre_stim_mask = bin_centers < 0
        post_stim_mask = bin_centers > 0
        
        pre_stim_spikes = np.sum(psth_counts[pre_stim_mask])
        post_stim_spikes = np.sum(psth_counts[post_stim_mask])
        
        print(f"\n刺激前Spike数量: {pre_stim_spikes}")
        print(f"刺激后Spike数量: {post_stim_spikes}")
        print(f"刺激前/刺激后Spike比例: {pre_stim_spikes / post_stim_spikes:.2f}")
        
        if pre_stim_spikes < post_stim_spikes:
            print("\n✅ PSTH分析修复成功！刺激后Spike数量大于刺激前")
        else:
            print("\n❌ PSTH分析修复失败！刺激前Spike数量仍然大于刺激后")
    else:
        print(f"PSTH分析失败: {output.error_message}")

if __name__ == '__main__':
    # 测试test2目录中的HDF5文件
    test2_hdf5 = "test2/data/processed/FC_Grating_012.h5"
    test_psth_fix(test2_hdf5)
