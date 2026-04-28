"""
调试TTL时间计算，找出为什么TTL时间都是0.000秒
"""

import numpy as np
from src.parsers.nev_parser import parse_nev

def debug_ttl_time(nev_file):
    """
    调试TTL时间计算，找出为什么TTL时间都是0.000秒
    
    Args:
        nev_file: NEV文件路径
    """
    print(f"\n=== 调试TTL时间计算: {nev_file} ===")
    
    # 解析NEV文件
    result = parse_nev(nev_file)
    
    if not result:
        print("解析失败")
        return
    
    # 提取Spike事件和数字事件
    spike_events = result['spike_events']
    digital_events = result['digital_events']
    trials = result['trials']
    
    print(f"\n共 {len(spike_events)} 个Spike事件")
    print(f"共 {len(digital_events)} 个数字事件")
    print(f"共 {len(trials)} 个试次")
    
    # 检查数字事件类型
    print("\n数字事件类型:")
    event_types = {}  # type: ignore
    for event in digital_events:
        if event.event_type not in event_types:
            event_types[event.event_type] = 0
        event_types[event.event_type] += 1
    
    for event_type, count in event_types.items():
        print(f"  {event_type}: {count}")
    
    # 检查是否有TTL事件（elec_id=129）
    print("\n检查TTL事件:")
    ttl_events = [e for e in digital_events if e.event_type == "TTL"]
    print(f"  TTL事件数量: {len(ttl_events)}")
    
    # 检查PAUSEOFF和PAUSEON事件
    print("\n检查PAUSEOFF和PAUSEON事件:")
    pause_off_events = [e for e in digital_events if e.event_type == "PAUSEOFF"]
    pause_on_events = [e for e in digital_events if e.event_type == "PAUSEON"]
    print(f"  PAUSEOFF事件数量: {len(pause_off_events)}")
    print(f"  PAUSEON事件数量: {len(pause_on_events)}")
    
    # 打印前几个PAUSEOFF和PAUSEON事件
    print("\n前5个PAUSEOFF事件:")
    for i, event in enumerate(pause_off_events[:5]):
        print(f"  {i+1}: {event.timestamp:.3f}秒")
    
    print("\n前5个PAUSEON事件:")
    for i, event in enumerate(pause_on_events[:5]):
        print(f"  {i+1}: {event.timestamp:.3f}秒")
    
    # 检查试次的TTL时间
    print("\n试次TTL时间:")
    print("-" * 50)
    print(f"{'试次':<5} {'TTL时间':<12} {'开始时间':<12} {'结束时间':<12}")
    print("-" * 50)
    
    for trial in trials[:10]:
        print(f"{trial.trial_num:<5} {trial.ttl_time:<12.3f} {trial.start_time:<12.3f} {trial.end_time:<12.3f}")
    
    print("-" * 50)

if __name__ == '__main__':
    # 分析test2目录中的NEV文件
    test2_nev = "test2/data/raw/FC_Grating_012.nev"
    debug_ttl_time(test2_nev)
