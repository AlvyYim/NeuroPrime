"""
View Raw LFP Data - 查看原始LFP数据算法

这是一个示例自定义算法，用于查看原始LFP信号数据的可视化
仅支持LFP数据，不支持Spike或行为数据
只显示第一个通道的数据
"""

import numpy as np
from typing import Dict, Any

# 导入基类 - 当从scheduler加载时，路径已经设置好了
from src.algorithms.base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput, ParameterType, create_parameter


class ViewRawLFPData(BaseAlgorithm):
    """
    查看原始LFP数据算法
    
    功能：
    - 仅支持LFP信号数据
    - 只显示第一个通道的数据
    - 显示完整时间范围
    """
    
    def __init__(self):
        super().__init__()
        self.name = "ViewRawLFPData"
        self.description = "查看原始LFP信号数据（仅支持LFP数据，只显示第一个通道）"
        self.category = "自定义算法"
        self.version = "1.2"
        self.author = "NeuroPrime"
    
    def get_parameters_schema(self):
        """获取参数配置模式 - 无需参数"""
        return []
    
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        """验证输入数据 - 仅接受LFP数据"""
        return input_data.lfp_data is not None and input_data.lfp_data.size > 0
    
    def run(self, input_data: AlgorithmInput, parameters: Dict) -> AlgorithmOutput:
        """
        运行算法
        
        Args:
            input_data: 输入数据，必须包含lfp_data
            parameters: 参数字典（本算法不使用参数）
            
        Returns:
            AlgorithmOutput: 算法输出结果
        """
        import time
        start_time = time.time()
        
        try:
            lfp_data = input_data.lfp_data
            fs = input_data.sampling_rate
            
            # 获取数据维度
            # 支持1D数据 [样本数] 和 2D数据 [通道数 x 样本数]
            if lfp_data.ndim == 1:
                # 1D数据: 转换为2D [1 x 样本数]
                lfp_data = lfp_data.reshape(1, -1)
            
            n_channels = lfp_data.shape[0]
            n_samples = lfp_data.shape[1]
            total_duration = n_samples / fs
            
            # 只取第一个通道的数据
            selected_data = lfp_data[0:1, :]  # 保持2D形状 [1 x 样本数]
            channel_indices = [0]
            
            # 计算统计信息（基于第一个通道）
            first_channel_data = lfp_data[0, :]
            stats = {
                'mean': float(np.mean(first_channel_data)),
                'std': float(np.std(first_channel_data)),
                'min': float(np.min(first_channel_data)),
                'max': float(np.max(first_channel_data)),
                'n_channels': n_channels,
                'n_samples': n_samples,
                'duration': total_duration,
                'sampling_rate': fs,
                'displayed_channel': 1  # 显示的是第1个通道
            }
            
            # 生成完整时间轴
            times = np.arange(n_samples) / fs
            
            execution_time = time.time() - start_time
            
            # 准备输出
            output = AlgorithmOutput(
                data={
                    'signal_data': selected_data,
                    'times': times,
                    'channel_indices': channel_indices,
                    'all_channel_indices': list(range(n_channels)),
                    'sampling_rate': fs,
                    'data_type': 'lfp'
                },
                statistics=stats,
                plot_config={
                    'type': 'raw_signal',
                    'title': f'LFP原始信号 - 通道1 / 共{n_channels}通道 - {total_duration:.1f}秒',
                    'xlabel': '时间 (s)',
                    'ylabel': '幅值 (μV)',
                    'show_grid': True
                },
                export_data={
                    'signal_data': lfp_data,  # 导出所有通道数据
                    'times': times,
                    'channel_indices': list(range(n_channels)),
                    'sampling_rate': fs,
                    'statistics': stats
                },
                metadata={
                    'data_type': 'lfp',
                    'n_channels': n_channels,
                    'n_samples': n_samples,
                    'duration': total_duration,
                    'sampling_rate': fs,
                    'displayed_channel': 1
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


# 算法信息（用于动态加载）
ALGORITHM_INFO = {
    'name': 'ViewRawLFPData',
    'description': '查看原始LFP信号数据（仅支持LFP数据，只显示第一个通道）',
    'category': '自定义算法',
    'version': '1.2',
    'author': 'NeuroPrime',
    'class': ViewRawLFPData
}


if __name__ == '__main__':
    # 测试代码
    print("=== Testing ViewRawLFPData Algorithm ===\n")
    
    # 创建模拟LFP数据（20个通道）
    fs = 1000  # 1kHz采样率
    duration = 10.0  # 10秒
    n_samples = int(fs * duration)
    n_channels = 20
    
    # 生成模拟LFP数据
    np.random.seed(42)
    t = np.arange(n_samples) / fs
    
    lfp_data = np.zeros((n_channels, n_samples))
    for ch in range(n_channels):
        delta = 10 * np.sin(2 * np.pi * 2 * t)
        theta = 5 * np.sin(2 * np.pi * 6 * t)
        alpha = 3 * np.sin(2 * np.pi * 10 * t)
        noise = np.random.randn(n_samples) * 2
        lfp_data[ch, :] = delta + theta + alpha + noise
    
    # 创建算法实例
    algorithm = ViewRawLFPData()
    
    # 测试
    print("Testing ViewRawLFPData (single channel)...")
    input_data = AlgorithmInput(
        lfp_data=lfp_data,
        sampling_rate=fs
    )
    params = {}
    output = algorithm.run(input_data, params)
    
    if output.success:
        print(f"   ✓ Success!")
        print(f"     Total Channels: {output.statistics['n_channels']}")
        print(f"     Displayed Channel: {output.statistics['displayed_channel']}")
        print(f"     Duration: {output.statistics['duration']:.1f}s")
        print(f"     Data shape: {output.data['signal_data'].shape}")
    else:
        print(f"   ✗ Failed: {output.error_message}")
    
    print("\n✅ ViewRawLFPData tests completed!")
