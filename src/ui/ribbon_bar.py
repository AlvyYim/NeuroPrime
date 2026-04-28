"""
RibbonBar - Ribbon工具栏组件

提供标签页式工具栏，包含数据加载、Spike检测、Spike排序、LFP分析、行为分析、智能分析、自定义算法等标签页
"""

from typing import Dict, Any, Optional, Callable, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QToolButton, QLabel, QButtonGroup, QFrame,
    QSizePolicy, QSpacerItem, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QAction

# 导入样式
from .styles import Styles


class RibbonTab(QWidget):
    """Ribbon标签页基类"""
    
    action_triggered = pyqtSignal(str, dict)  # action_name, params
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI - 子类重写"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        layout.addStretch()
    
    def _create_tool_button(self, text: str, icon_name: str = None,
                           tooltip: str = None, checkable: bool = False) -> QToolButton:
        """创建工具按钮"""
        btn = QToolButton(self)
        btn.setText(text)
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        if icon_name:
            # 这里可以使用实际的图标
            btn.setIconSize(QSize(24, 24))
        
        if tooltip:
            btn.setToolTip(tooltip)
        
        btn.setCheckable(checkable)
        btn.setMinimumSize(40, 40)
        btn.setMaximumSize(150, 70)
        btn.setEnabled(True)  # 确保按钮被启用
        
        # 设置按钮样式，使其更明显
        btn.setStyleSheet(Styles.TOOL_BUTTON)
        
        return btn
    
    def _create_separator(self) -> QFrame:
        """创建分隔线"""
        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator
    
    def set_enabled(self, enabled: bool):
        """设置标签页内所有按钮的启用状态"""
        for child in self.findChildren(QToolButton):
            child.setEnabled(enabled)


