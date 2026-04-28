"""
LFP Analysis Algorithms - LFP分析算法

提供功率谱分析和时频分析功能
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import signal
from scipy.ndimage import gaussian_filter1d

try:
    from .base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput, ParameterType, create_parameter
except ImportError:
    from base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput, ParameterType, create_parameter


class LFPPowerSpectrum(BaseAlgorithm):
    """
    LFP功率谱分析算法
    
    计算LFP信号的功率谱密度（PSD），支持多种窗函数和平均方法。
    
    可设置参数:
    - window_type: 窗函数类型（hann/hamming/blackman/bartlett）
    - nfft: FFT点数
    - noverlap: 重叠样本数
    - freq_range: 频率范围（Hz）
    - average_method: 平均方法（mean/median）
    """
    
    def __init__(self):
        super().__init__()
        self.name = "LFPPowerSpectrum"
        self.description = "LFP功率谱密度分析"
        self.category = "LFP"
        self.version = "1.0"
        self.required_data_types = ['lfp']
        self.data_requirements_description = "需要LFP信号数据"
    
    def get_parameters_schema(self):
        return [
            create_parameter(
                "window_type", ParameterType.SELECT,
                "窗函数类型", "hann",
                options=["hann", "hamming", "blackman", "bartlett", "boxcar"]
            ),
            create_parameter(
                "nfft", ParameterType.INTEGER,
                "FFT点数", 2048,
                min_value=256, max_value=8192
            ),
            create_parameter(
                "noverlap", ParameterType.INTEGER,
                "重叠样本数", 1024,
                min_value=0, max_value=4096
            ),
            create_parameter(
                "freq_low", ParameterType.FLOAT,
                "最低频率（Hz）", 1.0,
                min_value=0.1, max_value=100.0
            ),
            create_parameter(
                "freq_high", ParameterType.FLOAT,
                "最高频率（Hz）", 100.0,
                min_value=10.0, max_value=500.0
            ),
            create_parameter(
                "average_method", ParameterType.SELECT,
                "平均方法", "mean",
                options=["mean", "median"]
            ),
            create_parameter(
                "smooth_sigma", ParameterType.FLOAT,
                "平滑系数（高斯滤波）", 1.0,
                min_value=0.0, max_value=5.0
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
            window_type = parameters.get("window_type", "hann")
            nfft = parameters.get("nfft", 2048)
            noverlap = parameters.get("noverlap", 1024)
            freq_low = parameters.get("freq_low", 1.0)
            freq_high = parameters.get("freq_high", 100.0)
            average_method = parameters.get("average_method", "mean")
            smooth_sigma = parameters.get("smooth_sigma", 1.0)
            
            # 检查数据长度并调整参数
            data_length = lfp_data.shape[1]
            
            # 如果nfft超过数据长度，自动调整
            if nfft > data_length:
                nfft = min(256, data_length // 2 * 2)  # 使用小于数据长度的最大2的幂
                if nfft < 256:
                    nfft = data_length // 2 * 2
                noverlap = nfft // 2
                print(f"警告: FFT点数超过数据长度，自动调整为 nfft={nfft}, noverlap={noverlap}")
            
            # 获取窗函数
            window = self._get_window(window_type, nfft)
            
            all_psd = []
            all_freqs = None
            
            # 对每个通道计算PSD
            for ch_idx in range(lfp_data.shape[0]):
                channel_data = lfp_data[ch_idx, :]
                
                # 计算PSD
                freqs, psd = signal.welch(
                    channel_data, fs,
                    window=window,
                    nfft=nfft,
                    noverlap=noverlap,
                    scaling='density',
                    average=average_method
                )
                
                if all_freqs is None:
                    all_freqs = freqs
                
                all_psd.append(psd)
            
            # 转换为数组
            all_psd = np.array(all_psd)
            
            # 应用平滑
            if smooth_sigma > 0:
                for i in range(all_psd.shape[0]):
                    all_psd[i, :] = gaussian_filter1d(all_psd[i, :], sigma=smooth_sigma)
            
            # 频率范围筛选
            freq_mask = (all_freqs >= freq_low) & (all_freqs <= freq_high)
            freqs_filtered = all_freqs[freq_mask]
            psd_filtered = all_psd[:, freq_mask]
            
            # 计算统计信息
            psd_mean = np.mean(psd_filtered, axis=0)
            psd_std = np.std(psd_filtered, axis=0)
            
            # 计算频段功率
            band_powers = self._calculate_band_powers(freqs_filtered, psd_mean)
            
            execution_time = time.time() - start_time
            
            # 准备输出
            output = AlgorithmOutput(
                data={
                    'frequencies': freqs_filtered,
                    'psd': psd_filtered,
                    'psd_mean': psd_mean,
                    'psd_std': psd_std
                },
                statistics={
                    'total_power': float(np.sum(psd_mean)),
                    'peak_frequency': float(freqs_filtered[np.argmax(psd_mean)]),
                    'peak_power': float(np.max(psd_mean)),
                    **band_powers
                },
                plot_config={
                    'type': 'power_spectrum',
                    'title': 'LFP Power Spectrum',
                    'xlabel': 'Frequency (Hz)',
                    'ylabel': 'Power (μV²/Hz)',
                    'xscale': 'log',
                    'yscale': 'log'
                },
                export_data={
                    'frequencies': freqs_filtered,
                    'psd': psd_filtered,
                    'psd_mean': psd_mean
                },
                metadata={
                    'band_powers': band_powers,
                    'freq_range': (freq_low, freq_high),
                    'n_channels': lfp_data.shape[0]
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
    
    def _get_window(self, window_type: str, nfft: int) -> np.ndarray:
        """获取窗函数"""
        if window_type == "hann":
            return signal.windows.hann(nfft)
        elif window_type == "hamming":
            return signal.windows.hamming(nfft)
        elif window_type == "blackman":
            return signal.windows.blackman(nfft)
        elif window_type == "bartlett":
            return signal.windows.bartlett(nfft)
        else:  # boxcar
            return signal.windows.boxcar(nfft)
    
    def _calculate_band_powers(self, freqs: np.ndarray, psd: np.ndarray) -> Dict[str, float]:
        """计算各频段功率"""
        bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 100)
        }
        
        band_powers = {}
        for band_name, (low, high) in bands.items():
            mask = (freqs >= low) & (freqs <= high)
            if np.any(mask):
                band_powers[f'{band_name}_power'] = float(np.sum(psd[mask]))
            else:
                band_powers[f'{band_name}_power'] = 0.0
        
        return band_powers


class LFPSpectrogram(BaseAlgorithm):
    """
    LFP时频分析算法（Spectrogram）
    
    计算LFP信号的时频表示，支持多种窗函数。
    
    可设置参数:
    - window_type: 窗函数类型
    - nperseg: 每段样本数
    - noverlap: 重叠样本数
    - nfft: FFT点数
    - freq_range: 频率范围（Hz）
    """
    
    def __init__(self):
        super().__init__()
        self.name = "LFPSpectrogram"
        self.description = "LFP时频分析（Spectrogram）"
        self.category = "LFP"
        self.version = "1.0"
        self.required_data_types = ['lfp']
        self.data_requirements_description = "需要LFP信号数据"
    
    def get_parameters_schema(self):
        return [
            create_parameter(
                "window_type", ParameterType.SELECT,
                "窗函数类型", "hann",
                options=["hann", "hamming", "blackman", "bartlett"]
            ),
            create_parameter(
                "nperseg", ParameterType.INTEGER,
                "每段样本数", 256,
                min_value=64, max_value=2048
            ),
            create_parameter(
                "noverlap", ParameterType.INTEGER,
                "重叠样本数", 128,
                min_value=0, max_value=1024
            ),
            create_parameter(
                "nfft", ParameterType.INTEGER,
                "FFT点数", 256,
                min_value=64, max_value=2048
            ),
            create_parameter(
                "freq_low", ParameterType.FLOAT,
                "最低频率（Hz）", 1.0,
                min_value=0.1, max_value=100.0
            ),
            create_parameter(
                "freq_high", ParameterType.FLOAT,
                "最高频率（Hz）", 100.0,
                min_value=10.0, max_value=500.0
            ),
            create_parameter(
                "channel_idx", ParameterType.INTEGER,
                "通道索引（-1计算均值）", -1,
                min_value=-1, max_value=1000
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
            window_type = parameters.get("window_type", "hann")
            nperseg = parameters.get("nperseg", 256)
            noverlap = parameters.get("noverlap", 128)
            nfft = parameters.get("nfft", 256)
            freq_low = parameters.get("freq_low", 1.0)
            freq_high = parameters.get("freq_high", 100.0)
            channel_idx = parameters.get("channel_idx", -1)
            
            # 选择通道数据
            if channel_idx == -1:
                # 平均所有通道
                data = np.mean(lfp_data, axis=0)
            else:
                if channel_idx >= lfp_data.shape[0]:
                    return AlgorithmOutput(
                        success=False,
                        error_message=f"Channel index {channel_idx} out of range"
                    )
                data = lfp_data[channel_idx, :]
            
            # 检查数据长度并调整参数
            data_length = len(data)
            if nperseg > data_length:
                nperseg = min(256, data_length // 2)
                if nperseg < 64:
                    nperseg = data_length // 2
                noverlap = nperseg // 2
                nfft = nperseg
                print(f"警告: 窗口长度超过数据长度，自动调整为 nperseg={nperseg}, noverlap={noverlap}")
            
            # 获取窗函数
            window = self._get_window(window_type, nperseg)
            
            # 计算Spectrogram
            freqs, times, Sxx = signal.spectrogram(
                data, fs,
                window=window,
                nperseg=nperseg,
                noverlap=noverlap,
                nfft=nfft,
                scaling='density'
            )
            
            # 频率范围筛选
            freq_mask = (freqs >= freq_low) & (freqs <= freq_high)
            freqs_filtered = freqs[freq_mask]
            Sxx_filtered = Sxx[freq_mask, :]
            
            # 转换为dB
            Sxx_db = 10 * np.log10(Sxx_filtered + 1e-10)
            
            # 计算统计信息
            mean_power = np.mean(Sxx_filtered, axis=1)
            max_power_time = np.max(np.mean(Sxx_filtered, axis=0))
            
            execution_time = time.time() - start_time
            
            # 准备输出
            output = AlgorithmOutput(
                data={
                    'frequencies': freqs_filtered,
                    'times': times,
                    'spectrogram': Sxx_filtered,
                    'spectrogram_db': Sxx_db
                },
                statistics={
                    'mean_power': float(np.mean(Sxx_filtered)),
                    'max_power': float(np.max(Sxx_filtered)),
                    'max_power_time': float(max_power_time),
                    'freq_resolution': float(freqs[1] - freqs[0]) if len(freqs) > 1 else 0,
                    'time_resolution': float(times[1] - times[0]) if len(times) > 1 else 0
                },
                plot_config={
                    'type': 'spectrogram',
                    'title': 'LFP Spectrogram',
                    'xlabel': 'Time (s)',
                    'ylabel': 'Frequency (Hz)',
                    'colorbar_label': 'Power (dB)'
                },
                export_data={
                    'frequencies': freqs_filtered,
                    'times': times,
                    'spectrogram': Sxx_filtered,
                    'spectrogram_db': Sxx_db
                },
                metadata={
                    'freq_range': (freq_low, freq_high),
                    'channel_idx': channel_idx,
                    'nperseg': nperseg,
                    'noverlap': noverlap
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
    
    def _get_window(self, window_type: str, nperseg: int) -> np.ndarray:
        """获取窗函数"""
        if window_type == "hann":
            return signal.windows.hann(nperseg)
        elif window_type == "hamming":
            return signal.windows.hamming(nperseg)
        elif window_type == "blackman":
            return signal.windows.blackman(nperseg)
        else:  # bartlett
            return signal.windows.bartlett(nperseg)


if __name__ == '__main__':
    # 测试代码
    print("=== Testing LFP Analysis Algorithms ===\n")
    
    # 创建模拟LFP数据
    fs = 1000  # 1kHz采样率
    duration = 10.0  # 10秒
    n_samples = int(fs * duration)
    n_channels = 4
    
    # 生成模拟LFP数据（包含不同频段成分）
    np.random.seed(42)
    t = np.arange(n_samples) / fs
    
    lfp_data = np.zeros((n_channels, n_samples))
    for ch in range(n_channels):
        # 添加不同频段的成分
        delta = 10 * np.sin(2 * np.pi * 2 * t)  # 2 Hz (delta)
        theta = 5 * np.sin(2 * np.pi * 6 * t)   # 6 Hz (theta)
        alpha = 3 * np.sin(2 * np.pi * 10 * t)  # 10 Hz (alpha)
        beta = 2 * np.sin(2 * np.pi * 20 * t)   # 20 Hz (beta)
        gamma = 1 * np.sin(2 * np.pi * 40 * t)  # 40 Hz (gamma)
        noise = np.random.randn(n_samples) * 2
        
        lfp_data[ch, :] = delta + theta + alpha + beta + gamma + noise
    
    # 测试功率谱分析
    print("1. Testing LFPPowerSpectrum...")
    psd_analyzer = LFPPowerSpectrum()
    
    input_data = AlgorithmInput(
        lfp_data=lfp_data,
        sampling_rate=fs
    )
    
    params = psd_analyzer.get_default_parameters()
    params['freq_high'] = 100.0
    
    output = psd_analyzer.run(input_data, params)
    
    if output.success:
        print(f"   ✓ PSD analysis successful")
        print(f"     Total power: {output.statistics['total_power']:.2f} μV²")
        print(f"     Peak frequency: {output.statistics['peak_frequency']:.2f} Hz")
        print(f"     Peak power: {output.statistics['peak_power']:.2f} μV²/Hz")
        print(f"     Delta power: {output.statistics.get('delta_power', 0):.2f}")
        print(f"     Theta power: {output.statistics.get('theta_power', 0):.2f}")
        print(f"     Alpha power: {output.statistics.get('alpha_power', 0):.2f}")
        print(f"     Execution time: {output.execution_time:.4f}s")
    else:
        print(f"   ✗ PSD analysis failed: {output.error_message}")
    print()
    
    # 测试时频分析
    print("2. Testing LFPSpectrogram...")
    spec_analyzer = LFPSpectrogram()
    
    spec_params = spec_analyzer.get_default_parameters()
    spec_params['freq_high'] = 100.0
    spec_params['channel_idx'] = 0
    
    spec_output = spec_analyzer.run(input_data, spec_params)
    
    if spec_output.success:
        print(f"   ✓ Spectrogram analysis successful")
        print(f"     Spectrogram shape: {spec_output.data['spectrogram'].shape}")
        print(f"     Frequency range: {spec_output.data['frequencies'][0]:.1f} - {spec_output.data['frequencies'][-1]:.1f} Hz")
        print(f"     Time range: {spec_output.data['times'][0]:.2f} - {spec_output.data['times'][-1]:.2f} s")
        print(f"     Mean power: {spec_output.statistics['mean_power']:.2f}")
        print(f"     Execution time: {spec_output.execution_time:.4f}s")
    else:
        print(f"   ✗ Spectrogram analysis failed: {spec_output.error_message}")
    
    print("\n✅ LFP analysis tests completed!")
