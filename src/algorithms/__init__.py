"""
Algorithms Module - 算法模块

提供NeuroPrime的核心分析算法实现
"""

from .base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput, AlgorithmParameter, ParameterType, create_parameter
from .scheduler import AlgorithmScheduler

# Spike检测和排序
from .spike_detection import SpikeDetectionThreshold, SpikeSortingPCA

# LFP分析
from .lfp_analysis import LFPPowerSpectrum, LFPSpectrogram

# Spike分析
from .spike_analysis import PSTHAnalysis, RasterPlotAnalysis, TuningCurveAnalysis

# 行为分析
from .behavior_analysis import ROCAnalysis

# 解码
from .decoding import LDADecoder, SVMClassifier, RandomForestClassifier

__all__ = [
    # 基类和调度器
    'BaseAlgorithm', 'AlgorithmInput', 'AlgorithmOutput', 'AlgorithmParameter',
    'ParameterType', 'create_parameter', 'AlgorithmScheduler',
    # Spike算法
    'SpikeDetectionThreshold', 'SpikeSortingPCA',
    # LFP算法
    'LFPPowerSpectrum', 'LFPSpectrogram',
    # 行为分析算法
    'PSTHAnalysis', 'RasterPlotAnalysis', 'TuningCurveAnalysis', 'ROCAnalysis',
    # 解码算法
    'LDADecoder', 'SVMClassifier', 'RandomForestClassifier'
]