class DataLoadingTab(RibbonTab):
    """数据加载标签页"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # 工程操作组
        project_group = self._create_group("Project")
        self.new_project_btn = self._create_tool_button("New Project", tooltip="Create new project")
        self.new_project_btn.clicked.connect(lambda: self.action_triggered.emit("new_project", {}))
        project_group.layout().addWidget(self.new_project_btn)

        self.open_project_btn = self._create_tool_button("Open Project", tooltip="Open existing project")
        self.open_project_btn.clicked.connect(lambda: self.action_triggered.emit("open_project", {}))
        project_group.layout().addWidget(self.open_project_btn)

        self.save_project_btn = self._create_tool_button("Save Project", tooltip="Save current project")
        self.save_project_btn.clicked.connect(lambda: self.action_triggered.emit("save_project", {}))
        project_group.layout().addWidget(self.save_project_btn)

        layout.addWidget(project_group)
        layout.addWidget(self._create_separator())

        # 数据导入组
        import_group = self._create_group("Data Import")
        self.import_trial_btn = self._create_tool_button("Import Trial Data", tooltip="Import single trial data")
        self.import_trial_btn.clicked.connect(lambda: self.action_triggered.emit("import_trial", {}))
        import_group.layout().addWidget(self.import_trial_btn)

        self.batch_import_btn = self._create_tool_button("Batch Import", tooltip="Batch import multiple trials")
        self.batch_import_btn.clicked.connect(lambda: self.action_triggered.emit("batch_import", {}))
        import_group.layout().addWidget(self.batch_import_btn)

        layout.addWidget(import_group)
        layout.addWidget(self._create_separator())

        # 数据管理组
        manage_group = self._create_group("Data Management")
        self.refresh_btn = self._create_tool_button("Refresh Data List", tooltip="Refresh data list")
        self.refresh_btn.clicked.connect(lambda: self.action_triggered.emit("refresh", {}))
        manage_group.layout().addWidget(self.refresh_btn)

        self.delete_btn = self._create_tool_button("Delete Selected Data", tooltip="Delete selected data")
        self.delete_btn.clicked.connect(lambda: self.action_triggered.emit("delete", {}))
        manage_group.layout().addWidget(self.delete_btn)

        layout.addWidget(manage_group)
        layout.addStretch()

        # 初始化按钮状态：导入和管理按钮默认不可用
        self._set_import_buttons_enabled(False)
        self._set_manage_buttons_enabled(False)

    def _set_import_buttons_enabled(self, enabled: bool):
        """设置导入按钮的启用状态"""
        self.import_trial_btn.setEnabled(enabled)
        self.batch_import_btn.setEnabled(enabled)

    def _set_manage_buttons_enabled(self, enabled: bool):
        """设置数据管理按钮的启用状态"""
        self.refresh_btn.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)

    def set_project_opened(self, opened: bool):
        """设置工程已打开/关闭状态"""
        # 工程打开后，导入按钮可用
        self._set_import_buttons_enabled(opened)
        # 工程关闭后，管理按钮也不可用
        if not opened:
            self._set_manage_buttons_enabled(False)

    def set_data_imported(self, has_data: bool):
        """设置是否有数据导入"""
        # 有数据导入后，管理按钮可用
        self._set_manage_buttons_enabled(has_data)

    def _create_group(self, title: str) -> QFrame:
        """创建按钮组"""
        group = QFrame(self)
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        return group


class SpikeDetectionTab(RibbonTab):
    """Spike检测标签页 - 只保留阈值检测"""
    
    algorithm_selected = pyqtSignal(str)  # 算法选择信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_algorithm = "SpikeDetectionThreshold"
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # 检测方法组 - 只保留阈值检测
        method_group = self._create_group("Detection Method")
        self.threshold_btn = self._create_tool_button("Threshold Detection", tooltip="Threshold-based Spike detection", checkable=True)
        self.threshold_btn.setChecked(True)
        self.threshold_btn.clicked.connect(lambda: self._on_algorithm_selected("SpikeDetectionThreshold"))
        method_group.layout().addWidget(self.threshold_btn)
        
        layout.addWidget(method_group)
        layout.addStretch()
    
    def _on_algorithm_selected(self, algorithm_name: str):
        """处理算法选择"""
        self._current_algorithm = algorithm_name
        self.algorithm_selected.emit(algorithm_name)
    
    def _create_group(self, title: str) -> QFrame:
        """创建按钮组"""
        group = QFrame(self)
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        return group


class SpikeSortingTab(RibbonTab):
    """Spike排序标签页 - PCA+KMeans、高斯混合模型、小波变换"""

    algorithm_selected = pyqtSignal(str)  # 算法选择信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_algorithm = "SpikeSortingPCA"

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # 排序方法组
        method_group = self._create_group("排序方法")

        self.pca_btn = self._create_tool_button("PCA+KMeans", tooltip="主成分分析+K-Means聚类", checkable=True)
        self.pca_btn.setChecked(True)
        self.pca_btn.clicked.connect(lambda: self._on_algorithm_selected("SpikeSortingPCA"))
        method_group.layout().addWidget(self.pca_btn)

        self.gmm_btn = self._create_tool_button("高斯混合模型", tooltip="高斯混合模型聚类", checkable=True)
        self.gmm_btn.clicked.connect(lambda: self._on_algorithm_selected("gmm"))
        method_group.layout().addWidget(self.gmm_btn)

        self.wavelet_btn = self._create_tool_button("小波变换", tooltip="小波变换+聚类", checkable=True)
        self.wavelet_btn.clicked.connect(lambda: self._on_algorithm_selected("wavelet_clustering"))
        method_group.layout().addWidget(self.wavelet_btn)

        layout.addWidget(method_group)
        layout.addStretch()

    def _on_algorithm_selected(self, algorithm_name: str):
        """处理算法选择"""
        self._current_algorithm = algorithm_name
        # 更新按钮状态
        self.pca_btn.setChecked(algorithm_name == "SpikeSortingPCA")
        self.gmm_btn.setChecked(algorithm_name == "gmm")
        self.wavelet_btn.setChecked(algorithm_name == "wavelet_clustering")
        self.algorithm_selected.emit(algorithm_name)
    
    def _create_group(self, title: str) -> QFrame:
        """创建按钮组"""
        group = QFrame(self)
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        return group


class LFPAnalysisTab(RibbonTab):
    """LFP分析标签页 - 功率谱、时频图"""
    
    algorithm_selected = pyqtSignal(str)  # 算法选择信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_algorithm = "LFPPowerSpectrum"
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # 分析方法组
        method_group = self._create_group("分析方法")
        
        self.power_spectrum_btn = self._create_tool_button("功率谱", tooltip="计算功率谱密度", checkable=True)
        self.power_spectrum_btn.setChecked(True)
        self.power_spectrum_btn.clicked.connect(lambda: self._on_algorithm_selected("LFPPowerSpectrum"))
        method_group.layout().addWidget(self.power_spectrum_btn)
        
        self.spectrogram_btn = self._create_tool_button("时频图", tooltip="计算时频谱图", checkable=True)
        self.spectrogram_btn.clicked.connect(lambda: self._on_algorithm_selected("LFPSpectrogram"))
        method_group.layout().addWidget(self.spectrogram_btn)
        
        layout.addWidget(method_group)
        layout.addStretch()
    
    def _on_algorithm_selected(self, algorithm_name: str):
        """处理算法选择"""
        self._current_algorithm = algorithm_name
        self.power_spectrum_btn.setChecked(algorithm_name == "LFPPowerSpectrum")
        self.spectrogram_btn.setChecked(algorithm_name == "LFPSpectrogram")
        self.algorithm_selected.emit(algorithm_name)
    
    def _create_group(self, title: str) -> QFrame:
        """创建按钮组"""
        group = QFrame(self)
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        return group


class SpikeAnalysisTab(RibbonTab):
    """Spike分析标签页 - PSTH、栅格图、调谐曲线"""
    
    algorithm_selected = pyqtSignal(str)  # 算法选择信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_algorithm = "PSTHAnalysis"
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # 分析方法组
        method_group = self._create_group("Analysis Method")
        
        self.psth_btn = self._create_tool_button("PSTH Analysis", tooltip="Peri-Stimulus Time Histogram", checkable=True)
        self.psth_btn.setChecked(True)
        self.psth_btn.clicked.connect(lambda: self._on_algorithm_selected("PSTHAnalysis"))
        method_group.layout().addWidget(self.psth_btn)
        
        self.raster_btn = self._create_tool_button("Raster Plot", tooltip="Spike time raster plot", checkable=True)
        self.raster_btn.clicked.connect(lambda: self._on_algorithm_selected("RasterPlotAnalysis"))
        method_group.layout().addWidget(self.raster_btn)
        
        self.tuning_curve_btn = self._create_tool_button("Tuning Curve", tooltip="Stimulus-response tuning relationship", checkable=True)
        self.tuning_curve_btn.clicked.connect(lambda: self._on_algorithm_selected("TuningCurveAnalysis"))
        method_group.layout().addWidget(self.tuning_curve_btn)
        
        layout.addWidget(method_group)
        layout.addStretch()
    
    def _on_algorithm_selected(self, algorithm_name: str):
        """处理算法选择"""
        self._current_algorithm = algorithm_name
        self.psth_btn.setChecked(algorithm_name == "PSTHAnalysis")
        self.raster_btn.setChecked(algorithm_name == "RasterPlotAnalysis")
        self.tuning_curve_btn.setChecked(algorithm_name == "TuningCurveAnalysis")
        self.algorithm_selected.emit(algorithm_name)
    
    def _create_group(self, title: str) -> QFrame:
        """创建按钮组"""
        group = QFrame(self)
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        return group


class BehaviorAnalysisTab(RibbonTab):
    """行为分析标签页 - 仅ROC分析"""
    
    algorithm_selected = pyqtSignal(str)  # 算法选择信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_algorithm = "ROCAnalysis"
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # 分析方法组
        method_group = self._create_group("Analysis Method")
        
        self.roc_btn = self._create_tool_button("ROC Analysis", tooltip="Receiver Operating Characteristic curve", checkable=True)
        self.roc_btn.setChecked(True)
        self.roc_btn.clicked.connect(lambda: self._on_algorithm_selected("ROCAnalysis"))
        method_group.layout().addWidget(self.roc_btn)
        
        layout.addWidget(method_group)
        layout.addStretch()
    
    def _on_algorithm_selected(self, algorithm_name: str):
        """处理算法选择"""
        self._current_algorithm = algorithm_name
        self.roc_btn.setChecked(algorithm_name == "ROCAnalysis")
        self.algorithm_selected.emit(algorithm_name)
    
    def _create_group(self, title: str) -> QFrame:
        """创建按钮组"""
        group = QFrame(self)
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        return group


class IntelligenceAnalysisTab(RibbonTab):
    """智能分析标签页 - LDA解码、SVM分类、随机森林"""
    
    algorithm_selected = pyqtSignal(str)  # 算法选择信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_algorithm = "LDADecoder"
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # 分析方法组
        method_group = self._create_group("分析方法")
        
        self.lda_btn = self._create_tool_button("LDA解码", tooltip="线性判别分析", checkable=True)
        self.lda_btn.setChecked(True)
        self.lda_btn.clicked.connect(lambda: self._on_algorithm_selected("LDADecoder"))
        method_group.layout().addWidget(self.lda_btn)
        
        self.svm_btn = self._create_tool_button("SVM分类", tooltip="支持向量机", checkable=True)
        self.svm_btn.clicked.connect(lambda: self._on_algorithm_selected("SVMClassifier"))
        method_group.layout().addWidget(self.svm_btn)
        
        self.rf_btn = self._create_tool_button("随机森林", tooltip="随机森林分类器", checkable=True)
        self.rf_btn.clicked.connect(lambda: self._on_algorithm_selected("RandomForestClassifier"))
        method_group.layout().addWidget(self.rf_btn)
        
        layout.addWidget(method_group)
        layout.addStretch()
    
    def _on_algorithm_selected(self, algorithm_name: str):
        """处理算法选择"""
        self._current_algorithm = algorithm_name
        self.lda_btn.setChecked(algorithm_name == "LDADecoder")
        self.svm_btn.setChecked(algorithm_name == "SVMClassifier")
        self.rf_btn.setChecked(algorithm_name == "RandomForestClassifier")
        self.algorithm_selected.emit(algorithm_name)
    
    def _create_group(self, title: str) -> QFrame:
        """创建按钮组"""
        group = QFrame(self)
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        return group


class MNEAlgorithmTab(RibbonTab):
    """MNE算法标签页"""
    
    algorithm_selected = pyqtSignal(str)  # 算法选择信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_algorithm = "MNE_CSP"
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # MNE算法组
        mne_group = self._create_group("MNE算法")
        
        self.csp_btn = self._create_tool_button("CSP解码", tooltip="Common Spatial Patterns解码", checkable=True)
        self.csp_btn.setChecked(True)
        self.csp_btn.clicked.connect(lambda: self._on_algorithm_selected("MNE_CSP"))
        mne_group.layout().addWidget(self.csp_btn)
        
        self.ica_btn = self._create_tool_button("ICA分析", tooltip="独立成分分析", checkable=True)
        self.ica_btn.clicked.connect(lambda: self._on_algorithm_selected("MNE_ICA"))
        mne_group.layout().addWidget(self.ica_btn)
        
        self.time_freq_btn = self._create_tool_button("时频分析", tooltip="MNE时频分析", checkable=True)
        self.time_freq_btn.clicked.connect(lambda: self._on_algorithm_selected("MNE_TimeFrequency"))
        mne_group.layout().addWidget(self.time_freq_btn)
        
        self.source_loc_btn = self._create_tool_button("源定位", tooltip="MNE源定位", checkable=True)
        self.source_loc_btn.clicked.connect(lambda: self._on_algorithm_selected("MNE_SourceLocalization"))
        mne_group.layout().addWidget(self.source_loc_btn)
        
        layout.addWidget(mne_group)
        layout.addStretch()
    
    def _on_algorithm_selected(self, algorithm_name: str):
        """处理算法选择"""
        self._current_algorithm = algorithm_name
        self.csp_btn.setChecked(algorithm_name == "MNE_CSP")
        self.ica_btn.setChecked(algorithm_name == "MNE_ICA")
        self.time_freq_btn.setChecked(algorithm_name == "MNE_TimeFrequency")
        self.source_loc_btn.setChecked(algorithm_name == "MNE_SourceLocalization")
        self.algorithm_selected.emit(algorithm_name)
    
    def _create_group(self, title: str) -> QFrame:
        """创建按钮组"""
        group = QFrame(self)
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        return group


class CustomAlgorithmTab(RibbonTab):
    """自定义算法标签页"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # 插件管理组
        plugin_group = self._create_group("插件管理")
        self.import_algo_btn = self._create_tool_button("导入自定义算法", tooltip="导入自定义Python算法文件")
        self.import_algo_btn.clicked.connect(lambda: self.action_triggered.emit("import_custom_algorithm", {}))
        plugin_group.layout().addWidget(self.import_algo_btn)
        
        self.manage_algo_btn = self._create_tool_button("管理自定义算法", tooltip="查看/启用/禁用已导入的算法")
        self.manage_algo_btn.clicked.connect(lambda: self.action_triggered.emit("manage_custom_algorithms", {}))
        plugin_group.layout().addWidget(self.manage_algo_btn)
        
        layout.addWidget(plugin_group)
        layout.addWidget(self._create_separator())
        
        # 工具组
        tool_group = self._create_group("工具")
        # 自定义算法编辑按钮
        self.custom_algorithm_edit_btn = self._create_tool_button("自定义算法编辑", tooltip="打开算法脚本编辑器")
        self.custom_algorithm_edit_btn.clicked.connect(lambda: self.action_triggered.emit("open_mne_terminal", {}))
        tool_group.layout().addWidget(self.custom_algorithm_edit_btn)
        
        layout.addWidget(tool_group)
        layout.addStretch()
    
    def _create_group(self, title: str) -> QFrame:
        """创建按钮组"""
        group = QFrame(self)
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        return group


