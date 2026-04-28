"""
HDF5 Writer - 将解析后的数据写入HDF5标准格式

HDF5文件结构:
{试验名称}.h5
├── /metadata        # 元数据
├── /signals         # 信号数据 (LFP等)
├── /spikes          # Spike数据
└── /behavior        # 行为数据
"""

import h5py
import numpy as np
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime


class HDF5Writer:
    """
    HDF5文件写入器
    
    用法:
        writer = HDF5Writer("FC_Grating_014.h5")
        writer.create_file()
        writer.write_metadata(...)
        writer.write_signals(...)
        writer.write_spikes(...)
        writer.close()
    """
    
    def __init__(self, file_path: str):
        """
        初始化写入器
        
        Args:
            file_path: HDF5文件路径
        """
        self.file_path = Path(file_path)
        self.file: Optional[h5py.File] = None
    
    def create_file(self, overwrite: bool = False) -> bool:
        """
        创建HDF5文件
        
        Args:
            overwrite: 是否覆盖已存在的文件
            
        Returns:
            True if successful
        """
        try:
            mode = 'w' if overwrite else 'w-'
            self.file = h5py.File(self.file_path, mode)
            
            # 创建标准组结构
            self.file.create_group('metadata')
            self.file.create_group('signals')
            self.file.create_group('spikes')
            self.file.create_group('behavior')
            
            return True
        except Exception as e:
            print(f"Error creating HDF5 file: {e}")
            return False
    
    def write_metadata(self, 
                       trial_name: str,
                       experiment_name: str,
                       sampling_rate: float,
                       duration: float,
                       num_channels: int,
                       source_files: Dict[str, str],
                       creation_time: Optional[str] = None,
                       **kwargs) -> bool:
        """
        写入元数据
        
        Args:
            trial_name: 试验名称
            experiment_name: 实验名称
            sampling_rate: 采样率 (Hz)
            duration: 记录时长 (秒)
            num_channels: 通道数
            source_files: 源文件路径字典 {'ns3': '...', 'nev': '...', 'mbm': '...'}
            creation_time: 创建时间 (ISO格式)
            **kwargs: 其他元数据
        """
        if self.file is None:
            print("Error: HDF5 file not created")
            return False
        
        try:
            metadata_group = self.file['metadata']
            
            # 基本信息
            metadata_group.attrs['trial_name'] = trial_name
            metadata_group.attrs['experiment_name'] = experiment_name
            metadata_group.attrs['sampling_rate'] = sampling_rate
            metadata_group.attrs['duration'] = duration
            metadata_group.attrs['num_channels'] = num_channels
            
            # 时间戳
            if creation_time is None:
                creation_time = datetime.now().isoformat()
            metadata_group.attrs['creation_time'] = creation_time
            metadata_group.attrs['file_version'] = '1.0'
            
            # 源文件信息
            source_group = metadata_group.create_group('source_files')
            for file_type, file_path in source_files.items():
                source_group.attrs[file_type] = file_path
            
            # 其他元数据
            for key, value in kwargs.items():
                if isinstance(value, (str, int, float, bool)):
                    metadata_group.attrs[key] = value
                else:
                    # 复杂类型存储为JSON字符串
                    metadata_group.attrs[key] = json.dumps(value)
            
            return True
        except Exception as e:
            print(f"Error writing metadata: {e}")
            return False
    
    def write_signals(self,
                      lfp_data: Optional[np.ndarray] = None,
                      raw_data: Optional[np.ndarray] = None,
                      channel_info: Optional[List[Dict]] = None) -> bool:
        """
        写入信号数据
        
        Args:
            lfp_data: LFP信号数据 [通道数 × 样本数]
            raw_data: 原始信号数据 [通道数 × 样本数]
            channel_info: 通道信息列表
        """
        if self.file is None:
            print("Error: HDF5 file not created")
            return False
        
        try:
            signals_group = self.file['signals']
            
            # 写入LFP数据
            if lfp_data is not None:
                if 'lfp_data' in signals_group:
                    del signals_group['lfp_data']
                
                # 使用压缩存储
                signals_group.create_dataset(
                    'lfp_data',
                    data=lfp_data,
                    compression='gzip',
                    compression_opts=4,
                    chunks=True
                )
                signals_group['lfp_data'].attrs['unit'] = 'uV'
                signals_group['lfp_data'].attrs['description'] = 'Local Field Potential'
            
            # 写入原始数据（可选，默认不保存以节省空间）
            if raw_data is not None:
                if 'raw_data' in signals_group:
                    del signals_group['raw_data']
                
                signals_group.create_dataset(
                    'raw_data',
                    data=raw_data,
                    compression='gzip',
                    compression_opts=4,
                    chunks=True
                )
                signals_group['raw_data'].attrs['unit'] = 'digital'
                signals_group['raw_data'].attrs['description'] = 'Raw digital signal'
            
            # 写入通道信息
            if channel_info is not None:
                if 'channel_info' in signals_group:
                    del signals_group['channel_info']
                
                # 将通道信息转换为结构化数组
                dtype = [
                    ('channel_id', 'i4'),
                    ('electrode_id', 'i4'),
                    ('electrode_label', 'S32'),
                    ('connector', 'S8'),
                    ('pin', 'i4'),
                    ('unit', 'S8'),
                    ('conversion_factor', 'f4')
                ]
                
                channel_array = np.array([
                    (
                        ch.get('channel_id', 0),
                        ch.get('electrode_id', 0),
                        ch.get('electrode_label', '').encode('utf-8')[:32],
                        ch.get('connector', '').encode('utf-8')[:8],
                        ch.get('pin', 0),
                        ch.get('unit', '').encode('utf-8')[:8],
                        ch.get('conversion_factor', 1.0)
                    )
                    for ch in channel_info
                ], dtype=dtype)
                
                signals_group.create_dataset('channel_info', data=channel_array)
            
            return True
        except Exception as e:
            print(f"Error writing signals: {e}")
            return False
    
    def write_spikes(self,
                     spike_times: np.ndarray,
                     spike_waveforms: np.ndarray,
                     spike_elec_ids: np.ndarray,
                     spike_units: Optional[np.ndarray] = None,
                     channel_info: Optional[List[Dict]] = None) -> bool:
        """
        写入Spike数据
        
        Args:
            spike_times: Spike时间戳数组
            spike_waveforms: Spike波形数组 [事件数 × 样本数]
            spike_elec_ids: Spike电极ID数组
            spike_units: Spike聚类单元数组 (可选)
            channel_info: 通道信息列表
        """
        if self.file is None:
            print("Error: HDF5 file not created")
            return False
        
        try:
            spikes_group = self.file['spikes']
            
            # Spike时间戳
            if 'spike_times' in spikes_group:
                del spikes_group['spike_times']
            spikes_group.create_dataset('spike_times', data=spike_times)
            spikes_group['spike_times'].attrs['unit'] = 'second'
            
            # Spike波形
            if 'spike_waveforms' in spikes_group:
                del spikes_group['spike_waveforms']
            spikes_group.create_dataset(
                'spike_waveforms',
                data=spike_waveforms,
                compression='gzip',
                compression_opts=4
            )
            spikes_group['spike_waveforms'].attrs['unit'] = 'uV'
            
            # 电极ID
            if 'spike_elec_ids' in spikes_group:
                del spikes_group['spike_elec_ids']
            spikes_group.create_dataset('spike_elec_ids', data=spike_elec_ids)
            
            # 聚类单元
            if spike_units is not None:
                if 'spike_units' in spikes_group:
                    del spikes_group['spike_units']
                spikes_group.create_dataset('spike_units', data=spike_units)
                spikes_group['spike_units'].attrs['description'] = '0=unsorted, 1-5=sorted units'
            
            # 通道信息
            if channel_info is not None:
                if 'channel_info' in spikes_group:
                    del spikes_group['channel_info']
                
                dtype = [
                    ('elec_id', 'i4'),
                    ('connector', 'S8'),
                    ('pin', 'i4'),
                    ('scale_nv', 'f4'),
                    ('high_threshold_uv', 'f4'),
                    ('low_threshold_uv', 'f4'),
                    ('num_unit', 'i4')
                ]
                
                channel_array = np.array([
                    (
                        ch.get('elec_id', 0),
                        ch.get('connector', '').encode('utf-8')[:8],
                        ch.get('pin', 0),
                        ch.get('scale_nv', 0.0),
                        ch.get('high_threshold_uv', 0.0),
                        ch.get('low_threshold_uv', 0.0),
                        ch.get('num_unit', 0)
                    )
                    for ch in channel_info
                ], dtype=dtype)
                
                spikes_group.create_dataset('channel_info', data=channel_array)
            
            return True
        except Exception as e:
            print(f"Error writing spikes: {e}")
            return False
    
    def write_behavior(self,
                       trials: Optional[List[Dict]] = None,
                       events: Optional[List[Dict]] = None,
                       mbm_data: Optional[Dict] = None) -> bool:
        """
        写入行为数据
        
        Args:
            trials: 试次信息列表
            events: 事件列表
            mbm_data: MBM行为数据
        """
        if self.file is None:
            print("Error: HDF5 file not created")
            return False
        
        try:
            # 创建或获取behavior组
            if 'behavior' in self.file:
                behavior_group = self.file['behavior']
            else:
                behavior_group = self.file.create_group('behavior')
            
            # 试次信息
            if trials is not None:
                if 'trials' in behavior_group:
                    del behavior_group['trials']
                
                dtype = [
                    ('trial_num', 'i4'),
                    ('start_time', 'f8'),
                    ('end_time', 'f8'),
                    ('stim_cnd', 'i4'),
                    ('aborted', 'i1')
                ]
                
                trial_array = np.array([
                    (
                        t.get('trial_num', 0),
                        t.get('start_time', 0.0),
                        t.get('end_time', 0.0),
                        t.get('stim_cnd', -1),
                        1 if t.get('abort_time') is not None else 0
                    )
                    for t in trials
                ], dtype=dtype)
                
                behavior_group.create_dataset('trials', data=trial_array)
            
            # 事件
            if events is not None:
                if 'events' in behavior_group:
                    del behavior_group['events']
                
                # 事件类型编码
                event_types = {'PAUSEOFF': 1, 'PAUSEON': 2, 'STIMCND': 3, 
                              'ABORT': 4, 'VSGTRIG': 5, 'START': 6, 'STOP': 7}
                
                dtype = [
                    ('timestamp', 'f8'),
                    ('event_type', 'i4'),
                    ('value', 'i4')
                ]
                
                event_array = np.array([
                    (
                        e.get('timestamp', 0.0),
                        event_types.get(e.get('event_type', ''), 0),
                        e.get('value', 0)
                    )
                    for e in events
                ], dtype=dtype)
                
                behavior_group.create_dataset('events', data=event_array)
            
            # MBM数据
            if mbm_data is not None:
                mbm_group = behavior_group.create_group('mbm_data')
                for key, value in mbm_data.items():
                    if isinstance(value, np.ndarray):
                        mbm_group.create_dataset(key, data=value)
                    elif isinstance(value, (list, tuple)):
                        mbm_group.create_dataset(key, data=np.array(value))
                    else:
                        mbm_group.attrs[key] = value
            
            return True
        except Exception as e:
            print(f"Error writing behavior: {e}")
            return False
    
    def close(self):
        """关闭HDF5文件"""
        if self.file is not None:
            self.file.close()
            self.file = None
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


