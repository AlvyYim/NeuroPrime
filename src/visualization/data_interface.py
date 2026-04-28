"""
Visualization Data Interface - 可视化数据统一接口

为所有可视化模块提供统一的数据访问接口
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.hdf5_reader import HDF5Reader


class VisualizationDataInterface:
    """
    可视化数据统一接口
    
    所有可视化模块通过此接口获取数据，提供：
    - 信号数据接口 (LFP等)
    - Spike数据接口
    - 行为数据接口
    - 分析数据接口 (PSTH, Raster等)
    """
    
    def __init__(self, hdf5_file_path: str):
        """
        初始化可视化数据接口
        
        Args:
            hdf5_file_path: HDF5文件路径
        """
        self.hdf5_file_path = Path(hdf5_file_path)
        self._reader: Optional[HDF5Reader] = None
        self._cache: Dict[str, Any] = {}
    
    def open(self) -> bool:
        """
        打开HDF5文件
        
        Returns:
            True if successful
        """
        try:
            self._reader = HDF5Reader(str(self.hdf5_file_path))
            return self._reader.open()
        except Exception as e:
            print(f"Error opening HDF5 file: {e}")
            return False
    
    def close(self):
        """关闭HDF5文件"""
        if self._reader:
            self._reader.close()
            self._reader = None
    
    def __enter__(self):
        """上下文管理器入口"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    # ========== 信号数据接口 ==========
    
    def get_lfp_signal(self, 
                       channel_ids: List[int],
                       time_range: Tuple[float, float]) -> np.ndarray:
        """
        获取LFP信号数据
        
        Args:
            channel_ids: 通道ID列表
            time_range: (开始时间, 结束时间)，单位秒
            
        Returns:
            信号数组 [通道数 × 样本数]
        """
        if self._reader is None:
            raise RuntimeError("HDF5 file not opened")
        
        return self._reader.get_lfp_data(time_range=time_range, channels=channel_ids)
    
    def get_signal_segment(self, 
                          channel_id: int,
                          trial_id: int,
                          pre_time: float = 0.5,
                          post_time: float = 1.0) -> np.ndarray:
        """
        获取指定试次的信号片段
        
        Args:
            channel_id: 通道ID
            trial_id: 试次ID (从1开始)
            pre_time: 试次开始前时间 (秒)
            post_time: 试次开始后时间 (秒)
            
        Returns:
            信号片段
        """
        if self._reader is None:
            raise RuntimeError("HDF5 file not opened")
        
        # 获取试次信息
        trials = self._reader.get_trials()
        if trial_id < 1 or trial_id > len(trials):
            raise ValueError(f"Invalid trial_id: {trial_id}")
        
        trial = trials[trial_id - 1]
        trial_start = trial['start_time']
        
        # 计算时间范围
        start_time = trial_start - pre_time
        end_time = trial_start + post_time
        
        return self._reader.get_lfp_data(
            time_range=(start_time, end_time),
            channels=[channel_id]
        )
    
    # ========== Spike数据接口 ==========
    
    def get_spike_times(self,
                       channel_ids: Optional[List[int]] = None,
                       unit_ids: Optional[List[int]] = None,
                       time_range: Optional[Tuple[float, float]] = None) -> Dict:
        """
        获取Spike时间戳
        
        Args:
            channel_ids: 通道ID筛选 (None=所有)
            unit_ids: 单元筛选 (None=所有)
            time_range: 时间范围筛选 (None=所有)
            
        Returns:
            {
                'times': np.ndarray,      # Spike时间戳
                'channels': np.ndarray,   # 对应通道
                'units': np.ndarray,      # 对应单元
            }
        """
        if self._reader is None:
            raise RuntimeError("HDF5 file not opened")
        
        # 获取所有Spike数据
        spike_times = np.array(self._reader.file['spikes/spike_times'])
        spike_channels = np.array(self._reader.file['spikes/spike_elec_ids'])
        
        # 获取单元信息（如果有）
        if 'spikes/spike_units' in self._reader.file:
            spike_units = np.array(self._reader.file['spikes/spike_units'])
        else:
            spike_units = np.zeros(len(spike_times), dtype=int)
        
        # 应用筛选
        mask = np.ones(len(spike_times), dtype=bool)
        
        if channel_ids is not None:
            mask &= np.isin(spike_channels, channel_ids)
        
        if unit_ids is not None:
            mask &= np.isin(spike_units, unit_ids)
        
        if time_range is not None:
            mask &= (spike_times >= time_range[0]) & (spike_times <= time_range[1])
        
        return {
            'times': spike_times[mask],
            'channels': spike_channels[mask],
            'units': spike_units[mask]
        }
    
    def get_spike_waveforms(self,
                           channel_id: Optional[int] = None) -> np.ndarray:
        """
        获取Spike波形
        
        Args:
            channel_id: 通道ID筛选 (None=所有)
            
        Returns:
            Spike波形数组 [事件数 × 样本数]
        """
        if self._reader is None:
            raise RuntimeError("HDF5 file not opened")
        
        return self._reader.get_spike_waveforms(elec_id=channel_id)
    
    def get_raster_data(self,
                       channel_id: int,
                       trial_ids: List[int],
                       time_window: Tuple[float, float] = (-0.5, 1.0),
                       align_event: str = 'trial_start') -> Dict:
        """
        获取栅格图数据
        
        Args:
            channel_id: 通道ID
            trial_ids: 试次ID列表
            time_window: 时间窗口 (相对对齐事件)
            align_event: 对齐事件 ('trial_start', 'stimulus_onset')
            
        Returns:
            {
                'spike_times': List[np.ndarray],  # 每个试次的Spike时间列表
                'trial_ids': List[int],           # 试次ID
                'channel_id': int,                # 通道ID
                'time_window': Tuple[float, float]  # 时间窗口
            }
        """
        if self._reader is None:
            raise RuntimeError("HDF5 file not opened")
        
        # 获取试次信息
        trials = self._reader.get_trials()
        
        # 获取该通道的所有Spike时间
        spike_data = self.get_spike_times(channel_ids=[channel_id])
        all_spike_times = spike_data['times']
        
        raster_spikes = []
        valid_trial_ids = []
        
        for trial_id in trial_ids:
            if trial_id < 1 or trial_id > len(trials):
                continue
            
            trial = trials[trial_id - 1]
            
            # 确定对齐时间
            if align_event == 'trial_start':
                align_time = trial['start_time']
            elif align_event == 'stimulus_onset':
                # 使用试次开始作为刺激开始时间
                align_time = trial['start_time']
            else:
                align_time = trial['start_time']
            
            # 计算时间窗口
            window_start = align_time + time_window[0]
            window_end = align_time + time_window[1]
            
            # 筛选该试次时间窗口内的Spike
            trial_mask = (all_spike_times >= window_start) & (all_spike_times <= window_end)
            trial_spikes = all_spike_times[trial_mask]
            
            # 转换为相对时间
            relative_spikes = trial_spikes - align_time
            
            raster_spikes.append(relative_spikes)
            valid_trial_ids.append(trial_id)
        
        return {
            'spike_times': raster_spikes,
            'trial_ids': valid_trial_ids,
            'channel_id': channel_id,
            'time_window': time_window
        }
    
    # ========== 行为数据接口 ==========
    
    def get_trial_info(self, trial_ids: Optional[List[int]] = None) -> List[Dict]:
        """
        获取试次信息
        
        Args:
            trial_ids: 试次ID列表 (None=所有)
            
        Returns:
            试次信息列表
        """
        if self._reader is None:
            raise RuntimeError("HDF5 file not opened")
        
        trials = self._reader.get_trials()
        
        if trial_ids is None:
            return trials
        
        # 筛选指定试次
        selected_trials = []
        for trial_id in trial_ids:
            if 1 <= trial_id <= len(trials):
                selected_trials.append(trials[trial_id - 1])
        
        return selected_trials
    
    def get_events(self, 
                  event_types: Optional[List[str]] = None,
                  time_range: Optional[Tuple[float, float]] = None) -> List[Dict]:
        """
        获取事件信息
        
        Args:
            event_types: 事件类型列表 (None=所有)
            time_range: 时间范围 (None=所有)
            
        Returns:
            事件信息列表
        """
        if self._reader is None:
            raise RuntimeError("HDF5 file not opened")
        
        events = self._reader.get_events()
        
        # 应用筛选
        filtered_events = []
        for event in events:
            # 类型筛选
            if event_types is not None and event['event_type'] not in event_types:
                continue
            
            # 时间范围筛选
            if time_range is not None:
                if not (time_range[0] <= event['timestamp'] <= time_range[1]):
                    continue
            
            filtered_events.append(event)
        
        return filtered_events
    
    def get_psth_data(self,
                     channel_id: int,
                     condition: Optional[str] = None,
                     bin_size: float = 0.01,
                     time_window: Tuple[float, float] = (-0.5, 1.0),
                     align_event: str = 'trial_start') -> Dict:
        """
        获取PSTH数据 (刺激后时间直方图)
        
        Args:
            channel_id: 通道ID
            condition: 条件筛选 (None=所有试次)
            bin_size: 分箱大小 (秒)
            time_window: 时间窗口 (相对对齐事件)
            align_event: 对齐事件
            
        Returns:
            {
                'bin_centers': np.ndarray,    # 时间轴 (分箱中心)
                'bin_edges': np.ndarray,      # 分箱边界
                'firing_rate': np.ndarray,    # 发放率 (Hz)
                'spike_counts': np.ndarray,   # Spike计数
                'trial_count': int,           # 试次数
                'sem': np.ndarray             # 标准误
            }
        """
        if self._reader is None:
            raise RuntimeError("HDF5 file not opened")
        
        # 获取试次信息
        trials = self._reader.get_trials()
        
        # 获取该通道的所有Spike时间
        spike_data = self.get_spike_times(channel_ids=[channel_id])
        all_spike_times = spike_data['times']
        
        # 收集每个试次的Spike时间
        trial_spike_times = []
        
        for trial in trials:
            # 确定对齐时间
            if align_event == 'trial_start':
                align_time = trial['start_time']
            else:
                align_time = trial['start_time']
            
            # 计算时间窗口
            window_start = align_time + time_window[0]
            window_end = align_time + time_window[1]
            
            # 筛选该试次时间窗口内的Spike
            trial_mask = (all_spike_times >= window_start) & (all_spike_times <= window_end)
            trial_spikes = all_spike_times[trial_mask]
            
            # 转换为相对时间
            relative_spikes = trial_spikes - align_time
            trial_spike_times.append(relative_spikes)
        
        # 计算PSTH
        num_trials = len(trial_spike_times)
        bin_edges = np.arange(time_window[0], time_window[1] + bin_size, bin_size)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # 计算每个试次的Spike计数
        trial_counts = np.zeros((num_trials, len(bin_centers)))
        for i, spikes in enumerate(trial_spike_times):
            trial_counts[i, :], _ = np.histogram(spikes, bins=bin_edges)
        
        # 计算平均发放率
        spike_counts = np.sum(trial_counts, axis=0)
        firing_rate = spike_counts / (num_trials * bin_size)  # 转换为Hz
        
        # 计算标准误
        sem = np.std(trial_counts / bin_size, axis=0) / np.sqrt(num_trials)
        
        return {
            'bin_centers': bin_centers,
            'bin_edges': bin_edges,
            'firing_rate': firing_rate,
            'spike_counts': spike_counts,
            'trial_count': num_trials,
            'sem': sem
        }
    
    # ========== 元数据接口 ==========
    
    def get_metadata(self) -> Dict:
        """
        获取元数据
        
        Returns:
            元数据字典
        """
        if self._reader is None:
            raise RuntimeError("HDF5 file not opened")
        
        return self._reader.get_metadata()
    
    def get_channel_info(self, channel_ids: Optional[List[int]] = None) -> List[Dict]:
        """
        获取通道信息
        
        Args:
            channel_ids: 通道ID列表 (None=所有)
            
        Returns:
            通道信息列表
        """
        if self._reader is None:
            raise RuntimeError("HDF5 file not opened")
        
        channels = self._reader.get_channel_info()
        
        if channel_ids is None:
            return channels
        
        # 筛选指定通道
        return [ch for ch in channels if ch['channel_id'] in channel_ids]
    
    def get_data_summary(self) -> Dict:
        """
        获取数据摘要
        
        Returns:
            数据摘要字典
        """
        if self._reader is None:
            raise RuntimeError("HDF5 file not opened")
        
        return self._reader.get_data_summary()


