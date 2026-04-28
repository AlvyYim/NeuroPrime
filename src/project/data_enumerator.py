"""
Data Enumerator - 数据枚举器

枚举工程中所有可用的数据项，提供统一的数据访问接口
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.hdf5_reader import HDF5Reader


@dataclass
class DataItem:
    """数据项信息"""
    trial_name: str
    data_type: str  # 'lfp', 'spike', 'behavior', 'trial'
    name: str
    description: str
    time_range: Tuple[float, float]  # (start, end) in seconds
    shape: Optional[Tuple] = None
    unit: str = ""
    sampling_rate: float = 0.0
    
    def get_duration(self) -> float:
        """获取数据持续时间"""
        return self.time_range[1] - self.time_range[0]


@dataclass
class TrialDataSummary:
    """试验数据摘要"""
    trial_name: str
    experiment_name: str
    duration: float
    num_channels: int
    sampling_rate: float
    num_spikes: int
    num_trials: int
    has_lfp: bool
    has_spike: bool
    has_behavior: bool


class DataEnumerator:
    """
    数据枚举器
    
    提供工程中所有可用数据项的枚举和查询功能：
    - 枚举所有试验的数据项
    - 获取数据时间范围
    - 查询特定类型的数据
    - 提供数据摘要信息
    
    用法:
        enumerator = DataEnumerator(project_manager)
        
        # 获取所有数据项
        all_items = enumerator.enumerate_all_data()
        
        # 获取特定试验的数据项
        trial_items = enumerator.get_trial_data_items("FC_Grating_014")
        
        # 获取数据摘要
        summary = enumerator.get_data_summary("FC_Grating_014")
    """
    
    def __init__(self, project_manager):
        """
        初始化数据枚举器
        
        Args:
            project_manager: ProjectManager实例
        """
        self.project_manager = project_manager
        self._cache: Dict[str, Any] = {}  # 缓存数据
    
    def enumerate_all_data(self) -> List[DataItem]:
        """
        枚举工程中的所有数据项
        
        Returns:
            数据项列表
        """
        all_items = []
        
        if not self.project_manager.is_project_opened():
            return all_items
        
        # 遍历所有试验
        for trial_name in self.project_manager.get_trial_names():
            items = self.get_trial_data_items(trial_name)
            all_items.extend(items)
        
        return all_items
    
    def get_trial_data_items(self, trial_name: str) -> List[DataItem]:
        """
        获取特定试验的所有数据项
        
        Args:
            trial_name: 试验名称
            
        Returns:
            数据项列表
        """
        items = []
        
        # 获取HDF5文件路径
        hdf5_path = self.project_manager.get_hdf5_path(trial_name)
        if hdf5_path is None or not hdf5_path.exists():
            return items
        
        try:
            with HDF5Reader(str(hdf5_path)) as reader:
                metadata = reader.get_metadata()
                duration = metadata.get('duration', 0.0)
                sampling_rate = metadata.get('sampling_rate', 0.0)
                
                # LFP数据项
                if 'signals/lfp_data' in reader.file:
                    lfp_shape = reader.file['signals/lfp_data'].shape
                    items.append(DataItem(
                        trial_name=trial_name,
                        data_type='lfp',
                        name=f"{trial_name}_LFP",
                        description="Local Field Potential",
                        time_range=(0.0, duration),
                        shape=lfp_shape,
                        unit='uV',
                        sampling_rate=sampling_rate
                    ))
                
                # Spike数据项
                if 'spikes/spike_times' in reader.file:
                    num_spikes = len(reader.file['spikes/spike_times'])
                    items.append(DataItem(
                        trial_name=trial_name,
                        data_type='spike',
                        name=f"{trial_name}_Spikes",
                        description=f"Spike events ({num_spikes} spikes)",
                        time_range=(0.0, duration),
                        shape=(num_spikes,),
                        unit='uV',
                        sampling_rate=30000.0  # Spike波形采样率
                    ))
                
                # 试次数据项
                if 'behavior/trials' in reader.file:
                    num_trials = len(reader.file['behavior/trials'])
                    items.append(DataItem(
                        trial_name=trial_name,
                        data_type='trial',
                        name=f"{trial_name}_Trials",
                        description=f"Trial information ({num_trials} trials)",
                        time_range=(0.0, duration),
                        shape=(num_trials,),
                        unit='',
                        sampling_rate=0.0
                    ))
                
                # 事件数据项
                if 'behavior/events' in reader.file:
                    num_events = len(reader.file['behavior/events'])
                    items.append(DataItem(
                        trial_name=trial_name,
                        data_type='behavior',
                        name=f"{trial_name}_Events",
                        description=f"Behavioral events ({num_events} events)",
                        time_range=(0.0, duration),
                        shape=(num_events,),
                        unit='',
                        sampling_rate=0.0
                    ))
        
        except Exception as e:
            print(f"Error reading HDF5 file for trial '{trial_name}': {e}")
        
        return items
    
    def get_data_items_by_type(self, data_type: str) -> List[DataItem]:
        """
        获取特定类型的所有数据项
        
        Args:
            data_type: 数据类型 ('lfp', 'spike', 'behavior', 'trial')
            
        Returns:
            数据项列表
        """
        all_items = self.enumerate_all_data()
        return [item for item in all_items if item.data_type == data_type]
    
    def get_data_summary(self, trial_name: str) -> Optional[TrialDataSummary]:
        """
        获取试验数据摘要
        
        Args:
            trial_name: 试验名称
            
        Returns:
            TrialDataSummary对象，未找到返回None
        """
        trial_info = self.project_manager.get_trial(trial_name)
        if trial_info is None:
            return None
        
        # 获取HDF5文件路径
        hdf5_path = self.project_manager.get_hdf5_path(trial_name)
        if hdf5_path is None or not hdf5_path.exists():
            return TrialDataSummary(
                trial_name=trial_name,
                experiment_name=trial_info.experiment_name,
                duration=trial_info.duration,
                num_channels=trial_info.num_channels,
                sampling_rate=trial_info.sampling_rate,
                num_spikes=trial_info.num_spikes,
                num_trials=trial_info.num_trials,
                has_lfp=False,
                has_spike=False,
                has_behavior=False
            )
        
        try:
            with HDF5Reader(str(hdf5_path)) as reader:
                metadata = reader.get_metadata()
                
                has_lfp = 'signals/lfp_data' in reader.file
                has_spike = 'spikes/spike_times' in reader.file
                has_behavior = 'behavior/trials' in reader.file
                
                return TrialDataSummary(
                    trial_name=trial_name,
                    experiment_name=trial_info.experiment_name,
                    duration=metadata.get('duration', trial_info.duration),
                    num_channels=metadata.get('num_channels', trial_info.num_channels),
                    sampling_rate=metadata.get('sampling_rate', trial_info.sampling_rate),
                    num_spikes=len(reader.file['spikes/spike_times']) if has_spike else 0,
                    num_trials=len(reader.file['behavior/trials']) if has_behavior else 0,
                    has_lfp=has_lfp,
                    has_spike=has_spike,
                    has_behavior=has_behavior
                )
        
        except Exception as e:
            print(f"Error getting data summary for trial '{trial_name}': {e}")
            return None
    
    def get_all_data_summaries(self) -> List[TrialDataSummary]:
        """
        获取所有试验的数据摘要
        
        Returns:
            TrialDataSummary列表
        """
        summaries = []
        
        if not self.project_manager.is_project_opened():
            return summaries
        
        for trial_name in self.project_manager.get_trial_names():
            summary = self.get_data_summary(trial_name)
            if summary is not None:
                summaries.append(summary)
        
        return summaries
    
    def get_time_range(self, trial_name: str) -> Optional[Tuple[float, float]]:
        """
        获取试验数据的时间范围
        
        Args:
            trial_name: 试验名称
            
        Returns:
            (start_time, end_time)元组，单位秒
        """
        trial_info = self.project_manager.get_trial(trial_name)
        if trial_info is None:
            return None
        
        return (0.0, trial_info.duration)
    
    def get_common_time_range(self, trial_names: List[str]) -> Optional[Tuple[float, float]]:
        """
        获取多个试验的共同时间范围
        
        Args:
            trial_names: 试验名称列表
            
        Returns:
            (start_time, end_time)元组，单位秒
        """
        if not trial_names:
            return None
        
        min_duration = float('inf')
        
        for trial_name in trial_names:
            time_range = self.get_time_range(trial_name)
            if time_range is None:
                return None
            min_duration = min(min_duration, time_range[1])
        
        return (0.0, min_duration)
    
    def check_data_compatibility(self, trial_names: List[str]) -> Dict[str, Any]:
        """
        检查多个试验数据的兼容性
        
        Args:
            trial_names: 试验名称列表
            
        Returns:
            兼容性检查结果
        """
        result = {
            'compatible': True,
            'issues': [],
            'common_sampling_rate': None,
            'common_channels': None,
            'min_duration': None
        }
        
        if len(trial_names) < 2:
            return result
        
        sampling_rates = set()
        channel_counts = set()
        durations = []
        
        for trial_name in trial_names:
            summary = self.get_data_summary(trial_name)
            if summary is None:
                result['compatible'] = False
                result['issues'].append(f"Trial '{trial_name}' not found")
                continue
            
            sampling_rates.add(summary.sampling_rate)
            channel_counts.add(summary.num_channels)
            durations.append(summary.duration)
        
        # 检查采样率一致性
        if len(sampling_rates) > 1:
            result['issues'].append(f"Inconsistent sampling rates: {sampling_rates}")
        else:
            result['common_sampling_rate'] = sampling_rates.pop() if sampling_rates else None
        
        # 检查通道数一致性
        if len(channel_counts) > 1:
            result['issues'].append(f"Inconsistent channel counts: {channel_counts}")
        else:
            result['common_channels'] = channel_counts.pop() if channel_counts else None
        
        # 获取最小持续时间
        if durations:
            result['min_duration'] = min(durations)
        
        result['compatible'] = len(result['issues']) == 0
        
        return result
    
    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()


if __name__ == '__main__':
    # 测试代码
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    from project_manager import ProjectManager
    
    print("=== Testing DataEnumerator ===\n")
    
    # 使用已有的测试工程
    project_path = Path(r"c:\Users\buaal\Desktop\NeuroPrime\TestProject")
    
    # 创建工程管理器并打开工程
    manager = ProjectManager()
    
    # 如果没有测试工程，先创建一个
    if not project_path.exists():
        print("Creating test project...")
        manager.create_project(project_path, "TestProject", "Test project for DataEnumerator")
        
        # 添加试验信息
        from project_manager import TrialInfo
        trial = TrialInfo(
            name="FC_Grating_014",
            experiment_name="FC_Grating",
            creation_time=datetime.now().isoformat(),
            hdf5_file="FC_Grating_014.h5",
            duration=84.812,
            num_channels=101,
            sampling_rate=2000.0,
            num_trials=61,
            num_spikes=150496
        )
        manager.add_trial(trial)
    else:
        manager.open_project(project_path)
    
    if manager.is_project_opened():
        # 创建数据枚举器
        enumerator = DataEnumerator(manager)
        
        # 测试获取所有数据项
        print("1. All data items:")
        all_items = enumerator.enumerate_all_data()
        for item in all_items:
            print(f"   - {item.name}: {item.data_type}, "
                  f"{item.time_range[1]:.2f}s, shape={item.shape}")
        print()
        
        # 测试按类型获取数据项
        print("2. LFP data items:")
        lfp_items = enumerator.get_data_items_by_type('lfp')
        for item in lfp_items:
            print(f"   - {item.name}: {item.description}")
        print()
        
        # 测试获取数据摘要
        print("3. Data summaries:")
        summaries = enumerator.get_all_data_summaries()
        for summary in summaries:
            print(f"   - {summary.trial_name}:")
            print(f"     Duration: {summary.duration:.2f}s")
            print(f"     Channels: {summary.num_channels}")
            print(f"     Spikes: {summary.num_spikes}")
            print(f"     Has LFP: {summary.has_lfp}, Spike: {summary.has_spike}, Behavior: {summary.has_behavior}")
        print()
        
        # 测试获取时间范围
        print("4. Time ranges:")
        for trial_name in manager.get_trial_names():
            time_range = enumerator.get_time_range(trial_name)
            if time_range:
                print(f"   - {trial_name}: {time_range[0]:.2f}s - {time_range[1]:.2f}s")
        print()
        
        # 测试数据兼容性检查
        print("5. Data compatibility check:")
        trial_names = manager.get_trial_names()
        if len(trial_names) >= 1:
            compatibility = enumerator.check_data_compatibility(trial_names)
            print(f"   Compatible: {compatibility['compatible']}")
            print(f"   Common sampling rate: {compatibility['common_sampling_rate']}")
            print(f"   Common channels: {compatibility['common_channels']}")
            print(f"   Min duration: {compatibility['min_duration']}")
            if compatibility['issues']:
                print(f"   Issues: {compatibility['issues']}")
        print()
        
        print("✅ DataEnumerator tests completed!")
    else:
        print("❌ Failed to open project")
