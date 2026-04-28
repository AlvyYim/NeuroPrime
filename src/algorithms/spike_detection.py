"""
Spike Detection Algorithms - Spike检测算法

提供基于阈值的Spike检测功能
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import signal
from scipy.ndimage import maximum_filter1d

try:
    from .base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput, ParameterType, create_parameter
except ImportError:
    from base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput, ParameterType, create_parameter


class SpikeDetectionThreshold(BaseAlgorithm):
    """
    基于阈值的Spike检测算法
    
    使用电压阈值检测Spike事件，支持正负阈值和多种阈值计算方法。
    
    可设置参数:
    - threshold_factor: 阈值系数（相对于噪声标准差）
    - threshold_type: 阈值类型（positive/negative/both）
    - window_ms: 检测窗口大小（毫秒）
    - refractory_ms: 不应期（毫秒）
    - filter_low: 高通滤波器截止频率（Hz）
    - filter_high: 低通滤波器截止频率（Hz）
    """
    
    def __init__(self):
        super().__init__()
        self.name = "SpikeDetectionThreshold"
        self.description = "基于电压阈值的Spike检测"
        self.category = "Spike"
        self.version = "1.0"
        self.required_data_types = ['lfp']
        self.data_requirements_description = "需要LFP信号数据"
    
    def get_parameters_schema(self):
        return [
            create_parameter(
                "threshold_factor", ParameterType.FLOAT,
                "阈值系数（相对于噪声标准差）", 4.5,
                min_value=2.0, max_value=10.0
            ),
            create_parameter(
                "threshold_type", ParameterType.SELECT,
                "阈值类型", "both",
                options=["positive", "negative", "both"]
            ),
            create_parameter(
                "window_ms", ParameterType.FLOAT,
                "检测窗口大小（毫秒）", 1.0,
                min_value=0.5, max_value=5.0
            ),
            create_parameter(
                "refractory_ms", ParameterType.FLOAT,
                "不应期（毫秒）", 1.0,
                min_value=0.5, max_value=3.0
            ),
            create_parameter(
                "filter_low", ParameterType.FLOAT,
                "高通滤波器截止频率（Hz）", 300.0,
                min_value=100.0, max_value=1000.0
            ),
            create_parameter(
                "filter_high", ParameterType.FLOAT,
                "低通滤波器截止频率（Hz）", 3000.0,
                min_value=2000.0, max_value=6000.0
            ),
            create_parameter(
                "use_filter", ParameterType.BOOLEAN,
                "应用带通滤波器", True
            )
        ]
    
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        return input_data.lfp_data is not None and input_data.sampling_rate > 0
    
    def run(self, input_data: AlgorithmInput, parameters: Dict) -> AlgorithmOutput:
        import time
        start_time = time.time()
        
        try:
            lfp_data = input_data.lfp_data
            fs = input_data.sampling_rate
            
            # 提取参数
            threshold_factor = parameters.get("threshold_factor", 4.5)
            threshold_type = parameters.get("threshold_type", "both")
            window_ms = parameters.get("window_ms", 1.0)
            refractory_ms = parameters.get("refractory_ms", 1.0)
            filter_low = parameters.get("filter_low", 300.0)
            filter_high = parameters.get("filter_high", 3000.0)
            use_filter = parameters.get("use_filter", True)
            
            # 计算样本数
            window_samples = int(window_ms * fs / 1000)
            refractory_samples = int(refractory_ms * fs / 1000)
            
            all_spike_times = []
            all_spike_channels = []
            all_spike_waveforms = []
            
            # 对每个通道进行检测
            for ch_idx in range(lfp_data.shape[0]):
                channel_data = lfp_data[ch_idx, :]
                
                # 应用带通滤波器
                if use_filter:
                    filtered_data = self._bandpass_filter(
                        channel_data, fs, filter_low, filter_high
                    )
                else:
                    filtered_data = channel_data
                
                # 计算阈值
                noise_std = np.median(np.abs(filtered_data)) / 0.6745
                threshold = threshold_factor * noise_std
                
                # 检测Spike
                spike_indices = self._detect_spikes(
                    filtered_data, threshold, threshold_type, 
                    window_samples, refractory_samples
                )
                
                # 提取波形
                waveforms = self._extract_waveforms(
                    filtered_data, spike_indices, window_samples
                )
                
                # 转换为时间（秒）
                spike_times = spike_indices / fs
                
                all_spike_times.extend(spike_times)
                all_spike_channels.extend([ch_idx] * len(spike_times))
                all_spike_waveforms.extend(waveforms)
            
            # 按时间排序
            sort_indices = np.argsort(all_spike_times)
            spike_times = np.array(all_spike_times)[sort_indices]
            spike_channels = np.array(all_spike_channels)[sort_indices]
            spike_waveforms = np.array(all_spike_waveforms)[sort_indices]
            
            execution_time = time.time() - start_time
            
            # 准备输出
            output = AlgorithmOutput(
                data={
                    'spike_times': spike_times,
                    'spike_channels': spike_channels,
                    'spike_waveforms': spike_waveforms
                },
                statistics={
                    'total_spikes': len(spike_times),
                    'spikes_per_channel': len(spike_times) / lfp_data.shape[0] if lfp_data.shape[0] > 0 else 0,
                    'firing_rate': len(spike_times) / (lfp_data.shape[1] / fs) / lfp_data.shape[0] if lfp_data.shape[0] > 0 else 0
                },
                plot_config={
                    'type': 'spike_detection',
                    'title': 'Spike Detection Results',
                    'xlabel': 'Time (s)',
                    'ylabel': 'Channel'
                },
                export_data={
                    'spike_times': spike_times,
                    'spike_channels': spike_channels,
                    'spike_waveforms': spike_waveforms
                },
                execution_time=execution_time,
                success=True
            )
            
            self._record_execution(input_data, parameters, output)
            return output
            
        except Exception as e:
            return AlgorithmOutput(
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    def _bandpass_filter(self, data: np.ndarray, fs: float, 
                        lowcut: float, highcut: float) -> np.ndarray:
        """应用带通滤波器"""
        nyquist = fs / 2
        
        # 确保截止频率在有效范围内 (0 < Wn < 1)
        # 归一化频率 = 截止频率 / 奈奎斯特频率
        low = lowcut / nyquist
        high = highcut / nyquist
        
        # 限制在有效范围内
        low = max(0.001, min(low, 0.999))
        high = max(0.001, min(high, 0.999))
        
        # 确保low < high
        if low >= high:
            low = high * 0.1
        
        b, a = signal.butter(4, [low, high], btype='band')
        return signal.filtfilt(b, a, data)
    
    def _detect_spikes(self, data: np.ndarray, threshold: float,
                      threshold_type: str, window_samples: int,
                      refractory_samples: int) -> np.ndarray:
        """检测Spike峰值"""
        if threshold_type == "positive":
            crossings = data > threshold
        elif threshold_type == "negative":
            crossings = data < -threshold
        else:  # both
            crossings = np.abs(data) > threshold
        
        # 找到所有穿越点
        crossing_indices = np.where(crossings)[0]
        
        if len(crossing_indices) == 0:
            return np.array([])
        
        # 应用不应期
        spike_indices = []
        last_spike = -refractory_samples
        
        for idx in crossing_indices:
            if idx - last_spike >= refractory_samples:
                # 在窗口内找到峰值
                start_idx = max(0, idx - window_samples // 2)
                end_idx = min(len(data), idx + window_samples // 2)
                
                if threshold_type == "positive":
                    peak_idx = start_idx + np.argmax(data[start_idx:end_idx])
                elif threshold_type == "negative":
                    peak_idx = start_idx + np.argmin(data[start_idx:end_idx])
                else:
                    peak_idx = start_idx + np.argmax(np.abs(data[start_idx:end_idx]))
                
                spike_indices.append(peak_idx)
                last_spike = peak_idx
        
        return np.array(spike_indices)
    
    def _extract_waveforms(self, data: np.ndarray, spike_indices: np.ndarray,
                          window_samples: int) -> np.ndarray:
        """提取Spike波形"""
        half_window = window_samples // 2
        waveforms = []
        
        for idx in spike_indices:
            start = max(0, idx - half_window)
            end = min(len(data), idx + half_window)
            
            waveform = data[start:end]
            
            # 填充到固定长度
            if len(waveform) < window_samples:
                pad_before = (window_samples - len(waveform)) // 2
                pad_after = window_samples - len(waveform) - pad_before
                waveform = np.pad(waveform, (pad_before, pad_after), mode='constant')
            
            waveforms.append(waveform)
        
        return np.array(waveforms) if waveforms else np.array([]).reshape(0, window_samples)


class SpikeSortingPCA(BaseAlgorithm):
    """
    基于PCA的Spike排序算法
    
    使用PCA降维和K-Means聚类对Spike进行排序。
    
    可设置参数:
    - n_components: PCA主成分数量
    - n_clusters: 聚类数量
    - max_iterations: 最大迭代次数
    """
    
    def __init__(self):
        super().__init__()
        self.name = "SpikeSortingPCA"
        self.description = "基于PCA和K-Means的Spike排序"
        self.category = "Spike"
        self.version = "1.0"
        self.required_data_types = ['spike']
        self.data_requirements_description = "需要Spike数据"
    
    def get_parameters_schema(self):
        return [
            create_parameter(
                "n_components", ParameterType.INTEGER,
                "PCA主成分数量", 3,
                min_value=2, max_value=10
            ),
            create_parameter(
                "n_clusters", ParameterType.INTEGER,
                "聚类数量", 3,
                min_value=2, max_value=10
            ),
            create_parameter(
                "max_iterations", ParameterType.INTEGER,
                "最大迭代次数", 100,
                min_value=50, max_value=500
            ),
            create_parameter(
                "random_state", ParameterType.INTEGER,
                "随机种子", 42,
                min_value=0, max_value=1000
            )
        ]
    
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        return (input_data.spike_waveforms is not None and 
                len(input_data.spike_waveforms) > 0)
    
    def run(self, input_data: AlgorithmInput, parameters: Dict) -> AlgorithmOutput:
        import time
        start_time = time.time()
        
        try:
            waveforms = input_data.spike_waveforms
            
            # 提取参数
            n_components = parameters.get("n_components", 3)
            n_clusters = parameters.get("n_clusters", 3)
            max_iterations = parameters.get("max_iterations", 100)
            random_state = parameters.get("random_state", 42)
            
            # 数据预处理
            # 归一化
            waveforms_normalized = (waveforms - np.mean(waveforms, axis=1, keepdims=True)) / (
                np.std(waveforms, axis=1, keepdims=True) + 1e-10
            )
            
            # PCA降维
            # n_components必须小于等于min(n_samples, n_features)
            max_components = min(waveforms.shape[0], waveforms.shape[1])
            n_components = min(n_components, max_components)
            
            from sklearn.decomposition import PCA
            pca = PCA(n_components=n_components)
            features = pca.fit_transform(waveforms_normalized)
            
            # K-Means聚类
            # n_clusters必须小于等于样本数
            n_clusters = min(n_clusters, waveforms.shape[0])
            
            from sklearn.cluster import KMeans
            kmeans = KMeans(
                n_clusters=n_clusters,
                max_iter=max_iterations,
                random_state=random_state,
                n_init=10
            )
            labels = kmeans.fit_predict(features)
            
            # 计算聚类中心波形
            cluster_centers = []
            for i in range(n_clusters):
                cluster_waveforms = waveforms[labels == i]
                if len(cluster_waveforms) > 0:
                    cluster_centers.append(np.mean(cluster_waveforms, axis=0))
                else:
                    cluster_centers.append(np.zeros(waveforms.shape[1]))
            
            cluster_centers = np.array(cluster_centers)
            
            # 计算每个聚类的统计信息
            cluster_stats = {}
            for i in range(n_clusters):
                cluster_size = np.sum(labels == i)
                cluster_stats[f'cluster_{i}'] = {
                    'size': int(cluster_size),
                    'percentage': float(cluster_size / len(labels) * 100)
                }
            
            execution_time = time.time() - start_time
            
            # 准备输出
            output = AlgorithmOutput(
                data={
                    'labels': labels,
                    'features': features,
                    'cluster_centers': cluster_centers,
                    'explained_variance_ratio': pca.explained_variance_ratio_
                },
                statistics={
                    'total_spikes': len(labels),
                    'n_clusters': n_clusters,
                    **{f'cluster_{i}_count': int(np.sum(labels == i)) for i in range(n_clusters)}
                },
                plot_config={
                    'type': 'spike_sorting',
                    'title': 'Spike Sorting Results',
                    'n_clusters': n_clusters,
                    'n_components': n_components
                },
                export_data={
                    'labels': labels,
                    'features': features,
                    'cluster_centers': cluster_centers
                },
                metadata={
                    'cluster_stats': cluster_stats,
                    'explained_variance_ratio': pca.explained_variance_ratio_.tolist()
                },
                execution_time=execution_time,
                success=True
            )
            
            self._record_execution(input_data, parameters, output)
            return output
            
        except Exception as e:
            return AlgorithmOutput(
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )


if __name__ == '__main__':
    # 测试代码
    print("=== Testing Spike Detection and Sorting Algorithms ===\n")
    
    # 创建模拟数据
    fs = 20000  # 20kHz采样率
    duration = 1.0  # 1秒
    n_samples = int(fs * duration)
    n_channels = 4
    
    # 生成模拟LFP数据（包含一些Spike）
    np.random.seed(42)
    lfp_data = np.random.randn(n_channels, n_samples) * 5  # 噪声
    
    # 添加一些模拟Spike
    for ch in range(n_channels):
        spike_times = np.random.choice(n_samples, size=20, replace=False)
        for t in spike_times:
            if t > 10 and t < n_samples - 10:
                # 添加高斯形状的Spike
                window = np.arange(-10, 11)
                spike_shape = -50 * np.exp(-window**2 / 8)  # 负向Spike
                lfp_data[ch, t-10:t+11] += spike_shape
    
    # 测试Spike检测
    print("1. Testing SpikeDetectionThreshold...")
    detector = SpikeDetectionThreshold()
    
    input_data = AlgorithmInput(
        lfp_data=lfp_data,
        sampling_rate=fs
    )
    
    params = detector.get_default_parameters()
    params['threshold_factor'] = 3.5
    
    output = detector.run(input_data, params)
    
    if output.success:
        print(f"   ✓ Detection successful")
        print(f"     Total spikes: {output.statistics['total_spikes']}")
        print(f"     Spikes per channel: {output.statistics['spikes_per_channel']:.1f}")
        print(f"     Firing rate: {output.statistics['firing_rate']:.2f} Hz")
        print(f"     Execution time: {output.execution_time:.4f}s")
    else:
        print(f"   ✗ Detection failed: {output.error_message}")
    print()
    
    # 测试Spike排序
    if output.success and len(output.data['spike_waveforms']) > 0:
        print("2. Testing SpikeSortingPCA...")
        sorter = SpikeSortingPCA()
        
        sort_input = AlgorithmInput(
            spike_waveforms=output.data['spike_waveforms']
        )
        
        sort_params = sorter.get_default_parameters()
        sort_params['n_clusters'] = 3
        
        sort_output = sorter.run(sort_input, sort_params)
        
        if sort_output.success:
            print(f"   ✓ Sorting successful")
            print(f"     Total spikes: {sort_output.statistics['total_spikes']}")
            print(f"     Number of clusters: {sort_output.statistics['n_clusters']}")
            for i in range(sort_params['n_clusters']):
                count = sort_output.statistics.get(f'cluster_{i}_count', 0)
                print(f"     Cluster {i}: {count} spikes")
            print(f"     Execution time: {sort_output.execution_time:.4f}s")
        else:
            print(f"   ✗ Sorting failed: {sort_output.error_message}")
    else:
        print("2. Skipping SpikeSortingPCA test (no spikes detected)")
    
    print("\n✅ Spike detection and sorting tests completed!")