if __name__ == '__main__':
    # 测试代码
    import sys
    
    test_file = r"c:\Users\buaal\Desktop\NeuroPrime\test_output\test_fc_grating_014.h5"
    
    print(f"Testing VisualizationDataInterface with {test_file}...\n")
    
    with VisualizationDataInterface(test_file) as viz:
        # 测试获取元数据
        print("=== Metadata ===")
        metadata = viz.get_metadata()
        print(f"Trial: {metadata.get('trial_name')}")
        print(f"Sampling Rate: {metadata.get('sampling_rate')} Hz")
        print()
        
        # 测试获取LFP信号
        print("=== LFP Signal ===")
        lfp_data = viz.get_lfp_signal(channel_ids=[0, 1], time_range=(0, 1))
        print(f"Shape: {lfp_data.shape}")
        print(f"Range: [{lfp_data.min():.2f}, {lfp_data.max():.2f}] uV")
        print()
        
        # 测试获取Spike时间
        print("=== Spike Times ===")
        spike_data = viz.get_spike_times(channel_ids=[71], time_range=(0, 10))
        print(f"Channel 71 spikes in first 10s: {len(spike_data['times'])}")
        print()
        
        # 测试获取试次信息
        print("=== Trial Info ===")
        trials = viz.get_trial_info(trial_ids=[1, 2, 3])
        for trial in trials:
            print(f"Trial {trial['trial_num']}: {trial['start_time']:.3f}s - {trial['end_time']:.3f}s")
        print()
        
        # 测试获取PSTH数据
        print("=== PSTH Data ===")
        psth = viz.get_psth_data(channel_id=71, bin_size=0.05, time_window=(-0.5, 1.0))
        print(f"Bin centers: {psth['bin_centers'][:5]}...")
        print(f"Firing rate range: [{psth['firing_rate'].min():.2f}, {psth['firing_rate'].max():.2f}] Hz")
        print(f"Trial count: {psth['trial_count']}")
        print()
        
        # 测试获取栅格图数据
        print("=== Raster Data ===")
        raster = viz.get_raster_data(channel_id=71, trial_ids=[1, 2, 3, 4, 5])
        print(f"Trials: {raster['trial_ids']}")
        for i, spikes in enumerate(raster['spike_times']):
            print(f"  Trial {raster['trial_ids'][i]}: {len(spikes)} spikes")
        print()
    
    print("✅ VisualizationDataInterface tests completed!")
