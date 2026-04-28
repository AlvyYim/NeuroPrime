"""
测试PSTH分析，验证时间对齐修复是否成功
"""

import numpy as np
from src.parsers.nev_parser import parse_nev
from src.algorithms.spike_analysis import PSTHAnalysis
from src.algorithms.base import AlgorithmInput

def test_psth_analysis(nev_file):
    """
    测试PSTH分析，验证时间对齐修复是否成功
    
    Args:
        nev_file: NEV文件路径
    """
    print(f"\n=== 测试PSTH分析: {nev_file} ===")
    
    # 解析NEV文件
    result = parse_nev(nev_file)
    
    if not result:
        print("解析失败")
        return
    
    # 提取Spike时间和试次信息
    spike_events = result['spike_events']
    trials = result['trials']
    
    if not spike_events or not trials:
        print("没有Spike事件或试次信息")
        return
    
    # 准备PSTH分析输入
    spike_times = np.array([e.timestamp for e in spike_events])
    
    # 转换试次信息为字典列表
    trial_info = []
    for trial in trials:
        trial_info.append({
            'trial_num': trial.trial_num,
            'start_time': trial.start_time,
            'end_time': trial.end_time,
            'stim_cnd': trial.stim_cnd,
            'aborted': trial.abort_time is not None
        })
    
    input_data = AlgorithmInput(
        spike_times=spike_times,
        trial_info=trial_info
    )
    
    # 运行PSTH分析
    psth_analyzer = PSTHAnalysis()
    params = psth_analyzer.get_default_parameters()
    
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
            print("\n✅ 时间对齐修复成功！刺激后Spike数量大于刺激前")
        else:
            print("\n❌ 时间对齐修复失败！刺激前Spike数量仍然大于刺激后")
    else:
        print(f"PSTH分析失败: {output.error_message}")

if __name__ == '__main__':
    # 测试test2目录中的NEV文件
    test2_nev = "test2/data/raw/FC_Grating_012.nev"
    test_psth_analysis(test2_nev)
