"""
NeuroPrime UI 原型
基于PyQt6的猕猴脑电生理数据分析软件界面原型
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTreeWidget, QTreeWidgetItem,
    QTabWidget, QGroupBox, QFormLayout, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QTextEdit,
    QSplitter, QFrame, QMenu, QMessageBox, QFileDialog,
    QStatusBar, QToolButton, QDialog, QTableWidget, QTableWidgetItem,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QAction


class NavigationPanel(QTreeWidget):
    """左侧导航栏"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("工程导航")
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #cccccc;
                background-color: #f5f5f5;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        self.load_sample_data()
        self.expandAll()
        
    def load_sample_data(self):
        project = QTreeWidgetItem(self)
        project.setText(0, "猕猴V1区电生理实验")
        project.setFont(0, QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        
        trial1 = QTreeWidgetItem(project)
        trial1.setText(0, "试验1 (2024-01-15)")
        
        signals1 = QTreeWidgetItem(trial1)
        signals1.setText(0, "电信号数据")
        
        spike1 = QTreeWidgetItem(signals1)
        spike1.setText(0, "Spike数据")
        
        QTreeWidgetItem(spike1).setText(0, "时间戳")
        QTreeWidgetItem(spike1).setText(0, "波形")
        QTreeWidgetItem(spike1).setText(0, "聚类标签")
        
        lfp1 = QTreeWidgetItem(signals1)
        lfp1.setText(0, "LFP信号")
        
        behavior1 = QTreeWidgetItem(trial1)
        behavior1.setText(0, "行为数据")
        
        QTreeWidgetItem(behavior1).setText(0, "事件")
        QTreeWidgetItem(behavior1).setText(0, "试次")
        QTreeWidgetItem(behavior1).setText(0, "刺激")
        
        trial2 = QTreeWidgetItem(project)
        trial2.setText(0, "试验2 (2024-01-16)")
        
        signals2 = QTreeWidgetItem(trial2)
        signals2.setText(0, "电信号数据")
        
        spike2 = QTreeWidgetItem(signals2)
        spike2.setText(0, "Spike数据")
        
        behavior2 = QTreeWidgetItem(trial2)
        behavior2.setText(0, "行为数据")


class TimeAlignDialog(QDialog):
    """时间对齐对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("时间对齐设置")
        self.setGeometry(300, 300, 700, 400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        desc = QLabel("请设置各数据的时间对齐参数。修改一行后，其他行的初始时间和持续时间将自动同步。")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666666; font-size: 11px;")
        layout.addWidget(desc)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["数据名称", "原始时间范围", "分析初始时间", "持续时间"])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 120)
        
        parent = self.parent()
        if parent:
            checked_items = []
            for i in range(parent.data_list.topLevelItemCount()):
                item = parent.data_list.topLevelItem(i)
                if item.checkState(0) == Qt.CheckState.Checked:
                    checked_items.append({
                        'name': item.text(1),
                        'time_range': item.text(3)
                    })
            
            self.table.setRowCount(len(checked_items))
            
            for i, item_data in enumerate(checked_items):
                name_item = QTableWidgetItem(item_data['name'])
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(i, 0, name_item)
                
                range_item = QTableWidgetItem(item_data['time_range'])
                range_item.setFlags(range_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(i, 1, range_item)
                
                start_spin = QDoubleSpinBox()
                start_spin.setRange(0, 1000)
                start_spin.setValue(0)
                start_spin.setSuffix(" s")
                start_spin.setDecimals(2)
                start_spin.valueChanged.connect(self.on_start_time_changed)
                self.table.setCellWidget(i, 2, start_spin)
                
                duration_spin = QDoubleSpinBox()
                duration_spin.setRange(0.1, 1000)
                duration_spin.setValue(10)
                duration_spin.setSuffix(" s")
                duration_spin.setDecimals(2)
                duration_spin.valueChanged.connect(self.on_duration_changed)
                self.table.setCellWidget(i, 3, duration_spin)
        
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("确认对齐")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
    def on_start_time_changed(self, value):
        sender = self.sender()
        sender_row = -1
        
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 2) == sender:
                sender_row = row
                break
        
        if sender_row >= 0:
            for row in range(self.table.rowCount()):
                if row != sender_row:
                    widget = self.table.cellWidget(row, 2)
                    if widget:
                        widget.blockSignals(True)
                        widget.setValue(value)
                        widget.blockSignals(False)
                        
    def on_duration_changed(self, value):
        sender = self.sender()
        sender_row = -1
        
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 3) == sender:
                sender_row = row
                break
        
        if sender_row >= 0:
            for row in range(self.table.rowCount()):
                if row != sender_row:
                    widget = self.table.cellWidget(row, 3)
                    if widget:
                        widget.blockSignals(True)
                        widget.setValue(value)
                        widget.blockSignals(False)


class ParameterPanel(QWidget):
    """参数配置面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 上半部分：参数配置
        title = QLabel("参数配置")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #333333; margin-bottom: 5px;")
        layout.addWidget(title)
        
        self.tabs = QTabWidget()
        self.setup_spike_detection_tab()
        self.setup_advanced_tab()
        layout.addWidget(self.tabs)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #cccccc; margin: 10px 0;")
        line.setFixedHeight(2)
        layout.addWidget(line)
        
        # 下半部分：数据选择
        data_title = QLabel("数据选择")
        data_title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        data_title.setStyleSheet("color: #333333; margin-bottom: 5px;")
        layout.addWidget(data_title)
        
        self.data_list = QTreeWidget()
        self.data_list.setHeaderLabels(["选择", "数据名称", "类型", "时间范围"])
        self.data_list.setColumnWidth(0, 50)
        self.data_list.setColumnWidth(1, 120)
        self.data_list.setColumnWidth(2, 80)
        self.data_list.setColumnWidth(3, 120)
        self.data_list.setMaximumHeight(200)
        self.load_sample_data_list()
        layout.addWidget(self.data_list)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        self.align_btn = QPushButton("时间对齐")
        self.align_btn.setEnabled(False)
        self.align_btn.setStyleSheet("""
            QPushButton {
                background-color: #cccccc;
                color: #666666;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:enabled {
                background-color: #28a745;
                color: white;
            }
            QPushButton:enabled:hover {
                background-color: #218838;
            }
        """)
        self.align_btn.clicked.connect(self.show_time_align_dialog)
        btn_layout.addWidget(self.align_btn)
        
        self.analyze_btn = QPushButton("数据分析")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        btn_layout.addWidget(self.analyze_btn)
        
        layout.addLayout(btn_layout)
        
        self.data_list.itemChanged.connect(self.on_data_selection_changed)
        
    def load_sample_data_list(self):
        sample_items = [
            ("试验1_Spike数据", "Spike", "0-20s"),
            ("试验1_LFP信号", "LFP", "0-20s"),
            ("试验1_行为事件", "行为", "0-20s"),
            ("试验2_Spike数据", "Spike", "0-15s"),
            ("试验2_LFP信号", "LFP", "0-15s"),
        ]
        
        for name, dtype, time_range in sample_items:
            item = QTreeWidgetItem()
            item.setCheckState(0, Qt.CheckState.Unchecked)
            item.setText(1, name)
            item.setText(2, dtype)
            item.setText(3, time_range)
            self.data_list.addTopLevelItem(item)
            
    def on_data_selection_changed(self, item, column):
        if column == 0:
            checked_count = 0
            for i in range(self.data_list.topLevelItemCount()):
                if self.data_list.topLevelItem(i).checkState(0) == Qt.CheckState.Checked:
                    checked_count += 1
            
            self.align_btn.setEnabled(checked_count >= 2)
            
    def show_time_align_dialog(self):
        dialog = TimeAlignDialog(self)
        dialog.exec()
        
    def setup_spike_detection_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setSpacing(15)
        
        method_combo = QComboBox()
        method_combo.addItem("阈值检测")
        layout.addRow("检测方法:", method_combo)
        
        threshold_spin = QDoubleSpinBox()
        threshold_spin.setRange(1.0, 10.0)
        threshold_spin.setValue(4.0)
        threshold_spin.setSingleStep(0.5)
        layout.addRow("阈值倍数:", threshold_spin)
        
        channel_combo = QComboBox()
        channel_combo.addItem("全部通道")
        channel_combo.addItem("选定通道")
        layout.addRow("检测通道:", channel_combo)
        
        window_spin = QSpinBox()
        window_spin.setRange(10, 100)
        window_spin.setValue(50)
        window_spin.setSuffix(" ms")
        layout.addRow("波形窗口:", window_spin)
        
        self.tabs.addTab(tab, "基本参数")
        
    def setup_advanced_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setSpacing(15)
        
        filter_check = QCheckBox("启用滤波")
        filter_check.setChecked(True)
        layout.addRow("滤波:", filter_check)
        
        band_combo = QComboBox()
        band_combo.addItem("300-6000 Hz (Spike)")
        band_combo.addItem("0.5-250 Hz (LFP)")
        layout.addRow("滤波频段:", band_combo)
        
        ref_combo = QComboBox()
        ref_combo.addItem("共平均参考 (CAR)")
        ref_combo.addItem("局部平均参考")
        layout.addRow("重参考:", ref_combo)
        
        self.tabs.addTab(tab, "高级参数")


class VisualizationPanel(QWidget):
    """可视化显示区域"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title_layout = QHBoxLayout()
        title = QLabel("数据可视化")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        zoom_in_btn = QPushButton("放大")
        zoom_out_btn = QPushButton("缩小")
        reset_btn = QPushButton("重置")
        export_btn = QPushButton("导出")
        
        for btn in [zoom_in_btn, zoom_out_btn, reset_btn, export_btn]:
            btn.setFixedHeight(28)
            title_layout.addWidget(btn)
        
        layout.addLayout(title_layout)
        
        self.viz_area = QTextEdit()
        self.viz_area.setReadOnly(True)
        self.viz_area.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 2px dashed #cccccc;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                color: #666666;
            }
        """)
        self.viz_area.setText("可视化区域 - PyQtGraph绘图区")
        layout.addWidget(self.viz_area)
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("采样率: 30000 Hz"))
        status_layout.addWidget(QLabel("通道数: 4"))
        status_layout.addWidget(QLabel("时长: 20.0 s"))
        status_layout.addStretch()
        layout.addLayout(status_layout)


