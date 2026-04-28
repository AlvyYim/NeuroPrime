import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.parsers.nev_parser import NEVParser, NEVDigitalEvent
import numpy as np

# 创建一个模拟的NEVParser实例进行测试
class MockNEVParser:
    def __init__(self):
        self.digital_events = []
        self.trials = []
    
    def _parse_trials(self):
        """解析试次信息"""
        # 从数字事件中提取试次信息
        pause_off_events = [e for e in self.digital_events if e.event_type == "PAUSEOFF"]
        pause_on_events = [e for e in self.digital_events if e.event_type == "PAUSEON"]
        stim_cnd_events = [e for e in self.digital_events if e.event_type == "STIMCND"]
        abort_events = [e for e in self.digital_events if e.event_type == "ABORT"]
        
        # 按时间排序
        pause_off_events.sort(key=lambda x: x.timestamp)
        pause_on_events.sort(key=lambda x: x.timestamp)
        abort_events.sort(key=lambda x: x.timestamp)
        
        # 创建试次
        num_trials = min(len(pause_off_events), len(pause_on_events))
        
        # 按LoadSpike.m逻辑处理abort事件：按顺序关联
        abort_index = 0
        abort_count = len(abort_events)
        
        for i in range(num_trials):
            # 确保开始时间小于结束时间
            start_time = pause_off_events[i].timestamp
            end_time = pause_on_events[i].timestamp
            
            # 如果开始时间大于结束时间，交换它们
            if start_time > end_time:
                start_time, end_time = end_time, start_time
            
            # 模拟NEVTrialInfo
            trial = {
                'trial_num': i + 1,
                'start_time': start_time,
                'end_time': end_time,
                'stim_cnd': stim_cnd_events[i].value if i < len(stim_cnd_events) else -1,
                'abort_time': None
            }
            
            # 按LoadSpike.m逻辑：按顺序关联abort事件
            if abort_index < abort_count:
                trial['abort_time'] = abort_events[abort_index].timestamp
                abort_index += 1
            
            self.trials.append(trial)

# 测试用例
def test_abort_event_processing():
    print("=" * 60)
    print("测试abort事件处理")
    print("=" * 60)
    
    # 创建测试事件
    parser = MockNEVParser()
    
    # 添加PAUSEOFF事件（试次开始）
    parser.digital_events.append(NEVDigitalEvent(timestamp=1.0, event_type="PAUSEOFF", value=0))
    parser.digital_events.append(NEVDigitalEvent(timestamp=3.0, event_type="PAUSEOFF", value=0))
    parser.digital_events.append(NEVDigitalEvent(timestamp=5.0, event_type="PAUSEOFF", value=0))
    
    # 添加ABORT事件
    parser.digital_events.append(NEVDigitalEvent(timestamp=2.0, event_type="ABORT", value=0))
    parser.digital_events.append(NEVDigitalEvent(timestamp=6.0, event_type="ABORT", value=0))
    
    # 添加PAUSEON事件（试次结束）
    parser.digital_events.append(NEVDigitalEvent(timestamp=4.0, event_type="PAUSEON", value=0))
    parser.digital_events.append(NEVDigitalEvent(timestamp=7.0, event_type="PAUSEON", value=0))
    parser.digital_events.append(NEVDigitalEvent(timestamp=9.0, event_type="PAUSEON", value=0))
    
    # 添加STIMCND事件
    parser.digital_events.append(NEVDigitalEvent(timestamp=1.5, event_type="STIMCND", value=1))
    parser.digital_events.append(NEVDigitalEvent(timestamp=3.5, event_type="STIMCND", value=2))
    parser.digital_events.append(NEVDigitalEvent(timestamp=5.5, event_type="STIMCND", value=3))
    
    # 解析试次
    parser._parse_trials()
    
    # 打印结果
    print("\n解析结果：")
    for i, trial in enumerate(parser.trials):
        print(f"试次{i+1}: start={trial['start_time']:.1f}, end={trial['end_time']:.1f}, "
              f"stim_cnd={trial['stim_cnd']}, abort_time={trial['abort_time']}")
    
    # 验证结果
    expected_abort_times = [2.0, 6.0, None]
    actual_abort_times = [trial['abort_time'] for trial in parser.trials]
    
    print(f"\n预期abort时间: {expected_abort_times}")
    print(f"实际abort时间: {actual_abort_times}")
    
    if actual_abort_times == expected_abort_times:
        print("\n✅ 测试通过：abort事件处理正确")
    else:
        print("\n❌ 测试失败：abort事件处理不正确")

if __name__ == "__main__":
    test_abort_event_processing()
    input("\n按回车键退出...")
