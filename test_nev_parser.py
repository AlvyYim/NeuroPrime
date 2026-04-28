import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.parsers.nev_parser import NEVParser

def test_nev_parser():
    print("=" * 60)
    print("测试NEV解析器")
    print("=" * 60)
    
    # 测试文件路径
    # 请替换为实际的NEV文件路径
    nev_file = r"c:\Users\Administrator\Desktop\new hope\code\NeuroPrime\test2\data\raw\FC_Grating_012.nev"
    
    if not Path(nev_file).exists():
        print(f"NEV文件不存在: {nev_file}")
        return
    
    print(f"解析NEV文件: {nev_file}")
    
    # 创建解析器并解析文件
    parser = NEVParser(nev_file)
    
    if parser.parse():
        print("\n解析成功！")
        
        # 显示基本信息
        print(f"\n基本信息:")
        print(f"  事件数: {len(parser.spike_events)}")
        print(f"  数字事件数: {len(parser.digital_events)}")
        print(f"  试次数: {len(parser.trials)}")
        
        # 显示MBM信息
        if parser.valid_mbm:
            print(f"\nMBM信息:")
            print(f"  试次数: {parser.mbm_info.nTrials}")
            print(f"  刺激条件: {parser.mbm_info.StimID[:5]}...")
            print(f"  响应代码: {parser.mbm_info.RespCode[:5]}...")
        else:
            print("\n未找到MBM文件或解析失败")
        
        # 显示试次信息
        print(f"\n试次信息 (前5个):")
        for i, trial in enumerate(parser.trials[:5]):
            print(f"  试次{i+1}:")
            print(f"    start_time: {trial.start_time:.3f}s")
            print(f"    end_time: {trial.end_time:.3f}s")
            print(f"    stim_cnd: {trial.stim_cnd}")
            print(f"    abort_time: {trial.abort_time}")
            print(f"    ttl_time: {trial.ttl_time}")
        
        # 显示数字事件信息
        print(f"\n数字事件 (前10个):")
        for i, event in enumerate(parser.digital_events[:10]):
            print(f"  事件{i+1}: {event.event_type} at {event.timestamp:.3f}s, value={event.value}")
        
    else:
        print("\n解析失败！")

if __name__ == "__main__":
    test_nev_parser()
    input("\n按回车键退出...")
