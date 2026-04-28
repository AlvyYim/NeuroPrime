"""
Time Alignment Configuration - 时间对齐配置

为可视化/分析前对多组数据进行时间对齐提供配置管理
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field


@dataclass
class DataTimeConfig:
    """单个数据项的时间配置"""
    data_id: str
    original_range: Tuple[float, float]  # 原始时间范围 (start, end)
    start_time: float = 0.0  # 对齐后的起始时间
    duration: float = 10.0   # 持续时间
    
    def get_end_time(self) -> float:
        """获取对齐后的结束时间"""
        return self.start_time + self.duration
    
    def is_valid(self) -> bool:
        """检查配置是否有效（在原始范围内）"""
        aligned_start = self.start_time
        aligned_end = self.get_end_time()
        orig_start, orig_end = self.original_range
        
        return (aligned_start >= orig_start and 
                aligned_end <= orig_end and
                self.duration > 0)


class TimeAlignmentConfig:
    """
    时间对齐配置
    
    使用场景：
    1. 用户在数据选择列表勾选多个数据项
    2. 点击"时间对齐"按钮，弹出时间对齐对话框
    3. 系统显示各数据的原始时间范围
    4. 用户设置统一的初始时间和持续时间
    5. 对齐参数传递给后续的可视化或分析算法
    
    示例:
        config = TimeAlignmentConfig()
        
        # 添加数据项
        config.add_data_item("trial1_lfp", (0.0, 100.0))
        config.add_data_item("trial1_spike", (0.0, 100.0))
        
        # 设置全局时间窗口
        config.set_global_time_window(10.0, 50.0)
        
        # 验证对齐
        is_valid, error_msg = config.validate_alignment()
        
        # 获取对齐后的时间窗口
        start, end = config.get_aligned_time_window("trial1_lfp")
    """
    
    def __init__(self):
        """初始化时间对齐配置"""
        # 各数据项的对齐参数
        self._data_configs: Dict[str, DataTimeConfig] = {}
        
        # 全局对齐参数（所有数据共用）
        self.global_start: float = 0.0
        self.global_duration: float = 10.0
        
        # 对齐模式
        self.sync_mode: str = 'global'  # 'global'(全局同步) / 'individual'(独立设置)
    
    def add_data_item(self, data_id: str, original_time_range: Tuple[float, float]):
        """
        添加数据项到对齐配置
        
        Args:
            data_id: 数据项标识符
            original_time_range: 原始时间范围 (start, end)
        """
        self._data_configs[data_id] = DataTimeConfig(
            data_id=data_id,
            original_range=original_time_range,
            start_time=self.global_start,
            duration=self.global_duration
        )
    
    def remove_data_item(self, data_id: str) -> bool:
        """
        移除数据项
        
        Args:
            data_id: 数据项标识符
            
        Returns:
            True if removed successfully
        """
        if data_id in self._data_configs:
            del self._data_configs[data_id]
            return True
        return False
    
    def set_global_time_window(self, start: float, duration: float):
        """
        设置全局时间窗口（修改一行，其他行自动同步）
        
        Args:
            start: 初始时间（秒）
            duration: 持续时间（秒）
        """
        self.global_start = start
        self.global_duration = duration
        
        # 同步到所有数据项
        if self.sync_mode == 'global':
            for config in self._data_configs.values():
                config.start_time = start
                config.duration = duration
    
    def set_individual_time_window(self, data_id: str, start: float, duration: float) -> bool:
        """
        设置单个数据项的时间窗口（独立模式）
        
        Args:
            data_id: 数据项标识符
            start: 起始时间
            duration: 持续时间
            
        Returns:
            True if successful
        """
        if data_id not in self._data_configs:
            return False
        
        config = self._data_configs[data_id]
        config.start_time = start
        config.duration = duration
        return True
    
    def get_aligned_time_window(self, data_id: str) -> Optional[Tuple[float, float]]:
        """
        获取指定数据项对齐后的时间窗口
        
        Args:
            data_id: 数据项标识符
            
        Returns:
            (对齐后起始时间, 对齐后结束时间)，未找到返回None
        """
        config = self._data_configs.get(data_id)
        if config is None:
            return None
        
        return (config.start_time, config.get_end_time())
    
    def get_original_time_range(self, data_id: str) -> Optional[Tuple[float, float]]:
        """
        获取指定数据项的原始时间范围
        
        Args:
            data_id: 数据项标识符
            
        Returns:
            (原始起始时间, 原始结束时间)，未找到返回None
        """
        config = self._data_configs.get(data_id)
        if config is None:
            return None
        
        return config.original_range
    
    def validate_alignment(self) -> Tuple[bool, str]:
        """
        验证对齐参数是否有效
        
        Returns:
            (是否有效, 错误信息)
        """
        for data_id, config in self._data_configs.items():
            if not config.is_valid():
                orig_start, orig_end = config.original_range
                aligned_start = config.start_time
                aligned_end = config.get_end_time()
                
                error_msg = (
                    f"数据项 '{data_id}' 的对齐时间范围 [{aligned_start:.2f}, {aligned_end:.2f}] "
                    f"超出原始范围 [{orig_start:.2f}, {orig_end:.2f}]"
                )
                return False, error_msg
        
        return True, ""
    
    def get_all_data_ids(self) -> List[str]:
        """
        获取所有数据项ID
        
        Returns:
            数据项ID列表
        """
        return list(self._data_configs.keys())
    
    def get_data_config(self, data_id: str) -> Optional[DataTimeConfig]:
        """
        获取数据项配置
        
        Args:
            data_id: 数据项标识符
            
        Returns:
            DataTimeConfig对象，未找到返回None
        """
        return self._data_configs.get(data_id)
    
    def get_common_time_range(self) -> Optional[Tuple[float, float]]:
        """
        获取所有数据项的共同时间范围
        
        Returns:
            (共同起始时间, 共同结束时间)，无数据返回None
        """
        if not self._data_configs:
            return None
        
        # 计算所有数据项原始范围的交集
        max_start = max(config.original_range[0] for config in self._data_configs.values())
        min_end = min(config.original_range[1] for config in self._data_configs.values())
        
        if max_start >= min_end:
            return None
        
        return (max_start, min_end)
    
    def suggest_alignment(self) -> Tuple[float, float]:
        """
        建议对齐参数（使用共同时间范围）
        
        Returns:
            (建议起始时间, 建议持续时间)
        """
        common_range = self.get_common_time_range()
        if common_range is None:
            return (0.0, 10.0)
        
        start, end = common_range
        duration = end - start
        
        return (start, duration)
    
    def apply_suggested_alignment(self):
        """应用建议的对齐参数"""
        start, duration = self.suggest_alignment()
        self.set_global_time_window(start, duration)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典，便于传递给算法
        
        Returns:
            配置字典
        """
        return {
            'global_start': self.global_start,
            'global_duration': self.global_duration,
            'sync_mode': self.sync_mode,
            'data_configs': {
                data_id: {
                    'original_range': config.original_range,
                    'start_time': config.start_time,
                    'duration': config.duration
                }
                for data_id, config in self._data_configs.items()
            }
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'TimeAlignmentConfig':
        """
        从字典创建配置
        
        Args:
            config_dict: 配置字典
            
        Returns:
            TimeAlignmentConfig对象
        """
        config = cls()
        config.global_start = config_dict.get('global_start', 0.0)
        config.global_duration = config_dict.get('global_duration', 10.0)
        config.sync_mode = config_dict.get('sync_mode', 'global')
        
        for data_id, data_config in config_dict.get('data_configs', {}).items():
            config.add_data_item(
                data_id=data_id,
                original_time_range=tuple(data_config['original_range'])
            )
            config.set_individual_time_window(
                data_id=data_id,
                start=data_config['start_time'],
                duration=data_config['duration']
            )
        
        return config
    
    def clear(self):
        """清除所有配置"""
        self._data_configs.clear()
        self.global_start = 0.0
        self.global_duration = 10.0


if __name__ == '__main__':
    # 测试代码
    print("=== Testing TimeAlignmentConfig ===\n")
    
    # 创建配置
    config = TimeAlignmentConfig()
    
    # 添加数据项
    print("1. Adding data items...")
    config.add_data_item("trial1_lfp", (0.0, 100.0))
    config.add_data_item("trial1_spike", (0.0, 100.0))
    config.add_data_item("trial2_lfp", (5.0, 95.0))
    print(f"   Added {len(config.get_all_data_ids())} data items")
    print()
    
    # 获取共同时间范围
    print("2. Common time range:")
    common_range = config.get_common_time_range()
    print(f"   {common_range}")
    print()
    
    # 建议对齐
    print("3. Suggested alignment:")
    suggested = config.suggest_alignment()
    print(f"   Start: {suggested[0]:.2f}s, Duration: {suggested[1]:.2f}s")
    print()
    
    # 应用建议对齐
    print("4. Applying suggested alignment...")
    config.apply_suggested_alignment()
    print(f"   Global start: {config.global_start:.2f}s")
    print(f"   Global duration: {config.global_duration:.2f}s")
    print()
    
    # 验证对齐
    print("5. Validating alignment...")
    is_valid, error_msg = config.validate_alignment()
    print(f"   Valid: {is_valid}")
    if not is_valid:
        print(f"   Error: {error_msg}")
    print()
    
    # 获取对齐后的时间窗口
    print("6. Aligned time windows:")
    for data_id in config.get_all_data_ids():
        window = config.get_aligned_time_window(data_id)
        print(f"   {data_id}: [{window[0]:.2f}, {window[1]:.2f}]")
    print()
    
    # 测试无效对齐
    print("7. Testing invalid alignment...")
    config.set_global_time_window(50.0, 100.0)  # 超出某些数据项的范围
    is_valid, error_msg = config.validate_alignment()
    print(f"   Valid: {is_valid}")
    if not is_valid:
        print(f"   Error: {error_msg}")
    print()
    
    # 转换为字典
    print("8. Converting to dict...")
    config_dict = config.to_dict()
    print(f"   Keys: {list(config_dict.keys())}")
    print()
    
    # 从字典恢复
    print("9. Restoring from dict...")
    restored_config = TimeAlignmentConfig.from_dict(config_dict)
    print(f"   Restored {len(restored_config.get_all_data_ids())} data items")
    print()
    
    print("✅ TimeAlignmentConfig tests completed!")
