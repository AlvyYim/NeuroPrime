"""
Data Preprocessor - 数据预处理层

为所有分析算法提供统一的数据加载、验证、合并和对齐功能。

设计目标：
1. 解耦数据加载与算法执行
2. 统一管理多试验数据合并
3. 支持时间对齐配置
4. 缓存机制避免重复加载

用法:
    preprocessor = DataPreprocessor(project_manager)
    
    # 准备数据
    input_data = preprocessor.prepare_input(
        data_items=[...],
        algorithm_name="ROCAnalysis",
        time_alignment_config=time_config
    )
    
    # 运行算法
    output = algorithm.run(input_data, parameters)
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
import numpy as np
from pathlib import Path

try:
    from .base import AlgorithmInput
    from ..visualization.time_alignment import TimeAlignmentConfig
except ImportError:
    from base import AlgorithmInput
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from visualization.time_alignment import TimeAlignmentConfig


@dataclass
class DataCacheEntry:
    """数据缓存条目"""
    data: np.ndarray
    trial_name: str
    data_id: str
    data_type: str
    load_time: float = field(default_factory=lambda: __import__('time').time())


class DataPreprocessor:
    """
    数据预处理器
    
    统一管理多组数据的加载、验证、时间对齐和合并。
    为算法提供一致的AlgorithmInput接口。
    """
    
    def __init__(self, project_manager):
        """
        初始化数据预处理器
        
        Args:
            project_manager: 工程管理器实例
        """
        self.project_manager = project_manager
        self._cache: Dict[str, DataCacheEntry] = {}
        self._last_data_signature: Optional[str] = None
    
    def _get_data_signature(self, data_items: List[Dict]) -> str:
        """
        生成数据项集合的签名，用于检测数据选择是否变化
        
        Args:
            data_items: 数据项列表
            
        Returns:
            签名字符串
        """
        # 按trial_name和id排序后生成签名
        sorted_items = sorted(
            [(item.get('trial_name', ''), item.get('id', '')) 
             for item in data_items if isinstance(item, dict)],
            key=lambda x: f"{x[0]}/{x[1]}"
        )
        return "|".join([f"{t}/{i}" for t, i in sorted_items])
    
    def _get_unique_id(self, trial_name: str, data_id: str) -> str:
        """生成唯一标识符"""
        return f"{trial_name}/{data_id}"
    
    def _load_data_item(self, item: Dict[str, Any], 
                       time_config: Optional[TimeAlignmentConfig] = None) -> Optional[np.ndarray]:
        """
        加载单个数据项
        
        Args:
            item: 数据项字典
            time_config: 时间对齐配置
            
        Returns:
            加载的数据，失败返回None
        """
        if not isinstance(item, dict):
            print(f"[DataPreprocessor] 警告: 数据项不是字典类型: {type(item)}")
            return None
        
        data_id = item.get('id', '')
        trial_name = item.get('trial_name', '')
        data_type = item.get('data_type', '')
        unique_id = self._get_unique_id(trial_name, data_id)
        
        print(f"[DataPreprocessor] 加载数据: {unique_id}, type={data_type}")
        
        try:
            trial = self.project_manager.get_trial(trial_name)
            hdf5_path = self.project_manager.get_hdf5_path(trial_name)
            
            if not trial or not hdf5_path or not hdf5_path.exists():
                print(f"[DataPreprocessor] 错误: 无法找到试验 {trial_name} 的HDF5文件")
                return None
            
            import h5py
            with h5py.File(str(hdf5_path), 'r') as f:
                # 根据数据类型构建HDF5路径
                if data_type == 'spike':
                    path = '/spikes/spike_times'
                elif data_type == 'lfp':
                    path = '/signals/lfp_data'
                elif data_type == 'behavior':
                    path = 'behavior/events'
                else:
                    path = f'/{data_id}'
                
                if path not in f:
                    print(f"[DataPreprocessor] 错误: HDF5中未找到路径 {path}")
                    return None
                
                data = f[path][:]
                
                # 应用时间对齐（如果需要）
                if time_config is not None and data_type != 'spike':
                    aligned_window = time_config.get_aligned_time_window(unique_id)
                    if aligned_window:
                        start_time, end_time = aligned_window
                        # 从属性获取采样率
                        sampling_rate = f[path].attrs.get('sampling_rate', 2000.0)
                        
                        # 计算样本索引
                        start_sample = int(start_time * sampling_rate)
                        end_sample = int(end_time * sampling_rate)
                        
                        # 截取数据
                        if data.ndim == 2:  # LFP数据 [通道 x 样本]
                            start_sample = max(0, min(start_sample, data.shape[1]))
                            end_sample = max(0, min(end_sample, data.shape[1]))
                            if start_sample < end_sample:
                                data = data[:, start_sample:end_sample]
                        else:  # 1D数据
                            start_sample = max(0, min(start_sample, len(data)))
                            end_sample = max(0, min(end_sample, len(data)))
                            if start_sample < end_sample:
                                data = data[start_sample:end_sample]
                
                print(f"[DataPreprocessor] 成功加载: shape={data.shape if hasattr(data, 'shape') else len(data)}")
                return data
                
        except Exception as e:
            print(f"[DataPreprocessor] 加载数据失败 {unique_id}: {e}")
            return None
    
    def _load_trials_info(self, trial_names: Set[str], 
                         time_offsets: Dict[str, float]) -> List[Dict]:
        """
        加载多个试验的试次信息
        
        Args:
            trial_names: 试验名称集合
            time_offsets: 各试验的时间偏移量
            
        Returns:
            试次信息列表
        """
        all_trial_info = []
        
        for trial_name in trial_names:
            time_offset = time_offsets.get(trial_name, 0.0)
            
            try:
                hdf5_path = self.project_manager.get_hdf5_path(trial_name)
                if not hdf5_path or not hdf5_path.exists():
                    continue
                
                import h5py
                with h5py.File(str(hdf5_path), 'r') as f:
                    trials_path = None
                    for path in ['behavior/trials', '/behavior/trials']:
                        if path in f:
                            trials_path = path
                            break
                    
                    if trials_path:
                        trials_data = f[trials_path][:]
                        for i, trial in enumerate(trials_data):
                            try:
                                trial_dict = {
                                    'trial_num': int(trial['trial_num']) if 'trial_num' in trial.dtype.names else i + 1,
                                    'start_time': float(trial['start_time']) + time_offset if 'start_time' in trial.dtype.names else time_offset,
                                    'stim_cnd': int(trial['stim_cnd']) if 'stim_cnd' in trial.dtype.names else 0,
                                    'trial_source': trial_name
                                }
                                all_trial_info.append(trial_dict)
                            except Exception:
                                continue
            except Exception as e:
                print(f"[DataPreprocessor] 加载试验 {trial_name} 信息失败: {e}")
                continue
        
        return all_trial_info
    
    def prepare_input(self, 
                     data_items: List[Dict[str, Any]], 
                     algorithm_name: str,
                     time_alignment_config: Optional[TimeAlignmentConfig] = None) -> Tuple[AlgorithmInput, Dict[str, Any]]:
        """
        准备算法输入数据
        
        Args:
            data_items: 数据项列表
            algorithm_name: 算法名称
            time_alignment_config: 时间对齐配置（可选）
            
        Returns:
            (AlgorithmInput, metadata) 元组
        """
        print(f"[DataPreprocessor] 准备输入数据: algorithm={algorithm_name}, items={len(data_items)}")
        
        input_data = AlgorithmInput()
        metadata = {
            'data_sources': {},
            'time_offsets': {},
            'load_errors': []
        }
        
        # 按数据类型分组
        spike_items = []
        lfp_items = []
        behavior_items = []
        
        for item in data_items:
            if not isinstance(item, dict):
                continue
            data_type = item.get('data_type', '')
            if data_type == 'spike':
                spike_items.append(item)
            elif data_type == 'lfp':
                lfp_items.append(item)
            elif data_type == 'behavior':
                behavior_items.append(item)
        
        print(f"[DataPreprocessor] 数据分组: spike={len(spike_items)}, lfp={len(lfp_items)}, behavior={len(behavior_items)}")
        
        # 处理Spike数据（多试验合并）
        if spike_items:
            all_spike_times = []
            trial_time_offsets = {}
            current_offset = 0.0
            
            for item in spike_items:
                trial_name = item.get('trial_name', '')
                data_id = item.get('id', '')
                unique_id = self._get_unique_id(trial_name, data_id)
                
                # 加载数据
                spike_data = self._load_data_item(item, time_alignment_config)
                
                if spike_data is not None:
                    # 记录时间偏移
                    trial_time_offsets[trial_name] = current_offset
                    
                    # 转换并添加偏移
                    if isinstance(spike_data, np.ndarray):
                        spike_list = spike_data.tolist()
                    else:
                        spike_list = list(spike_data)
                    
                    offset_spikes = [t + current_offset for t in spike_list]
                    all_spike_times.extend(offset_spikes)
                    
                    # 更新偏移量
                    if spike_list:
                        current_offset += max(spike_list) + 10.0
                    else:
                        current_offset += 100.0
                    
                    metadata['data_sources'][unique_id] = {
                        'trial_name': trial_name,
                        'data_type': 'spike',
                        'time_offset': trial_time_offsets[trial_name],
                        'n_points': len(spike_list)
                    }
                else:
                    metadata['load_errors'].append(f"Failed to load spike data: {unique_id}")
            
            if all_spike_times:
                input_data.spike_times = np.array(all_spike_times)
                print(f"[DataPreprocessor] Spike数据: 合并了 {len(spike_items)} 个来源, 共 {len(all_spike_times)} 个Spike")
        
        # 处理LFP数据（通常只取第一个）
        if lfp_items:
            # 对于LFP数据，通常只使用第一个数据项
            item = lfp_items[0]
            trial_name = item.get('trial_name', '')
            data_id = item.get('id', '')
            unique_id = self._get_unique_id(trial_name, data_id)
            
            lfp_data = self._load_data_item(item, time_alignment_config)
            
            if lfp_data is not None:
                # 确保是2D数组 [通道 x 样本]
                if lfp_data.ndim == 1:
                    lfp_data = lfp_data.reshape(1, -1)
                
                input_data.lfp_data = lfp_data
                input_data.num_channels = lfp_data.shape[0]
                
                # 尝试获取采样率
                try:
                    hdf5_path = self.project_manager.get_hdf5_path(trial_name)
                    if hdf5_path and hdf5_path.exists():
                        import h5py
                        with h5py.File(str(hdf5_path), 'r') as f:
                            if '/signals/lfp_data' in f:
                                input_data.sampling_rate = f['/signals/lfp_data'].attrs.get('sampling_rate', 2000.0)
                except:
                    pass
                
                metadata['data_sources'][unique_id] = {
                    'trial_name': trial_name,
                    'data_type': 'lfp',
                    'shape': lfp_data.shape
                }
                print(f"[DataPreprocessor] LFP数据: shape={lfp_data.shape}, sampling_rate={input_data.sampling_rate}")
            else:
                metadata['load_errors'].append(f"Failed to load LFP data: {unique_id}")
        
        # 加载试次信息
        trial_names = set()
        for item in data_items:
            if isinstance(item, dict):
                trial_name = item.get('trial_name', '')
                if trial_name:
                    trial_names.add(trial_name)
        
        # 如果没有behavior数据项，从spike数据项的试验加载试次信息
        if not behavior_items and spike_items:
            for item in spike_items:
                trial_name = item.get('trial_name', '')
                if trial_name:
                    trial_names.add(trial_name)
        
        # 加载试次信息
        trial_time_offsets = metadata.get('time_offsets', {})
        all_trial_info = self._load_trials_info(trial_names, trial_time_offsets)
        
        if all_trial_info:
            input_data.trial_info = all_trial_info
            print(f"[DataPreprocessor] 试次信息: 从 {len(trial_names)} 个试验加载了 {len(all_trial_info)} 个试次")
        
        # 设置时间范围
        if time_alignment_config:
            input_data.time_range = (time_alignment_config.global_start, 
                                    time_alignment_config.global_start + time_alignment_config.global_duration)
        
        metadata['algorithm_name'] = algorithm_name
        metadata['n_data_items'] = len(data_items)
        metadata['trial_names'] = list(trial_names)
        
        print(f"[DataPreprocessor] 输入数据准备完成")
        return input_data, metadata
    
    def clear_cache(self):
        """清除数据缓存"""
        self._cache.clear()
        self._last_data_signature = None
        print("[DataPreprocessor] 缓存已清除")


if __name__ == '__main__':
    # 测试代码
    print("=== Testing DataPreprocessor ===\n")
    
    # 注意：这里需要实际的project_manager才能测试
    # 以下只是接口演示
    
    print("DataPreprocessor 类定义完成")
    print("用法:")
    print("  preprocessor = DataPreprocessor(project_manager)")
    print("  input_data, metadata = preprocessor.prepare_input(")
    print("      data_items=data_items,")
    print("      algorithm_name='ROCAnalysis',")
    print("      time_alignment_config=time_config")
    print("  )")
    print("  output = algorithm.run(input_data, parameters)")
