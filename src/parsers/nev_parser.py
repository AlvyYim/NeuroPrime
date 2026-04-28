"""
NEV Parser - 解析Blackrock NEV Spike事件文件

文件格式:
- Basic Header: 336字节
- Extended Headers: 每个32字节
- Data Packets: 每个108字节 (含48样本波形)

参考: LoadSpike.m
"""

import struct
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path

from .mbm_parser import load_mbm, MBMInfo


@dataclass
class NEVBasicHeader:
    """NEV Basic Header (336字节)"""
    file_type: str           # "NEURALEV"
    version: str             # 版本号 "major.minor"
    extra_flag: str          # 波形标志
    header_size: int         # 头文件总大小
    dp_size: int            # 数据包大小 (108字节)
    clock_fs: int           # 时钟频率 (Hz)
    waveform_fs: int        # 波形采样率 (Hz)
    time_origin: List[int]  # 时间原点
    software_version: str    # 软件版本
    num_extend: int         # Extended Header数量


@dataclass
class NEUNEVWAVHeader:
    """NEUEVWAV Extended Header - 神经事件波形"""
    packet_id: str = "NEUEVWAV"
    elec_id: int = 0
    connector: str = ""
    pin: int = 0
    scale: int = 0           # nV per LSB
    energy_threshold: int = 0
    high_threshold: int = 0  # uV
    low_threshold: int = 0   # uV
    num_unit: int = 0
    waveform_size: int = 48  # 波形样本数


@dataclass
class NEVSpikeEvent:
    """NEV Spike事件"""
    timestamp: float         # 时间戳 (秒)
    elec_id: int            # 电极ID
    unit: int               # 聚类单元 (0=未分类, 1-5=已分类)
    waveform: np.ndarray    # 波形数据 (48样本)


@dataclass
class NEVDigitalEvent:
    """NEV数字事件 (行为标记)"""
    timestamp: float         # 时间戳 (秒)
    event_type: str          # 事件类型
    value: int              # 事件值


@dataclass
class NEVTrialInfo:
    """试次信息"""
    trial_num: int
    start_time: float        # PAUSEOFF时间
    end_time: float         # PAUSEON时间
    stim_cnd: int          # 刺激条件
    abort_time: Optional[float] = None
    ttl_time: Optional[float] = None


