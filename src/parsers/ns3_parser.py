"""
NS3 Parser - 解析Blackrock NS3连续信号文件

文件格式:
- Basic Header: 314字节
- Extended Header: 每个电极66字节
- Data Packets: 变长数据包

参考: LoadLFP.m
"""

import struct
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class NS3BasicHeader:
    """NS3 Basic Header (314字节)"""
    file_type: str           # "NEURALSG" 或 "NEURALCD"
    version: str             # 版本号 "major.minor"
    header_size: int         # 头文件总大小
    label: str               # 记录标签
    period: int              # 采样周期
    clock_fs: int            # 时钟频率 (Hz)
    fs: float                # 实际采样率 = clock_fs / period
    time_origin: List[int]   # 时间原点 [年,月,日,时,分,秒,毫秒,微秒]
    num_elec: int            # 电极数量


@dataclass
class NS3ExtendedHeader:
    """NS3 Extended Header (每个电极66字节)"""
    packet_id: str           # "CC" = 连续通道
    elec_id: int             # 电极ID
    elec_label: str          # 电极标签
    connector: str           # 连接器编号 (A, B, C, D)
    pin: int                 # 引脚编号
    min_digital_value: int   # 最小数字值
    max_digital_value: int   # 最大数字值
    min_analog_value: int    # 最小模拟值 (uV)
    max_analog_value: int    # 最大模拟值 (uV)
    analog_unit: str         # 单位 "uv" 或 "mv"
    high_cut_freq: int       # 高通截止频率
    high_cut_order: int      # 高通阶数
    high_cut_type: int       # 高通类型
    low_cut_freq: int        # 低通截止频率
    low_cut_order: int       # 低通阶数
    low_cut_type: int        # 低通类型


@dataclass
class NS3DataPacket:
    """NS3 Data Packet"""
    header: int              # 0x01 数据包头标记
    timestamp: int           # 时间戳（时钟周期数）
    num_samples: int         # 样本数
    data: np.ndarray         # 实际数据 [电极数 × 样本数]


