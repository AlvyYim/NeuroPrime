"""
ParameterPanel - 参数配置面板

提供算法参数配置、数据选择、时间对齐等功能
根据当前Ribbon标签页动态调整显示内容
支持跨试验数据选择
"""

from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from enum import Enum

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QGroupBox, QFormLayout, QScrollArea,
    QFrame, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

# 导入样式
from .styles import Styles

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from algorithms.scheduler import AlgorithmScheduler
from visualization.time_alignment import TimeAlignmentConfig
from utils.debug_logger import get_logger, log_vars
logger = get_logger()


class PanelMode(Enum):
    """面板显示模式"""
    ANALYSIS = "analysis"           # 分析模式（Spike检测、排序、LFP分析、行为分析、智能分析）
    CUSTOM_ALGORITHM = "custom"     # 自定义算法模式


class ParameterPanel(QWidget):
    """
    参数配置面板
    
    根据当前Ribbon标签页动态调整显示内容：
    - 分析模式（Spike检测、排序、LFP分析、行为分析、智能分析）：
      显示参数配置 + 数据选择 + 操作按钮
    - 自定义算法模式：
      显示算法选择 + 数据选择 + 操作按钮（不显示参数配置）
    
    支持跨试验数据选择，用户可以从左侧导航栏双击添加数据项
    """
    
    run_analysis_requested = pyqtSignal(dict)  # 运行分析请求
    time_alignment_requested = pyqtSignal()  # 时间对齐请求
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.scheduler = AlgorithmScheduler()
        self.scheduler.register_builtin_algorithms()
        
        # 已选择的数据项列表（支持跨试验）
        self.selected_data_items: List[Dict[str, Any]] = []
        self.selected_data_ids: Set[str] = set()  # 用于去重
        
        self.time_alignment_config: Optional[TimeAlignmentConfig] = None
        self.current_algorithm: Optional[str] = None
        self.current_mode: PanelMode = PanelMode.ANALYSIS  # 默认分析模式
        self.current_tab_name: str = ""  # 当前Ribbon标签页名称
        
        self._init_ui()
        self._populate_algorithms()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 创建滚动区域
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # 内容容器
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(15)
        
        # 创建各个控件组（但先不添加到布局）
        self._create_algorithm_group()
        self._create_data_selection_group()
        self._create_parameter_group()
        self._create_action_group()
        
        # 默认显示分析模式
        self._setup_analysis_mode()
        
        # 添加弹性空间，确保控件底部对齐
        self.content_layout.addStretch(1)
        
        # 确保参数配置组有足够的最小高度
        self.param_group.setMinimumHeight(200)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # 应用样式
        self.setStyleSheet(Styles.PARAMETER_PANEL)
    
    def _create_algorithm_group(self):
        """创建算法选择组"""
        self.algo_group = QGroupBox("Algorithm Selection")
        algo_layout = QFormLayout(self.algo_group)
        
        self.algo_combo = QComboBox()
        self.algo_combo.currentTextChanged.connect(self._on_algorithm_changed)
        algo_layout.addRow("Select Algorithm:", self.algo_combo)
        
        self.algo_description = QLabel("Please select an algorithm")
        self.algo_description.setWordWrap(True)
        self.algo_description.setStyleSheet("color: gray; font-size: 11px;")
        algo_layout.addRow(self.algo_description)
    
    def _create_data_selection_group(self):
        """创建数据选择组（支持跨试验）"""
        self.data_group = QGroupBox("Data Selection (Cross-Trial)")
        data_layout = QVBoxLayout(self.data_group)

        # 提示标签 - 保存为成员变量以便动态更新
        self.data_hint_label = QLabel("Hint: Double-click data items or trials from the left navigator to add here")
        self.data_hint_label.setStyleSheet("color: gray; font-size: 11px; font-style: italic;")
        self.data_hint_label.setWordWrap(True)  # 允许自动换行
        data_layout.addWidget(self.data_hint_label)

        # 已选择的数据列表
        self.selected_data_list = QListWidget()
        self.selected_data_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        # 默认最大高度200，在自定义算法模式下会增加
        self.selected_data_list.setMaximumHeight(200)
        self.selected_data_list.setToolTip("Selected data items, supporting cross-trial selection")
        data_layout.addWidget(QLabel("Selected Data Items:"))
        data_layout.addWidget(self.selected_data_list)
        
        # 数据操作按钮
        btn_layout = QHBoxLayout()
        
        self.remove_selected_btn = QPushButton("Remove Selected")
        self.remove_selected_btn.setToolTip("Remove selected data items from the list")
        self.remove_selected_btn.clicked.connect(self._remove_selected_data)
        btn_layout.addWidget(self.remove_selected_btn)
        
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.setToolTip("Clear all selected data items")
        self.clear_all_btn.clicked.connect(self._clear_all_data)
        btn_layout.addWidget(self.clear_all_btn)
        
        btn_layout.addStretch()
        data_layout.addLayout(btn_layout)
        
        # 时间对齐按钮
        self.time_align_btn = QPushButton("⏱ Time Alignment")
        self.time_align_btn.setToolTip("Configure time alignment for multiple data items")
        self.time_align_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.time_align_btn.clicked.connect(self._on_time_alignment_clicked)
        data_layout.addWidget(self.time_align_btn)
    
    def _create_parameter_group(self):
        """创建参数配置组"""
        self.param_group = QGroupBox("Parameter Configuration")
        self.param_layout = QFormLayout(self.param_group)
        self.param_layout.setSpacing(10)
        
        # 设置字段增长策略：标签列固定宽度，字段列扩展
        self.param_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        # 设置标签对齐方式：左对齐
        self.param_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # 设置表单对齐方式：左对齐
        self.param_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # 设置参数配置组的最小高度，确保即使为空时也有固定高度
        self.param_group.setMinimumHeight(150)

        # 动态参数控件将在这里添加
        self.param_widgets: Dict[str, QWidget] = {}
    
    def _create_action_group(self):
        """创建操作按钮组"""
        self.action_group = QGroupBox("Actions")
        action_layout = QHBoxLayout(self.action_group)
        
        self.run_btn = QPushButton("▶ Run Analysis")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        self.run_btn.clicked.connect(self._on_run_clicked)
        action_layout.addWidget(self.run_btn)
        
        self.reset_btn = QPushButton("Reset Parameters")
        self.reset_btn.clicked.connect(self._reset_parameters)
        action_layout.addWidget(self.reset_btn)
        
        action_layout.addStretch()
    
    def _clear_content_layout(self):
        """清空内容布局"""
        while self.content_layout.count() > 0:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
    
    def _clear_parameter_widgets(self):
        """清除参数控件"""
        # 移除所有参数行
        while self.param_layout.rowCount() > 0:
            self.param_layout.removeRow(0)
        
        self.param_widgets.clear()
    
    def _setup_analysis_mode(self):
        """设置分析模式布局（Spike检测、排序、LFP分析、行为分析、智能分析）"""
        self._clear_content_layout()

        # 分析模式显示：参数配置 + 数据选择 + 操作按钮
        # 恢复数据选择区域的默认高度
        self.selected_data_list.setMaximumHeight(200)

        self.content_layout.addWidget(self.param_group)
        self.content_layout.addWidget(self.data_group)
        self.content_layout.addWidget(self.action_group)

        # 隐藏算法选择组（分析模式下通过Ribbon标签页选择算法类型）
        self.algo_group.setParent(None)

        # Restore algorithm list (show all algorithms)
        self._populate_algorithms()

        self.current_mode = PanelMode.ANALYSIS
    
    def _setup_custom_algorithm_mode(self):
        """Set up custom algorithm mode layout"""
        self._clear_content_layout()

        # Custom algorithm mode shows: algorithm selection + data selection + action buttons (no parameter configuration)
        # Since there's no parameter panel, increase height of data selection area to fill space
        self.selected_data_list.setMaximumHeight(350)  # Increase height from 200 to 350

        self.content_layout.addWidget(self.algo_group)
        self.content_layout.addWidget(self.data_group)
        self.content_layout.addWidget(self.action_group)

        # Hide parameter configuration group
        self.param_group.setParent(None)

        # Repopulate algorithm list, showing only custom algorithms
        self._populate_custom_algorithms()

        self.current_mode = PanelMode.CUSTOM_ALGORITHM
    
    def set_panel_mode(self, tab_name: str):
        """
        Set panel mode based on Ribbon tab name
        
        Args:
            tab_name: Ribbon tab name
        """
        self.current_tab_name = tab_name
        
        # Custom Algorithms tab uses special mode
        if tab_name == "Custom Algorithms":
            if self.current_mode != PanelMode.CUSTOM_ALGORITHM:
                self._setup_custom_algorithm_mode()
        else:
            # All other analysis tabs use analysis mode
            if self.current_mode != PanelMode.ANALYSIS:
                self._setup_analysis_mode()
    
    def set_algorithm(self, algorithm_name: str):
        """
        设置当前算法并加载对应的参数配置
        
        Args:
            algorithm_name: 算法名称
        """
        self.current_algorithm = algorithm_name
        
        # 根据算法名称加载对应的参数配置
        self._load_parameters_for_algorithm(algorithm_name)
    
    def _update_data_hint_for_algorithm(self, algorithm_name: str):
        """
        根据算法更新数据选择提示
        
        Args:
            algorithm_name: 算法名称
        """
        try:
            # 导入算法模块获取数据需求
            from src.algorithms import AlgorithmScheduler
            
            # 创建临时调度器获取算法信息
            scheduler = AlgorithmScheduler()
            scheduler.register_builtin_algorithms()
            
            algorithm = scheduler.get_algorithm(algorithm_name)
            if algorithm:
                data_req = algorithm.get_data_requirements()
                required_types = data_req.get('required_types', [])
                description = data_req.get('description', '')
                
                if required_types:
                    # 构建提示文本
                    hint_text = f"【数据需求】{description}\n"
                    
                    # 添加具体的数据类型说明
                    if 'lfp' in required_types and 'spike' not in required_types:
                        hint_text += "请选择：LFP信号数据"
                    elif 'spike' in required_types and 'lfp' not in required_types:
                        if 'behavior' in required_types:
                            hint_text += "请选择：Spike数据 + 行为数据（试次信息）"
                        else:
                            hint_text += "请选择：Spike数据"
                    elif 'spike' in required_types and 'lfp' in required_types:
                        hint_text += "请选择：Spike数据或LFP数据 + 行为数据"
                    elif 'behavior' in required_types:
                        hint_text += "请选择：行为数据"
                    
                    # 更新提示标签样式（与原始提示样式一致）
                    self.data_hint_label.setText(hint_text)
                    self.data_hint_label.setStyleSheet("color: gray; font-size: 11px; font-style: italic;")
                else:
                    # 没有特定数据需求（如自定义算法）
                    self.data_hint_label.setText("提示：从左侧导航栏双击数据项或试验项添加到此处")
                    self.data_hint_label.setStyleSheet("color: gray; font-size: 11px; font-style: italic;")
            else:
                # 算法未找到，使用默认提示
                self.data_hint_label.setText("提示：从左侧导航栏双击数据项或试验项添加到此处")
                self.data_hint_label.setStyleSheet("color: gray; font-size: 11px; font-style: italic;")
                
        except Exception as e:
            # 出错时使用默认提示
            print(f"更新数据提示失败: {e}")
            self.data_hint_label.setText("提示：从左侧导航栏双击数据项或试验项添加到此处")
            self.data_hint_label.setStyleSheet("color: gray; font-size: 11px; font-style: italic;")
    
    def _load_parameters_for_algorithm(self, algorithm_name: str):
        """
        根据算法名称加载对应的参数配置
        
        Args:
            algorithm_name: 算法名称
        """
        # 清除现有参数
        self._clear_parameter_widgets()
        
        # 设置参数组标题
        self.param_group.setTitle(f"参数配置 - {algorithm_name}")
        
        # 更新数据选择提示
        self._update_data_hint_for_algorithm(algorithm_name)
        
        # 根据算法名称加载对应参数
        if algorithm_name == "SpikeDetectionThreshold":
            self._create_spike_detection_parameters()
        elif algorithm_name == "template_matching":
            self._create_template_matching_parameters()
        elif algorithm_name == "SpikeSortingPCA":
            self._create_spike_sorting_parameters()
        elif algorithm_name == "waveform_features":
            self._create_waveform_features_parameters()
        elif algorithm_name == "kmeans":
            self._create_kmeans_parameters()
        elif algorithm_name == "gmm":
            self._create_gmm_parameters()
        elif algorithm_name == "LFPPowerSpectrum":
            self._create_lfp_power_spectrum_parameters()
        elif algorithm_name == "LFPSpectrogram":
            self._create_lfp_spectrogram_parameters()
        elif algorithm_name == "PSTHAnalysis":
            self._create_psth_parameters()
        elif algorithm_name == "RasterPlotAnalysis":
            self._create_raster_parameters()
        elif algorithm_name == "TuningCurveAnalysis":
            self._create_tuning_curve_parameters()
        elif algorithm_name == "ROCAnalysis":
            self._create_roc_parameters()
        elif algorithm_name == "LDADecoder":
            self._create_lda_parameters()
        elif algorithm_name == "SVMClassifier":
            self._create_svm_parameters()
        elif algorithm_name == "RandomForestClassifier":
            self._create_random_forest_parameters()
        else:
            # 尝试从算法获取参数模式（用于自定义算法）
            self._create_parameters_from_algorithm(algorithm_name)
    
    def _create_parameters_from_algorithm(self, algorithm_name: str):
        """
        从算法定义动态创建参数控件（用于自定义算法）
        
        Args:
            algorithm_name: 算法名称
        """
        try:
            # 获取算法实例
            algorithm = self.scheduler.get_algorithm(algorithm_name)
            if algorithm and hasattr(algorithm, 'get_parameters_schema'):
                # 获取参数模式
                params_schema = algorithm.get_parameters_schema()
                
                if params_schema:
                    for param in params_schema:
                        param_type = param.param_type
                        param_name = param.name
                        description = param.description
                        default_value = param.default_value
                        
                        # 根据参数类型创建对应控件
                        if param_type.value == "integer":
                            self._add_int_parameter(
                                param_name, description, default_value,
                                param.min_value, param.max_value
                            )
                        elif param_type.value == "float":
                            self._add_float_parameter(
                                param_name, description, default_value,
                                param.min_value, param.max_value
                            )
                        elif param_type.value == "select":
                            self._add_select_parameter(
                                param_name, description, default_value,
                                param.options or []
                            )
                        elif param_type.value == "boolean":
                            self._add_bool_parameter(
                                param_name, description, default_value
                            )
                        else:
                            # 字符串或其他类型
                            self._add_string_parameter(
                                param_name, description, default_value
                            )
                else:
                    # 算法没有参数
                    label = QLabel("该算法无需配置参数")
                    label.setStyleSheet("color: gray; font-style: italic;")
                    self.param_layout.addRow(label)
            else:
                # 无法获取算法信息
                label = QLabel(f"算法 '{algorithm_name}' 的参数配置不可用")
                label.setStyleSheet("color: gray; font-style: italic;")
                self.param_layout.addRow(label)
        except Exception as e:
            logger.error(f"创建参数控件失败: {e}")
            label = QLabel(f"加载参数失败: {str(e)}")
            label.setStyleSheet("color: red;")
            self.param_layout.addRow(label)
    
    def _create_spike_detection_parameters(self):
        """创建Spike检测算法参数配置"""
        self.param_group.setTitle("参数配置 - Spike检测")
        
        # 阈值系数
        self._add_float_parameter(
            "threshold_factor", "阈值系数",
            4.5, 2.0, 10.0,
            "相对于噪声标准差的倍数"
        )
        
        # 阈值类型
        self._add_select_parameter(
            "threshold_type", "阈值类型",
            ["positive", "negative", "both"],
            "both"
        )
        
        # 检测窗口大小
        self._add_float_parameter(
            "window_ms", "检测窗口大小",
            1.0, 0.5, 5.0,
            "毫秒"
        )
        
        # 不应期
        self._add_float_parameter(
            "refractory_ms", "不应期",
            1.0, 0.5, 3.0,
            "毫秒"
        )
        
        # 高通滤波器截止频率
        self._add_float_parameter(
            "filter_low", "高通滤波器截止频率",
            300.0, 100.0, 1000.0,
            "Hz"
        )
        
        # 低通滤波器截止频率
        self._add_float_parameter(
            "filter_high", "低通滤波器截止频率",
            3000.0, 2000.0, 6000.0,
            "Hz"
        )
        
        # 应用带通滤波器
        self._add_bool_parameter(
            "use_filter", "应用带通滤波器",
            True
        )
    
    def _create_template_matching_parameters(self):
        """创建模板匹配算法参数配置"""
        self.param_group.setTitle("参数配置 - 模板匹配")
        
        # 模板数量
        self._add_int_parameter(
            "n_templates", "模板数量",
            5, 1, 20
        )
        
        # 匹配阈值
        self._add_float_parameter(
            "match_threshold", "匹配阈值",
            0.8, 0.5, 1.0,
            ""
        )
        
        # 模板长度
        self._add_float_parameter(
            "template_length_ms", "模板长度",
            2.0, 1.0, 5.0,
            "毫秒"
        )
    
    def _create_spike_sorting_parameters(self):
        """创建Spike排序算法参数配置"""
        self.param_group.setTitle("参数配置 - Spike排序")
        
        # PCA主成分数量
        self._add_int_parameter(
            "n_components", "PCA主成分数量",
            3, 2, 10
        )
        
        # 聚类数量
        self._add_int_parameter(
            "n_clusters", "聚类数量",
            3, 2, 10
        )
        
        # 最大迭代次数
        self._add_int_parameter(
            "max_iterations", "最大迭代次数",
            100, 50, 500
        )
        
        # 随机种子
        self._add_int_parameter(
            "random_state", "随机种子",
            42, 0, 1000
        )
    
    def _create_waveform_features_parameters(self):
        """创建波形特征算法参数配置"""
        self.param_group.setTitle("参数配置 - 波形特征")
        
        # 峰值数量
        self._add_int_parameter(
            "n_peaks", "峰值数量",
            3, 1, 10
        )
        
        # 谷值数量
        self._add_int_parameter(
            "n_valleys", "谷值数量",
            2, 1, 10
        )
        
        # 波形长度
        self._add_float_parameter(
            "waveform_length_ms", "波形长度",
            3.0, 1.0, 5.0,
            "毫秒"
        )
    
    def _create_kmeans_parameters(self):
        """创建K-Means聚类参数配置"""
        self.param_group.setTitle("参数配置 - K-Means聚类")
        
        # 聚类数量
        self._add_int_parameter(
            "n_clusters", "聚类数量",
            3, 2, 10
        )
        
        # 最大迭代次数
        self._add_int_parameter(
            "max_iter", "最大迭代次数",
            300, 100, 1000
        )
        
        # 随机种子
        self._add_int_parameter(
            "random_state", "随机种子",
            42, 0, 1000
        )
    
    def _create_gmm_parameters(self):
        """创建GMM聚类参数配置"""
        self.param_group.setTitle("参数配置 - GMM聚类")
        
        # 聚类数量
        self._add_int_parameter(
            "n_components", "聚类数量",
            3, 2, 10
        )
        
        # 最大迭代次数
        self._add_int_parameter(
            "max_iter", "最大迭代次数",
            100, 50, 500
        )
        
        # 协方差类型
        self._add_select_parameter(
            "covariance_type", "协方差类型",
            ["full", "tied", "diag", "spherical"],
            "full"
        )
        
        # 随机种子
        self._add_int_parameter(
            "random_state", "随机种子",
            42, 0, 1000
        )
    
    def _create_lfp_analysis_parameters(self):
        """创建LFP分析参数配置"""
        self.param_group.setTitle("参数配置 - LFP分析")
        
        # 频谱分析方法
        self._add_select_parameter(
            "spectrum_method", "频谱分析方法",
            ["welch", "multitaper", "periodogram"],
            "welch"
        )
        
        # 窗口大小
        self._add_float_parameter(
            "window_size", "窗口大小",
            1.0, 0.1, 10.0,
            "秒"
        )
        
        # 重叠比例
        self._add_float_parameter(
            "overlap", "重叠比例",
            0.5, 0.0, 0.9,
            ""
        )
        
        # 频率分辨率
        self._add_float_parameter(
            "freq_resolution", "频率分辨率",
            1.0, 0.1, 10.0,
            "Hz"
        )
    
    def _create_lfp_power_spectrum_parameters(self):
        """创建LFP功率谱参数配置"""
        self.param_group.setTitle("参数配置 - LFP功率谱")
        
        # 窗函数类型
        self._add_select_parameter(
            "window_type", "窗函数类型",
            ["hann", "hamming", "blackman", "bartlett", "boxcar"],
            "hann"
        )
        
        # FFT点数
        self._add_int_parameter(
            "nfft", "FFT点数",
            2048, 256, 8192
        )
        
        # 重叠样本数
        self._add_int_parameter(
            "noverlap", "重叠样本数",
            1024, 0, 4096
        )
        
        # 最低频率
        self._add_float_parameter(
            "freq_low", "最低频率",
            1.0, 0.1, 100.0,
            "Hz"
        )
        
        # 最高频率
        self._add_float_parameter(
            "freq_high", "最高频率",
            100.0, 10.0, 500.0,
            "Hz"
        )
        
        # 平均方法
        self._add_select_parameter(
            "average_method", "平均方法",
            ["mean", "median"],
            "mean"
        )
        
        # 平滑系数
        self._add_float_parameter(
            "smooth_sigma", "平滑系数",
            1.0, 0.0, 5.0,
            ""
        )
    
    def _create_lfp_spectrogram_parameters(self):
        """创建LFP时频图参数配置"""
        self.param_group.setTitle("参数配置 - LFP时频图")
        
        # 窗函数类型
        self._add_select_parameter(
            "window_type", "窗函数类型",
            ["hann", "hamming", "blackman", "bartlett"],
            "hann"
        )
        
        # 每段样本数
        self._add_int_parameter(
            "nperseg", "每段样本数",
            256, 64, 2048
        )
        
        # 重叠样本数
        self._add_int_parameter(
            "noverlap", "重叠样本数",
            128, 0, 1024
        )
        
        # FFT点数
        self._add_int_parameter(
            "nfft", "FFT点数",
            256, 64, 2048
        )
        
        # 最低频率
        self._add_float_parameter(
            "freq_low", "最低频率",
            1.0, 0.1, 100.0,
            "Hz"
        )
        
        # 最高频率
        self._add_float_parameter(
            "freq_high", "最高频率",
            100.0, 10.0, 500.0,
            "Hz"
        )
        
        # 通道索引
        self._add_int_parameter(
            "channel_idx", "通道索引",
            -1, -1, 100
        )
    
    def _create_behavior_analysis_parameters(self):
        """创建行为分析参数配置"""
        self.param_group.setTitle("参数配置 - 行为分析")
        
        # 时间窗口大小
        self._add_float_parameter(
            "time_window", "时间窗口大小",
            0.1, 0.01, 1.0,
            "秒"
        )
        
        # 分箱大小
        self._add_float_parameter(
            "bin_size", "分箱大小",
            0.01, 0.001, 0.1,
            "秒"
        )
        
        # 平滑窗口
        self._add_int_parameter(
            "smooth_window", "平滑窗口",
            5, 1, 20
        )
        
        # 是否归一化
        self._add_bool_parameter(
            "normalize", "归一化",
            True
        )
    
    def _create_intelligence_analysis_parameters(self):
        """创建智能分析参数配置"""
        self.param_group.setTitle("参数配置 - 智能分析")
        
        # 分析方法
        self._add_select_parameter(
            "analysis_method", "分析方法",
            ["lda", "svm", "random_forest"],
            "lda"
        )
        
        # 训练集比例
        self._add_float_parameter(
            "train_ratio", "训练集比例",
            0.8, 0.5, 0.9,
            ""
        )
        
        # 交叉验证折数
        self._add_int_parameter(
            "cv_folds", "交叉验证折数",
            5, 2, 10
        )
        
        # 随机种子
        self._add_int_parameter(
            "random_state", "随机种子",
            42, 0, 1000
        )
    
    def _create_psth_parameters(self):
        """创建PSTH分析参数配置"""
        self.param_group.setTitle("参数配置 - PSTH分析")

        # 刺激前时间（与算法参数名一致）
        self._add_float_parameter(
            "pre_time", "刺激前时间",
            200.0, 50.0, 1000.0,
            "ms"
        )

        # 刺激后时间（与算法参数名一致）
        self._add_float_parameter(
            "post_time", "刺激后时间",
            1000.0, 100.0, 2000.0,
            "ms"
        )

        # 时间窗大小（与算法参数名一致）
        self._add_float_parameter(
            "bin_size", "时间窗大小",
            10.0, 1.0, 100.0,
            "ms"
        )

        # 高斯平滑系数（与算法参数名一致）
        self._add_float_parameter(
            "smoothing_sigma", "高斯平滑系数",
            20.0, 0.0, 100.0,
            "ms"
        )

        # 事件类型（与算法参数名一致）
        self._add_string_parameter(
            "event_type", "事件类型",
            "stimulus_onset"
        )
    
    def _create_raster_parameters(self):
        """创建栅格图参数配置"""
        self.param_group.setTitle("参数配置 - 栅格图")
        
        # 刺激前时间（与算法参数名一致）
        self._add_float_parameter(
            "pre_time", "刺激前时间",
            200.0, 50.0, 1000.0,
            "ms"
        )
        
        # 刺激后时间（与算法参数名一致）
        self._add_float_parameter(
            "post_time", "刺激后时间",
            1000.0, 100.0, 2000.0,
            "ms"
        )
        
        # 排序方式（与算法参数名一致）
        self._add_select_parameter(
            "sort_by", "排序方式",
            ["time", "response"], "time"
        )
        
        # 显示基线期（与算法参数名一致）
        self._add_bool_parameter(
            "show_baseline", "显示基线期",
            True
        )
    
    def _create_tuning_curve_parameters(self):
        """创建调谐曲线参数配置"""
        self.param_group.setTitle("参数配置 - 调谐曲线")
        
        # 刺激前基线时间（与算法参数名一致）
        self._add_float_parameter(
            "pre_time", "刺激前基线时间",
            200.0, 50.0, 1000.0,
            "ms"
        )
        
        # 刺激后响应时间（与算法参数名一致）
        self._add_float_parameter(
            "post_time", "刺激后响应时间",
            500.0, 100.0, 2000.0,
            "ms"
        )
        
        # 响应指标（与算法参数名一致）
        self._add_select_parameter(
            "metric", "响应指标",
            ["rate", "count"], "rate"
        )
        
        # 刺激条件字段名（与算法参数名一致）
        self._add_string_parameter(
            "stim_condition_key", "刺激条件字段名",
            "stim_cnd"
        )
    
    def _create_roc_parameters(self):
        """创建ROC分析参数配置"""
        self.param_group.setTitle("参数配置 - ROC分析")
        
        # 基线时间
        self._add_float_parameter(
            "pre_time", "基线时间",
            200.0, 50.0, 1000.0,
            "ms"
        )
        
        # 响应时间
        self._add_float_parameter(
            "post_time", "响应时间",
            500.0, 100.0, 2000.0,
            "ms"
        )
        
        # 正类标签
        self._add_int_parameter(
            "positive_class", "正类标签",
            1, 0, 10
        )
    
    def _create_lda_parameters(self):
        """创建LDA解码参数配置"""
        self.param_group.setTitle("参数配置 - LDA解码")
        
        # 求解器
        self._add_select_parameter(
            "solver", "求解器",
            ["svd", "lsqr", "eigen"],
            "svd"
        )
        
        # 收缩参数
        self._add_select_parameter(
            "shrinkage", "收缩参数",
            ["auto", "none", "manual"],
            "auto"
        )
        
        # 手动收缩值（当shrinkage为manual时使用）
        self._add_float_parameter(
            "shrinkage_value", "手动收缩值",
            0.1, 0.0, 1.0,
            ""
        )
        
        # 降维维度
        self._add_int_parameter(
            "n_components", "降维维度",
            2, 1, 10
        )
        
        # 测试集比例
        self._add_float_parameter(
            "test_size", "测试集比例",
            0.2, 0.1, 0.5,
            ""
        )
        
        # 交叉验证折数
        self._add_int_parameter(
            "cv_folds", "交叉验证折数",
            5, 2, 10
        )
        
        # 随机种子
        self._add_int_parameter(
            "random_state", "随机种子",
            42, 0, 1000
        )
        
        # 特征类型
        self._add_select_parameter(
            "feature_type", "特征类型",
            ["spike", "lfp", "combined"],
            "spike"
        )
    
    def _create_svm_parameters(self):
        """创建SVM分类参数配置"""
        self.param_group.setTitle("参数配置 - SVM分类")
        
        # 核函数
        self._add_select_parameter(
            "kernel", "核函数",
            ["rbf", "linear", "poly", "sigmoid"],
            "rbf"
        )
        
        # C参数
        self._add_float_parameter(
            "C", "正则化参数",
            1.0, 0.01, 100.0,
            ""
        )
        
        # gamma参数 - 算法定义中是SELECT类型
        self._add_select_parameter(
            "gamma", "核系数",
            ["scale", "auto"],
            "scale"
        )
        
        # 多项式次数（仅poly核使用）
        self._add_int_parameter(
            "degree", "多项式次数",
            3, 2, 10
        )
        
        # 测试集比例 - 与算法定义一致
        self._add_float_parameter(
            "test_size", "测试集比例",
            0.2, 0.1, 0.5,
            ""
        )
        
        # 交叉验证折数
        self._add_int_parameter(
            "cv_folds", "交叉验证折数",
            5, 2, 10
        )
        
        # 随机种子
        self._add_int_parameter(
            "random_state", "随机种子",
            42, 0, 1000
        )
        
        # 特征类型
        self._add_select_parameter(
            "feature_type", "特征类型",
            ["spike", "lfp", "combined"],
            "spike"
        )
    
    def _create_random_forest_parameters(self):
        """创建随机森林参数配置"""
        self.param_group.setTitle("参数配置 - 随机森林")
        
        # 树的数量
        self._add_int_parameter(
            "n_estimators", "树的数量",
            100, 10, 500
        )
        
        # 最大深度
        self._add_int_parameter(
            "max_depth", "最大深度",
            10, 1, 50
        )
        
        # 最小分裂样本数
        self._add_int_parameter(
            "min_samples_split", "分裂最小样本数",
            2, 2, 20
        )
        
        # 叶子最小样本数
        self._add_int_parameter(
            "min_samples_leaf", "叶子最小样本数",
            1, 1, 20
        )
        
        # 特征采样
        self._add_select_parameter(
            "max_features", "特征采样",
            ["sqrt", "log2", "auto"],
            "sqrt"
        )
        
        # 测试集比例
        self._add_float_parameter(
            "test_size", "测试集比例",
            0.2, 0.1, 0.5,
            ""
        )
        
        # 交叉验证折数
        self._add_int_parameter(
            "cv_folds", "交叉验证折数",
            5, 2, 10
        )
        
        # 随机种子
        self._add_int_parameter(
            "random_state", "随机种子",
            42, 0, 1000
        )
        
        # 特征类型
        self._add_select_parameter(
            "feature_type", "特征类型",
            ["spike", "lfp", "combined"],
            "spike"
        )
    
    def _add_float_parameter(self, name: str, label: str, 
                            default: float, min_val: float, max_val: float,
                            unit: str = ""):
        """
        添加浮点数参数
        
        Args:
            name: 参数名
            label: 显示标签
            default: 默认值
            min_val: 最小值
            max_val: 最大值
            unit: 单位
        """
        # 创建标签（包含范围信息）
        range_text = f"({min_val} - {max_val}"
        if unit:
            range_text += f" {unit}"
        range_text += ")"
        
        full_label = f"{label} {range_text}"
        
        # 创建标签控件，启用自动换行
        label_widget = QLabel(full_label)
        label_widget.setWordWrap(True)
        label_widget.setMinimumHeight(30)  # 设置最小高度确保文字不被截断
        label_widget.setMaximumWidth(200)  # 设置标签最大宽度
        
        # 创建输入框
        edit = QLineEdit()
        edit.setText(str(default))
        edit.setPlaceholderText(f"默认值: {default}")
        edit.setMinimumHeight(25)  # 设置输入框最小高度
        edit.setMinimumWidth(80)   # 设置输入框最小宽度
        edit.setStyleSheet("QLineEdit { padding: 2px 5px; }")
        
        # 添加到布局
        self.param_layout.addRow(label_widget, edit)
        self.param_widgets[name] = edit
    
    def _add_int_parameter(self, name: str, label: str,
                          default: int, min_val: int, max_val: int):
        """
        添加整数参数
        
        Args:
            name: 参数名
            label: 显示标签
            default: 默认值
            min_val: 最小值
            max_val: 最大值
        """
        # 创建标签（包含范围信息）
        full_label = f"{label} ({min_val} - {max_val})"
        
        # 创建标签控件，启用自动换行
        label_widget = QLabel(full_label)
        label_widget.setWordWrap(True)
        label_widget.setMinimumHeight(30)  # 设置最小高度确保文字不被截断
        label_widget.setMaximumWidth(200)  # 设置标签最大宽度
        
        # 创建输入框
        edit = QLineEdit()
        edit.setText(str(default))
        edit.setPlaceholderText(f"默认值: {default}")
        edit.setMinimumHeight(25)  # 设置输入框最小高度
        edit.setMinimumWidth(80)   # 设置输入框最小宽度
        edit.setStyleSheet("QLineEdit { padding: 2px 5px; }")
        
        # 添加到布局
        self.param_layout.addRow(label_widget, edit)
        self.param_widgets[name] = edit
    
    def _add_select_parameter(self, name: str, label: str,
                             options: List[str], default: str):
        """
        添加选择参数
        
        Args:
            name: 参数名
            label: 显示标签
            options: 选项列表
            default: 默认值
        """
        # 创建标签控件，启用自动换行
        label_widget = QLabel(f"{label}:")
        label_widget.setWordWrap(True)
        label_widget.setMinimumHeight(30)  # 设置最小高度确保文字不被截断
        label_widget.setMaximumWidth(200)  # 设置标签最大宽度
        
        # 创建下拉框
        combo = QComboBox()
        for option in options:
            combo.addItem(option)
        
        # 设置默认值
        index = combo.findText(default)
        if index >= 0:
            combo.setCurrentIndex(index)
        
        combo.setMinimumHeight(25)  # 设置最小高度
        combo.setMinimumWidth(80)   # 设置最小宽度
        
        # 添加到布局
        self.param_layout.addRow(label_widget, combo)
        self.param_widgets[name] = combo
    
    def _add_bool_parameter(self, name: str, label: str, default: bool):
        """
        添加布尔参数
        
        Args:
            name: 参数名
            label: 显示标签
            default: 默认值
        """
        # 创建复选框
        checkbox = QCheckBox(label)
        checkbox.setChecked(default)
        checkbox.setMinimumHeight(25)  # 设置最小高度确保文字不被截断
        
        # 添加到布局
        self.param_layout.addRow(checkbox)
        self.param_widgets[name] = checkbox
    
    def _add_string_parameter(self, name: str, label: str, default: str = ""):
        """
        添加字符串参数
        
        Args:
            name: 参数名
            label: 显示标签
            default: 默认值
        """
        # 创建输入框
        edit = QLineEdit()
        edit.setText(str(default))
        edit.setPlaceholderText(f"默认值: {default}")
        
        # 添加到布局
        self.param_layout.addRow(f"{label}:", edit)
        self.param_widgets[name] = edit
    
    def add_data_item(self, data_item: Dict[str, Any]):
        """
        添加数据项到选择列表（支持跨试验）
        
        Args:
            data_item: 数据项字典，包含id, name, trial_name, data_type等信息
        """
        logger.info("add_data_item 被调用")
        logger.log_vars(data_item_type=type(data_item))
        
        # 确保data_item是字典类型
        if not isinstance(data_item, dict):
            logger.error(f"add_data_item接收到的不是字典类型: {type(data_item)}, 值: {data_item}")
            return
        
        # 生成唯一标识
        data_id = data_item.get('id', '')
        trial_name = data_item.get('trial_name', '')
        unique_id = f"{trial_name}/{data_id}"
        
        # 检查是否已存在
        if unique_id in self.selected_data_ids:
            return
        
        # 添加到列表
        self.selected_data_items.append(data_item)
        self.selected_data_ids.add(unique_id)
        
        # 更新UI
        self._update_selected_data_list()
    
    def add_trial_data(self, trial_name: str, data_items: List[Dict[str, Any]]):
        """
        添加整个试验的所有数据项
        
        Args:
            trial_name: 试验名称
            data_items: 该试验的数据项列表
        """
        for data_item in data_items:
            # 确保data_item是字典类型
            if not isinstance(data_item, dict):
                print(f"警告: add_trial_data中包含非字典类型: {type(data_item)}")
                continue
            
            # 确保数据项包含试验名称
            if 'trial_name' not in data_item:
                data_item['trial_name'] = trial_name
            self.add_data_item(data_item)
    
    def _update_selected_data_list(self):
        """更新已选择数据列表的UI显示"""
        self.selected_data_list.clear()
        
        for item in self.selected_data_items:
            # 确保item是字典类型
            if not isinstance(item, dict):
                print(f"警告: selected_data_items中包含非字典类型: {type(item)}")
                continue
                
            trial_name = item.get('trial_name', 'Unknown')
            data_name = item.get('display_name', item.get('id', 'Unknown'))
            data_type = item.get('data_type', '')
            
            # 显示格式：试验名 - 数据名 (类型)
            display_text = f"[{trial_name}] {data_name}"
            if data_type:
                display_text += f" ({data_type})"
            
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            list_item.setToolTip(f"试验: {trial_name}\n数据: {data_name}\n类型: {data_type}")
            self.selected_data_list.addItem(list_item)
        
        # 更新数据选择组标题
        count = len(self.selected_data_items)
        self.data_group.setTitle(f"数据选择（跨试验）- 已选择 {count} 项")
    
    def _remove_selected_data(self):
        """移除选中的数据项"""
        selected_rows = []
        for item in self.selected_data_list.selectedItems():
            row = self.selected_data_list.row(item)
            selected_rows.append(row)
        
        # 从后往前删除，避免索引变化
        for row in sorted(selected_rows, reverse=True):
            if 0 <= row < len(self.selected_data_items):
                data_item = self.selected_data_items.pop(row)
                # 从ID集合中移除
                if isinstance(data_item, dict):
                    data_id = data_item.get('id', '')
                    trial_name = data_item.get('trial_name', '')
                    unique_id = f"{trial_name}/{data_id}"
                    self.selected_data_ids.discard(unique_id)
        
        self._update_selected_data_list()
    
    def _clear_all_data(self):
        """清空所有数据项"""
        self.selected_data_items.clear()
        self.selected_data_ids.clear()
        self._update_selected_data_list()
    
    def _populate_algorithms(self):
        """填充算法下拉列表 - 显示所有算法"""
        algorithms = self.scheduler.get_available_algorithms()
        
        self.algo_combo.clear()
        self.algo_combo.addItem("-- 选择算法 --", None)
        
        for algo in algorithms:
            display_text = f"{algo['name']} ({algo['category']})"
            self.algo_combo.addItem(display_text, algo['name'])
    
    def _populate_custom_algorithms(self):
        """Populate custom algorithms dropdown - show only custom algorithms"""
        logger.info("=" * 60)
        logger.info("_populate_custom_algorithms started")
        
        # Force reload custom algorithms
        try:
            logger.info("Attempting to reload custom algorithms...")
            # Clear module cache
            import sys
            # Clear all potential custom algorithm modules
            modules_to_remove = []
            for module_name in list(sys.modules.keys()):
                if (module_name.startswith('src.algorithms') or
                    module_name.startswith('custom_algorithms') or
                    module_name.endswith('algorithm')):
                    modules_to_remove.append(module_name)
            
            # Clear module cache
            for module_name in modules_to_remove:
                if module_name in sys.modules:
                    del sys.modules[module_name]
                    logger.info(f"Removed module from cache: {module_name}")
            
            # Reload custom algorithms
            self.scheduler._load_custom_algorithms()
            logger.info("Custom algorithms reload completed")
        except Exception as e:
            logger.error(f"Failed to reload custom algorithms: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Get all algorithm instances
        algorithms = self.scheduler.get_algorithms()
        
        logger.info(f"Total algorithms available: {len(algorithms)}")
        
        self.algo_combo.clear()
        self.algo_combo.addItem("-- Select Algorithm --", None)
        
        custom_count = 0
        for algo_name, algo_class in algorithms.items():
            # Show only custom algorithms, consistent with manage algorithms dialog
            if hasattr(algo_class, 'category') and algo_class.category == "Custom Algorithm":
                display_text = f"{algo_name}"
                self.algo_combo.addItem(display_text, algo_name)
                custom_count += 1
                logger.info(f"Added custom algorithm: {algo_name} (category: {algo_class.category})")
        
        logger.info(f"Total custom algorithms added: {custom_count}")
        logger.info("=" * 60)
    
    def _on_algorithm_changed(self, text: str):
        """算法选择改变"""
        try:
            if text == "-- 选择算法 --":
                self.current_algorithm = None
                self.algo_description.setText("请选择算法")
                # 清空参数面板
                self._clear_parameter_widgets()
                return
            
            algo_name = self.algo_combo.currentData()
            if algo_name:
                self.current_algorithm = algo_name
                self._update_algorithm_info(algo_name)
        except Exception as e:
            print(f"算法选择错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_algorithm_info(self, algo_name: str):
        """更新算法信息"""
        # 获取算法信息
        algo_info = self.scheduler.get_algorithm_info(algo_name)
        if algo_info:
            description = algo_info.get('description', '无描述')
            self.algo_description.setText(description)
    
    def set_available_data(self, data_items: List[Any]):
        """
        设置可用数据项（旧方法，保留兼容）
        现在主要使用add_data_item方法添加跨试验数据
        """
        # 这个方法保留用于兼容性，实际数据通过add_data_item添加
        pass
    
    def _select_all_data(self):
        """全选数据（已弃用，保留兼容）"""
        self.selected_data_list.selectAll()
    
    def _clear_data_selection(self):
        """清除数据选择（已弃用，保留兼容）"""
        pass
    
    def _on_time_alignment_clicked(self):
        """时间对齐按钮点击"""
        # 检查是否有足够的数据项
        if len(self.selected_data_items) < 2:
            QMessageBox.information(self, "提示", "请至少选择2个数据项进行时间对齐")
            return
        
        self.time_alignment_requested.emit()
    
    def set_time_alignment(self, config: TimeAlignmentConfig):
        """设置时间对齐配置"""
        self.time_alignment_config = config
    
    def _get_selected_data_items(self) -> List[Dict[str, Any]]:
        """获取选中的数据项"""
        # 返回所有已选择的数据项（支持跨试验），过滤掉非字典类型的数据
        logger.info("_get_selected_data_items 被调用")
        logger.log_vars(selected_data_items_len=len(self.selected_data_items))
        
        for i, item in enumerate(self.selected_data_items):
            logger.log_vars(**{f"selected_data_items_{i}_type": type(item)})
            if not isinstance(item, dict):
                logger.error(f"selected_data_items[{i}] 不是字典! 类型: {type(item)}, 值: {item}")
        
        valid_items = [item for item in self.selected_data_items if isinstance(item, dict)]
        logger.info(f"返回 {len(valid_items)} 个有效数据项")
        return valid_items
    
    def _get_default_parameters_for_algorithm(self, algorithm_name: str) -> Dict[str, Any]:
        """
        获取算法的默认参数
        
        Args:
            algorithm_name: 算法名称
            
        Returns:
            默认参数字典
        """
        try:
            algorithm = self.scheduler.get_algorithm(algorithm_name)
            if algorithm and hasattr(algorithm, 'get_default_parameters'):
                return algorithm.get_default_parameters()
            elif algorithm and hasattr(algorithm, 'get_parameters_schema'):
                # 从参数模式构建默认参数
                params_schema = algorithm.get_parameters_schema()
                defaults = {}
                for param in params_schema:
                    defaults[param.name] = param.default_value
                return defaults
        except Exception as e:
            logger.error(f"获取算法默认参数失败: {e}")
        
        return {}
    
    def _get_parameter_values(self) -> Dict[str, Any]:
        """获取参数值"""
        values = {}
        
        for param_name, widget in self.param_widgets.items():
            if isinstance(widget, QLineEdit):
                text = widget.text()
                # 尝试转换为数字
                try:
                    if '.' in text:
                        values[param_name] = float(text)
                    else:
                        values[param_name] = int(text)
                except ValueError:
                    values[param_name] = text
            elif isinstance(widget, QComboBox):
                values[param_name] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                values[param_name] = widget.isChecked()
        
        return values
    
    def _on_run_clicked(self):
        """运行按钮点击"""
        logger.info("=" * 60)
        logger.info("_on_run_clicked 被调用")
        
        # 检查数据选择
        selected_data = self._get_selected_data_items()
        logger.log_vars(
            selected_data_type=type(selected_data),
            selected_data_len=len(selected_data) if selected_data else 0
        )
        
        if selected_data:
            for i, item in enumerate(selected_data):
                logger.log_vars(**{f"item_{i}_type": type(item)})
                if isinstance(item, dict):
                    logger.info(f"item[{i}] keys: {list(item.keys())}")
                else:
                    logger.error(f"item[{i}] 不是字典! 值: {item}")
        
        if not selected_data:
            QMessageBox.warning(self, "警告", "请从左侧导航栏双击添加要分析的数据")
            return
        
        # 确定要运行的算法名称
        # 优先使用当前选择的算法，如果没有则使用标签页名称映射
        if self.current_algorithm and self.current_algorithm != "":
            algorithm_name = self.current_algorithm
        else:
            # Map tab name to default algorithm
            algorithm_name = self._get_default_algorithm_for_tab(self.current_tab_name)
        
        # Get parameters
        if self.current_mode == PanelMode.CUSTOM_ALGORITHM:
            # Custom algorithm mode: use algorithm default parameters
            parameters = self._get_default_parameters_for_algorithm(algorithm_name)
            logger.info(f"Custom algorithm using default parameters: {parameters}")
        else:
            # Analysis mode: get parameters from parameter panel
            parameters = self._get_parameter_values()
        
        logger.log_vars(parameters_keys=list(parameters.keys()) if parameters else [])
        
        logger.log_vars(algorithm_name=algorithm_name, current_algorithm=self.current_algorithm)
        
        # Handle time alignment configuration
        time_alignment_dict = None
        if self.time_alignment_config:
            try:
                time_alignment_dict = self.time_alignment_config.to_dict()
                logger.info(f"Time alignment config: {time_alignment_dict}")
            except Exception as e:
                logger.exception(e, "Error converting time alignment config")
                time_alignment_dict = None
        
        # 构建请求
        request = {
            'algorithm': algorithm_name,
            'data_items': selected_data,
            'parameters': parameters,
            'time_alignment': time_alignment_dict
        }
        
        logger.info(f"发送请求: algorithm={algorithm_name}, data_items数量={len(selected_data)}")
        self.run_analysis_requested.emit(request)
    
    def _get_default_algorithm_for_tab(self, tab_name: str) -> str:
        """
        Get default algorithm based on tab name
        
        Args:
            tab_name: Tab name
            
        Returns:
            Algorithm name
        """
        tab_algorithm_map = {
            "Spike Detection": "SpikeDetectionThreshold",
            "Spike Sorting": "SpikeSortingPCA",
            "LFP Analysis": "LFPPowerSpectrum",
            "Behavior Analysis": "PSTHAnalysis",
            "Smart Analysis": "LDADecoder",
            "Custom Algorithms": ""
        }
        return tab_algorithm_map.get(tab_name, "")
    
    def _reset_parameters(self):
        """重置参数"""
        # 根据当前标签页重新加载默认参数
        if self.current_tab_name:
            self._load_parameters_for_tab(self.current_tab_name)
    
    def clear_all_data(self):
        """清空所有数据（公共接口）"""
        self._clear_all_data()
    
    def get_selected_data_count(self) -> int:
        """获取已选择的数据项数量"""
        return len(self.selected_data_items)


if __name__ == '__main__':
    # 测试代码
    import sys
    from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = QWidget()
    layout = QVBoxLayout(window)
    
    panel = ParameterPanel()
    panel.run_analysis_requested.connect(lambda req: print(f"Run analysis: {req}"))
    layout.addWidget(panel)
    
    # 添加测试按钮
    btn_analysis = QPushButton("Switch to Spike Detection")
    btn_analysis.clicked.connect(lambda: panel.set_panel_mode("Spike Detection"))
    layout.addWidget(btn_analysis)
    
    btn_sorting = QPushButton("Switch to Spike Sorting")
    btn_sorting.clicked.connect(lambda: panel.set_panel_mode("Spike Sorting"))
    layout.addWidget(btn_sorting)
    
    btn_lfp = QPushButton("Switch to LFP Analysis")
    btn_lfp.clicked.connect(lambda: panel.set_panel_mode("LFP Analysis"))
    layout.addWidget(btn_lfp)
    
    btn_custom = QPushButton("Switch to Custom Algorithms")
    btn_custom.clicked.connect(lambda: panel.set_panel_mode("Custom Algorithms"))
    layout.addWidget(btn_custom)
    
    # 添加测试数据按钮
    def add_test_data():
        test_data = {
            'id': 'test_data_1',
            'display_name': 'Test Data 1',
            'trial_name': 'Trial_001',
            'data_type': 'spike'
        }
        panel.add_data_item(test_data)
    
    btn_add_data = QPushButton("添加测试数据")
    btn_add_data.clicked.connect(add_test_data)
    layout.addWidget(btn_add_data)
    
    window.show()
    
    sys.exit(app.exec())