def convert_ns3_to_hdf5(ns3_file: str, hdf5_file: str, 
                        trial_name: str = None,
                        experiment_name: str = "") -> bool:
    """
    将NS3文件转换为HDF5格式
    
    Args:
        ns3_file: NS3文件路径
        hdf5_file: 输出HDF5文件路径
        trial_name: 试验名称
        experiment_name: 实验名称
        
    Returns:
        True if successful
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from parsers.ns3_parser import parse_ns3
    
    # 解析NS3文件
    result = parse_ns3(ns3_file)
    if result is None:
        print(f"Error: Failed to parse {ns3_file}")
        return False
    
    # 自动提取试验名称
    if trial_name is None:
        trial_name = Path(ns3_file).stem
    
    # 创建HDF5文件
    writer = HDF5Writer(hdf5_file)
    if not writer.create_file(overwrite=True):
        return False
    
    # 写入元数据
    source_files = {'ns3': ns3_file}
    writer.write_metadata(
        trial_name=trial_name,
        experiment_name=experiment_name,
        sampling_rate=result['sampling_rate'],
        duration=result['duration'],
        num_channels=len(result['channel_info']),
        source_files=source_files
    )
    
    # 写入信号数据
    writer.write_signals(
        lfp_data=result['physical_data'],
        channel_info=result['channel_info']
    )
    
    writer.close()
    print(f"Successfully converted {ns3_file} to {hdf5_file}")
    return True


def parse_log_condition_values(log_file: str) -> list:
    """
    从.log文件中解析Condition Value字段
    
    Args:
        log_file: .log文件路径
        
    Returns:
        条件值列表，每个元素表示对应试次的条件索引（从1开始）
    """
    import re
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        
        # 查找 STIMULUS SETTINGS 部分
        stim_start = content.find('@START STUMULUS SETTINGS')
        if stim_start == -1:
            return []
        
        stim_end = content.find('@END STUMULUS SETTINGS', stim_start)
        stim_section = content[stim_start:stim_end] if stim_end != -1 else content[stim_start:]
        
        # 在 STIMULUS SETTINGS 部分中查找 Condition Value
        var_start = stim_section.find('@VARIABLE definition section')
        if var_start == -1:
            return []
        
        var_section = stim_section[var_start:]
        
        # 解析 Condition Value
        cv_match = re.search(r'Condition Value\s*=\s*([\d.;]+)', var_section)
        if cv_match:
            values_str = cv_match.group(1)
            condition_values = [int(float(v)) for v in values_str.split(';') if v]
            return condition_values
        
        return []
    except Exception as e:
        print(f"Warning: Failed to parse log file {log_file}: {e}")
        return []


def convert_nev_to_hdf5(nev_file: str, hdf5_file: str, log_file: str = None) -> bool:
    """
    将NEV文件中的Spike数据添加到HDF5文件
    
    Args:
        nev_file: NEV文件路径
        hdf5_file: 已存在的HDF5文件路径
        log_file: 可选的.log文件路径，用于获取正确的刺激条件信息
        
    Returns:
        True if successful
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from parsers.nev_parser import parse_nev
    
    # 解析NEV文件
    result = parse_nev(nev_file)
    if result is None:
        print(f"Error: Failed to parse {nev_file}")
        return False
    
    # 尝试从.log文件获取刺激条件信息
    log_condition_values = []
    if log_file is None:
        # 自动查找同名的.log文件
        potential_log = Path(nev_file).with_suffix('.log')
        if potential_log.exists():
            log_file = str(potential_log)
    
    if log_file and Path(log_file).exists():
        log_condition_values = parse_log_condition_values(log_file)
        if log_condition_values:
            print(f"Loaded {len(log_condition_values)} condition values from {log_file}")
    
    # 打开HDF5文件
    writer = HDF5Writer(hdf5_file)
    try:
        writer.file = h5py.File(hdf5_file, 'a')
    except Exception as e:
        print(f"Error opening HDF5 file: {e}")
        return False
    
    # 提取Spike数据
    spike_times = np.array([e.timestamp for e in result['spike_events']])
    spike_waveforms = np.array([e.waveform for e in result['spike_events']])
    spike_elec_ids = np.array([e.elec_id for e in result['spike_events']])
    spike_units = np.array([e.unit for e in result['spike_events']])
    
    # 写入Spike数据
    writer.write_spikes(
        spike_times=spike_times,
        spike_waveforms=spike_waveforms,
        spike_elec_ids=spike_elec_ids,
        spike_units=spike_units,
        channel_info=result['channel_info']
    )
    
    # 写入行为数据
    trials_data = []
    for i, trial in enumerate(result['trials']):
        # 优先使用.log文件中的条件值
        if log_condition_values and i < len(log_condition_values):
            stim_cnd = log_condition_values[i]
        else:
            stim_cnd = trial.stim_cnd
        
        trials_data.append({
            'trial_num': trial.trial_num,
            'start_time': trial.start_time,
            'end_time': trial.end_time,
            'stim_cnd': stim_cnd,
            'abort_time': trial.abort_time
        })
    
    events_data = []
    for event in result['digital_events']:
        events_data.append({
            'timestamp': event.timestamp,
            'event_type': event.event_type,
            'value': event.value
        })
    
    writer.write_behavior(
        trials=trials_data,
        events=events_data
    )
    
    # 更新源文件信息
    if 'metadata' in writer.file:
        source_group = writer.file['metadata'].require_group('source_files')
        source_group.attrs['nev'] = nev_file
        if log_file:
            source_group.attrs['log'] = log_file
    
    writer.close()
    print(f"Successfully added NEV data from {nev_file} to {hdf5_file}")
    return True