class NEVParser:
    """
    NEV文件解析器

    用法:
        parser = NEVParser("path/to/file.nev")
        parser.parse()

        # 获取解析结果
        spike_events = parser.spike_events
        digital_events = parser.digital_events
        trials = parser.trials
    """

    EVENT_TYPES = {
        1: "START",
        2: "STOP",
        3: "PAUSEON",      # 试次结束
        4: "PAUSEOFF",     # 试次开始
        5: "ABORT",
        128: "VSGTRIG",
        253: "STIMCND",    # 刺激条件 (512+)
        254: "STIMCND",    # 刺激条件 (256-511)
        255: "STIMCND"     # 刺激条件 (0-255)
    }

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file = None
        self.file_size = 0

        self.basic_header: Optional[NEVBasicHeader] = None
        self.extended_headers: List[Dict] = []
        self.waveform_headers: Dict[int, NEUNEVWAVHeader] = {}

        self.spike_events: List[NEVSpikeEvent] = []
        self.digital_events: List[NEVDigitalEvent] = []
        self.trials: List[NEVTrialInfo] = []

        self.mbm_info: Optional[MBMInfo] = None
        self.valid_mbm: bool = False

        self.ttl_events: List[NEVDigitalEvent] = []

        self.raw_timestamps: Optional[np.ndarray] = None
        self.raw_elec_ids: Optional[np.ndarray] = None
        self.raw_units: Optional[np.ndarray] = None
        self.raw_waveforms: Optional[np.ndarray] = None

        self.off_pos: np.ndarray = None
        self.on_pos: np.ndarray = None
        self.ttl_time: np.ndarray = None

    def parse(self) -> bool:
        try:
            with open(self.file_path, 'rb') as f:
                self.file = f

                f.seek(0, 2)
                self.file_size = f.tell()
                f.seek(0, 0)

                if not self._read_basic_header():
                    return False

                if not self._read_extended_headers():
                    return False

                if not self._read_data_packets():
                    return False

                self._parse_digital_events()
                self._load_mbm()
                self._parse_trials()
                self._compare_with_mbm()
                self._adjust_spike_timestamps()

            return True

        except Exception as e:
            print(f"Error parsing NEV file: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _read_basic_header(self) -> bool:
        f = self.file

        try:
            file_type = struct.unpack('8s', f.read(8))[0].decode('ascii', errors='ignore').strip('\x00')
        except:
            file_type = "Unknown"

        ver_major, ver_minor = struct.unpack('2B', f.read(2))
        version = f"{ver_major}.{ver_minor}"

        waveform_bit = struct.unpack('H', f.read(2))[0]
        extra_flag = "all 16-bit wav" if waveform_bit == 1 else "mixed 16-bit wav"

        header_size = struct.unpack('I', f.read(4))[0]
        dp_size = struct.unpack('I', f.read(4))[0]
        clock_fs = struct.unpack('I', f.read(4))[0]
        waveform_fs = struct.unpack('I', f.read(4))[0]

        time_origin = list(struct.unpack('8H', f.read(16)))

        try:
            software_version = struct.unpack('32s', f.read(32))[0].decode('ascii', errors='ignore').strip('\x00')
        except:
            software_version = "Unknown"

        curr_pos = f.tell()
        offset = 332 - curr_pos
        if offset != 0:
            f.seek(offset, 1)

        num_extend = struct.unpack('I', f.read(4))[0]

        curr_pos = f.tell()
        if curr_pos != 336:
            print(f"Warning: Basic header position mismatch. Expected 336, got {curr_pos}")
            f.seek(336, 0)

        expected_header_size = 336 + num_extend * 32
        if header_size != expected_header_size:
            print(f"Error: Extended header size mismatch. Expected {expected_header_size}, got {header_size}")
            return False

        self.basic_header = NEVBasicHeader(
            file_type=file_type,
            version=version,
            extra_flag=extra_flag,
            header_size=header_size,
            dp_size=dp_size,
            clock_fs=clock_fs,
            waveform_fs=waveform_fs,
            time_origin=time_origin,
            software_version=software_version,
            num_extend=num_extend
        )

        return True

    def _read_extended_headers(self) -> bool:
        f = self.file
        num_extend = self.basic_header.num_extend

        for i in range(num_extend):
            packet_id = struct.unpack('8s', f.read(8))[0].decode('ascii').strip('\x00')

            if packet_id == 'NEUEVWAV':
                header = self._read_neuevwav_header(f)
                self.waveform_headers[header.elec_id] = header
                self.extended_headers.append({
                    'type': 'NEUEVWAV',
                    'data': header
                })
            else:
                f.seek(24, 1)
                self.extended_headers.append({
                    'type': packet_id,
                    'data': None
                })

        if f.tell() != self.basic_header.header_size:
            print(f"Error: Extended header position mismatch")
            return False

        return True

    def _read_neuevwav_header(self, f) -> NEUNEVWAVHeader:
        elec_id = struct.unpack('H', f.read(2))[0]

        connector_code = struct.unpack('B', f.read(1))[0]
        connector = chr(64 + connector_code)

        pin = struct.unpack('B', f.read(1))[0]

        scale = struct.unpack('H', f.read(2))[0]

        energy_threshold = struct.unpack('H', f.read(2))[0]

        high_threshold = struct.unpack('h', f.read(2))[0]

        low_threshold = struct.unpack('h', f.read(2))[0]

        num_unit = struct.unpack('B', f.read(1))[0]

        waveform_size = struct.unpack('B', f.read(1))[0]
        if waveform_size == 0:
            waveform_size = 48

        f.seek(10, 1)

        return NEUNEVWAVHeader(
            elec_id=elec_id,
            connector=connector,
            pin=pin,
            scale=scale,
            energy_threshold=energy_threshold,
            high_threshold=high_threshold,
            low_threshold=low_threshold,
            num_unit=num_unit,
            waveform_size=waveform_size
        )

    def _read_data_packets(self) -> bool:
        f = self.file
        dp_size = self.basic_header.dp_size
        clock_fs = self.basic_header.clock_fs

        num_dp = (self.file_size - self.basic_header.header_size) // dp_size

        timestamps = []
        elec_ids = []
        units = []
        waveforms = []

        for i in range(num_dp):
            timestamp_raw = struct.unpack('I', f.read(4))[0]
            timestamp = timestamp_raw / clock_fs

            elec_id = struct.unpack('H', f.read(2))[0]

            unit = struct.unpack('B', f.read(1))[0]

            f.seek(1, 1)

            waveform_samples = (dp_size - 8) // 2
            waveform = np.fromfile(f, dtype=np.int16, count=waveform_samples)

            timestamps.append(timestamp)
            elec_ids.append(elec_id)
            units.append(unit)
            waveforms.append(waveform)

        self.raw_timestamps = np.array(timestamps)
        self.raw_elec_ids = np.array(elec_ids)
        self.raw_units = np.array(units)
        self.raw_waveforms = np.array(waveforms)

        spike_mask = (self.raw_elec_ids != 0) & (self.raw_elec_ids != 129)

        for i in np.where(spike_mask)[0]:
            elec_id = self.raw_elec_ids[i]
            scale = 1.0
            if elec_id in self.waveform_headers:
                scale = self.waveform_headers[elec_id].scale / 1000.0

            waveform_physical = self.raw_waveforms[i] * scale

            event = NEVSpikeEvent(
                timestamp=self.raw_timestamps[i],
                elec_id=elec_id,
                unit=self.raw_units[i],
                waveform=waveform_physical.astype(np.float32)
            )
            self.spike_events.append(event)

        return True
    
    def _adjust_spike_timestamps(self):
        """
        调整Spike时间戳，确保与试次时间使用相同的时间基准
        由于没有TTL事件，使用试次的开始时间作为参考
        """
        if not self.trials or not self.spike_events:
            return
        
        # 计算Spike时间和试次时间的偏移
        # 找到第一个试次开始时间
        first_trial_start = self.trials[0].start_time
        
        # 找到第一个试次开始时间前后的Spike分布
        spike_times = np.array([e.timestamp for e in self.spike_events])
        pre_trial_spikes = spike_times[spike_times < first_trial_start]
        post_trial_spikes = spike_times[spike_times >= first_trial_start]
        
        print(f"\n=== 时间对齐调整 ===")
        print(f"第一个试次开始时间: {first_trial_start:.3f} 秒")
        print(f"试次前Spike数量: {len(pre_trial_spikes)}")
        print(f"试次后Spike数量: {len(post_trial_spikes)}")
        
        # 检查Spike时间范围和试次时间范围
        min_spike_time = spike_times.min()
        max_spike_time = spike_times.max()
        min_trial_time = min(t.start_time for t in self.trials)
        max_trial_time = max(t.end_time for t in self.trials)
        
        print(f"Spike时间范围: {min_spike_time:.3f} - {max_spike_time:.3f} 秒")
        print(f"试次时间范围: {min_trial_time:.3f} - {max_trial_time:.3f} 秒")
        
        # 如果Spike时间从0开始，而试次时间从某个时间点开始，说明时间基准不同
        if min_spike_time < 1.0 and min_trial_time > 10.0:
            # 计算时间偏移，使Spike时间与试次时间对齐
            # 使用试次的开始时间作为参考点
            # 找到第一个试次开始时间对应的Spike时间
            # 假设第一个试次开始时，Spike时间应该为0
            time_offset = first_trial_start
            
            print(f"试次1开始时间: {first_trial_start:.3f} 秒")
            print(f"计算的时间偏移: {time_offset:.3f} 秒")
            
            # 调整所有Spike的时间戳
            for event in self.spike_events:
                event.timestamp += time_offset
            
            # 调整raw_timestamps
            if self.raw_timestamps is not None:
                self.raw_timestamps += time_offset
            
            print(f"调整后的Spike时间范围: {self.spike_events[0].timestamp:.3f} - {self.spike_events[-1].timestamp:.3f} 秒")
            print(f"调整后的试次1开始时间: {self.trials[0].start_time:.3f} 秒")
        else:
            print("Spike时间和试次时间已经对齐，不需要调整")

    def _parse_digital_events(self):
        digital_mask = self.raw_elec_ids == 0

        for i in np.where(digital_mask)[0]:
            unit = self.raw_units[i]

            if unit & 0x01:
                if len(self.raw_waveforms[i]) >= 2:
                    lower_byte = int(self.raw_waveforms[i][0]) & 0xFF
                    higher_byte = int(self.raw_waveforms[i][1]) & 0xFF

                    if lower_byte in self.EVENT_TYPES:
                        event_type = self.EVENT_TYPES[lower_byte]

                        if lower_byte == 255:
                            value = higher_byte
                        elif lower_byte == 254:
                            value = 256 + higher_byte
                        elif lower_byte == 253:
                            value = 512 + higher_byte
                        else:
                            value = higher_byte

                        event = NEVDigitalEvent(
                            timestamp=self.raw_timestamps[i],
                            event_type=event_type,
                            value=value
                        )
                        self.digital_events.append(event)

    def _load_mbm(self):
        mbm_path = self.file_path.with_suffix('.mbm')

        if mbm_path.exists():
            print(f"加载MBM文件: {mbm_path}")
            self.mbm_info = load_mbm(str(mbm_path))
            self.valid_mbm = self.mbm_info is not None
        else:
            print(f"MBM文件不存在: {mbm_path}")
            self.valid_mbm = False
            self.mbm_info = None

    def _parse_trials(self):
        pause_off_events = [e for e in self.digital_events if e.event_type == "PAUSEOFF"]
        pause_on_events = [e for e in self.digital_events if e.event_type == "PAUSEON"]
        stim_cnd_events = [e for e in self.digital_events if e.event_type == "STIMCND"]
        abort_events = [e for e in self.digital_events if e.event_type == "ABORT"]

        pause_off_events.sort(key=lambda x: x.timestamp)
        pause_on_events.sort(key=lambda x: x.timestamp)
        abort_events.sort(key=lambda x: x.timestamp)

        num_pause_off = len(pause_off_events)
        num_pause_on = len(pause_on_events)
        num_abort = len(abort_events)
        num_stim_cnd = len(stim_cnd_events)

        if not ((num_pause_off == num_pause_on - 1 or num_pause_off == num_pause_on)
                and num_pause_off >= num_abort and num_pause_off >= num_stim_cnd):
            print(f"警告: PAUSEON/OFF/ABORT数量关系异常")
            print(f"  NumPauseOff={num_pause_off}, NumPauseOn={num_pause_on}, NumAbort={num_abort}, NumStimCnd={num_stim_cnd}")

        ttldppos = np.where(self.raw_elec_ids == 129)[0]

        off_pos = np.array([i for i, e in enumerate(self.digital_events) if e.event_type == "PAUSEOFF"])
        on_pos = np.array([i for i, e in enumerate(self.digital_events) if e.event_type == "PAUSEON"])

        ttl_time = np.full((num_pause_off, 1000), np.nan)

        for ttl_idx in ttldppos:
            ttl_time_stamp = self.raw_timestamps[ttl_idx]
            for trial_idx in range(num_pause_off):
                if trial_idx < num_pause_on:
                    off_time = pause_off_events[trial_idx].timestamp
                    on_time = pause_on_events[trial_idx].timestamp

                    if off_time <= ttl_time_stamp <= on_time:
                        col = np.argmax(np.isnan(ttl_time[trial_idx, :]))
                        ttl_time[trial_idx, col] = ttl_time_stamp

        if num_pause_on > num_pause_off:
            start_idx = num_pause_on - num_pause_off
            on_pos = on_pos[start_idx:]
            pause_on_events = pause_on_events[start_idx:]

        for i in range(min(len(pause_off_events), len(pause_on_events))):
            if pause_off_events[i].timestamp > pause_on_events[i].timestamp:
                print(f"警告: 试次{i+1}的OffTime > OnTime，时间关系异常")

        # 获取TTL时间 (TTLTime(:,1))
        time_offsets = ttl_time[:, 0]

        num_trials = min(len(pause_off_events), len(pause_on_events))

        trials_data = []
        for i in range(num_trials):
            # 由于没有TTL事件，直接使用原始时间作为试次时间
            # 这样试次时间和Spike时间使用相同的时间基准
            start_time = pause_off_events[i].timestamp
            end_time = pause_on_events[i].timestamp

            ttl_offset = time_offsets[i] if i < len(time_offsets) else np.nan
            
            # 直接使用原始时间，不减去TTL偏移
            adjusted_start_time = start_time
            adjusted_end_time = end_time

            trial = NEVTrialInfo(
                trial_num=i + 1,
                start_time=adjusted_start_time,
                end_time=adjusted_end_time,
                stim_cnd=stim_cnd_events[i].value if i < len(stim_cnd_events) else -1
            )

            trial.ttl_time = 0.0

            trials_data.append(trial)

        # 按照LoadSpike.m的逻辑计算AbortT
        # ExpMonitor.AbortT = AbortTime-TTLTime(:,1);
        # ExpMonitor.AbortT(isnan(TTLTime(:,1))) = -999;
        abort_index = 0
        for i in range(num_trials):
            if abort_index < num_abort:
                ttl_offset = time_offsets[i] if i < len(time_offsets) else np.nan
                
                if not np.isnan(ttl_offset):
                    trials_data[i].abort_time = abort_events[abort_index].timestamp - ttl_offset
                else:
                    # 如果TTL时间为NaN，设置为-999
                    trials_data[i].abort_time = -999.0
                
                abort_index += 1

        self.trials = trials_data
        self.off_pos = off_pos
        self.on_pos = on_pos
        self.ttl_time = ttl_time

    def _compare_with_mbm(self):
        if not self.valid_mbm or self.mbm_info is None:
            return

        mbm_trials = self.mbm_info.nTrials
        spike_trials = len(self.trials)

        print(f"MBM试次数: {mbm_trials}, SPIKE试次数: {spike_trials}")

        if mbm_trials != spike_trials:
            print(f"警告：MBM和SPIKE试次数不匹配")
            return

        for i in range(min(mbm_trials, spike_trials)):
            trial = self.trials[i]
            mbm_resp_code = self.mbm_info.RespCode[i]

            mbm_valid = mbm_resp_code > 0
            spike_valid = trial.abort_time is None

            if mbm_valid != spike_valid:
                print(f"修正试次{i+1}的abort状态")
                if not mbm_valid:
                    trial.abort_time = trial.start_time
                else:
                    trial.abort_time = None

            mbm_stim_id = self.mbm_info.StimID[i]
            if trial.stim_cnd == -1 or trial.stim_cnd != mbm_stim_id:
                print(f"修正试次{i+1}的stim_cnd: {trial.stim_cnd} -> {mbm_stim_id}")
                trial.stim_cnd = mbm_stim_id

    def get_spike_times(self, elec_id: int = None, unit: int = None) -> np.ndarray:
        spikes = self.spike_events

        if elec_id is not None:
            spikes = [s for s in spikes if s.elec_id == elec_id]

        if unit is not None:
            spikes = [s for s in spikes if s.unit == unit]

        return np.array([s.timestamp for s in spikes])

    def get_spike_waveforms(self, elec_id: int = None) -> np.ndarray:
        spikes = self.spike_events

        if elec_id is not None:
            spikes = [s for s in spikes if s.elec_id == elec_id]

        return np.array([s.waveform for s in spikes])

    def get_channel_info(self) -> List[Dict]:
        channels = []
        for elec_id, header in self.waveform_headers.items():
            channels.append({
                'elec_id': elec_id,
                'connector': header.connector,
                'pin': header.pin,
                'scale_nv': header.scale,
                'high_threshold_uv': header.high_threshold,
                'low_threshold_uv': header.low_threshold,
                'num_unit': header.num_unit
            })
        return channels


def parse_nev(file_path: str) -> Optional[Dict]:
    parser = NEVParser(file_path)

    if not parser.parse():
        return None

    return {
        'basic_header': parser.basic_header,
        'extended_headers': parser.extended_headers,
        'waveform_headers': parser.waveform_headers,
        'spike_events': parser.spike_events,
        'digital_events': parser.digital_events,
        'trials': parser.trials,
        'channel_info': parser.get_channel_info()
    }


if __name__ == '__main__':
    import sys

    test_file = r"c:\Users\buaal\Desktop\NeuroPrime\coco1227rawdata\FC_Grating_014.nev"

    print(f"Parsing {test_file}...")
    result = parse_nev(test_file)

    if result:
        print("\n=== Basic Header ===")
        bh = result['basic_header']
        print(f"File Type: {bh.file_type}")
        print(f"Version: {bh.version}")
        print(f"Clock Fs: {bh.clock_fs} Hz")
        print(f"Waveform Fs: {bh.waveform_fs} Hz")
        print(f"Num Extended Headers: {bh.num_extend}")

        print(f"\n=== Spike Events ===")
        print(f"Total Spike Events: {len(result['spike_events'])}")

        if result['spike_events']:
            from collections import Counter
            elec_counts = Counter([s.elec_id for s in result['spike_events']])
            print(f"Active Electrodes: {len(elec_counts)}")
            print("Top 5 electrodes:")
            for elec_id, count in elec_counts.most_common(5):
                print(f"  Elec {elec_id}: {count} spikes")

        print(f"\n=== Digital Events ===")
        print(f"Total Digital Events: {len(result['digital_events'])}")

        from collections import Counter
        event_counts = Counter([e.event_type for e in result['digital_events']])
        for event_type, count in event_counts.items():
            print(f"  {event_type}: {count}")

        print(f"\n=== Trials ===")
        print(f"Number of Trials: {len(result['trials'])}")
        if result['trials']:
            print("First 3 trials:")
            for trial in result['trials'][:3]:
                print(f"  Trial {trial.trial_num}: {trial.start_time:.3f}s - {trial.end_time:.3f}s, "
                      f"StimCnd={trial.stim_cnd}, Aborted={trial.abort_time is not None}")

        print("\nParsing successful!")
    else:
        print("Parsing failed!")
        sys.exit(1)
