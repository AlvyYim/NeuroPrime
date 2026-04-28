"""
VisualizationArea - 可视化区域组件

提供图表显示、标签页管理、图表交互等功能
使用matplotlib进行实际的图表绘制
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QToolBar, QSplitter,
    QFrame, QMessageBox, QFileDialog, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon

# 导入样式
from .styles import Styles

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入matplotlib
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

# 设置matplotlib中文字体
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = True  # 使用Unicode负号
matplotlib.rcParams['mathtext.default'] = 'regular'  # 使用常规字体渲染数学符号


class PlotTab(QWidget):
    """图表标签页 - 使用matplotlib绘制"""
    
    def __init__(self, title: str, plot_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        
        self.title = title
        self.plot_data = plot_data
        
        self._init_ui()
        self._draw_plot()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 工具栏
        toolbar = QToolBar()
        
        save_action = QAction("保存", self)
        save_action.triggered.connect(self._save_plot)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        zoom_in_action = QAction("放大", self)
        zoom_in_action.triggered.connect(self._zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("缩小", self)
        zoom_out_action.triggered.connect(self._zoom_out)
        toolbar.addAction(zoom_out_action)
        
        reset_action = QAction("重置", self)
        reset_action.triggered.connect(self._reset_view)
        toolbar.addAction(reset_action)
        
        layout.addWidget(toolbar)
        
        # 创建matplotlib图表
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: white;")
        
        layout.addWidget(self.canvas)
        
        # 添加matplotlib导航工具栏
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.mpl_toolbar)
    
    def _draw_plot(self):
        """根据数据类型绘制图表"""
        data_type = self.plot_data.get('data_type', 'unknown')
        
        try:
            if data_type == 'signal':
                self._draw_signal()
            elif data_type == 'raw_signal':
                self._draw_raw_signal()
            elif data_type == 'spike_waveforms':
                self._draw_spike_waveforms()
            elif data_type == 'spike_sorting':
                self._draw_spike_sorting()
            elif data_type == 'spike_raster':
                self._draw_spike_raster()
            elif data_type == 'raster':
                self._draw_raster()
            elif data_type == 'psth':
                self._draw_psth()
            elif data_type == 'tuning_curve':
                self._draw_tuning_curve()
            elif data_type == 'power_spectrum':
                self._draw_power_spectrum()
            elif data_type == 'spectrogram':
                self._draw_spectrogram()
            elif data_type == 'roc_curve':
                self._draw_roc_curve()
            elif data_type == 'decoding_results':
                self._draw_decoding_results()
            else:
                self._draw_default()
        except Exception as e:
            # 绘制失败时显示错误信息
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, f'绘图失败: {str(e)}', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='red')
            ax.set_axis_off()
            self.canvas.draw()
    
    def _draw_signal(self):
        """绘制信号波形"""
        signal_data = self.plot_data.get('data', np.random.randn(1000))
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        time = np.arange(len(signal_data)) / 1000.0  # 假设采样率1000Hz
        ax.plot(time, signal_data, linewidth=0.5)
        ax.set_xlabel('时间 (s)')
        ax.set_ylabel('幅度')
        ax.set_title(self.title)
        ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
    
    def _draw_raw_signal(self):
        """绘制原始信号（支持多通道，3x3网格布局）"""
        signal_data = self.plot_data.get('signal_data', np.random.randn(1, 1000))
        
        # 处理3D数据（形状为[1 × 样本数 × 通道数]）
        if signal_data.ndim == 3 and signal_data.shape[0] == 1:
            # 转换为2D数据（形状为[通道数 × 样本数]）
            signal_data = signal_data[0].T
        
        times = self.plot_data.get('times', np.arange(signal_data.shape[1]) / 1000.0)
        channel_indices = self.plot_data.get('channel_indices', [0])
        
        # 确保channel_indices与通道数匹配
        if len(channel_indices) != signal_data.shape[0] and signal_data.ndim == 2:
            channel_indices = list(range(signal_data.shape[0]))
        
        # 获取绘图配置
        plot_config = self.plot_data.get('plot_config', {})
        show_grid = plot_config.get('show_grid', True)
        line_color = plot_config.get('line_color', 'blue')
        xlabel = plot_config.get('xlabel', '时间 (s)')
        ylabel = plot_config.get('ylabel', '幅值 (μV)')
        
        # 定义多通道颜色列表
        channel_colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        # 每张图最多显示9个子图（3x3网格）
        max_channels_per_plot = 9
        grid_rows = 3
        grid_cols = 3
        
        n_channels = len(channel_indices)
        
        # 计算需要的绘图数量
        n_plots = (n_channels + max_channels_per_plot - 1) // max_channels_per_plot
        
        # 如果只有一个绘图，直接绘制
        if n_plots == 1:
            self.figure.clear()
            
            if n_channels == 1:
                # 单通道 - 绘制一个图
                ax = self.figure.add_subplot(111)
                ax.plot(times, signal_data[0, :], linewidth=0.8, color=line_color)
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel)
                ax.set_title(self.title)
                if show_grid:
                    ax.grid(True, alpha=0.3)
            else:
                # 多通道 - 使用3x3网格布局
                for i, ch_idx in enumerate(channel_indices):
                    ax = self.figure.add_subplot(grid_rows, grid_cols, i + 1)
                    # 为每个通道使用不同的颜色
                    color = channel_colors[i % len(channel_colors)]
                    # 检查该通道是否全为NaN值
                    if not np.all(np.isnan(signal_data[i, :])):
                        ax.plot(times, signal_data[i, :], linewidth=0.5, color=color)
                    else:
                        # 如果通道全为NaN值，不绘制任何内容，显示为空白
                        pass
                    ax.set_ylabel(f'Ch{ch_idx}', fontsize=8)
                    if show_grid:
                        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
                    
                    # 只在最下面一行显示x轴标签
                    row = i // grid_cols
                    col = i % grid_cols
                    if row == grid_rows - 1 or i == n_channels - 1:
                        ax.set_xlabel(xlabel, fontsize=8)
                    else:
                        ax.set_xticklabels([])
                    
                    # 只在最左边一列显示y轴标签
                    if col == 0:
                        ax.set_ylabel(f'Ch{ch_idx}\n(μV)', fontsize=8)
                    else:
                        ax.set_yticklabels([])
                    
                    # 调整刻度字体大小
                    ax.tick_params(axis='both', which='major', labelsize=7)
                
                self.figure.suptitle(self.title, fontsize=10)
            
            self.figure.tight_layout()
            self.canvas.draw()
        else:
            # 多个绘图，需要创建新的绘图窗口
            # 首先绘制当前窗口的内容
            self.figure.clear()
            
            # 绘制前9个通道
            for i, ch_idx in enumerate(channel_indices[:max_channels_per_plot]):
                ax = self.figure.add_subplot(grid_rows, grid_cols, i + 1)
                # 为每个通道使用不同的颜色
                color = channel_colors[i % len(channel_colors)]
                # 检查该通道是否全为NaN值
                if not np.all(np.isnan(signal_data[i, :])):
                    ax.plot(times, signal_data[i, :], linewidth=0.5, color=color)
                else:
                    # 如果通道全为NaN值，不绘制任何内容，显示为空白
                    pass
                ax.set_ylabel(f'Ch{ch_idx}', fontsize=8)
                if show_grid:
                    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
                
                # 只在最下面一行显示x轴标签
                row = i // grid_cols
                col = i % grid_cols
                if row == grid_rows - 1 or i == min(max_channels_per_plot, n_channels) - 1:
                    ax.set_xlabel(xlabel, fontsize=8)
                else:
                    ax.set_xticklabels([])
                
                # 只在最左边一列显示y轴标签
                if col == 0:
                    ax.set_ylabel(f'Ch{ch_idx}\n(μV)', fontsize=8)
                else:
                    ax.set_yticklabels([])
                
                # 调整刻度字体大小
                ax.tick_params(axis='both', which='major', labelsize=7)
            
            self.figure.suptitle(f"{self.title} (1/{n_plots})", fontsize=10)
            self.figure.tight_layout()
            self.canvas.draw()
            
            # 为剩余的通道创建新的绘图窗口
            for plot_idx in range(1, n_plots):
                start_idx = plot_idx * max_channels_per_plot
                end_idx = min((plot_idx + 1) * max_channels_per_plot, n_channels)
                
                # 提取当前批次的通道数据
                batch_channels = channel_indices[start_idx:end_idx]
                batch_data = signal_data[start_idx:end_idx, :]
                
                # 创建新的绘图数据
                new_plot_data = {
                    'data_type': 'raw_signal',
                    'signal_data': batch_data,
                    'times': times,
                    'channel_indices': batch_channels,
                    'plot_config': plot_config
                }
                
                # 创建新的绘图窗口
                plot_title = f"{self.title} ({plot_idx + 1}/{n_plots})"
                self.parent().add_plot(plot_title, new_plot_data)
    
    def _draw_spike_waveforms(self):
        """绘制Spike波形"""
        waveforms = self.plot_data.get('waveforms', np.random.randn(50, 64))
        times = self.plot_data.get('times', np.arange(waveforms.shape[1]))
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 绘制所有波形（透明度较低）
        for i in range(min(waveforms.shape[0], 100)):  # 最多显示100个
            ax.plot(times, waveforms[i], alpha=0.3, color='gray', linewidth=0.5)
        
        # 绘制平均波形
        mean_waveform = np.mean(waveforms, axis=0)
        ax.plot(times, mean_waveform, color='red', linewidth=2, label='Average')
        
        ax.set_xlabel('时间 (ms)')
        ax.set_ylabel('幅值 (μV)')
        ax.set_title(self.title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
    
    def _draw_spike_sorting(self):
        """绘制Spike排序结果（聚类波形）"""
        result_data = self.plot_data.get('data', {})
        labels = result_data.get('labels', [])
        cluster_centers = result_data.get('cluster_centers', [])

        if len(labels) == 0 or len(cluster_centers) == 0:
            self._draw_default()
            return

        n_clusters = len(cluster_centers)
        waveform_length = len(cluster_centers[0])

        # 生成时间轴（波形长度20个样本点 = 10ms，采样率2000Hz）
        # 时间范围：-5ms 到 +5ms
        times_ms = np.linspace(-5.0, 5.0, waveform_length)

        self.figure.clear()

        # 创建子图网格
        n_cols = min(3, n_clusters)
        n_rows = (n_clusters + n_cols - 1) // n_cols

        for i in range(n_clusters):
            ax = self.figure.add_subplot(n_rows, n_cols, i + 1)

            # 绘制聚类中心波形（使用实际时间轴）
            ax.plot(times_ms, cluster_centers[i], linewidth=2, label=f'Cluster {i}')

            # 统计该聚类的Spike数量
            cluster_count = np.sum(labels == i)

            ax.set_title(f'聚类 {i}\n(n={cluster_count})', fontsize=10)
            ax.set_xlabel('时间 (ms)', fontsize=8)
            ax.set_ylabel('幅值 (μV)', fontsize=8)
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='both', which='major', labelsize=7)

            # 添加零时刻参考线（Spike峰值位置）
            ax.axvline(x=0, color='red', linestyle='--', alpha=0.5, linewidth=0.8)

        self.figure.suptitle(self.title, fontsize=12)
        self.figure.tight_layout()
        self.canvas.draw()
    
    def _draw_spike_raster(self):
        """绘制Spike时间分布"""
        spike_times = self.plot_data.get('spike_times', [])
        time_range = self.plot_data.get('time_range', (0, 10))
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 绘制Spike时间线
        ax.scatter(spike_times, [0] * len(spike_times), marker='|', s=200, color='black')
        
        # 绘制直方图
        ax2 = ax.twinx()
        bins = np.linspace(time_range[0], time_range[1], 50)
        ax2.hist(spike_times, bins=bins, alpha=0.3, color='blue')
        ax2.set_ylabel('Spike计数')
        
        ax.set_xlabel('时间 (s)')
        ax.set_ylabel('Spike')
        ax.set_title(self.title)
        ax.set_xlim(time_range)
        ax.set_yticks([])
        ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
    
    def _draw_raster(self):
        """绘制栅格图 - 支持多试验数据用不同颜色显示"""
        raster_data = self.plot_data.get('data', {})
        spike_times = raster_data.get('spike_times', [])
        time_range = raster_data.get('time_range', None)
        trial_sources = raster_data.get('trial_sources', None)  # 试次来源信息
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 如果没有数据，显示提示
        if not spike_times or len(spike_times) == 0:
            ax.text(0.5, 0.5, '无栅格图数据', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(self.title)
            self.canvas.draw()
            return
        
        # 定义颜色列表用于区分不同试验来源
        colors = ['black', 'blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink']
        
        # 如果有试次来源信息，为每个来源分配颜色
        if trial_sources is not None and len(trial_sources) == len(spike_times):
            # 获取唯一的试验来源
            unique_sources = []
            for source in trial_sources:
                if source not in unique_sources:
                    unique_sources.append(source)
            
            # 为每个试次绘制Spike，使用不同颜色区分来源
            for i, (spikes, source) in enumerate(zip(spike_times, trial_sources)):
                if len(spikes) > 0:
                    # 根据来源选择颜色
                    source_idx = unique_sources.index(source) if source in unique_sources else 0
                    color = colors[source_idx % len(colors)]
                    ax.scatter(spikes, [i] * len(spikes), marker='|', s=20, 
                              color=color, alpha=0.8, linewidths=1)
            
            # 添加图例说明不同颜色代表的试验
            if len(unique_sources) > 1:
                from matplotlib.lines import Line2D
                legend_elements = [Line2D([0], [0], marker='|', color='w', 
                                         markerfacecolor=colors[i % len(colors)], 
                                         markersize=10, label=source)
                                  for i, source in enumerate(unique_sources)]
                ax.legend(handles=legend_elements, loc='upper right', fontsize=8)
        else:
            # 没有试次来源信息，统一使用黑色
            for i, spikes in enumerate(spike_times):
                if len(spikes) > 0:
                    ax.scatter(spikes, [i] * len(spikes), marker='|', s=20, 
                              color='black', alpha=0.8, linewidths=1)
        
        ax.set_xlabel('时间 (s)')
        # 根据数据类型决定Y轴标签
        ylabel = raster_data.get('ylabel', '试次')
        ax.set_ylabel(ylabel)
        ax.set_title(self.title)
        ax.set_ylim(-0.5, len(spike_times) - 0.5)
        
        # 设置X轴范围（如果有time_range）
        if time_range and isinstance(time_range, (list, tuple)) and len(time_range) >= 2:
            ax.set_xlim(time_range[0], time_range[1])
        
        # 添加刺激 onset 线（时间=0）
        ax.axvline(x=0, color='r', linestyle='--', linewidth=1, alpha=0.5, label='刺激 onset')
        
        # 设置Y轴刻度标签
        n_trials = len(spike_times)
        if n_trials <= 20:
            ax.set_yticks(range(n_trials))
            ax.set_yticklabels([f'{i+1}' for i in range(n_trials)])
        else:
            # 如果试次太多，只显示部分刻度
            tick_positions = np.linspace(0, n_trials-1, min(10, n_trials), dtype=int)
            ax.set_yticks(tick_positions)
            ax.set_yticklabels([f'{i+1}' for i in tick_positions])
        
        self.canvas.draw()
    
    def _draw_psth(self):
        """绘制PSTH"""
        psth_data = self.plot_data.get('data', {})
        
        # 支持两种数据格式:
        # 1. bins (边界数组, 长度=n+1) + counts
        # 2. bin_centers (中心点数组, 长度=n) + counts
        bins = psth_data.get('bins', None)
        counts = psth_data.get('counts', None)
        
        if bins is None or counts is None:
            # 使用默认数据
            bins = np.linspace(-0.5, 1.0, 50)
            counts = np.random.poisson(10, len(bins)-1)
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 判断bins是边界数组还是中心点数组
        if len(bins) == len(counts) + 1:
            # bins是边界数组
            ax.bar(bins[:-1], counts, width=np.diff(bins), align='edge', alpha=0.7)
        else:
            # bins是中心点数组，计算宽度
            if len(bins) > 1:
                width = np.mean(np.diff(bins))
            else:
                width = 0.01
            ax.bar(bins, counts, width=width, align='center', alpha=0.7)
        
        ax.set_xlabel('时间 (s)')
        ax.set_ylabel('发放率 (Hz)')
        ax.set_title(self.title)
        ax.axvline(x=0, color='r', linestyle='--', label='Stimulus Onset')
        ax.legend()
        
        self.canvas.draw()
    
    def _draw_tuning_curve(self):
        """绘制调谐曲线 - 支持多试验"""
        tuning_data = self.plot_data.get('data', {})
        
        # 支持两种数据格式
        # 新格式: conditions, mean_responses, std_responses, sem_responses, trial_curves
        # 旧格式: stimuli, responses
        if 'conditions' in tuning_data:
            conditions = tuning_data.get('conditions', np.arange(8))
            mean_responses = tuning_data.get('mean_responses', np.random.rand(8) * 50)
            std_responses = tuning_data.get('std_responses', None)
            sem_responses = tuning_data.get('sem_responses', None)
            trial_curves = tuning_data.get('trial_curves', None)
        else:
            # 兼容旧格式
            conditions = tuning_data.get('stimuli', np.arange(8))
            mean_responses = tuning_data.get('responses', np.random.rand(8) * 50)
            std_responses = None
            sem_responses = None
            trial_curves = None
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 定义颜色列表
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        # 如果有多个试验的曲线，绘制每个试验
        if trial_curves is not None and isinstance(trial_curves, dict):
            for idx, (trial_name, trial_response) in enumerate(trial_curves.items()):
                color = colors[idx % len(colors)]
                # 使用实线绘制单个试验
                ax.plot(conditions, trial_response, 'o-', linewidth=2, markersize=8, 
                       color=color, label=f'{trial_name}')
        
        # 绘制均值曲线（虚线，粗细与其他曲线一致）
        ax.plot(conditions, mean_responses, 'o--', linewidth=2, markersize=8, 
               color='black', label='Mean', zorder=10)
        
        # 绘制误差线（使用标准误SEM）
        if sem_responses is not None and len(sem_responses) == len(conditions):
            ax.errorbar(conditions, mean_responses, yerr=sem_responses, 
                       fmt='none', ecolor='black', alpha=0.5, capsize=5, 
                       linewidth=2, zorder=10)
        elif std_responses is not None and len(std_responses) == len(conditions):
            ax.errorbar(conditions, mean_responses, yerr=std_responses, 
                       fmt='none', ecolor='gray', alpha=0.3, capsize=5, 
                       linewidth=2, zorder=10)
        
        ax.set_xlabel('刺激条件')
        ax.set_ylabel('平均发放率 (Hz)')
        ax.set_title(self.title)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=8)
        
        self.canvas.draw()
    
    def _draw_roc_curve(self):
        """绘制ROC曲线 - 支持多条曲线对比"""
        roc_data = self.plot_data.get('data', {})
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 检查是否有多个试验来源的ROC曲线
        roc_curves = roc_data.get('roc_curves', {})
        
        if roc_curves and len(roc_curves) > 1:
            # 多条ROC曲线对比
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
            
            for idx, (source, curve_data) in enumerate(roc_curves.items()):
                fpr = curve_data.get('fpr', [])
                tpr = curve_data.get('tpr', [])
                auc_value = curve_data.get('auc', 0.0)
                
                if len(fpr) > 0 and len(tpr) > 0:
                    color = colors[idx % len(colors)]
                    # 简化试验名称显示
                    short_name = source.split('_')[0] if '_' in source else source
                    ax.plot(fpr, tpr, color=color, linewidth=2, 
                           label=f'{short_name} (AUC={auc_value:.3f})')
            
            # 绘制对角线
            ax.plot([0, 1], [0, 1], 'k--', linewidth=1, alpha=0.5, label='Random')
            
            # 添加图例
            ax.legend(loc='lower right', fontsize=9)
            
        elif roc_curves and len(roc_curves) == 1:
            # 单条ROC曲线（从roc_curves字典中获取）
            source = list(roc_curves.keys())[0]
            curve_data = roc_curves[source]
            fpr = curve_data.get('fpr', [])
            tpr = curve_data.get('tpr', [])
            auc_value = curve_data.get('auc', 0.0)
            
            if len(fpr) == 0 or len(tpr) == 0:
                ax.text(0.5, 0.5, '无ROC曲线数据', ha='center', va='center', transform=ax.transAxes)
                ax.set_title(self.title)
                self.canvas.draw()
                return
            
            # 绘制ROC曲线
            short_name = source.split('_')[0] if '_' in source else source
            ax.plot(fpr, tpr, 'b-', linewidth=2, label=f'{short_name} (AUC = {auc_value:.3f})')
            
            # 绘制对角线
            ax.plot([0, 1], [0, 1], 'k--', linewidth=1, alpha=0.5, label='Random Classifier')
            
            # 添加图例
            ax.legend(loc='lower right')
            
            # 添加AUC值文本
            ax.text(0.6, 0.2, f'AUC = {auc_value:.3f}', fontsize=12, 
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        else:
            # 没有ROC曲线数据
            ax.text(0.5, 0.5, '无ROC曲线数据', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(self.title)
            self.canvas.draw()
            return
        
        # 设置坐标轴
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate (FPR)')
        ax.set_ylabel('True Positive Rate (TPR)')
        ax.set_title(self.title)
        ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
    
    def _draw_power_spectrum(self):
        """绘制功率谱"""
        spectrum_data = self.plot_data.get('data', {})
        freqs = spectrum_data.get('freqs', np.linspace(0, 100, 100))
        power = spectrum_data.get('power', np.random.rand(100))
        psd_mean = spectrum_data.get('psd_mean', None)
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 检查power是2D数组(多通道)还是1D数组(单通道)
        if isinstance(power, np.ndarray) and power.ndim == 2:
            # 多通道数据 - 绘制每条曲线
            n_channels = min(power.shape[0], 10)  # 最多显示10条
            colors = plt.cm.tab10(np.linspace(0, 1, n_channels))
            
            for i in range(n_channels):
                ax.semilogy(freqs, power[i, :], linewidth=0.8, 
                           color=colors[i], alpha=0.6, label=f'Ch {i+1}')
            
            # 如果有平均值，用粗黑线显示
            if psd_mean is not None:
                ax.semilogy(freqs, psd_mean, linewidth=2, 
                           color='black', label='平均值')
            
            ax.legend(loc='upper right', fontsize=8)
        else:
            # 单通道数据
            ax.semilogy(freqs, power, linewidth=1)
        
        ax.set_xlabel('频率 (Hz)')
        ax.set_ylabel('功率谱密度 (uV^2/Hz)')
        ax.set_title(self.title)
        ax.set_xlim(0, 100)
        ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
    
    def _draw_spectrogram(self):
        """绘制时频图"""
        spec_data = self.plot_data.get('data', {})
        
        # 获取实际数据
        times = spec_data.get('times', [])
        freqs = spec_data.get('freqs', [])
        spectrogram = spec_data.get('spectrogram', None)
        
        # 如果没有数据，使用示例数据
        if spectrogram is None or len(times) == 0 or len(freqs) == 0:
            times = np.linspace(0, 10, 100)
            freqs = np.linspace(0, 100, 50)
            spectrogram = np.random.rand(50, 100)
        
        # 处理三维时频图数据（通道维度）
        if spectrogram.ndim == 3:
            # 对所有通道取平均值
            spectrogram = np.mean(spectrogram, axis=1)
        
        # 确保数据维度匹配
        # pcolormesh期望C的形状是 (M, N)，X的形状是 (N+1,) 或 (M, N+1)，Y的形状是 (M+1,) 或 (M+1, N)
        # 检查并调整数据维度
        if len(times) == spectrogram.shape[1] and len(freqs) == spectrogram.shape[0]:
            # 数据维度匹配，直接使用
            pass
        elif len(times) == spectrogram.shape[1] and len(freqs) != spectrogram.shape[0]:
            # 频率维度不匹配，使用默认频率范围
            freqs = np.linspace(0, 100, spectrogram.shape[0])
        elif len(times) != spectrogram.shape[1] and len(freqs) == spectrogram.shape[0]:
            # 时间维度不匹配，生成新的时间轴
            times = np.linspace(0, 10, spectrogram.shape[1])
        else:
            # 两个维度都不匹配，生成新的时间和频率轴
            times = np.linspace(0, 10, spectrogram.shape[1])
            freqs = np.linspace(0, 100, spectrogram.shape[0])
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 绘制时频图
        im = ax.pcolormesh(times, freqs, spectrogram, shading='gouraud', cmap='jet')
        ax.set_xlabel('时间 (s)')
        ax.set_ylabel('频率 (Hz)')
        ax.set_title(self.title)
        self.figure.colorbar(im, ax=ax, label='功率')
        
        self.canvas.draw()
    
    def _draw_decoding_results(self):
        """绘制解码/分类结果（LDA/SVM/随机森林）"""
        self.figure.clear()
        
        # 获取数据
        result_info = self.plot_data.get('result_info', '')
        stats = self.plot_data.get('statistics', {})
        conf_matrix = self.plot_data.get('confusion_matrix')
        classes = self.plot_data.get('classes', [])
        
        # 创建子图布局 - 使用2x2网格，更合理地利用空间
        if conf_matrix is not None and len(conf_matrix) > 0:
            # 有混淆矩阵，使用2x2布局
            gs = self.figure.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[1, 1.2])
            ax_title = self.figure.add_subplot(gs[0, 0])  # 左上：标题和主要结果
            ax_stats = self.figure.add_subplot(gs[1, 0])  # 左下：详细统计
            ax_matrix = self.figure.add_subplot(gs[:, 1])  # 右侧：混淆矩阵（跨两行）
        else:
            # 只有文本信息，使用上下布局
            gs = self.figure.add_gridspec(2, 1, height_ratios=[1, 2])
            ax_title = self.figure.add_subplot(gs[0])
            ax_stats = self.figure.add_subplot(gs[1])
            ax_matrix = None
        
        # 左上：显示标题和主要结果
        ax_title.set_xlim(0, 1)
        ax_title.set_ylim(0, 1)
        ax_title.axis('off')
        
        # 简化标题文本，避免过长
        title_text = f"{self.title}\n\n"
        if result_info:
            title_text += result_info
        
        # 使用更小的字体和边距，避免超出边界
        ax_title.text(0.5, 0.5, title_text,
                     transform=ax_title.transAxes,
                     verticalalignment='center',
                     horizontalalignment='center',
                     fontsize=10,
                     wrap=True,
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.3))
        
        # 左下：显示详细统计信息
        ax_stats.set_xlim(0, 1)
        ax_stats.set_ylim(0, 1)
        ax_stats.axis('off')
        
        # 构建详细统计文本 - 确保始终有内容显示
        stats_text = "详细统计:\n"
        has_content = False
        
        if stats and isinstance(stats, dict):
            if 'n_samples' in stats:
                stats_text += f"  总样本数: {stats['n_samples']}\n"
                has_content = True
            if 'n_train_samples' in stats:
                stats_text += f"  训练样本: {stats['n_train_samples']}\n"
                has_content = True
            if 'n_test_samples' in stats:
                stats_text += f"  测试样本: {stats['n_test_samples']}\n"
                has_content = True
            if 'n_classes' in stats:
                stats_text += f"  类别数: {stats['n_classes']}\n"
                has_content = True
            if 'n_features' in stats:
                stats_text += f"  特征数: {stats['n_features']}\n"
                has_content = True
            # 添加交叉验证信息
            if 'mean_cv_accuracy' in stats:
                stats_text += f"  交叉验证准确率: {stats['mean_cv_accuracy']:.2%}\n"
                has_content = True
            if 'std_cv_accuracy' in stats:
                stats_text += f"  交叉验证标准差: {stats['std_cv_accuracy']:.4f}\n"
                has_content = True
            # 添加算法特定信息
            if 'n_support_vectors' in stats:
                stats_text += f"  支持向量数: {stats['n_support_vectors']}\n"
                has_content = True
            if 'n_trees' in stats:
                stats_text += f"  决策树数量: {stats['n_trees']}\n"
                has_content = True
        
        # 如果没有统计内容，显示提示信息
        if not has_content:
            stats_text += "  (无详细统计数据)\n"
            if not stats:
                stats_text += "  stats为空\n"
            elif not isinstance(stats, dict):
                stats_text += f"  stats类型: {type(stats)}\n"
            else:
                stats_text += f"  stats键: {list(stats.keys())}\n"
        
        ax_stats.text(0.05, 0.95, stats_text,
                     transform=ax_stats.transAxes,
                     verticalalignment='top',
                     horizontalalignment='left',
                     fontsize=9,
                     wrap=True,
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='wheat', alpha=0.3))
        
        # 右侧显示混淆矩阵
        if ax_matrix is not None and conf_matrix is not None:
            import numpy as np
            conf_matrix = np.array(conf_matrix)
            
            im = ax_matrix.imshow(conf_matrix, interpolation='nearest', cmap=plt.cm.Blues)
            ax_matrix.set_title('混淆矩阵', fontsize=14, pad=10)
            
            # 设置坐标轴
            if classes is not None and len(classes) > 0:
                tick_marks = np.arange(len(classes))
                ax_matrix.set_xticks(tick_marks)
                ax_matrix.set_yticks(tick_marks)
                ax_matrix.set_xticklabels(classes)
                ax_matrix.set_yticklabels(classes)
            
            ax_matrix.set_ylabel('真实标签', fontsize=11)
            ax_matrix.set_xlabel('预测标签', fontsize=11)
            
            # 在每个单元格中显示数值
            thresh = conf_matrix.max() / 2.
            for i in range(conf_matrix.shape[0]):
                for j in range(conf_matrix.shape[1]):
                    ax_matrix.text(j, i, format(conf_matrix[i, j], 'd'),
                                 ha="center", va="center",
                                 color="white" if conf_matrix[i, j] > thresh else "black",
                                 fontsize=12, fontweight='bold')
            
            # 添加颜色条
            cbar = self.figure.colorbar(im, ax=ax_matrix)
            cbar.set_label('样本数', rotation=270, labelpad=15)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def _draw_default(self):
        """默认绘图"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, f'{self.title}\n(数据类型: {self.plot_data.get("data_type", "unknown")})', 
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=14)
        ax.set_axis_off()
        self.canvas.draw()
    
    def _save_plot(self):
        """保存图表"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存图表",
            "",
            "PNG图像 (*.png);;PDF文档 (*.pdf);;SVG图像 (*.svg)"
        )
        
        if file_path:
            self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
            QMessageBox.information(self, "提示", f"图表已保存到: {file_path}")
    
    def _zoom_in(self):
        """放大"""
        for ax in self.figure.axes:
            ax.autoscale(enable=False)
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            ax.set_xlim(xlim[0] * 0.9, xlim[1] * 0.9)
            ax.set_ylim(ylim[0] * 0.9, ylim[1] * 0.9)
        self.canvas.draw()
    
    def _zoom_out(self):
        """缩小"""
        for ax in self.figure.axes:
            ax.autoscale(enable=False)
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            ax.set_xlim(xlim[0] * 1.1, xlim[1] * 1.1)
            ax.set_ylim(ylim[0] * 1.1, ylim[1] * 1.1)
        self.canvas.draw()
    
    def _reset_view(self):
        """重置视图"""
        for ax in self.figure.axes:
            ax.autoscale(enable=True)
        self.canvas.draw()


class VisualizationArea(QWidget):
    """
    可视化区域组件
    
    提供：
    - 多标签页图表显示（使用matplotlib）
    - 图表工具栏（保存、缩放等）
    - 图表管理
    """
    
    plot_closed = pyqtSignal(str)  # 图表关闭信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.plots: Dict[str, PlotTab] = {}
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
        
        # 添加默认的数据预览标签页
        self._add_data_preview_tab()
        
        layout.addWidget(self.tab_widget)
        
        # 应用样式
        self.tab_widget.setStyleSheet(Styles.VISUALIZATION_AREA)
    
    def _add_data_preview_tab(self):
        """添加数据预览标签页"""
        preview_widget = QWidget()
        layout = QVBoxLayout(preview_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # 简化工具栏 - 只保留关闭所有图表按钮
        toolbar = QToolBar()

        # 关闭所有图表按钮
        close_all_btn = QPushButton("Close All Plots")
        close_all_btn.clicked.connect(self.clear_plots)
        toolbar.addWidget(close_all_btn)

        layout.addWidget(toolbar)

        # 图表显示区域 - 使用matplotlib
        self.preview_figure = Figure(figsize=(8, 6), dpi=100)
        self.preview_canvas = FigureCanvas(self.preview_figure)
        self.preview_canvas.setStyleSheet("background-color: white;")

        layout.addWidget(self.preview_canvas, 1)

        # 添加matplotlib导航工具栏
        self.preview_toolbar = NavigationToolbar(self.preview_canvas, preview_widget)
        layout.addWidget(self.preview_toolbar)

        # 移除了信息显示区域（数据信息、状态等）

        self.tab_widget.addTab(preview_widget, "Visualization")

        # 绘制默认预览图
        self._draw_preview()
    
    def _draw_preview(self):
        """绘制默认预览图 - 显示提示信息"""
        self.preview_figure.clear()
        ax = self.preview_figure.add_subplot(111)
        
        # 显示提示信息，而不是示例数据
        ax.text(0.5, 0.6, 'Please load data and run analysis first', 
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=16, fontweight='bold')
        ax.text(0.5, 0.4, '1. Double-click from left navigator to add data to selection list\n2. Select algorithm and configure parameters\n3. Click "Run Analysis" button', 
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=11, color='gray')
        ax.set_axis_off()
        
        self.preview_canvas.draw()
    
    def _refresh_plot(self):
        """刷新图表"""
        chart_type = self.chart_type_combo.currentText()
        self.status_info_label.setText(f"状态: 正在绘制 {chart_type}...")
        
        self.preview_figure.clear()
        ax = self.preview_figure.add_subplot(111)
        
        try:
            if chart_type == "信号波形":
                t = np.linspace(0, 1, 1000)
                signal = np.sin(2 * np.pi * 10 * t)
                ax.plot(t, signal, linewidth=1)
                ax.set_title('信号波形')
            elif chart_type == "Spike栅格图":
                for i in range(10):
                    spikes = np.random.rand(20) * 2 - 1
                    ax.scatter(spikes, [i] * 20, marker='|', s=100, color='black')
                ax.set_title('Spike栅格图')
                ax.set_xlabel('时间 (s)')
                ax.set_ylabel('试验')
            elif chart_type == "PSTH":
                bins = np.linspace(-0.5, 1.0, 30)
                counts = np.random.poisson(15, 29)
                ax.bar(bins[:-1], counts, width=np.diff(bins), align='edge', alpha=0.7)
                ax.axvline(x=0, color='r', linestyle='--')
                ax.set_title('PSTH')
                ax.set_xlabel('时间 (s)')
                ax.set_ylabel('发放率 (Hz)')
            elif chart_type == "调谐曲线":
                stimuli = np.arange(8)
                responses = np.random.rand(8) * 50
                ax.plot(stimuli, responses, 'o-', linewidth=2, markersize=8)
                ax.set_title('调谐曲线')
                ax.set_xlabel('刺激条件')
                ax.set_ylabel('平均发放率 (Hz)')
            elif chart_type == "功率谱密度":
                freqs = np.linspace(0, 100, 100)
                power = np.exp(-freqs/20) + np.random.rand(100) * 0.1
                ax.semilogy(freqs, power, linewidth=1)
                ax.set_title('功率谱密度')
                ax.set_xlabel('频率 (Hz)')
                ax.set_ylabel('功率')
                ax.set_xlim(0, 100)
            elif chart_type == "时频图":
                times = np.linspace(0, 10, 100)
                freqs = np.linspace(0, 100, 50)
                power = np.random.rand(50, 100)
                im = ax.pcolormesh(times, freqs, power, shading='gouraud', cmap='jet')
                ax.set_title('时频图')
                ax.set_xlabel('时间 (s)')
                ax.set_ylabel('频率 (Hz)')
                self.preview_figure.colorbar(im, ax=ax, label='功率')
            
            ax.grid(True, alpha=0.3)
            self.preview_canvas.draw()
            self.status_info_label.setText(f"状态: {chart_type} 绘制完成")
        
        except Exception as e:
            ax.text(0.5, 0.5, f'绘图失败: {str(e)}', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='red')
            ax.set_axis_off()
            self.preview_canvas.draw()
            self.status_info_label.setText(f"状态: 绘图失败")
    
    def _export_plot(self):
        """导出图表"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出图表",
            "",
            "PNG图像 (*.png);;PDF文档 (*.pdf);;SVG图像 (*.svg)"
        )
        if file_path:
            self.preview_figure.savefig(file_path, dpi=300, bbox_inches='tight')
            QMessageBox.information(self, "提示", f"图表已导出到: {file_path}")
    
    def add_plot(self, title: str, plot_data: Dict[str, Any]) -> str:
        """
        添加图表
        
        Args:
            title: 图表标题
            plot_data: 图表数据
            
        Returns:
            图表ID
        """
        # 生成唯一ID
        plot_id = f"plot_{len(self.plots)}"
        
        # 创建图表标签页
        plot_tab = PlotTab(title, plot_data, self)
        self.plots[plot_id] = plot_tab
        
        # 添加到标签页控件
        index = self.tab_widget.addTab(plot_tab, title)
        self.tab_widget.setCurrentIndex(index)
        
        return plot_id
    
    def remove_plot(self, plot_id: str):
        """移除图表"""
        if plot_id in self.plots:
            plot_tab = self.plots[plot_id]
            index = self.tab_widget.indexOf(plot_tab)
            
            if index >= 0:
                self.tab_widget.removeTab(index)
            
            del self.plots[plot_id]
            self.plot_closed.emit(plot_id)
    
    def clear_plots(self):
        """清除所有图表"""
        # 保留数据预览标签页
        while self.tab_widget.count() > 1:
            self.tab_widget.removeTab(1)
        
        self.plots.clear()
    
    def _on_tab_close_requested(self, index: int):
        """处理标签页关闭请求"""
        # 不关闭数据预览标签页
        if index == 0:
            return
        
        widget = self.tab_widget.widget(index)
        
        # 查找对应的plot_id
        plot_id_to_remove = None
        for plot_id, plot_tab in self.plots.items():
            if plot_tab == widget:
                plot_id_to_remove = plot_id
                break
        
        # 找到后移除图表
        if plot_id_to_remove:
            self.remove_plot(plot_id_to_remove)
    
    def get_current_plot(self) -> Optional[str]:
        """获取当前显示的图表ID"""
        index = self.tab_widget.currentIndex()
        
        # 跳过数据预览标签页
        if index == 0:
            return None
        
        widget = self.tab_widget.widget(index)
        
        for plot_id, plot_tab in self.plots.items():
            if plot_tab == widget:
                return plot_id
        
        return None
    
    def set_plot_title(self, plot_id: str, title: str):
        """设置图表标题"""
        if plot_id in self.plots:
            plot_tab = self.plots[plot_id]
            index = self.tab_widget.indexOf(plot_tab)
            
            if index >= 0:
                self.tab_widget.setTabText(index, title)
    
    def display_signal(self, signal_data: Any, title: str = "信号波形") -> str:
        """
        显示信号波形
        
        Args:
            signal_data: 信号数据
            title: 图表标题
            
        Returns:
            图表ID
        """
        plot_data = {
            'data_type': 'signal',
            'data': signal_data,
            'shape': getattr(signal_data, 'shape', 'unknown')
        }
        
        return self.add_plot(title, plot_data)
    
    def display_raster(self, raster_data: Dict, title: str = "栅格图") -> str:
        """
        显示栅格图
        
        Args:
            raster_data: 栅格图数据
            title: 图表标题
            
        Returns:
            图表ID
        """
        plot_data = {
            'data_type': 'raster',
            'data': raster_data,
            'channel': raster_data.get('channel_id', 'unknown'),
            'trials': len(raster_data.get('trial_ids', []))
        }
        
        return self.add_plot(title, plot_data)
    
    def display_psth(self, psth_data: Dict, title: str = "PSTH") -> str:
        """
        显示PSTH图
        
        Args:
            psth_data: PSTH数据
            title: 图表标题
            
        Returns:
            图表ID
        """
        plot_data = {
            'data_type': 'psth',
            'data': psth_data,
            'trials': psth_data.get('trial_count', 0)
        }
        
        return self.add_plot(title, plot_data)
    
    def display_tuning_curve(self, tuning_data: Dict, title: str = "调谐曲线") -> str:
        """
        显示调谐曲线
        
        Args:
            tuning_data: 调谐曲线数据
            title: 图表标题
            
        Returns:
            图表ID
        """
        plot_data = {
            'data_type': 'tuning_curve',
            'data': tuning_data
        }
        
        return self.add_plot(title, plot_data)
    
    def display_power_spectrum(self, spectrum_data: Dict, title: str = "功率谱") -> str:
        """
        显示功率谱
        
        Args:
            spectrum_data: 功率谱数据
            title: 图表标题
            
        Returns:
            图表ID
        """
        plot_data = {
            'data_type': 'power_spectrum',
            'data': spectrum_data
        }
        
        return self.add_plot(title, plot_data)
    
    def display_spectrogram(self, spec_data: Dict, title: str = "时频图") -> str:
        """
        显示时频图
        
        Args:
            spec_data: 时频图数据
            title: 图表标题
            
        Returns:
            图表ID
        """
        plot_data = {
            'data_type': 'spectrogram',
            'data': spec_data
        }
        
        return self.add_plot(title, plot_data)
    
    def display_roc_curve(self, roc_data: Dict, title: str = "ROC曲线") -> str:
        """
        显示ROC曲线
        
        Args:
            roc_data: ROC数据，包含fpr、tpr、auc等
            title: 图表标题
            
        Returns:
            图表ID
        """
        plot_data = {
            'data_type': 'roc_curve',
            'data': roc_data
        }
        
        return self.add_plot(title, plot_data)


if __name__ == '__main__':
    # 测试代码
    import sys
    import numpy as np
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    viz_area = VisualizationArea()
    viz_area.show()
    
    # 添加测试图表
    viz_area.display_signal(np.random.randn(1000), "测试信号")
    viz_area.display_raster({
        'channel_id': 71,
        'trial_ids': [1, 2, 3],
        'spike_times': [np.random.randn(10) for _ in range(3)]
    }, "测试栅格图")
    viz_area.display_psth({
        'bins': np.linspace(-0.5, 1.0, 30),
        'counts': np.random.poisson(15, 29)
    }, "测试PSTH")
    
    sys.exit(app.exec())
