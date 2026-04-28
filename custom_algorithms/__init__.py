"""
Custom Algorithms - 自定义算法模块

用户可以在此目录下添加自定义算法脚本
"""

from pathlib import Path
import sys

# 添加自定义算法目录到路径
custom_algorithms_path = Path(__file__).parent
if str(custom_algorithms_path) not in sys.path:
    sys.path.insert(0, str(custom_algorithms_path))

# 导出所有自定义算法
from .view_raw_lfp_data import ViewRawLFPData

__all__ = ['ViewRawLFPData']
