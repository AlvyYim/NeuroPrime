"""
HDF5 Reader - 从HDF5标准格式读取数据

HDF5文件结构:
{试验名称}.h5
├── /metadata        # 元数据
├── /signals         # 信号数据 (LFP等)
├── /spikes          # Spike数据
└── /behavior        # 行为数据
"""

import h5py
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path


class HDF5Reader:
    """
    HDF5文件读取器
    
    用法:
        reader = HDF5Reader("FC_Grating_014.h5")
        reader.open()
        
        # 获取元数据
        metadata = reader.get_metadata()
        
        # 获取信号数据
        lfp_data = reader.get_lfp_data()
        
        # 获取Spike数据
        spike_times = reader.get_spike_times()
        
        reader.close()
    """
    
    def __init__(self, file_path: str):
        """
        初始化读取器
        
        Args:
            file_path: HDF5文件路径
        """
        self.file_path = Path(file_path)
        self.file: Optional[h5py.File] = None
    
    def open(self) -> bool:
        """
        打开HDF5文件
        
        Returns:
            True if successful
        """
        try:
            self.file = h5py.File(self.file_path, 'r')
            return True
        except Exception as e:
            print(f"Error opening HDF5 file: {e}")
            return False
    
    def close(self):
        """关闭HDF5文件"""
        if self.file is not None:
            self.file.close()
            self.file = None
    
    def __enter__(self):
        """上下文管理器入口"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取元数据
        
        Returns:
            元数据字典
        """
        if self.file is None:
            raise RuntimeError("HDF5 file not opened")
        
        metadata = {}
        
        if 'metadata' in self.file:
            metadata_group = self.file['metadata']
            
            # 读取属性
            for key in metadata_group.attrs:
                metadata[key] = metadata_group.attrs[key]
            
            # 读取源文件信息
            if 'source_files' in metadata_group:
                source_files = {}
                for key in metadata_group['source_files'].attrs:
                    source_files[key] = metadata_group['source_files'].attrs[key]
                metadata['source_files'] = source_files
        
        return metadata
    
    def get_lfp_data(self, 
                     time_range: Optional[Tuple[float, float]] = None,
                     channels: Optional[List[int]] = None) -> np.ndarray:
        """
        获取LFP信号数据
        
        Args:
            time_range: 时间范围 (start, end)，单位秒
            channels: 通道索引列表 (None=所有通道)
        
        Returns:
            LFP数据 [通道数 × 样本数]
        """
        if self.file is None:
            raise RuntimeError("HDF5 file not opened")
        
        if 'signals/lfp_data' not in self.file:
            raise KeyError("LFP data not found in HDF5 file")
        
        lfp_dataset = self.file['signals/lfp_data']
        
        # 获取采样率
        metadata = self.get_metadata()
        fs = metadata.get('sampling_rate', 2000.0)
        
        # 计算样本索引
        if time_range is not None:
            start_idx = int(time_range[0] * fs)
            end_idx = int(time_range[1] * fs)
            start_idx = max(0, start_idx)
            end_idx = min(lfp_dataset.shape[1], end_idx)
        else:
            start_idx = 0
            end_idx = lfp_dataset.shape[1]
        
        # 读取数据
        if channels is not None:
            data = lfp_dataset[channels, start_idx:end_idx]
        else:
            data = lfp_dataset[:, start_idx:end_idx]
        
        return np.array(data)
    
    def get_channel_info(self) -> List[Dict]:
        """
        获取通道信息
        
        Returns:
            通道信息列表
        """
        if self.file is None:
            raise RuntimeError("HDF5 file not opened")
        
        channel_info = []
        
        # 尝试从signals组读取
        if 'signals/channel_info' in self.file:
            dataset = self.file['signals/channel_info']
            for row in dataset:
                channel_info.append({
                    'channel_id': int(row['channel_id']),
                    'electrode_id': int(row['electrode_id']),
                    'electrode_label': row['electrode_label'].decode('utf-8', errors='ignore').strip('\x00'),
                    'connector': row['connector'].decode('utf-8', errors='ignore').strip('\x00'),
                    'pin': int(row['pin']),
                    'unit': row['unit'].decode('utf-8', errors='ignore').strip('\x00'),
                    'conversion_factor': float(row['conversion_factor'])
                })
        
        return channel_info
    
    def get_spike_times(self, 
                        elec_id: Optional[int] = None,
                        unit: Optional[int] = None,
                        time_range: Optional[Tuple[float, float]] = None) -> np.ndarray:
        """
        获取Spike时间戳
        
        Args:
            elec_id: 电极ID筛选 (None=所有)
            unit: 单元筛选 (None=所有)
            time_range: 时间范围 (start, end)，单位秒
        
        Returns:
            Spike时间戳数组
        """
        if self.file is None:
            raise RuntimeError("HDF5 file not opened")
        
        if 'spikes/spike_times' not in self.file:
            raise KeyError("Spike times not found in HDF5 file")
        
        spike_times = np.array(self.file['spikes/spike_times'])
        spike_elec_ids = np.array(self.file['spikes/spike_elec_ids'])
        
        # 应用筛选
        mask = np.ones(len(spike_times), dtype=bool)
        
        if elec_id is not None:
            mask &= (spike_elec_ids == elec_id)
        
        if unit is not None and 'spikes/spike_units' in self.file:
            spike_units = np.array(self.file['spikes/spike_units'])
            mask &= (spike_units == unit)
        
        if time_range is not None:
            mask &= (spike_times >= time_range[0]) & (spike_times <= time_range[1])
        
        return spike_times[mask]
    
    def get_spike_waveforms(self, 
                            elec_id: Optional[int] = None) -> np.ndarray:
        """
        获取Spike波形
        
        Args:
            elec_id: 电极ID筛选 (None=所有)
        
        Returns:
            Spike波形数组 [事件数 × 样本数]
        """
        if self.file is None:
            raise RuntimeError("HDF5 file not opened")
        
        if 'spikes/spike_waveforms' not in self.file:
            raise KeyError("Spike waveforms not found in HDF5 file")
        
        waveforms = np.array(self.file['spikes/spike_waveforms'])
        spike_elec_ids = np.array(self.file['spikes/spike_elec_ids'])
        
        # 应用筛选
        if elec_id is not None:
            mask = (spike_elec_ids == elec_id)
            return waveforms[mask]
        
        return waveforms
    
    def get_trials(self) -> List[Dict]:
        """
        获取试次信息
        
        Returns:
            试次信息列表
        """
        if self.file is None:
            raise RuntimeError("HDF5 file not opened")
        
        trials = []
        
        if 'behavior/trials' in self.file:
            dataset = self.file['behavior/trials']
            for row in dataset:
                trials.append({
                    'trial_num': int(row['trial_num']),
                    'start_time': float(row['start_time']),
                    'end_time': float(row['end_time']),
                    'stim_cnd': int(row['stim_cnd']),
                    'aborted': bool(row['aborted'])
                })
        
        return trials
    
    def get_events(self, event_type: Optional[str] = None) -> List[Dict]:
        """
        获取事件信息
        
        Args:
            event_type: 事件类型筛选 (None=所有)
        
        Returns:
            事件信息列表
        """
        if self.file is None:
            raise RuntimeError("HDF5 file not opened")
        
        events = []
        
        # 事件类型解码
        event_type_names = {1: 'PAUSEOFF', 2: 'PAUSEON', 3: 'STIMCND', 
                           4: 'ABORT', 5: 'VSGTRIG', 6: 'START', 7: 'STOP'}
        
        if 'behavior/events' in self.file:
            dataset = self.file['behavior/events']
            for row in dataset:
                event = {
                    'timestamp': float(row['timestamp']),
                    'event_type': event_type_names.get(int(row['event_type']), 'UNKNOWN'),
                    'value': int(row['value'])
                }
                
                if event_type is None or event['event_type'] == event_type:
                    events.append(event)
        
        return events
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        获取数据摘要
        
        Returns:
            数据摘要字典
        """
        summary = {
            'file_path': str(self.file_path),
            'file_size_mb': self.file_path.stat().st_size / (1024 * 1024)
        }
        
        # 元数据
        try:
            metadata = self.get_metadata()
            summary.update({
                'trial_name': metadata.get('trial_name', 'Unknown'),
                'experiment_name': metadata.get('experiment_name', 'Unknown'),
                'sampling_rate': metadata.get('sampling_rate', 0),
                'duration': metadata.get('duration', 0),
                'num_channels': metadata.get('num_channels', 0)
            })
        except:
            pass
        
        # 信号数据
        try:
            if 'signals/lfp_data' in self.file:
                lfp_shape = self.file['signals/lfp_data'].shape
                summary['lfp_data_shape'] = lfp_shape
                summary['lfp_data_size_mb'] = self.file['signals/lfp_data'].nbytes / (1024 * 1024)
        except:
            pass
        
        # Spike数据
        try:
            if 'spikes/spike_times' in self.file:
                num_spikes = len(self.file['spikes/spike_times'])
                summary['num_spikes'] = num_spikes
        except:
            pass
        
        # 试次数据
        try:
            trials = self.get_trials()
            summary['num_trials'] = len(trials)
            summary['num_aborted_trials'] = sum(1 for t in trials if t['aborted'])
        except:
            pass
        
        return summary


def read_hdf5(file_path: str) -> Dict[str, Any]:
    """
    便捷函数：读取HDF5文件所有数据
    
    Args:
        file_path: HDF5文件路径
        
    Returns:
        包含所有数据的字典
    """
    with HDF5Reader(file_path) as reader:
        return {
            'metadata': reader.get_metadata(),
            'channel_info': reader.get_channel_info(),
            'lfp_data': reader.get_lfp_data(),
            'spike_times': reader.get_spike_times(),
            'spike_waveforms': reader.get_spike_waveforms(),
            'trials': reader.get_trials(),
            'events': reader.get_events(),
            'summary': reader.get_data_summary()
        }


if __name__ == '__main__':
    # 测试代码
    import sys
    
    test_file = r"c:\Users\buaal\Desktop\NeuroPrime\test_output.h5"
    
    print(f"Reading {test_file}...")
    
    with HDF5Reader(test_file) as reader:
        # 获取摘要
        print("\n=== Data Summary ===")
        summary = reader.get_data_summary()
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        # 获取元数据
        print("\n=== Metadata ===")
        metadata = reader.get_metadata()
        print(f"Trial: {metadata.get('trial_name')}")
        print(f"Experiment: {metadata.get('experiment_name')}")
        print(f"Sampling Rate: {metadata.get('sampling_rate')} Hz")
        print(f"Duration: {metadata.get('duration')} s")
        
        # 获取通道信息
        print("\n=== Channel Info (first 3) ===")
        channels = reader.get_channel_info()
        for ch in channels[:3]:
            print(f"Channel {ch['channel_id']}: {ch['electrode_label']}, "
                  f"Connector {ch['connector']}, Pin {ch['pin']}")
        
        # 获取LFP数据（前1秒）
        print("\n=== LFP Data (first 1 second) ===")
        lfp_data = reader.get_lfp_data(time_range=(0, 1))
        print(f"Shape: {lfp_data.shape}")
        print(f"Range: [{lfp_data.min():.2f}, {lfp_data.max():.2f}] uV")
        
        # 获取Spike数据
        print("\n=== Spike Data ===")
        spike_times = reader.get_spike_times()
        print(f"Total spikes: {len(spike_times)}")
        
        # 获取试次信息
        print("\n=== Trials (first 3) ===")
        trials = reader.get_trials()
        for trial in trials[:3]:
            print(f"Trial {trial['trial_num']}: {trial['start_time']:.3f}s - "
                  f"{trial['end_time']:.3f}s, StimCnd={trial['stim_cnd']}, "
                  f"Aborted={trial['aborted']}")
    
    print("\n✅ Reading successful!")