class RibbonBar(QWidget):
    """RibbonBar工具栏 - 使用QTabWidget实现标签页切换"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 顶部区域：标签页
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(10, 5, 10, 0)
        top_layout.setSpacing(5)
        
        # 创建标签页控件
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #f5f5f5;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-bottom-color: #f5f5f5;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 20px;
                margin-right: 2px;
                font-size: 12px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #f5f5f5;
                border-bottom-color: #f5f5f5;
                color: #0078d4;
            }
            QTabBar::tab:hover:!selected {
                background-color: #d0d0d0;
            }
        """)
        
        # 添加各个标签页（不含Home）
        self.tabs.addTab(self.create_data_load_tab(), "数据加载")
        self.tabs.addTab(self.create_spike_detect_tab(), "Spike检测")
        self.tabs.addTab(self.create_spike_sort_tab(), "Spike排序")
        self.tabs.addTab(self.create_lfp_tab(), "LFP分析")
        self.tabs.addTab(self.create_behavior_tab(), "行为分析")
        self.tabs.addTab(self.create_intelligent_tab(), "智能分析")
        self.tabs.addTab(self.create_custom_tab(), "自定义算法")
        
        top_layout.addWidget(self.tabs)
        top_layout.addStretch()
        
        layout.addWidget(top_widget)
        
        # 设置固定高度
        self.setFixedHeight(140)
        self.setStyleSheet("background-color: #f5f5f5;")
        
    def create_button_group(self, title, buttons):
        """创建按钮组"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-size: 10px;
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 3px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px;
                color: #666666;
            }
        """)
        
        group_layout = QHBoxLayout(group)
        group_layout.setSpacing(5)
        group_layout.setContentsMargins(5, 8, 5, 5)
        
        for text in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(65, 55)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f9f9f9;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    font-size: 9px;
                    text-align: center;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #e6f2ff;
                    border-color: #0078d4;
                }
                QPushButton:pressed {
                    background-color: #cce4ff;
                }
            """)
            group_layout.addWidget(btn)
        
        return group
        
    def create_data_load_tab(self):
        """数据加载标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        project_group = self.create_button_group("工程管理", ["新建工程", "打开工程", "保存工程"])
        layout.addWidget(project_group)
        
        import_group = self.create_button_group("导入文件", ["导入电信号", "导入行为数据"])
        layout.addWidget(import_group)
        
        layout.addStretch()
        return tab
        
    def create_spike_detect_tab(self):
        """Spike检测标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        detect_group = self.create_button_group("检测方法", ["阈值检测"])
        layout.addWidget(detect_group)
        
        layout.addStretch()
        return tab
        
    def create_spike_sort_tab(self):
        """Spike排序标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        sort_group = self.create_button_group("排序方法", ["PCA+KMeans", "高斯混合", "小波变换"])
        layout.addWidget(sort_group)
        
        layout.addStretch()
        return tab
        
    def create_lfp_tab(self):
        """LFP分析标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        analysis_group = self.create_button_group("分析方法", ["功率谱分析", "时频分析", "滤波分析"])
        layout.addWidget(analysis_group)
        
        layout.addStretch()
        return tab
        
    def create_behavior_tab(self):
        """行为分析标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        analysis_group = self.create_button_group("分析方法", ["PSTH分析", "栅格图", "调谐曲线", "ROC分析", "解码分析"])
        layout.addWidget(analysis_group)
        
        layout.addStretch()
        return tab
        
    def create_intelligent_tab(self):
        """智能分析标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        analysis_group = self.create_button_group("分析方法", ["LDA解码", "SVM分类", "随机森林"])
        layout.addWidget(analysis_group)
        
        layout.addStretch()
        return tab
        
    def create_custom_tab(self):
        """自定义算法标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        plugin_group = self.create_button_group("插件管理", ["导入算法", "管理算法", "接口测试", "算法文档", "示例代码"])
        layout.addWidget(plugin_group)
        
        layout.addStretch()
        return tab


class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeuroPrime - 猕猴脑电生理数据分析平台")
        self.setGeometry(100, 100, 1400, 900)
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # RibbonBar
        self.ribbon = RibbonBar()
        main_layout.addWidget(self.ribbon)
        
        # 内容区域
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧导航栏
        self.nav_panel = NavigationPanel()
        content_splitter.addWidget(self.nav_panel)
        
        # 右侧区域
        right_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 参数配置面板
        self.param_panel = ParameterPanel()
        self.param_panel.setMinimumWidth(300)
        self.param_panel.setMaximumWidth(400)
        right_splitter.addWidget(self.param_panel)
        
        # 可视化区域
        self.viz_panel = VisualizationPanel()
        right_splitter.addWidget(self.viz_panel)
        
        right_splitter.setSizes([350, 750])
        content_splitter.addWidget(right_splitter)
        content_splitter.setSizes([250, 1100])
        
        main_layout.addWidget(content_splitter)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("系统就绪 | 当前工程: 猕猴V1区电生理实验")
        self.setStatusBar(self.status_bar)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QStatusBar {
                background-color: #0078d4;
                color: white;
                padding: 5px;
            }
        """)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