if __name__ == '__main__':
    # 测试代码
    import sys
    
    # 测试NS3转换
    ns3_file = r"c:\Users\buaal\Desktop\NeuroPrime\coco1227rawdata\FC_Grating_014.ns3"
    hdf5_file = r"c:\Users\buaal\Desktop\NeuroPrime\test_output.h5"
    
    print("=== Testing NS3 to HDF5 conversion ===")
    if convert_ns3_to_hdf5(ns3_file, hdf5_file, experiment_name="Test Experiment"):
        print("NS3 conversion successful!")
        
        # 测试添加NEV数据
        print("\n=== Testing NEV to HDF5 conversion ===")
        nev_file = r"c:\Users\buaal\Desktop\NeuroPrime\coco1227rawdata\FC_Grating_014.nev"
        if convert_nev_to_hdf5(nev_file, hdf5_file):
            print("NEV conversion successful!")
            
            # 验证文件内容
            print("\n=== Verifying HDF5 file ===")
            with h5py.File(hdf5_file, 'r') as f:
                print("Groups:", list(f.keys()))
                print("Metadata:", dict(f['metadata'].attrs))
                print("Signals datasets:", list(f['signals'].keys()))
                print("Spikes datasets:", list(f['spikes'].keys()))
                print("Behavior datasets:", list(f['behavior'].keys()))
                print("\nLFP data shape:", f['signals/lfp_data'].shape)
                print("Spike times shape:", f['spikes/spike_times'].shape)
                print("Trials shape:", f['behavior/trials'].shape)
        else:
            print("NEV conversion failed!")
            sys.exit(1)
    else:
        print("NS3 conversion failed!")
        sys.exit(1)
