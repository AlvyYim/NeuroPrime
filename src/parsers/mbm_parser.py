"""
MBM Parser - 解析Blackrock MBM行为数据文件

参考: LoadSpike.m中的LoadMbm函数
"""

import struct
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MBMInfo:
    """MBM文件信息"""
    nTrials: int
    StimID: np.ndarray
    RespCode: np.ndarray
    RespTime: np.ndarray
    Fixation: np.ndarray
    RawStimID: np.ndarray
    RawRespCode: np.ndarray
    RawRespTime: np.ndarray
    RawFixation: np.ndarray


def parse_mbm(file_path: str) -> Optional[MBMInfo]:
    """
    解析MBM文件
    
    Args:
        file_path: MBM文件路径
        
    Returns:
        MBMInfo对象，如果解析失败返回None
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"MBM文件不存在: {file_path}")
            return None
        
        with open(file_path, 'rb') as f:
            # 读取文件大小
            f.seek(0, 2)
            file_size = f.tell()
            f.seek(0, 0)
            
            # 读取基本信息
            # 参考LoadSpike.m中的LoadMbm函数
            # 假设MBM文件格式与LoadSpike.m中处理的一致
            
            # 尝试读取试次数
            # 注意：这里需要根据实际MBM文件格式调整
            # 暂时实现一个基本版本
            n_trials = file_size // (4 * 4)  # 假设每个试次有4个4字节的字段
            
            if n_trials <= 0:
                print("MBM文件格式不正确")
                return None
            
            # 读取数据
            f.seek(0, 0)
            data = np.fromfile(f, dtype=np.float32)
            
            if len(data) < n_trials * 4:
                print("MBM文件数据不足")
                return None
            
            # 重组数据
            data = data.reshape(-1, 4)
            n_trials = data.shape[0]
            
            StimID = data[:, 0].astype(int)
            RespCode = data[:, 1].astype(int)
            RespTime = data[:, 2]
            Fixation = data[:, 3].astype(int)
            
            # 创建MBMInfo对象
            mbm_info = MBMInfo(
                nTrials=n_trials,
                StimID=StimID,
                RespCode=RespCode,
                RespTime=RespTime,
                Fixation=Fixation,
                RawStimID=StimID.copy(),
                RawRespCode=RespCode.copy(),
                RawRespTime=RespTime.copy(),
                RawFixation=Fixation.copy()
            )
            
            return mbm_info
            
    except Exception as e:
        print(f"解析MBM文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_mbm(file_path: str) -> Optional[MBMInfo]:
    """
    便捷函数：加载MBM文件
    
    Args:
        file_path: MBM文件路径
        
    Returns:
        MBMInfo对象，如果加载失败返回None
    """
    return parse_mbm(file_path)