class NS3Parser:
    """
    NS3文件解析器
    
    用法:
        parser = NS3Parser("path/to/file.ns3")
        parser.parse()
        
        # 获取解析结果
        basic_header = parser.basic_header
        extended_headers = parser.extended_headers
        raw_data = parser.raw_data  # 数字值
        physical_data = parser.get_physical_data()  # 物理值 (uV)
    """
    
    def __init__(self, file_path: str):
        """
        初始化解析器
        
        Args:
            file_path: NS3文件路径
        """
        self.file_path = Path(file_path)
        self.file = None
        self.file_size = 0
        
        # 解析结果
        self.basic_header: Optional[NS3BasicHeader] = None
        self.extended_headers: List[NS3ExtendedHeader] = []
        self.data_packets: List[NS3DataPacket] = []
        self.raw_data: Optional[np.ndarray] = None  # [通道数 × 样本数]
        
        # 转换因子缓存
        self._conversion_factors: Optional[np.ndarray] = None
    
    def parse(self) -> bool:
        """
        解析NS3文件
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.file_path, 'rb') as f:
                self.file = f
                
                # 获取文件大小
                f.seek(0, 2)
                self.file_size = f.tell()
                f.seek(0, 0)
                
                # 1. 读取Basic Header
                if not self._read_basic_header():
                    return False
                
                # 2. 读取Extended Headers
                if not self._read_extended_headers():
                    return False
                
                # 3. 读取Data Packets
                if not self._read_data_packets():
                    return False
                
            return True
            
        except Exception as e:
            print(f"Error parsing NS3 file: {e}")
            return False
    
    def _read_basic_header(self) -> bool:
        """读取Basic Header (314字节)"""
        f = self.file
        
        # File Type (8字节)
        file_type = struct.unpack('8s', f.read(8))[0].decode('ascii').strip('\x00')
        
        # Version (2字节)
        ver_major, ver_minor = struct.unpack('2B', f.read(2))
        version = f"{ver_major}.{ver_minor}"
        
        # Header Size (4字节)
        header_size = struct.unpack('I', f.read(4))[0]
        
        # Label (16字节)
        label = struct.unpack('16s', f.read(16))[0].decode('ascii').strip('\x00')
        
        # Reserved (256字节) - 跳过
        f.seek(256, 1)
        
        # Period (4字节)
        period = struct.unpack('I', f.read(4))[0]
        
        # Clock Frequency (4字节)
        clock_fs = struct.unpack('I', f.read(4))[0]
        
        # Time Origin (8 × 2字节)
        time_origin = list(struct.unpack('8H', f.read(16)))
        
        # Number of Electrodes (4字节)
        num_elec = struct.unpack('I', f.read(4))[0]
        
        # 验证位置
        current_pos = f.tell()
        if current_pos != 314:
            print(f"Error: Basic header size mismatch. Expected 314, got {current_pos}")
            return False
        
        # 验证Extended Header大小
        expected_header_size = 314 + num_elec * 66
        if header_size != expected_header_size:
            print(f"Error: Extended header size mismatch. Expected {expected_header_size}, got {header_size}")
            return False
        
        self.basic_header = NS3BasicHeader(
            file_type=file_type,
            version=version,
            header_size=header_size,
            label=label,
            period=period,
            clock_fs=clock_fs,
            fs=clock_fs / period,
            time_origin=time_origin,
            num_elec=num_elec
        )
        
        return True
    
    def _read_extended_headers(self) -> bool:
        """读取Extended Headers (每个电极66字节)"""
        f = self.file
        num_elec = self.basic_header.num_elec
        
        for i in range(num_elec):
            # Packet ID (2字节)
            packet_id = struct.unpack('2s', f.read(2))[0].decode('ascii')
            
            if packet_id != 'CC':
                print(f"Error: Unknown PacketID '{packet_id}' for electrode {i+1}")
                return False
            
            # Electrode ID (2字节)
            elec_id = struct.unpack('H', f.read(2))[0]
            
            # Electrode Label (16字节)
            elec_label = struct.unpack('16s', f.read(16))[0].decode('ascii').strip('\x00')
            
            # Connector (1字节) - 转换为字母 A, B, C, D
            connector_code = struct.unpack('B', f.read(1))[0]
            connector = chr(64 + connector_code)  # 1->A, 2->B, etc.
            
            # Pin (1字节)
            pin = struct.unpack('B', f.read(1))[0]
            
            # Min/Max Digital Value (2 × 2字节)
            min_digital = struct.unpack('h', f.read(2))[0]
            max_digital = struct.unpack('h', f.read(2))[0]
            
            # Min/Max Analog Value (2 × 2字节)
            min_analog = struct.unpack('h', f.read(2))[0]
            max_analog = struct.unpack('h', f.read(2))[0]
            
            # Analog Unit (16字节)
            analog_unit = struct.unpack('16s', f.read(16))[0].decode('ascii').strip('\x00').lower()
            
            # High Cut Filter (4 + 4 + 2字节)
            high_cut_freq = struct.unpack('I', f.read(4))[0]
            high_cut_order = struct.unpack('I', f.read(4))[0]
            high_cut_type = struct.unpack('H', f.read(2))[0]
            
            # Low Cut Filter (4 + 4 + 2字节)
            low_cut_freq = struct.unpack('I', f.read(4))[0]
            low_cut_order = struct.unpack('I', f.read(4))[0]
            low_cut_type = struct.unpack('H', f.read(2))[0]
            
            ext_header = NS3ExtendedHeader(
                packet_id=packet_id,
                elec_id=elec_id,
                elec_label=elec_label,
                connector=connector,
                pin=pin,
                min_digital_value=min_digital,
                max_digital_value=max_digital,
                min_analog_value=min_analog,
                max_analog_value=max_analog,
                analog_unit=analog_unit,
                high_cut_freq=high_cut_freq,
                high_cut_order=high_cut_order,
                high_cut_type=high_cut_type,
                low_cut_freq=low_cut_freq,
                low_cut_order=low_cut_order,
                low_cut_type=low_cut_type
            )
            
            self.extended_headers.append(ext_header)
        
        # 验证位置
        current_pos = f.tell()
        if current_pos != self.basic_header.header_size:
            print(f"Error: Extended header position mismatch")
            return False
        
        return True
    
    def _read_data_packets(self) -> bool:
        """读取Data Packets"""
        f = self.file
        num_elec = self.basic_header.num_elec
        
        all_data = []
        packet_count = 0
        
        while f.tell() < self.file_size:
            # Header (1字节) - 应为0x01
            header = struct.unpack('B', f.read(1))[0]
            
            if header != 0x01:
                print(f"Error: Invalid packet header 0x{header:02x} at packet {packet_count + 1}")
                return False
            
            # Timestamp (4字节)
            timestamp = struct.unpack('I', f.read(4))[0]
            
            # Number of Samples (4字节)
            num_samples = struct.unpack('I', f.read(4))[0]
            
            # Data (num_elec × num_samples × 2字节)
            data_size = num_elec * num_samples
            raw_bytes = f.read(data_size * 2)
            
            if len(raw_bytes) < data_size * 2:
                print(f"Warning: Incomplete data packet at position {f.tell()}")
                break
            
            # 解析为int16数组 [电极数 × 样本数]
            data = np.frombuffer(raw_bytes, dtype=np.int16).reshape(num_elec, num_samples)
            
            packet = NS3DataPacket(
                header=header,
                timestamp=timestamp,
                num_samples=num_samples,
                data=data
            )
            
            self.data_packets.append(packet)
            all_data.append(data)
            packet_count += 1
        
        # 合并所有数据包
        if all_data:
            self.raw_data = np.hstack(all_data)  # [通道数 × 总样本数]
        
        return True
    
    def get_conversion_factors(self) -> np.ndarray:
        """
        计算数字值到物理值的转换因子
        
        Returns:
            转换因子数组 [通道数]
        """
        if self._conversion_factors is None:
            factors = []
            for ext in self.extended_headers:
                # 转换公式: physical = digital × (max_analog - min_analog) / (max_digital - min_digital)
                digital_range = ext.max_digital_value - ext.min_digital_value
                analog_range = ext.max_analog_value - ext.min_analog_value
                
                if digital_range == 0:
                    factor = 1.0
                else:
                    factor = analog_range / digital_range
                
                factors.append(factor)
            
            self._conversion_factors = np.array(factors)
        
        return self._conversion_factors
    
    def get_physical_data(self) -> Optional[np.ndarray]:
        """
        获取物理值数据 (uV)
        
        Returns:
            物理值数组 [通道数 × 样本数]，单位uV
        """
        if self.raw_data is None:
            return None
        
        factors = self.get_conversion_factors()
        
        # 应用转换因子 [通道数 × 1] × [通道数 × 样本数]
        physical_data = self.raw_data * factors[:, np.newaxis]
        
        return physical_data.astype(np.float32)
    
    def get_channel_info(self) -> List[Dict]:
        """
        获取通道信息
        
        Returns:
            通道信息列表
        """
        channels = []
        for ext in self.extended_headers:
            channels.append({
                'channel_id': ext.elec_id,
                'electrode_id': ext.elec_id,
                'electrode_label': ext.elec_label,
                'connector': ext.connector,
                'pin': ext.pin,
                'unit': ext.analog_unit,
                'conversion_factor': self.get_conversion_factors()[len(channels)]
            })
        return channels
    
    def get_sampling_rate(self) -> float:
        """获取采样率 (Hz)"""
        return self.basic_header.fs if self.basic_header else 0.0
    
    def get_duration(self) -> float:
        """获取记录时长 (秒)"""
        if self.raw_data is None or self.basic_header is None:
            return 0.0
        return self.raw_data.shape[1] / self.basic_header.fs


def parse_ns3(file_path: str) -> Optional[Dict]:
    """
    便捷函数：解析NS3文件并返回所有数据
    
    Args:
        file_path: NS3文件路径
        
    Returns:
        包含解析结果的字典，解析失败返回None
    """
    parser = NS3Parser(file_path)
    
    if not parser.parse():
        return None
    
    return {
        'basic_header': parser.basic_header,
        'extended_headers': parser.extended_headers,
        'raw_data': parser.raw_data,
        'physical_data': parser.get_physical_data(),
        'channel_info': parser.get_channel_info(),
        'sampling_rate': parser.get_sampling_rate(),
        'duration': parser.get_duration()
    }


if __name__ == '__main__':
    # 测试代码
    import sys
    
    # 使用真实数据测试
    test_file = r"c:\Users\buaal\Desktop\NeuroPrime\coco1227rawdata\FC_Grating_014.ns3"
    
    print(f"Parsing {test_file}...")
    result = parse_ns3(test_file)
    
    if result:
        print("\n=== Basic Header ===")
        bh = result['basic_header']
        print(f"File Type: {bh.file_type}")
        print(f"Version: {bh.version}")
        print(f"Sampling Rate: {bh.fs:.1f} Hz")
        print(f"Number of Channels: {bh.num_elec}")
        print(f"Duration: {result['duration']:.2f} seconds")
        
        print("\n=== First 3 Channels ===")
        for i, ch in enumerate(result['channel_info'][:3]):
            print(f"Channel {i+1}: ID={ch['channel_id']}, Label={ch['electrode_label']}, "
                  f"Connector={ch['connector']}, Pin={ch['pin']}")
        
        print("\n=== Data Shape ===")
        print(f"Raw Data: {result['raw_data'].shape}")
        print(f"Physical Data: {result['physical_data'].shape}")
        print(f"Data Range: [{result['physical_data'].min():.2f}, {result['physical_data'].max():.2f}] uV")
        
        print("\nParsing successful!")
    else:
        print("Parsing failed!")
        sys.exit(1)