class RibbonBar(QWidget):
    """
    Ribbon工具栏组件
    
    提供标签页式工具栏，包含多个功能标签页：
    - 数据加载（始终可用）
    - Spike检测（数据加载后可用）
    - Spike排序（数据加载后可用）
    - LFP分析（数据加载后可用）
    - 行为分析（数据加载后可用）
    - 智能分析（数据加载后可用）
    - 自定义算法（数据加载后可用）
    """
    
    action_triggered = pyqtSignal(str, dict)  # action_name, params
    tab_changed = pyqtSignal(str)  # 标签页切换信号，传递标签页名称
    algorithm_selected = pyqtSignal(str)  # 算法选择信号，传递算法名称
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._analytical_tabs: List[QWidget] = []  # 需要数据加载后才能使用的标签页
        self._tab_names: List[str] = []  # 标签页名称列表
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setDocumentMode(True)
        
        # 创建各个标签页
        # 1. 数据加载标签页（始终可用）
        self.data_loading_tab = DataLoadingTab(self)
        self.data_loading_tab.action_triggered.connect(self._on_action_triggered)
        index = self.tab_widget.addTab(self.data_loading_tab, "Data Loading")
        self._tab_names.append("Data Loading")
        
        # 2. Spike检测标签页（需要数据）
        self.spike_detection_tab = SpikeDetectionTab(self)
        self.spike_detection_tab.action_triggered.connect(self._on_action_triggered)
        self.spike_detection_tab.algorithm_selected.connect(self._on_algorithm_selected)
        index = self.tab_widget.addTab(self.spike_detection_tab, "Spike Detection")
        self._analytical_tabs.append((index, self.spike_detection_tab))
        self._tab_names.append("Spike Detection")
        
        # 3. Spike排序标签页（需要数据）
        self.spike_sorting_tab = SpikeSortingTab(self)
        self.spike_sorting_tab.action_triggered.connect(self._on_action_triggered)
        self.spike_sorting_tab.algorithm_selected.connect(self._on_algorithm_selected)
        index = self.tab_widget.addTab(self.spike_sorting_tab, "Spike Sorting")
        self._analytical_tabs.append((index, self.spike_sorting_tab))
        self._tab_names.append("Spike Sorting")
        
        # 4. Spike分析标签页（需要数据）
        self.spike_analysis_tab = SpikeAnalysisTab(self)
        self.spike_analysis_tab.action_triggered.connect(self._on_action_triggered)
        self.spike_analysis_tab.algorithm_selected.connect(self._on_algorithm_selected)
        index = self.tab_widget.addTab(self.spike_analysis_tab, "Spike Analysis")
        self._analytical_tabs.append((index, self.spike_analysis_tab))
        self._tab_names.append("Spike Analysis")
        
        # 5. LFP分析标签页（需要数据）
        self.lfp_analysis_tab = LFPAnalysisTab(self)
        self.lfp_analysis_tab.action_triggered.connect(self._on_action_triggered)
        self.lfp_analysis_tab.algorithm_selected.connect(self._on_algorithm_selected)
        index = self.tab_widget.addTab(self.lfp_analysis_tab, "LFP Analysis")
        self._analytical_tabs.append((index, self.lfp_analysis_tab))
        self._tab_names.append("LFP Analysis")
        
        # 6. 行为分析标签页（需要数据）
        self.behavior_analysis_tab = BehaviorAnalysisTab(self)
        self.behavior_analysis_tab.action_triggered.connect(self._on_action_triggered)
        self.behavior_analysis_tab.algorithm_selected.connect(self._on_algorithm_selected)
        index = self.tab_widget.addTab(self.behavior_analysis_tab, "Behavior Analysis")
        self._analytical_tabs.append((index, self.behavior_analysis_tab))
        self._tab_names.append("Behavior Analysis")
        
        # 6. 智能分析标签页（需要数据）- 暂时注释掉
        # self.intelligence_analysis_tab = IntelligenceAnalysisTab(self)
        # self.intelligence_analysis_tab.action_triggered.connect(self._on_action_triggered)
        # self.intelligence_analysis_tab.algorithm_selected.connect(self._on_algorithm_selected)
        # index = self.tab_widget.addTab(self.intelligence_analysis_tab, "Intelligence Analysis")
        # self._analytical_tabs.append((index, self.intelligence_analysis_tab))
        # self._tab_names.append("Intelligence Analysis")

        
        # 8. 自定义算法标签页（需要数据）
        self.custom_algorithm_tab = CustomAlgorithmTab(self)
        self.custom_algorithm_tab.action_triggered.connect(self._on_action_triggered)
        index = self.tab_widget.addTab(self.custom_algorithm_tab, "Custom Algorithm")
        self._analytical_tabs.append((index, self.custom_algorithm_tab))
        self._tab_names.append("Custom Algorithm")
        
        # 连接标签页切换信号
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        layout.addWidget(self.tab_widget)
        
        # 设置固定高度
        self.setFixedHeight(120)
        # 应用样式
        self.setStyleSheet(Styles.RIBBON_BAR)
        
        # 初始状态：禁用分析标签页
        self.set_analytical_tabs_enabled(False)
    
    def _on_action_triggered(self, action_name: str, params: dict):
        """处理标签页动作"""
        self.action_triggered.emit(action_name, params)
    
    def _on_algorithm_selected(self, algorithm_name: str):
        """处理算法选择"""
        self.algorithm_selected.emit(algorithm_name)
    
    def _on_tab_changed(self, index: int):
        """处理标签页切换"""
        if 0 <= index < len(self._tab_names):
            tab_name = self._tab_names[index]
            self.tab_changed.emit(tab_name)
    
    def set_analytical_tabs_enabled(self, enabled: bool):
        """
        设置分析标签页的启用状态
        
        Args:
            enabled: True表示启用所有分析标签页，False表示禁用
        """
        for index, tab in self._analytical_tabs:
            # 禁用/启用标签页（通过设置tab是否可用）
            self.tab_widget.setTabEnabled(index, enabled)
            # 同时设置标签页内的按钮状态
            tab.set_enabled(enabled)
    
    def set_data_loaded(self, loaded: bool):
        """
        设置数据加载状态
        
        当用户加载数据后，启用所有分析标签页
        
        Args:
            loaded: 是否已加载数据
        """
        self.set_analytical_tabs_enabled(loaded)

    def set_project_opened(self, opened: bool):
        """
        设置工程打开状态
        
        当工程打开后，启用数据导入按钮
        当工程关闭后，禁用数据导入和管理按钮
        
        Args:
            opened: 工程是否已打开
        """
        self.data_loading_tab.set_project_opened(opened)

    def set_data_imported(self, has_data: bool):
        """
        设置数据导入状态
        
        当有数据导入后，启用数据管理按钮
        
        Args:
            has_data: 是否有数据导入
        """
        self.data_loading_tab.set_data_imported(has_data)

    def set_current_tab(self, index: int):
        """设置当前标签页"""
        self.tab_widget.setCurrentIndex(index)
    
    def get_current_tab(self) -> int:
        """获取当前标签页索引"""
        return self.tab_widget.currentIndex()


if __name__ == '__main__':
    # 测试代码
    import sys
    from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = QWidget()
    layout = QVBoxLayout(window)
    
    ribbon = RibbonBar()
    ribbon.action_triggered.connect(lambda name, params: print(f"Action: {name}, Params: {params}"))
    ribbon.algorithm_selected.connect(lambda name: print(f"Algorithm: {name}"))
    layout.addWidget(ribbon)
    
    # 添加测试按钮
    btn_enable = QPushButton("启用分析标签页（模拟数据已加载）")
    btn_enable.clicked.connect(lambda: ribbon.set_data_loaded(True))
    layout.addWidget(btn_enable)
    
    btn_disable = QPushButton("禁用分析标签页（模拟无数据）")
    btn_disable.clicked.connect(lambda: ribbon.set_data_loaded(False))
    layout.addWidget(btn_disable)
    
    window.show()
    
    sys.exit(app.exec())
