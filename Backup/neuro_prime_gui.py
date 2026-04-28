"""
猕猴脑电生理数据分析软件 - PyQt5 GUI
NeuroPrime - Macaque Electrophysiology Data Analysis Tool
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox,
                             QTabWidget, QSplitter, QTextEdit, QFileDialog,
                             QProgressBar, QCheckBox, QRadioButton, QButtonGroup,
                             QMessageBox, QStatusBar, QMenuBar, QAction, QToolBar,
                             QListWidget, QStackedWidget, QFrame, QGridLayout,
                             QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
import warnings
warnings.filterwarnings('ignore')

# 导入核心分析算法
from neuro_analysis_core import NeuroAnalysisCore


class AnalysisWorker(QThread):
    """后台分析工作线程"""
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(dict)
    log_signal = pyqtSignal(str)
    
    def __init__(self, analysis_type, params):
        super().__init__()
        self.analysis_type = analysis_type
        self.params = params
        self.core = NeuroAnalysisCore()
        
    def run(self):
        try:
            self.log_signal.emit(f"开始{self.analysis_type}分析...")
            
            if self.analysis_type == "generate_data":
                result = self.core.generate_simulated_data(**self.params)
                self.result_signal.emit({"type": "data_generated", "data": result})
                
            elif self.analysis_type == "preprocess":
                result = self.core.preprocess_data(**self.params)
                self.result_signal.emit({"type": "preprocessed", "data": result})
                
            elif self.analysis_type == "spike_detect":
                result = self.core.detect_spikes(**self.params)
                self.result_signal.emit({"type": "spikes_detected", "data": result})
                
            elif self.analysis_type == "lfp_analysis":
                result = self.core.compute_power_spectrum(**self.params)
                self.result_signal.emit({"type": "lfp_analyzed", "data": result})
                
            elif self.analysis_type == "psth":
                result = self.core.align_spikes_to_events(**self.params)
                self.result_signal.emit({"type": "psth_computed", "data": result})
                
            elif self.analysis_type == "tuning_curve":
                result = self.core.compute_tuning_curve(**self.params)
                self.result_signal.emit({"type": "tuning_computed", "data": result})
                
            elif self.analysis_type == "decode":
                result = self.core.decode_with_lda(**self.params)
                self.result_signal.emit({"type": "decoded", "data": result})
                
            self.progress_signal.emit(100)
            self.log_signal.emit(f"{self.analysis_type}分析完成!")
            
        except Exception as e:
            self.log_signal.emit(f"错误: {str(e)}")
            self.result_signal.emit({"type": "error", "message": str(e)})


class MplCanvas(FigureCanvas):
    """Matplotlib画布组件"""
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
    def clear(self):
        self.axes.clear()
        
    def draw_figure(self):
        self.draw()


class DataGenerationPanel(QWidget):
    """数据生成面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 参数设置组
        param_group = QGroupBox("模拟数据参数")
        param_layout = QGridLayout()
        
        # 时长
        param_layout.addWidget(QLabel("时长 (秒):"), 0, 0)
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(1, 60)
        self.duration_spin.setValue(10)
        param_layout.addWidget(self.duration_spin, 0, 1)
        
        # 采样率
        param_layout.addWidget(QLabel("采样率 (Hz):"), 1, 0)
        self.fs_spin = QSpinBox()
        self.fs_spin.setRange(1000, 50000)
        self.fs_spin.setValue(10000)
        self.fs_spin.setSingleStep(1000)
        param_layout.addWidget(self.fs_spin, 1, 1)
        
        # 通道数
        param_layout.addWidget(QLabel("通道数:"), 2, 0)
        self.channels_spin = QSpinBox()
        self.channels_spin.setRange(1, 32)
        self.channels_spin.setValue(4)
        param_layout.addWidget(self.channels_spin, 2, 1)
        
        # Spike发放率
        param_layout.addWidget(QLabel("Spike发放率 (Hz):"), 3, 0)
        self.spike_rate_spin = QDoubleSpinBox()
        self.spike_rate_spin.setRange(1, 50)
        self.spike_rate_spin.setValue(8)
        param_layout.addWidget(self.spike_rate_spin, 3, 1)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # 生成按钮
        self.generate_btn = QPushButton("生成模拟数据")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_data)
        layout.addWidget(self.generate_btn)
        
        # 加载真实数据按钮
        self.load_btn = QPushButton("加载真实数据文件")
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.load_btn.clicked.connect(self.load_data)
        layout