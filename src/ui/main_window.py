"""
Main Window - 主窗口

NeuroPrime软件的主窗口，包含RibbonBar、导航栏、参数配置面板和可视化区域
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QProgressBar, QLabel,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QKeySequence

# 导入样式
from .styles import Styles

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from project.project_manager import ProjectManager, TrialInfo
from project.data_enumerator import DataEnumerator
from datetime import datetime

# 导入调试日志
from utils.debug_logger import get_logger, log_vars
logger = get_logger()


class MainWindow(QMainWindow):
    """
    主窗口类
    
    布局结构:
    - 顶部: RibbonBar (工具栏)
    - 左侧: 导航栏 (工程/试验/数据树)
    - 右侧: 参数配置 + 可视化区域
    - 底部: 状态栏
    """
    
    def __init__(self):
        super().__init__()
        
        # 初始化成员变量
        self.project_manager = ProjectManager()
        self.data_enumerator: Optional[DataEnumerator] = None
        
        # UI组件引用
        self.ribbon_bar = None
        self.navigator = None
        self.parameter_panel = None
        self.visualization_area = None
        self.status_bar = None
        self.progress_bar = None
        
        # 初始化UI
        self._init_ui()
        self._init_status_bar()
        
        # 应用样式
        self.setStyleSheet(Styles.MAIN_WINDOW)
        
        # 设置窗口属性
        self.setWindowTitle("NeuroPrime - Macaque Electrophysiology Data Analysis Software")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)
    
    def _init_ui(self):
        """初始化UI布局"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. RibbonBar (顶部)
        from .ribbon_bar import RibbonBar
        self.ribbon_bar = RibbonBar(self)
        self.ribbon_bar.action_triggered.connect(self._on_ribbon_action)
        self.ribbon_bar.tab_changed.connect(self._on_ribbon_tab_changed)
        self.ribbon_bar.algorithm_selected.connect(self._on_algorithm_selected)
        main_layout.addWidget(self.ribbon_bar)
        
        # 2. 主内容区域 (三列水平分割)
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧: 导航栏 (数据浏览器)
        from .navigator import Navigator
        self.navigator = Navigator(self)
        self.navigator.item_selected.connect(self._on_navigator_selection)
        self.navigator.item_double_clicked.connect(self._on_navigator_double_click)
        content_splitter.addWidget(self.navigator)
        
        # 中间: 参数配置面板
        from .parameter_panel import ParameterPanel
        self.parameter_panel = ParameterPanel(self)
        self.parameter_panel.run_analysis_requested.connect(self._on_run_analysis)
        self.parameter_panel.time_alignment_requested.connect(self._on_time_alignment)
        content_splitter.addWidget(self.parameter_panel)
        
        # 右侧: 可视化区域
        from .visualization_area import VisualizationArea
        self.visualization_area = VisualizationArea(self)
        content_splitter.addWidget(self.visualization_area)
        
        # 设置三列分割比例 (左:中:右 = 1:1:2)
        content_splitter.setSizes([350, 350, 700])
        
        main_layout.addWidget(content_splitter, 1)
    
    def _init_menu(self):
        """初始化菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("File(&F)")
        
        new_project_action = QAction("New Project(&N)", self)
        new_project_action.setShortcut(QKeySequence.StandardKey.New)
        new_project_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("Open Project(&O)", self)
        open_project_action.setShortcut(QKeySequence.StandardKey.Open)
        open_project_action.triggered.connect(self._on_open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        import_data_action = QAction("Import Data(&I)", self)
        import_data_action.triggered.connect(self._on_import_data)
        file_menu.addAction(import_data_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("Tools(&T)")
        
        time_alignment_action = QAction("Time Alignment(&A)", self)
        time_alignment_action.triggered.connect(self._on_time_alignment)
        tools_menu.addAction(time_alignment_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("Help(&H)")
        
        about_action = QAction("About(&A)", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _init_status_bar(self):
        """初始化状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label, 1)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addWidget(self.progress_bar)
        
        # 信息标签
        self.info_label = QLabel("")
        self.status_bar.addWidget(self.info_label)
    
    # ========== 事件处理 ==========
    
    def _on_ribbon_action(self, action_name: str, params: Dict[str, Any]):
        """处理RibbonBar动作"""
        print(f"Ribbon action triggered: {action_name}")  # 调试输出
        
        if action_name == "new_project":
            self._on_new_project()
        elif action_name == "open_project":
            self._on_open_project()
        elif action_name == "import_data" or action_name == "import_trial":
            self._on_import_data()
        elif action_name == "batch_import":
            self._on_batch_import()
        elif action_name == "save_project":
            self._on_save_project()
        elif action_name == "time_alignment":
            self._on_time_alignment()
        elif action_name == "run_analysis":
            self._on_run_analysis(params)
        elif action_name == "export_results":
            self._on_export_results()
        elif action_name == "refresh":
            self.navigator.refresh_project(self.project_manager)
            self.status_label.setText("数据已刷新")
        elif action_name == "delete":
            # TODO: 实现删除功能
            QMessageBox.information(self, "提示", "删除功能开发中")
        elif action_name == "import_custom_algorithm":
            self._on_import_custom_algorithm()
        elif action_name == "manage_custom_algorithms":
            self._on_manage_custom_algorithms()
        elif action_name == "open_mne_terminal":
            self._open_mne_terminal()
        else:
            print(f"Unknown action: {action_name}")
    
    def _on_ribbon_tab_changed(self, tab_name: str):
        """处理Ribbon标签页切换"""
        print(f"Ribbon tab changed to: {tab_name}")
        
        # 更新参数面板显示模式
        self.parameter_panel.set_panel_mode(tab_name)
        
        # Update status bar hint based on tab type
        if tab_name == "Data Loading":
            self.status_label.setText("Data Loading Mode - Please import or manage data")
        elif tab_name == "Custom Algorithms":
            self.status_label.setText("Custom Algorithms Mode - Please import or manage custom algorithms")
        else:
            self.status_label.setText(f"{tab_name} Mode - Please configure parameters and select data")
    
    def _on_algorithm_selected(self, algorithm_name: str):
        """处理算法选择 - 更新参数配置"""
        print(f"Algorithm selected: {algorithm_name}")
        
        # 更新参数面板的算法参数配置
        self.parameter_panel.set_algorithm(algorithm_name)
        
        # 更新状态栏
        self.status_label.setText(f"已选择算法: {algorithm_name}")
    
    def _on_navigator_selection(self, item_type: str, item_data: Dict[str, Any]):
        """处理导航栏选择"""
        if item_type == "trial":
            trial_name = item_data.get("name")
            self._load_trial_data(trial_name)
        elif item_type == "data_item":
            data_id = item_data.get("id")
            self._select_data_item(data_id)
        elif item_type == "import_trial":
            # 从导航栏触发导入试验
            self._on_import_data()
        elif item_type == "data_category":
            # 选择数据类别
            trial_name = item_data.get("trial")
            category = item_data.get("category")
            self._load_data_category(trial_name, category)
    
    def _on_navigator_double_click(self, item_type: str, item_data: Dict[str, Any]):
        """处理导航栏双击 - 添加到数据选择列表"""
        try:
            # 确保item_data是字典类型
            if not isinstance(item_data, dict):
                print(f"警告: _on_navigator_double_click接收到的item_data不是字典类型: {type(item_data)}")
                return
            
            if item_type == "data_item":
                # 双击数据项，添加到选择列表
                self._add_data_item_to_selection(item_data)
            elif item_type == "trial":
                # 双击试验项，添加该试验的所有数据
                trial_name = item_data.get("name")
                self._add_trial_data_to_selection(trial_name)
            elif item_type == "data_category":
                # 双击数据类别，添加该类别下的所有数据
                trial_name = item_data.get("trial")
                category = item_data.get("category")
                self._add_category_data_to_selection(trial_name, category)
        except Exception as e:
            print(f"处理双击事件错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_data_item_to_selection(self, item_data: Dict[str, Any]):
        """添加单个数据项到选择列表"""
        # 确保item_data是字典类型
        if not isinstance(item_data, dict):
            print(f"警告: _add_data_item_to_selection接收到的不是字典类型: {type(item_data)}")
            return
        
        # 构建数据项信息
        data_item = {
            'id': item_data.get('id', ''),
            'display_name': item_data.get('display_name', item_data.get('id', 'Unknown')),
            'trial_name': item_data.get('trial_name', 'Unknown'),
            'data_type': item_data.get('data_type', ''),
            'description': item_data.get('description', ''),
            'time_range': item_data.get('time_range', None)
        }
        
        # 添加到参数面板
        self.parameter_panel.add_data_item(data_item)
        
        # 更新状态栏
        count = self.parameter_panel.get_selected_data_count()
        self.status_label.setText(f"已添加数据项: {data_item['display_name']} (共 {count} 项)")
    
    def _add_trial_data_to_selection(self, trial_name: str):
        """添加整个试验的数据到选择列表"""
        if self.data_enumerator is None:
            return
        
        try:
            # 获取试验的所有数据项
            data_items = self.data_enumerator.get_trial_data_items(trial_name)
            
            # 转换为字典列表
            data_dicts = []
            for item in data_items:
                if hasattr(item, 'name'):
                    # DataItem对象
                    data_dicts.append({
                        'id': item.name,
                        'display_name': f"{item.name} ({item.data_type})",
                        'trial_name': trial_name,
                        'data_type': item.data_type,
                        'description': item.description,
                        'time_range': item.time_range
                    })
                else:
                    # 已经是字典
                    item['trial_name'] = trial_name
                    data_dicts.append(item)
            
            # 添加到参数面板
            self.parameter_panel.add_trial_data(trial_name, data_dicts)
            
            # 更新状态栏
            count = self.parameter_panel.get_selected_data_count()
            self.status_label.setText(f"已添加试验 '{trial_name}' 的 {len(data_dicts)} 个数据项 (共 {count} 项)")
        
        except Exception as e:
            print(f"添加试验数据错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_category_data_to_selection(self, trial_name: str, category: str):
        """添加数据类别下的所有数据到选择列表"""
        if self.data_enumerator is None:
            return
        
        try:
            # 获取该试验的指定类别数据项
            data_items = self.data_enumerator.get_trial_data_items(trial_name)
            
            # 根据类别筛选数据项
            category_map = {
                'signals': 'lfp',
                'spikes': 'spike',
                'behavior': 'behavior'
            }
            target_type = category_map.get(category, category)
            
            # 转换为字典列表
            data_dicts = []
            for item in data_items:
                if hasattr(item, 'data_type') and item.data_type == target_type:
                    data_dicts.append({
                        'id': item.name,
                        'display_name': f"{item.name} ({item.data_type})",
                        'trial_name': trial_name,
                        'data_type': item.data_type,
                        'description': item.description,
                        'time_range': item.time_range
                    })
            
            # 添加到参数面板
            self.parameter_panel.add_trial_data(trial_name, data_dicts)
            
            # 更新状态栏
            count = self.parameter_panel.get_selected_data_count()
            category_names = {
                'signals': '信号数据',
                'spikes': 'Spike数据',
                'behavior': '行为数据'
            }
            category_name = category_names.get(category, category)
            self.status_label.setText(f"已添加 {trial_name} - {category_name} 的 {len(data_dicts)} 个数据项 (共 {count} 项)")
        
        except Exception as e:
            print(f"添加类别数据错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_new_project(self):
        """新建工程"""
        from .dialogs.new_project_dialog import NewProjectDialog
        dialog = NewProjectDialog(self)
        if dialog.exec():
            project_info = dialog.get_project_info()
            self._create_new_project(project_info)

    def _open_mne_terminal(self):
        """Open Custom Algorithm Editor"""
        from .mne_terminal import CustomAlgorithmEditor
        
        try:
            self.custom_algorithm_editor = CustomAlgorithmEditor(self)
            self.custom_algorithm_editor.setWindowTitle("Algorithm Editor")
            self.custom_algorithm_editor.script_executed.connect(self._on_mne_script_executed)
            self.custom_algorithm_editor.script_saved.connect(self._on_algorithm_script_saved)
            self.custom_algorithm_editor.show()
        except Exception as e:
            print(f"Error opening Algorithm Editor: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_mne_script_executed(self, result):
        """Callback when algorithm script execution completes"""
        print(f"Algorithm script executed, result: {result.keys() if result else 'None'}")
        # Handle script execution results here
        # e.g., display results, save results, etc.
    
    def _on_algorithm_script_saved(self, file_path):
        """Callback when algorithm script is saved"""
        print(f"Algorithm script saved: {file_path}")
        # Refresh custom algorithm list
        try:
            # Recreate scheduler instance to ensure complete refresh
            from src.algorithms.scheduler import AlgorithmScheduler
            self.parameter_panel.scheduler = AlgorithmScheduler()
            self.parameter_panel.scheduler.register_builtin_algorithms()
            
            # Update algorithm selection dropdown based on current tab
            if hasattr(self.parameter_panel, 'current_tab_name'):
                current_tab = self.parameter_panel.current_tab_name
                if current_tab == "Custom Algorithms":
                    # In Custom Algorithms tab, only update custom algorithm list
                    if hasattr(self.parameter_panel, '_populate_custom_algorithms'):
                        self.parameter_panel._populate_custom_algorithms()
                        print("Custom algorithm dropdown updated")
                else:
                    # In other tabs, update all algorithm lists
                    if hasattr(self.parameter_panel, '_populate_algorithms'):
                        self.parameter_panel._populate_algorithms()
                        print("All algorithms dropdown updated")
            else:
                # If current tab cannot be determined, update both lists
                if hasattr(self.parameter_panel, '_populate_custom_algorithms'):
                    self.parameter_panel._populate_custom_algorithms()
                    print("Custom algorithm dropdown updated")
                if hasattr(self.parameter_panel, '_populate_algorithms'):
                    self.parameter_panel._populate_algorithms()
                    print("All algorithms dropdown updated")
                
            print("Custom algorithm list updated")
        except Exception as e:
            print(f"Error updating custom algorithm list: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_manage_custom_algorithms(self):
        """Manage Custom Algorithms"""
        from .dialogs.manage_algorithms_dialog import ManageAlgorithmsDialog
        
        try:
            dialog = ManageAlgorithmsDialog(self)
            dialog.algorithms_updated.connect(self._on_algorithm_script_saved)
            dialog.exec()
        except Exception as e:
            print(f"Error opening algorithm management dialog: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_import_custom_algorithm(self):
        """Import Custom Algorithm"""
        # Open file dialog to select algorithm script
        default_dir = Path(__file__).parent.parent.parent / "custom_algorithms"
        if not default_dir.exists():
            default_dir = Path(__file__).parent.parent.parent
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Algorithm Script", str(default_dir), "Python Files (*.py)"
        )
        
        if file_path:
            try:
                # Import algorithm
                from src.algorithms.scheduler import AlgorithmScheduler
                scheduler = AlgorithmScheduler()
                
                # Load algorithm
                scheduler._load_custom_algorithms()
                
                # Update algorithm selection dropdown in UI
                if hasattr(self.parameter_panel, '_populate_custom_algorithms'):
                    self.parameter_panel._populate_custom_algorithms()
                
                if hasattr(self.parameter_panel, '_populate_algorithms'):
                    self.parameter_panel._populate_algorithms()
                
                QMessageBox.information(self, "Success", f"Algorithm imported: {Path(file_path).name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import algorithm: {str(e)}")
                print(f"Error importing algorithm: {e}")
                import traceback
                traceback.print_exc()
    
    def _on_open_project(self):
        """Open Project"""
        # Get software root directory as default path
        default_path = Path(__file__).parent.parent.parent
        
        project_path = QFileDialog.getExistingDirectory(
            self, "Select Project Folder", str(default_path)
        )
        if project_path:
            self._open_project(project_path)
    
    def _on_import_data(self):
        """Import Data"""
        # Check if a project is open
        if not self.project_manager or not self.project_manager.is_project_opened():
            QMessageBox.warning(self, "Warning", "Please open or create a project first")
            return
        
        from .dialogs.import_dialog import ImportDialog
        dialog = ImportDialog(self, self.project_manager)
        dialog.import_completed.connect(self._on_import_completed)
        dialog.exec()
    
    def _on_batch_import(self):
        """批量导入数据"""
        # 检查是否有工程已打开
        if not self.project_manager or not self.project_manager.is_project_opened():
            QMessageBox.warning(self, "警告", "请先打开或创建一个工程")
            return
        
        from .dialogs.batch_import_dialog import BatchImportDialog
        dialog = BatchImportDialog(self, self.project_manager)
        dialog.import_completed.connect(self._on_batch_import_completed)
        dialog.exec()
    
    def _on_save_project(self):
        """保存工程"""
        if self.project_manager.is_project_opened():
            self.project_manager.save_project()
            self.status_label.setText("工程已保存")
        else:
            QMessageBox.warning(self, "警告", "没有打开的工程")
    
    def _on_time_alignment(self):
        """时间对齐"""
        if not self.project_manager.is_project_opened():
            QMessageBox.warning(self, "警告", "请先打开或创建一个工程")
            return
        
        # 获取已选择的数据项
        selected_data = self.parameter_panel._get_selected_data_items()
        if len(selected_data) < 2:
            QMessageBox.information(self, "提示", "请至少选择2个数据项进行时间对齐\n\n提示：从左侧导航栏双击数据项添加到选择列表")
            return
        
        from .dialogs.time_alignment_dialog import TimeAlignmentDialog
        dialog = TimeAlignmentDialog(self, data_items=selected_data)
        if dialog.exec():
            alignment_config = dialog.get_alignment_config()
            self.parameter_panel.set_time_alignment(alignment_config)
            self.status_label.setText("时间对齐配置已应用")
    
    def _on_run_analysis(self, params: Dict[str, Any]):
        """运行分析"""
        logger.info("=" * 60)
        logger.info("_on_run_analysis 被调用")
        
        # 记录params的类型和内容
        logger.log_vars(params_type=type(params))
        
        algorithm_name = params.get("algorithm")
        data_items = params.get("data_items", [])
        parameters = params.get("parameters", {})
        time_alignment = params.get("time_alignment", {})
        
        logger.log_vars(
            algorithm_name=algorithm_name,
            data_items_type=type(data_items),
            data_items_len=len(data_items) if hasattr(data_items, '__len__') else 'N/A',
            parameters_type=type(parameters),
            time_alignment_type=type(time_alignment)
        )
        
        # 调试：检查data_items类型
        if data_items:
            logger.info(f"data_items[0] type: {type(data_items[0])}")
            if isinstance(data_items[0], dict):
                logger.info(f"data_items[0] keys: {list(data_items[0].keys())}")
            else:
                logger.error(f"data_items[0] 不是字典! 值: {data_items[0]}")
        
        if not algorithm_name:
            QMessageBox.warning(self, "警告", "请选择分析算法")
            return
        
        if not data_items:
            QMessageBox.warning(self, "警告", "请选择要分析的数据")
            return
        
        # 对于ViewRawLFPData算法，严格检查是否只选择了LFP数据
        if algorithm_name == "ViewRawLFPData":
            for item in data_items:
                if isinstance(item, dict):
                    data_type = item.get('data_type', '')
                    if data_type != 'lfp':
                        self.progress_bar.setVisible(False)
                        self.status_label.setText("分析失败: ViewRawLFPData仅支持LFP数据")
                        QMessageBox.warning(
                            self,
                            "数据类型错误",
                            "ViewRawLFPData 算法仅支持LFP信号数据，不支持其他类型的数据。\n\n"
                            f"您选择的数据类型为: {data_type if data_type else '未知'}\n\n"
                            "请在左侧数据浏览器中选择'LFP数据'类别的数据项。"
                        )
                        return
        
        # 检查算法的数据需求（除自定义算法外）
        if not algorithm_name.startswith("Custom") and not algorithm_name.startswith("custom"):
            try:
                from src.algorithms import AlgorithmScheduler
                scheduler = AlgorithmScheduler()
                scheduler.register_builtin_algorithms()
                
                algorithm = scheduler.get_algorithm(algorithm_name)
                if algorithm:
                    data_req = algorithm.get_data_requirements()
                    required_types = data_req.get('required_types', [])
                    
                    if required_types:
                        # 分析选择的数据类型
                        has_lfp = False
                        has_spike = False
                        has_behavior = False
                        
                        for item in data_items:
                            if isinstance(item, dict):
                                data_type = item.get('data_type', '')
                                item_id = item.get('id', '')
                                
                                if data_type == 'lfp' or 'signal' in item_id.lower() or 'lfp' in item_id.lower():
                                    has_lfp = True
                                elif data_type == 'spike' or 'spike' in item_id.lower():
                                    has_spike = True
                                elif data_type == 'behavior' or 'events' in item_id.lower() or 'trials' in item_id.lower():
                                    has_behavior = True
                        
                        # 验证数据类型是否满足需求
                        missing_types = []
                        
                        if 'lfp' in required_types and not has_lfp:
                            # 如果同时需要spike，且用户提供了spike，则不报错
                            if not ('spike' in required_types and has_spike):
                                missing_types.append("LFP信号数据")
                        
                        if 'spike' in required_types and not has_spike:
                            # 如果同时需要lfp，且用户提供了lfp，则不报错
                            if not ('lfp' in required_types and has_lfp):
                                missing_types.append("Spike数据")
                        
                        if 'behavior' in required_types and not has_behavior:
                            missing_types.append("行为数据（试次信息）")
                        
                        if missing_types:
                            self.progress_bar.setVisible(False)
                            self.status_label.setText(f"分析失败: 数据类型不匹配")
                            
                            # 构建错误信息
                            error_msg = f"【{algorithm_name}】需要以下数据类型：\n\n"
                            error_msg += f"{data_req.get('description', '')}\n\n"
                            error_msg += "您选择的数据缺少：\n"
                            for mt in missing_types:
                                error_msg += f"  • {mt}\n"
                            error_msg += "\n请在左侧数据浏览器中选择正确的数据类型。"
                            
                            QMessageBox.warning(
                                self,
                                "数据类型错误",
                                error_msg
                            )
                            return
                            
            except Exception as e:
                print(f"数据需求检查失败: {e}")
                # 继续执行，不阻止分析
        
        # 将时间对齐配置合并到参数中
        if time_alignment:
            parameters['time_alignment'] = time_alignment
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.status_label.setText(f"正在运行 {algorithm_name}...")
        
        # TODO: 在后台线程中运行算法
        # 这里先模拟运行
        self._run_analysis_async(algorithm_name, data_items, parameters)
    
    def _on_export_results(self):
        """导出结果"""
        # TODO: 实现结果导出
        QMessageBox.information(self, "提示", "导出功能开发中")
    
    def _on_import_completed(self, trial_name: str):
        """导入完成处理"""
        # 刷新导航栏
        self.navigator.refresh_project(self.project_manager)
        self.status_label.setText(f"已导入试验: {trial_name}")

        # 启用分析标签页
        self.ribbon_bar.set_data_loaded(True)

        # 有数据导入，启用管理按钮
        self.ribbon_bar.set_data_imported(True)
    
    def _on_batch_import_completed(self, successful_trials: list):
        """批量导入完成处理"""
        try:
            # 将成功导入的试验添加到工程
            for trial_info in successful_trials:
                trial = TrialInfo(
                    name=trial_info['name'],
                    experiment_name="Batch Import",
                    creation_time=datetime.now().isoformat(),
                    hdf5_file=trial_info['hdf5_file'],
                    source_files={
                        'ns3': trial_info['ns3_file'],
                        'nev': trial_info['nev_file'],
                        'mbm': trial_info.get('mbm_file', '')
                    }
                )
                self.project_manager.add_trial(trial)

            # 保存工程
            self.project_manager.save_project()

            # 刷新导航栏
            self.navigator.refresh_project(self.project_manager)
            self.status_label.setText(f"已批量导入 {len(successful_trials)} 个试验")

            # 启用分析标签页
            self.ribbon_bar.set_data_loaded(True)

            # 有数据导入，启用管理按钮
            self.ribbon_bar.set_data_imported(True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理导入结果失败: {str(e)}")
    
    def _on_about(self):
        """关于对话框"""
        QMessageBox.about(
            self,
            "关于 NeuroPrime",
            "<h2>NeuroPrime</h2>"
            "<p>猕猴脑电生理数据分析软件</p>"
            "<p>版本: 1.0.0</p>"
            "<p>用于分析Blackrock NeuroPort系统的神经电生理数据</p>"
        )
    
    # ========== 业务逻辑 ==========
    
    def _create_new_project(self, project_info: Dict[str, Any]):
        """创建新工程"""
        try:
            # 构建完整的工程路径（父目录 + 工程名称）
            parent_path = Path(project_info["path"])
            project_name = project_info["name"]
            project_path = parent_path / project_name
            description = project_info.get("description", "")
            
            print(f"Creating project: {project_path}")
            print(f"Parent path exists: {parent_path.exists()}")
            print(f"Project path exists: {project_path.exists()}")
            
            success = self.project_manager.create_project(
                project_path, project_name, description
            )
            
            if success:
                self.data_enumerator = DataEnumerator(self.project_manager)
                self.navigator.set_project_manager(self.project_manager)
                self.status_label.setText(f"工程已创建: {project_name}")
                self.setWindowTitle(f"NeuroPrime - {project_name}")

                # 新工程没有数据，禁用分析标签页
                self.ribbon_bar.set_data_loaded(False)

                # 工程已打开，启用导入按钮，禁用管理按钮
                self.ribbon_bar.set_project_opened(True)
                self.ribbon_bar.set_data_imported(False)
            else:
                if project_path.exists():
                    QMessageBox.critical(self, "错误", f"创建工程失败\n路径已存在: {project_path}\n\n请删除该文件夹或选择其他工程名称。")
                else:
                    QMessageBox.critical(self, "错误", f"创建工程失败\n路径: {project_path}\n\n请检查是否有写入权限。")
        
        except Exception as e:
            import traceback
            error_msg = f"创建工程失败: {str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
    
    def _open_project(self, project_path: str):
        """打开工程"""
        try:
            success = self.project_manager.open_project(Path(project_path))
            
            if success:
                self.data_enumerator = DataEnumerator(self.project_manager)
                self.navigator.set_project_manager(self.project_manager)
                project_name = self.project_manager.config.name
                self.status_label.setText(f"工程已打开: {project_name}")
                self.setWindowTitle(f"NeuroPrime - {project_name}")

                # 检查工程中是否有试验数据
                has_trials = len(self.project_manager.config.trials) > 0

                # 启用分析标签页（如果有数据）
                self.ribbon_bar.set_data_loaded(has_trials)

                # 工程已打开，启用导入按钮
                self.ribbon_bar.set_project_opened(True)

                # 如果有试验数据，启用管理按钮
                self.ribbon_bar.set_data_imported(has_trials)
            else:
                QMessageBox.critical(self, "错误", "打开工程失败")
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开工程失败: {str(e)}")
    
    def _load_trial_data(self, trial_name: str):
        """加载试验数据"""
        try:
            if self.data_enumerator is None:
                return
            
            # 获取试验数据项
            data_items = self.data_enumerator.get_trial_data_items(trial_name)
            
            # 更新参数面板
            self.parameter_panel.set_available_data(data_items)
            
            self.status_label.setText(f"已加载试验: {trial_name}")
        except Exception as e:
            print(f"加载试验数据错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _select_data_item(self, data_id: str):
        """选择数据项"""
        # TODO: 更新参数面板中的数据选择
        pass
    
    def _load_data_category(self, trial_name: str, category: str):
        """加载数据类别"""
        try:
            if self.data_enumerator is None:
                return
            
            # 获取该试验的指定类别数据项
            data_items = self.data_enumerator.get_trial_data_items(trial_name)
            
            # 根据类别筛选数据项（处理DataItem对象）
            category_map = {
                'signals': 'lfp',
                'spikes': 'spike', 
                'behavior': 'behavior'
            }
            target_type = category_map.get(category, category)
            filtered_items = [item for item in data_items if item.data_type == target_type]
            
            # 更新参数面板
            self.parameter_panel.set_available_data(filtered_items)
            
            category_names = {
                'signals': '信号数据',
                'spikes': 'Spike数据',
                'behavior': '行为数据'
            }
            category_name = category_names.get(category, category)
            self.status_label.setText(f"已选择: {trial_name} - {category_name}")
        except Exception as e:
            print(f"加载数据类别错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _quick_preview_data(self, data_id: str):
        """快速预览数据"""
        # TODO: 实现快速预览
        pass
    
    def _on_import_custom_algorithm(self):
        """Import Custom Algorithm
        
        Import workflow:
        1. Select algorithm file
        2. Validate algorithm
        3. Check for duplicate algorithm name
        4. Integrate algorithm
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Custom Algorithm File", "",
            "Python Files (*.py);;All Files (*)"
        )
        if not file_path:
            return
        
        try:
            # Step 1: Read algorithm file
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Step 2: Validate algorithm
            validation_result = self._validate_algorithm_code(code)
            if not validation_result['success']:
                # Validation failed, show error dialog
                QMessageBox.critical(
                    self, 
                    "Validation Failed", 
                    f"Algorithm validation failed, cannot import.\n\nError:\n{validation_result['error']}"
                )
                return
            
            # Step 3: Extract algorithm name
            algorithm_name = validation_result['algorithm_name']
            
            # Step 4: Check for duplicate algorithm name
            existing_algorithms = self._get_existing_algorithm_names()
            if algorithm_name in existing_algorithms:
                # Algorithm name exists, ask user if they want to overwrite
                reply = QMessageBox.question(
                    self,
                    "Duplicate Algorithm Name",
                    f"Algorithm '{algorithm_name}' already exists.\n\nOverwrite with new algorithm?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    # 用户取消，不导入
                    return
                # 用户确认覆盖，继续导入流程
            
            # Step 5: 集成算法（Integrate）
            integrate_result = self._integrate_algorithm_code(code, algorithm_name)
            if integrate_result['success']:
                QMessageBox.information(
                    self,
                    "导入成功",
                    f"算法 '{algorithm_name}' 导入成功！\n\n保存路径: {integrate_result['file_path']}"
                )
                # 刷新算法列表
                self._refresh_algorithm_list()
            else:
                QMessageBox.critical(
                    self,
                    "导入失败",
                    f"算法集成失败。\n\n错误信息:\n{integrate_result['error']}"
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "导入错误",
                f"导入过程中发生错误:\n{str(e)}"
            )
    
    def _validate_algorithm_code(self, code: str) -> dict:
        """验证算法代码
        
        Returns:
            dict: {
                'success': bool,
                'algorithm_name': str or None,
                'error': str or None
            }
        """
        result = {
            'success': False,
            'algorithm_name': None,
            'error': None
        }
        
        try:
            # 检查代码是否为空
            if not code or len(code.strip()) < 100:
                result['error'] = "代码为空或内容过少"
                return result
            
            # 语法检查
            try:
                compile(code, '<string>', 'exec')
            except SyntaxError as e:
                result['error'] = f"语法错误 (第{e.lineno}行): {e.msg}"
                return result
            
            # 创建临时模块执行代码
            import importlib.util
            import inspect
            
            spec = importlib.util.spec_from_loader("temp_algorithm", loader=None)
            module = importlib.util.module_from_spec(spec)
            exec(code, module.__dict__)
            
            # 检查 run_algorithm 函数
            if not hasattr(module, 'run_algorithm'):
                result['error'] = "未找到 run_algorithm 函数"
                return result
            
            # 检查 run_algorithm 参数
            sig = inspect.signature(module.run_algorithm)
            params = list(sig.parameters.keys())
            if len(params) != 2:
                result['error'] = f"run_algorithm 函数应有2个参数 (input_data, parameters)，实际有 {len(params)} 个"
                return result
            
            # 检查 ALGORITHM_INFO
            if not hasattr(module, 'ALGORITHM_INFO'):
                result['error'] = "未找到 ALGORITHM_INFO"
                return result
            
            # 尝试执行算法获取算法名称
            try:
                import numpy as np
                
                class MockInputData:
                    def __init__(self):
                        self.spike_times = np.random.rand(10) * 10
                        self.trial_info = [
                            {'start_time': 0, 'end_time': 5},
                            {'start_time': 5, 'end_time': 10}
                        ]
                        self.sampling_rate = 2000.0
                        self.lfp_data = np.random.randn(8, 1000)
                
                input_data = MockInputData()
                parameters = {}
                algorithm_result = module.run_algorithm(input_data, parameters)
                
                # 检查返回结果格式
                if not hasattr(algorithm_result, 'data') or not hasattr(algorithm_result, 'success'):
                    result['error'] = "run_algorithm 应返回 AlgorithmOutput 对象"
                    return result
                
            except Exception as e:
                result['error'] = f"执行算法测试失败: {str(e)}"
                return result
            
            # 提取算法名称
            algorithm_name = None
            
            # 从类名提取
            import re
            class_match = re.search(r'class\s+(\w+)\s*\(', code)
            if class_match:
                algorithm_name = class_match.group(1)
            
            # 从 ALGORITHM_INFO 提取
            if hasattr(module, 'ALGORITHM_INFO') and isinstance(module.ALGORITHM_INFO, dict):
                if 'name' in module.ALGORITHM_INFO:
                    algorithm_name = module.ALGORITHM_INFO['name']
            
            if not algorithm_name:
                result['error'] = "无法提取算法名称"
                return result
            
            result['success'] = True
            result['algorithm_name'] = algorithm_name
            return result
            
        except Exception as e:
            result['error'] = f"验证过程发生错误: {str(e)}"
            return result
    
    def _get_existing_algorithm_names(self) -> set:
        """获取已存在的算法名称集合"""
        existing_names = set()
        
        # 从 custom_algorithms 目录获取
        custom_algorithms_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'custom_algorithms')
        if os.path.exists(custom_algorithms_dir):
            for filename in os.listdir(custom_algorithms_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    # 提取算法名称（去掉.py后缀，转换为类名格式）
                    algorithm_name = filename[:-3].replace('_', ' ').title().replace(' ', '')
                    existing_names.add(algorithm_name)
        
        # 从内置算法列表获取
        if hasattr(self, 'algorithm_manager') and self.algorithm_manager:
            for algo_name in self.algorithm_manager.algorithms.keys():
                existing_names.add(algo_name)
        
        return existing_names
    
    def _integrate_algorithm_code(self, code: str, algorithm_name: str) -> dict:
        """集成算法代码
        
        Returns:
            dict: {
                'success': bool,
                'file_path': str or None,
                'error': str or None
            }
        """
        result = {
            'success': False,
            'file_path': None,
            'error': None
        }
        
        try:
            import re
            
            # 更新代码中的算法名称和类别
            updated_code = code
            
            # 更新 ALGORITHM_INFO 中的 name
            updated_code = re.sub(
                r"'name':\s*algorithm\.name",
                f"'name': '{algorithm_name}'",
                updated_code
            )
            
            # Update category to "Custom Algorithm"
            updated_code = re.sub(
                r"'category':\s*algorithm\.category",
                "'category': 'Custom Algorithm'",
                updated_code
            )
            
            # Update self.category in __init__
            pattern = r'self\.category\s*=\s*[\'"]([^\'"]*)[\'"]'
            updated_code = re.sub(
                pattern,
                "self.category = 'Custom Algorithm'",
                updated_code
            )
            
            # 更新 __init__ 中的 self.name
            name_pattern = r'self\.name\s*=\s*[\'"]([^\'"]*)[\'"]'
            if re.search(name_pattern, updated_code):
                updated_code = re.sub(
                    name_pattern,
                    f"self.name = '{algorithm_name}'",
                    updated_code
                )
            
            # 保存到 custom_algorithms 目录
            custom_algorithms_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'custom_algorithms')
            if not os.path.exists(custom_algorithms_dir):
                os.makedirs(custom_algorithms_dir)
            
            # 生成文件名
            filename = f"{algorithm_name.lower().replace(' ', '_')}.py"
            file_path = os.path.join(custom_algorithms_dir, filename)
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_code)
            
            result['success'] = True
            result['file_path'] = file_path
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _refresh_algorithm_list(self):
        """Refresh algorithm list"""
        try:
            # Reload custom algorithms
            if hasattr(self, 'algorithm_manager') and self.algorithm_manager:
                self.algorithm_manager.load_custom_algorithms()
            
            # 更新算法选择下拉框
            if hasattr(self, 'algorithm_combo'):
                self._update_algorithm_combo()
            
            # 发送信号通知其他组件
            if hasattr(self, 'algorithm_imported'):
                self.algorithm_imported.emit()
                
        except Exception as e:
            print(f"刷新算法列表失败: {e}")
    

    
    def _collect_data_items(self, data_items, data_map):
        """收集spike和behavior数据项"""
        spike_data_items = []
        behavior_data_items = []
        
        for idx, item in enumerate(data_items):
            if isinstance(item, dict):
                data_type = item.get('data_type', '')
                trial_name = item.get('trial_name', '')
                data_id = item.get('id', '')
                unique_id = f"{trial_name}/{data_id}"
                
                if data_type == 'spike' and unique_id in data_map:
                    spike_data_items.append({
                        'item': item,
                        'data': data_map[unique_id],
                        'trial_name': trial_name
                    })
                elif data_type == 'behavior':
                    behavior_data_items.append({
                        'item': item,
                        'trial_name': trial_name
                    })
        
        return spike_data_items, behavior_data_items
    
    def _validate_spike_data(self, spike_data_items, algorithm_name):
        """验证spike数据"""
        if not spike_data_items:
            self.progress_bar.setVisible(False)
            self.status_label.setText("分析失败: 缺少Spike数据")
            QMessageBox.warning(
                self, 
                "数据选择错误", 
                f"{algorithm_name} 需要选择Spike数据。\n\n" +
                "请在左侧数据浏览器中选择至少一个'Spike数据'。"
            )
            return False
        return True
    
    def _merge_spike_data(self, spike_data_items):
        """合并spike数据并分配时间偏移"""
        all_spike_times = []
        trial_time_offsets = {}  # trial_name -> time_offset
        current_offset = 0.0
        
        for spike_item in spike_data_items:
            trial_name = spike_item['trial_name']
            spike_data = spike_item['data']
            
            # 为该试验分配时间偏移量
            trial_time_offsets[trial_name] = current_offset
            
            if isinstance(spike_data, np.ndarray):
                spike_list = spike_data.tolist()
            elif isinstance(spike_data, list):
                spike_list = spike_data
            else:
                spike_list = []
            
            # 将Spike时间加上偏移量
            offset_spikes = [t + current_offset for t in spike_list]
            all_spike_times.extend(offset_spikes)
            
            # 更新偏移量（假设每个试验约100秒）
            if spike_list:
                current_offset += max(spike_list) + 10.0  # 加10秒间隔
            else:
                current_offset += 100.0
        
        if not all_spike_times:
            self.progress_bar.setVisible(False)
            self.status_label.setText("分析失败: Spike数据为空")
            QMessageBox.warning(self, "数据错误", "选择的Spike数据为空")
            return None, None
        
        return np.array(all_spike_times), trial_time_offsets
    
    def _load_trial_info(self, behavior_data_items, spike_data_items, trial_time_offsets):
        """加载trial信息"""
        all_trial_info = []
        
        # 如果没有选择behavior数据，尝试从Spike数据对应的试验加载
        if not behavior_data_items:
            for spike_item in spike_data_items:
                trial_name = spike_item['trial_name']
                if trial_name:
                    behavior_data_items.append({'trial_name': trial_name})
        
        for behav_item in behavior_data_items:
            trial_name = behav_item.get('trial_name', '')
            if not trial_name:
                continue
            
            # 获取该试验的时间偏移量
            time_offset = trial_time_offsets.get(trial_name, 0.0)
            
            try:
                hdf5_path = self.project_manager.get_hdf5_path(trial_name)
                if hdf5_path and hdf5_path.exists():
                    import h5py
                    with h5py.File(str(hdf5_path), 'r') as f:
                        trials_path = None
                        for path in ['behavior/trials', '/behavior/trials']:
                            if path in f:
                                trials_path = path
                                break
                        
                        if trials_path:
                            trials_data = f[trials_path][:]
                            print(f"[DEBUG] Loaded {len(trials_data)} trials from {trial_name}")
                            if len(trials_data) > 0:
                                print(f"[DEBUG] Trial dtype names: {trials_data.dtype.names}")
                                print(f"[DEBUG] First trial: {trials_data[0]}")
                            for i, trial in enumerate(trials_data):
                                try:
                                    stim_cnd = int(trial['stim_cnd']) if 'stim_cnd' in trial.dtype.names else 0
                                    print(f"[DEBUG] Trial {i}: stim_cnd={stim_cnd}")
                                    trial_dict = {
                                        'trial_num': int(trial['trial_num']) if 'trial_num' in trial.dtype.names else i + 1,
                                        'start_time': float(trial['start_time']) + time_offset if 'start_time' in trial.dtype.names else time_offset,
                                        'stim_cnd': stim_cnd,
                                        'trial_source': trial_name
                                    }
                                    all_trial_info.append(trial_dict)
                                except Exception as e:
                                    print(f"[DEBUG] Error processing trial {i}: {e}")
                                    continue
            except Exception as e:
                print(f"[DEBUG] 加载试验 {trial_name} 的行为数据失败: {e}")
                continue
        
        return all_trial_info
    
    def _validate_trial_info(self, all_trial_info):
        """验证trial信息"""
        if not all_trial_info:
            self.progress_bar.setVisible(False)
            self.status_label.setText("分析失败: 未找到行为数据")
            QMessageBox.warning(
                self, 
                "数据错误", 
                "未找到任何试验的行为数据（trials）。\n\n" +
                "请确保选择的试验已导入行为数据。"
            )
            return False
        return True
    
    def _print_trial_distribution(self, all_trial_info):
        """打印试验分布信息"""
        # 打印试验来源分布
        trial_sources = [t.get('trial_source', 'unknown') for t in all_trial_info]
        unique_sources = sorted(set(trial_sources))
        print(f"[DEBUG] 试验来源分布: {unique_sources}")
        for source in unique_sources:
            count = trial_sources.count(source)
            print(f"[DEBUG]  试验 {source}: {count} 个试次")
        
        # 打印刺激条件分布
        stim_cnds = [t.get('stim_cnd', 0) for t in all_trial_info]
        unique_cnds = sorted(set(stim_cnds))
        print(f"[DEBUG] 刺激条件分布: {unique_cnds}")
        for cnd in unique_cnds:
            count = stim_cnds.count(cnd)
            print(f"[DEBUG]  条件 {cnd}: {count} 个试次")
    
    def _on_download_sample_code(self):
        """下载示例代码"""
        # TODO: 实现示例代码下载
        QMessageBox.information(self, "提示", "示例代码下载功能开发中")
    
    def _run_analysis_async(self, algorithm_name: str, data_items: list, parameters: dict):
        """异步运行分析"""
        logger.info("=" * 60)
        logger.info("_run_analysis_async 被调用")
        logger.log_vars(
            algorithm_name=algorithm_name,
            data_items_type=type(data_items),
            data_items_len=len(data_items) if data_items else 0,
            parameters_keys=list(parameters.keys()) if parameters else []
        )
        
        try:
            # 调试：检查data_items类型
            if data_items:
                logger.info(f"data_items[0] type: {type(data_items[0])}")
                if isinstance(data_items[0], dict):
                    logger.info(f"data_items[0] keys: {list(data_items[0].keys())}")
                else:
                    logger.error(f"data_items[0] 不是字典! 值: {data_items[0]}")
            
            # 获取算法调度器
            scheduler = self.parameter_panel.scheduler
            
            # 准备输入数据
            from algorithms.base import AlgorithmInput
            input_data = AlgorithmInput()
            
            # 从数据项中加载实际数据
            data_list = []
            sampling_rate = 2000.0  # 默认采样率
            
            # 获取时间对齐配置
            time_alignment = parameters.get('time_alignment', {})
            global_start = time_alignment.get('global_start', 0) if time_alignment else 0
            global_duration = time_alignment.get('global_duration', None) if time_alignment else None
            
            # 调试输出
            print(f"[DEBUG] time_alignment: {time_alignment}")
            print(f"[DEBUG] global_start: {global_start}")
            print(f"[DEBUG] global_duration: {global_duration}")
            print(f"[DEBUG] algorithm_name: {algorithm_name}")
            
            print(f"[DEBUG LOAD] 开始加载数据，data_items数量: {len(data_items)}")
            
            # 创建数据项到数据的映射，避免依赖索引对应关系
            data_map = {}  # key: unique_id, value: loaded_data
            
            for item_idx, item in enumerate(data_items):
                # 确保item是字典类型
                if not isinstance(item, dict):
                    print(f"[DEBUG LOAD] 警告: 数据项类型错误 {type(item)}, 跳过")
                    continue
                    
                data_id = item.get('id', '')
                trial_name = item.get('trial_name', '')
                data_type = item.get('data_type', '')
                unique_id = f"{trial_name}/{data_id}"
                
                print(f"[DEBUG LOAD] 加载数据项 {item_idx}: id={data_id}, trial={trial_name}, type={data_type}")
                
                # 尝试从HDF5文件加载数据
                try:
                    trial = self.project_manager.get_trial(trial_name)
                    hdf5_path = self.project_manager.get_hdf5_path(trial_name)
                    if trial and hdf5_path and hdf5_path.exists():
                        import h5py
                        with h5py.File(str(hdf5_path), 'r') as f:
                            # 根据数据类型构建正确的HDF5路径
                            if data_type == 'spike':
                                # Spike数据路径: /spikes/spike_times
                                path = '/spikes/spike_times'
                            elif data_type == 'lfp':
                                # LFP数据路径: /signals/lfp_data
                                path = '/signals/lfp_data'
                            elif data_type == 'behavior':
                                # 行为数据路径: behavior/events (HDF5中的相对路径)
                                path = 'behavior/events'
                            else:
                                path = f'/{data_id}'
                            
                            if path in f:
                                data = f[path][:]
                                
                                # 尝试从属性中读取采样率
                                if 'sampling_rate' in f[path].attrs:
                                    sampling_rate = f[path].attrs['sampling_rate']
                                
                                # 调试输出
                                print(f"[DEBUG] Loaded data shape: {data.shape}")
                                print(f"[DEBUG] sampling_rate: {sampling_rate}")
                                
                                # 应用时间对齐 - 截取指定时间范围的数据
                                # 注意：ViewRawLFPData算法总是显示完整数据，不应用时间对齐
                                # 注意：Spike数据（时间戳）也不应用样本索引截取，而是用时间范围过滤
                                should_truncate = (algorithm_name != "ViewRawLFPData" and 
                                                  global_duration is not None and 
                                                  sampling_rate > 0 and
                                                  data_type != 'spike')  # Spike数据不在这里截取
                                print(f"[DEBUG] should_truncate: {should_truncate}")
                                if should_truncate:
                                    start_sample = int(global_start * sampling_rate)
                                    end_sample = int((global_start + global_duration) * sampling_rate)
                                    
                                    # 确保不超出数据范围
                                    start_sample = max(0, start_sample)
                                    
                                    # 对于LFP数据(2D: 通道x样本)，按样本维度截取
                                    if data_type == 'lfp' and data.ndim == 2:
                                        end_sample = min(data.shape[1], end_sample)
                                        print(f"[DEBUG] Truncating LFP data: [{start_sample}:{end_sample}]")
                                        if start_sample < data.shape[1]:
                                            data = data[:, start_sample:end_sample]
                                    else:
                                        # 对于1D数据(Spike时间等) - 实际上不会执行到这里，因为spike类型已排除
                                        end_sample = min(len(data), end_sample)
                                        print(f"[DEBUG] Truncating 1D data: [{start_sample}:{end_sample}]")
                                        if start_sample < len(data):
                                            data = data[start_sample:end_sample]
                                else:
                                    print(f"[DEBUG] Data NOT truncated")
                                
                                print(f"[DEBUG] Final data shape: {data.shape}")
                                data_map[unique_id] = data
                                data_list.append(data)
                            else:
                                # 如果路径不存在，生成示例数据
                                sample_data = self._generate_sample_data(data_type)
                                data_map[unique_id] = sample_data
                                data_list.append(sample_data)
                    else:
                        # 没有HDF5文件，生成示例数据
                        sample_data = self._generate_sample_data(data_type)
                        data_map[unique_id] = sample_data
                        data_list.append(sample_data)
                except Exception as e:
                    print(f"加载数据 {data_id} 失败: {e}")
                    sample_data = self._generate_sample_data(data_type)
                    data_map[unique_id] = sample_data
                    data_list.append(sample_data)
            
            # 根据算法类型准备输入数据
            if algorithm_name == "SpikeDetectionThreshold":
                # Spike检测需要LFP数据 [通道数 x 样本数]
                if data_list:
                    # LFP数据从HDF5读取时已经是2D数组 [通道数 x 样本数]
                    lfp_data = data_list[0]
                    # 确保是2D数组
                    if lfp_data.ndim == 1:
                        lfp_data = lfp_data.reshape(1, -1)
                    input_data.lfp_data = lfp_data
                    input_data.sampling_rate = sampling_rate
                    input_data.num_channels = lfp_data.shape[0]
            elif algorithm_name in ["SpikeSortingPCA", "kmeans", "gmm", "wavelet_clustering"]:
                # Spike排序需要Spike波形
                # 注意：从HDF5读取的是Spike时间戳，需要从LFP数据中提取波形
                if data_list:
                    # data_list中现在包含的是Spike时间戳（1D数组）
                    # 我们需要从对应的LFP数据中提取Spike波形
                    
                    # 首先，收集所有Spike时间戳（应用时间对齐）
                    all_spike_times = []
                    for d in data_list:
                        if len(d) > 0:
                            # 应用时间对齐过滤
                            if global_duration is not None:
                                # 只保留在时间范围内的Spike
                                mask = (d >= global_start) & (d <= global_start + global_duration)
                                filtered_spikes = d[mask]
                                all_spike_times.extend(filtered_spikes.tolist())
                            else:
                                all_spike_times.extend(d.tolist())
                    
                    # 去重并排序
                    all_spike_times = sorted(set(all_spike_times))
                    
                    if len(all_spike_times) == 0:
                        # 没有Spike，返回错误
                        output = AlgorithmOutput(
                            success=False,
                            error_message="在选定时间范围内未找到Spike"
                        )
                        self._display_analysis_results(algorithm_name, output, data_items)
                        return
                    
                    # 从LFP数据中提取Spike波形
                    # 需要从对应的试验中加载LFP数据
                    waveforms = self._extract_spike_waveforms_from_lfp(
                        data_items, all_spike_times, sampling_rate
                    )
                    
                    if waveforms is None or len(waveforms) == 0:
                        output = AlgorithmOutput(
                            success=False,
                            error_message="无法从LFP数据中提取Spike波形"
                        )
                        self._display_analysis_results(algorithm_name, output, data_items)
                        return
                    
                    input_data.spike_waveforms = waveforms
            elif algorithm_name in ["LFPPowerSpectrum", "LFPSpectrogram"]:
                # LFP分析需要LFP数据
                if data_list:
                    # LFP数据从HDF5读取时已经是2D数组 [通道数 x 样本数]
                    lfp_data = data_list[0]
                    # 确保是2D数组
                    if lfp_data.ndim == 1:
                        lfp_data = lfp_data.reshape(1, -1)
                    input_data.lfp_data = lfp_data
                    input_data.sampling_rate = sampling_rate
            elif algorithm_name == "ViewRawLFPData":
                # ViewRawLFPData仅支持LFP数据
                if data_list:
                    # LFP数据从HDF5读取时已经是2D数组 [通道数 x 样本数]
                    # 直接使用第一个数据项（因为通常只选择一个LFP数据项）
                    lfp_data = data_list[0]
                    # 确保是2D数组
                    if lfp_data.ndim == 1:
                        # 如果是1D，转换为2D [1 x 样本数]
                        lfp_data = lfp_data.reshape(1, -1)
                    input_data.lfp_data = lfp_data
                    input_data.sampling_rate = sampling_rate
            elif algorithm_name in ["PSTHAnalysis", "RasterPlotAnalysis"]:
                # PSTH和栅格图分析 - 支持多试验数据合并
                # 收集所有Spike数据项和行为数据项
                spike_data_items, behavior_data_items = self._collect_data_items(data_items, data_map)
                
                # 调试输出
                print(f"[DEBUG] data_items count: {len(data_items)}")
                print(f"[DEBUG] spike_data_items count: {len(spike_data_items)}")
                print(f"[DEBUG] behavior_data_items count: {len(behavior_data_items)}")
                for idx, item in enumerate(data_items):
                    if isinstance(item, dict):
                        print(f"[DEBUG] data_item[{idx}]: type={item.get('data_type')}, trial={item.get('trial_name')}")
                
                # 检查是否选择了Spike数据
                if not self._validate_spike_data(spike_data_items, algorithm_name):
                    return
                
                # 为每个试验分配时间偏移量，确保Spike时间不重叠
                all_spike_times = []
                trial_time_offsets = {}  # trial_name -> time_offset
                current_offset = 0.0
                
                for spike_item in spike_data_items:
                    trial_name = spike_item['trial_name']
                    spike_data = spike_item['data']
                    
                    # 为该试验分配时间偏移量
                    trial_time_offsets[trial_name] = current_offset
                    
                    if isinstance(spike_data, np.ndarray):
                        spike_list = spike_data.tolist()
                    elif isinstance(spike_data, list):
                        spike_list = spike_data
                    else:
                        spike_list = []
                    
                    # 将Spike时间加上偏移量
                    offset_spikes = [t + current_offset for t in spike_list]
                    all_spike_times.extend(offset_spikes)
                    
                    # 更新偏移量（假设每个试验约100秒）
                    if spike_list:
                        current_offset += max(spike_list) + 10.0  # 加10秒间隔
                    else:
                        current_offset += 100.0
                
                if not all_spike_times:
                    self.progress_bar.setVisible(False)
                    self.status_label.setText("分析失败: Spike数据为空")
                    QMessageBox.warning(self, "数据错误", "选择的Spike数据为空")
                    return
                
                input_data.spike_times = np.array(all_spike_times)
                print(f"[DEBUG] 合并了 {len(spike_data_items)} 个Spike数据，共 {len(all_spike_times)} 个Spike")
                
                # 从所有behavior数据加载trial信息，并应用时间偏移
                all_trial_info = []
                
                # 如果没有选择behavior数据，尝试从Spike数据对应的试验加载
                if not behavior_data_items:
                    for spike_item in spike_data_items:
                        trial_name = spike_item['trial_name']
                        if trial_name:
                            behavior_data_items.append({'trial_name': trial_name})
                
                for behav_item in behavior_data_items:
                    trial_name = behav_item.get('trial_name', '')
                    if not trial_name:
                        continue
                    
                    # 获取该试验的时间偏移量
                    time_offset = trial_time_offsets.get(trial_name, 0.0)
                    
                    try:
                        hdf5_path = self.project_manager.get_hdf5_path(trial_name)
                        if hdf5_path and hdf5_path.exists():
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
                                                'end_time': float(trial['end_time']) + time_offset if 'end_time' in trial.dtype.names else time_offset + 1.0,
                                                'stim_cnd': int(trial['stim_cnd']) if 'stim_cnd' in trial.dtype.names else 0,
                                                'aborted': bool(trial['aborted']) if 'aborted' in trial.dtype.names else False,
                                                'trial_source': trial_name
                                            }
                                            all_trial_info.append(trial_dict)
                                        except Exception as conv_e:
                                            continue
                    except Exception as e:
                        print(f"[DEBUG] 加载试验 {trial_name} 的行为数据失败: {e}")
                        continue
                
                if not all_trial_info:
                    self.progress_bar.setVisible(False)
                    self.status_label.setText("分析失败: 未找到行为数据")
                    QMessageBox.warning(
                        self, 
                        "数据错误", 
                        "未找到任何试验的行为数据（trials）。\n\n"
                        "请确保选择的试验已导入行为数据。"
                    )
                    return
                
                input_data.trial_info = all_trial_info
                print(f"[DEBUG] 合并了 {len(behavior_data_items)} 个试验的行为数据，共 {len(all_trial_info)} 个试次")
                
                # 打印试验来源分布
                trial_sources = [t.get('trial_source', 'unknown') for t in all_trial_info]
                unique_sources = sorted(set(trial_sources))
                print(f"[DEBUG] 试验来源分布: {unique_sources}")
                for source in unique_sources:
                    count = trial_sources.count(source)
                    print(f"[DEBUG]  试验 {source}: {count} 个试次")
                
                # 打印刺激条件分布
                stim_cnds = [t.get('stim_cnd', 0) for t in all_trial_info]
                unique_cnds = sorted(set(stim_cnds))
                print(f"[DEBUG] 刺激条件分布: {unique_cnds}")
                for cnd in unique_cnds:
                    count = stim_cnds.count(cnd)
                    print(f"[DEBUG]  条件 {cnd}: {count} 个试次")
            elif algorithm_name == "TuningCurveAnalysis":
                # 调谐曲线分析 - 支持多试验数据合并
                # 收集所有Spike数据项和行为数据项
                spike_data_items, behavior_data_items = self._collect_data_items(data_items, data_map)
                
                # 检查是否选择了Spike数据
                if not self._validate_spike_data(spike_data_items, algorithm_name):
                    return
                
                # 为每个试验分配时间偏移量，确保Spike时间不重叠
                all_spike_times, trial_time_offsets = self._merge_spike_data(spike_data_items)
                if all_spike_times is None:
                    return
                
                input_data.spike_times = all_spike_times
                print(f"[DEBUG] 合并了 {len(spike_data_items)} 个Spike数据，共 {len(all_spike_times)} 个Spike")
                
                # 从所有behavior数据加载trial信息，并应用时间偏移
                all_trial_info = self._load_trial_info(behavior_data_items, spike_data_items, trial_time_offsets)
                
                # 验证trial信息
                if not self._validate_trial_info(all_trial_info):
                    return
                
                input_data.trial_info = all_trial_info
                print(f"[DEBUG] 合并了 {len(behavior_data_items)} 个试验的行为数据，共 {len(all_trial_info)} 个试次")
                
                # 打印试验来源分布
                self._print_trial_distribution(all_trial_info)
            
            elif algorithm_name == "ROCAnalysis":
                # ROC分析 - 支持多试验数据合并
                # 收集所有Spike数据项和行为数据项
                spike_data_items, behavior_data_items = self._collect_data_items(data_items, data_map)
                
                # 打印ROC分析的调试信息
                print(f"[DEBUG ROC] data_items数量: {len(data_items)}, data_map数量: {len(data_map)}")
                print(f"[DEBUG ROC] 最终: spike_data_items={len(spike_data_items)}, behavior_data_items={len(behavior_data_items)}")
                
                # 检查是否选择了Spike数据
                if not self._validate_spike_data(spike_data_items, algorithm_name):
                    return
                
                # 为每个试验分配时间偏移量，确保Spike时间不重叠
                all_spike_times, trial_time_offsets = self._merge_spike_data(spike_data_items)
                if all_spike_times is None:
                    return
                
                input_data.spike_times = all_spike_times
                
                # 从所有behavior数据加载trial信息，并应用时间偏移
                all_trial_info = self._load_trial_info(behavior_data_items, spike_data_items, trial_time_offsets)
                
                # 验证trial信息
                if not self._validate_trial_info(all_trial_info):
                    return
                
                input_data.trial_info = all_trial_info
            
            elif algorithm_name in ["LDADecoder", "SVMClassifier", "RandomForestClassifier"]:
                # 解码算法需要Spike数据和行为数据
                # 初始化时间偏移量字典
                trial_time_offsets = {}
                
                # 收集Spike数据和行为数据
                spike_data_items = []
                behavior_data_items = []
                
                for item in data_items:
                    if isinstance(item, dict):
                        data_type = item.get('data_type', '')
                        if data_type == 'spike':
                            spike_data_items.append(item)
                        elif data_type == 'behavior' or 'events' in item.get('id', '').lower():
                            behavior_data_items.append(item)
                
                print(f"[DEBUG] LDADecoder: spike_items={len(spike_data_items)}, behavior_items={len(behavior_data_items)}")
                
                # 处理Spike数据
                if spike_data_items:
                    all_spike_times = []
                    for item in spike_data_items:
                        trial_name = item.get('trial_name', '')
                        data_id = item.get('id', '')
                        
                        try:
                            hdf5_path = self.project_manager.get_hdf5_path(trial_name)
                            if hdf5_path and hdf5_path.exists():
                                import h5py
                                with h5py.File(str(hdf5_path), 'r') as f:
                                    # 尝试多个可能的Spike数据路径
                                    possible_paths = [
                                        '/spikes/spike_times',
                                        f'/processing/spikes/{data_id}/times',
                                        f'/spikes/{data_id}/times',
                                        '/spikes/times'
                                    ]
                                    
                                    spike_path = None
                                    for path in possible_paths:
                                        if path in f:
                                            spike_path = path
                                            break
                                    
                                    if spike_path:
                                        spike_times = f[spike_path][:]
                                        all_spike_times.extend(spike_times.tolist())
                                        print(f"[DEBUG] Loaded {len(spike_times)} spikes from {trial_name} using path: {spike_path}")
                                    else:
                                        print(f"[DEBUG] Spike path not found in {trial_name}. Tried: {possible_paths}")
                                        # 列出HDF5文件中的所有键帮助调试
                                        print(f"[DEBUG] Available keys in HDF5: {list(f.keys())}")
                        except Exception as e:
                            print(f"[DEBUG] 加载Spike数据失败: {e}")
                            import traceback
                            traceback.print_exc()
                            continue
                    
                    if all_spike_times:
                        input_data.spike_times = np.array(sorted(all_spike_times))
                        print(f"[DEBUG] Total spikes loaded: {len(input_data.spike_times)}")
                    else:
                        print("[DEBUG] No spikes loaded")
                
                # 使用已有的方法加载行为数据
                if behavior_data_items or spike_data_items:
                    all_trial_info = self._load_trial_info(behavior_data_items, spike_data_items, trial_time_offsets)
                    print(f"[DEBUG] Loaded {len(all_trial_info)} trials")
                    
                    if all_trial_info:
                        # 为每个trial添加end_time（解码算法需要）
                        for trial in all_trial_info:
                            if 'end_time' not in trial:
                                # 默认试次持续1秒
                                trial['end_time'] = trial.get('start_time', 0) + 1.0
                        input_data.trial_info = all_trial_info
                        
                        # 打印试次分布信息
                        self._print_trial_distribution(all_trial_info)
                        
                        # 检查是否有多个类别
                        stim_cnds = [t.get('stim_cnd', 0) for t in all_trial_info]
                        unique_cnds = sorted(set(stim_cnds))
                        if len(unique_cnds) < 2:
                            QMessageBox.warning(
                                self,
                                "数据警告",
                                f"所有试次的刺激条件（stim_cnd）都相同（值为{unique_cnds[0] if unique_cnds else '无'}）。\n\n"
                                "LDA算法需要至少2个不同的类别才能进行分类。\n"
                                "请检查原始数据是否包含多个刺激条件。"
                            )
                    else:
                        print("[DEBUG] No trial info loaded")
                
                # 如果没有Spike数据但有LFP数据，也可以用于解码
                if input_data.spike_times is None and data_list:
                    for item in data_items:
                        if isinstance(item, dict) and item.get('data_type') == 'lfp':
                            # 使用LFP数据
                            lfp_data = data_list[0]
                            if lfp_data.ndim == 1:
                                lfp_data = lfp_data.reshape(1, -1)
                            input_data.lfp_data = lfp_data
                            input_data.sampling_rate = sampling_rate
                            print(f"[DEBUG] Using LFP data instead of spikes: shape={lfp_data.shape}")
                            break
                
                print(f"[DEBUG] Final input_data: spike_times={input_data.spike_times is not None}, trial_info={len(input_data.trial_info) if input_data.trial_info else 0}, lfp_data={input_data.lfp_data is not None}")
            else:
                # 处理自定义算法
                # 检查是否有LFP数据
                has_lfp_data = False
                for item in data_items:
                    if isinstance(item, dict):
                        data_type = item.get('data_type', '')
                        if data_type == 'lfp':
                            has_lfp_data = True
                            break
                
                if has_lfp_data and data_list:
                    # 自定义算法处理LFP数据
                    lfp_data = data_list[0]
                    # 确保是2D数组
                    if lfp_data.ndim == 1:
                        lfp_data = lfp_data.reshape(1, -1)
                    input_data.lfp_data = lfp_data
                    input_data.sampling_rate = sampling_rate
                    input_data.num_channels = lfp_data.shape[0]
                else:
                    # 其他类型数据，放入extra_data
                    input_data.extra_data['raw_data'] = data_list
            
            # 检查LFP算法的数据类型
            if algorithm_name in ["LFPPowerSpectrum", "LFPSpectrogram", "ViewRawLFPData"]:
                # 检查是否选择了LFP数据
                has_lfp_data = False
                for item in data_items:
                    # 确保item是字典类型
                    if isinstance(item, dict):
                        data_type = item.get('data_type', '')
                        item_id = item.get('id', '')
                        if data_type == 'lfp' or 'signal' in item_id.lower() or 'lfp' in item_id.lower():
                            has_lfp_data = True
                            break
                
                if not has_lfp_data:
                    self.progress_bar.setVisible(False)
                    self.status_label.setText("分析失败: 请选择LFP信号数据")
                    QMessageBox.warning(
                        self, 
                        "数据类型错误", 
                        f"{algorithm_name} 需要选择信号数据（LFP），而不是行为数据（Events）或Spike数据。\n\n"
                        "请在左侧数据浏览器中选择'LFP数据'类别的数据项。"
                    )
                    return
            
            # 运行算法
            output = scheduler.run_algorithm(algorithm_name, input_data, parameters)
            
            self.progress_bar.setVisible(False)
            
            if output.success:
                self.status_label.setText(f"分析完成: {algorithm_name}")
                
                # 在可视化区域显示结果
                self._display_analysis_results(algorithm_name, output, data_items, parameters)
            else:
                self.status_label.setText(f"分析失败: {algorithm_name}")
                QMessageBox.warning(self, "分析失败", f"{algorithm_name} 分析失败:\n{output.error_message}")
                
        except Exception as e:
            logger.exception(e, "运行分析时出错")
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"分析出错: {algorithm_name}")
            QMessageBox.critical(self, "错误", f"运行分析时出错:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def _extract_spike_waveforms_from_lfp(self, data_items: list, spike_times: list, sampling_rate: float) -> np.ndarray:
        """
        从LFP数据中提取Spike波形
        
        Args:
            data_items: 数据项列表
            spike_times: Spike时间戳列表（秒）
            sampling_rate: 采样率
            
        Returns:
            np.ndarray: Spike波形数组 [n_spikes x waveform_length]
        """
        import numpy as np
        import h5py
        
        if not spike_times:
            return None
        
        # 波形参数
        pre_ms = 5.0  # Spike前5ms
        post_ms = 5.0  # Spike后5ms
        pre_samples = int(pre_ms * sampling_rate / 1000)
        post_samples = int(post_ms * sampling_rate / 1000)
        waveform_length = pre_samples + post_samples
        
        waveforms = []
        
        # 从每个数据项对应的试验中加载LFP数据
        for item in data_items:
            if isinstance(item, dict):
                trial_name = item.get('trial_name')
                if not trial_name:
                    continue
                
                try:
                    trial = self.project_manager.get_trial(trial_name)
                    hdf5_path = self.project_manager.get_hdf5_path(trial_name)
                    
                    if not hdf5_path or not hdf5_path.exists():
                        continue
                    
                    with h5py.File(str(hdf5_path), 'r') as f:
                        # 加载LFP数据
                        lfp_path = '/signals/lfp_data'
                        if lfp_path not in f:
                            continue
                        
                        lfp_data = f[lfp_path][:]
                        
                        # 如果LFP数据是2D（多通道），取第一个通道
                        if lfp_data.ndim == 2:
                            lfp_data = lfp_data[0, :]
                        
                        # 提取该试验时间范围内的Spike
                        for spike_time in spike_times:
                            spike_sample = int(spike_time * sampling_rate)
                            
                            # 确保不越界
                            start_idx = max(0, spike_sample - pre_samples)
                            end_idx = min(len(lfp_data), spike_sample + post_samples)
                            
                            if end_idx - start_idx == waveform_length:
                                waveform = lfp_data[start_idx:end_idx]
                                waveforms.append(waveform)
                        
                except Exception as e:
                    print(f"从试验 {trial_name} 提取Spike波形失败: {e}")
                    continue
        
        if not waveforms:
            return None
        
        return np.array(waveforms)
    
    def _generate_sample_data(self, data_type: str) -> any:
        """生成示例数据用于测试"""
        import numpy as np
        
        if data_type == 'spike':
            # 生成随机spike时间
            return np.sort(np.random.rand(100) * 10)
        elif data_type == 'lfp':
            # 生成模拟LFP信号
            t = np.linspace(0, 10, 10000)
            return np.sin(2 * np.pi * 10 * t) + 0.5 * np.random.randn(10000)
        elif data_type == 'behavior':
            # 生成模拟行为数据
            return np.random.rand(100)
        else:
            return np.random.randn(1000)
    
    def _display_analysis_results(self, algorithm_name: str, output, data_items: list, parameters: dict = None):
        """在可视化区域显示分析结果"""
        if parameters is None:
            parameters = {}
        result_data = output.data if output.data else {}
        
        # 检查是否需要显示图像
        plot_config = result_data.get('plot_config', {})
        show_plot = plot_config.get('show_plot', True)
        
        # 检查是否有消息
        message = result_data.get('message', '')
        if message:
            QMessageBox.information(self, "分析结果", message)
        
        # 如果不需要显示图像，直接返回
        if not show_plot:
            return
        
        # 生成数据名称用于显示
        spike_data_items = []
        behavior_data_items = []
        
        # 收集所有spike和behavior数据项
        for item in data_items:
            if isinstance(item, dict):
                data_type = item.get('data_type', '')
                if data_type == 'spike':
                    spike_data_items.append(item)
                elif data_type == 'behavior':
                    behavior_data_items.append(item)
        
        # 生成合适的标题
        if len(spike_data_items) == 1:
            # 单个spike数据项
            first_item = spike_data_items[0]
            data_name = first_item.get('display_name', first_item.get('id', '数据'))
        elif len(spike_data_items) > 1:
            # 多个spike数据项
            data_name = f"多数据 ({len(spike_data_items)}个)"
        else:
            # 无spike数据项
            data_name = '数据'
        
        # 根据算法类型显示不同的图表
        if algorithm_name == "SpikeDetectionThreshold":
            # SpikeDetectionThreshold返回的数据结构:
            # {'spike_times': array, 'spike_channels': array, 'spike_waveforms': array}
            spike_times = result_data.get('spike_times', [])
            spike_channels = result_data.get('spike_channels', [])
            
            if len(spike_times) > 0:
                # 从第一个数据项获取时间对齐配置
                # time_range 是 tuple/list: (start, end)
                time_range = first_item.get('time_range', None) if isinstance(first_item, dict) else None
                if time_range and isinstance(time_range, (list, tuple)) and len(time_range) >= 2:
                    global_start = time_range[0]  # 获取起始时间
                else:
                    global_start = 0
                
                # 调整spike时间（加上全局起始时间）
                adjusted_spike_times = spike_times + global_start
                
                # 按通道组织spike时间
                unique_channels = np.unique(spike_channels) if len(spike_channels) > 0 else [0]
                spike_times_by_channel = []
                for ch in unique_channels:
                    mask = spike_channels == ch
                    spike_times_by_channel.append(adjusted_spike_times[mask])
                
                self.visualization_area.display_raster({
                    'channel_id': data_name,
                    'trial_ids': list(range(len(unique_channels))),
                    'spike_times': spike_times_by_channel,
                    'ylabel': '通道'  # 指定Y轴标签
                }, f"Spike检测 - {data_name} (共{len(spike_times)}个)")
            else:
                QMessageBox.information(self, "分析结果", "未检测到Spike")
                    
        elif algorithm_name in ["SpikeSortingPCA", "kmeans", "gmm", "wavelet_clustering"]:
            # Spike排序结果显示
            labels = result_data.get('labels', [])
            cluster_centers = result_data.get('cluster_centers', [])
            
            if len(labels) > 0:
                n_clusters = len(np.unique(labels))
                self.visualization_area.add_plot(
                    f"Spike排序 - {data_name}",
                    {
                        'data_type': 'spike_sorting',
                        'title': f'聚类结果 (n={n_clusters}类, 共{len(labels)}个Spike)',
                        'data': result_data
                    }
                )
            else:
                QMessageBox.information(self, "分析结果", "无排序结果")
                    
        elif algorithm_name == "LFPPowerSpectrum":
            # LFP功率谱结果显示
            if 'frequencies' in result_data and 'psd' in result_data:
                # 传递所有通道的功率谱数据
                self.visualization_area.display_power_spectrum({
                    'freqs': result_data['frequencies'],
                    'power': result_data['psd'],  # [通道数 x 频率点数]
                    'psd_mean': result_data.get('psd_mean', None)
                }, f"功率谱 - {data_name}")
            else:
                QMessageBox.information(self, "分析结果", "无功率谱分析结果")
                
        elif algorithm_name == "LFPSpectrogram":
            # LFP时频图结果显示
            if 'spectrogram' in result_data and 'frequencies' in result_data:
                # 获取时间对齐信息用于调整时间轴
                # time_range 是 tuple/list: (start, end)
                time_range = first_item.get('time_range', None) if isinstance(first_item, dict) else None
                if time_range and isinstance(time_range, (list, tuple)) and len(time_range) >= 2:
                    global_start = time_range[0]  # 获取起始时间
                else:
                    global_start = 0
                
                # 调整时间轴
                times = result_data.get('times', [])
                if len(times) > 0:
                    times = np.array(times) + global_start
                
                # 获取通道索引信息用于标题
                channel_idx = parameters.get('channel_idx', -1)
                if channel_idx == -1:
                    channel_str = "均值"
                else:
                    channel_str = f"Ch{channel_idx}"
                
                self.visualization_area.display_spectrogram({
                    'spectrogram': result_data['spectrogram'],
                    'times': times,
                    'freqs': result_data.get('frequencies', [])
                }, f"时频图 - {data_name} - {channel_str}")
            else:
                QMessageBox.information(self, "分析结果", "无时频图分析结果")
                    
        elif algorithm_name == "PSTHAnalysis":
            # PSTH结果显示
            # PSTH算法返回的数据键: 'bin_centers', 'psth_rate', 'psth_counts'
            if 'bin_centers' in result_data and 'psth_counts' in result_data:
                self.visualization_area.display_psth({
                    'bins': result_data['bin_centers'],
                    'counts': result_data['psth_counts'],
                    'rates': result_data.get('psth_rate', []),
                    'trial_count': result_data.get('n_trials', len(data_items))
                }, f"PSTH - {data_name}")
            else:
                QMessageBox.information(self, "分析结果", "无PSTH分析结果")
                    
        elif algorithm_name == "RasterPlotAnalysis":
            # 栅格图显示 - 支持按刺激条件分组
            # 栅格图算法返回的数据键: 'condition_rasters', 'time_range', 'unique_conditions'
            if 'condition_rasters' in result_data:
                condition_rasters = result_data['condition_rasters']
                time_range = result_data.get('time_range', (-0.2, 1.0))
                unique_conditions = result_data.get('unique_conditions', [])
                
                if condition_rasters and len(condition_rasters) > 0:
                    # 为每个刺激条件创建一个栅格图
                    for condition, raster_data in sorted(condition_rasters.items()):
                        trial_spikes = raster_data.get('trial_spikes', [])
                        n_trials = raster_data.get('n_trials', len(trial_spikes))
                        mean_response = raster_data.get('mean_response', 0.0)
                        
                        if isinstance(trial_spikes, list) and n_trials > 0:
                            total_spikes = sum(len(spikes) for spikes in trial_spikes)
                            # 获取试次来源信息（如果存在）
                            trial_sources = raster_data.get('trial_sources', None)
                            self.visualization_area.display_raster({
                                'channel_id': data_name,
                                'trial_ids': list(range(n_trials)),
                                'spike_times': trial_spikes,
                                'trial_sources': trial_sources,  # 传递试次来源信息
                                'time_range': time_range,
                                'ylabel': '试次',
                                'n_trials': n_trials,
                                'total_spikes': total_spikes,
                                'condition': condition,
                                'mean_response': mean_response
                            }, f"栅格图 - 条件{condition} - {data_name} ({n_trials}试次, {total_spikes}个Spike)")
                    
                    # 显示汇总信息
                    n_conditions = len(unique_conditions)
                    total_trials = sum(r['n_trials'] for r in condition_rasters.values())
                    QMessageBox.information(
                        self, 
                        "栅格图分析完成", 
                        f"已生成 {n_conditions} 个刺激条件的栅格图\n"
                        f"总试次数: {total_trials}"
                    )
                else:
                    QMessageBox.information(self, "分析结果", "无栅格图数据")
            else:
                QMessageBox.information(self, "分析结果", "无栅格图数据")
                    
        elif algorithm_name == "TuningCurveAnalysis":
            # 调谐曲线显示 - 支持多试验
            # 算法返回的数据键: 'conditions', 'mean_responses', 'trial_curves'
            if 'conditions' in result_data and 'mean_responses' in result_data:
                # 构建显示数据
                plot_data = {
                    'conditions': result_data['conditions'],
                    'mean_responses': result_data['mean_responses'],
                    'std_responses': result_data.get('std_responses', []),
                    'sem_responses': result_data.get('sem_responses', [])
                }
                
                # 如果有多个试验的曲线数据，添加进去
                if 'trial_curves' in result_data:
                    plot_data['trial_curves'] = result_data['trial_curves']
                    n_trials = len(result_data['trial_curves'])
                    title = f"调谐曲线 - {data_name} ({n_trials}个试验)"
                else:
                    title = f"调谐曲线 - {data_name}"
                
                self.visualization_area.display_tuning_curve(plot_data, title)
            else:
                QMessageBox.information(self, "分析结果", "无调谐曲线数据")
                    
        elif algorithm_name == "ROCAnalysis":
            # ROC分析结果显示
            roc_curves = result_data.get('roc_curves', {})
            
            if roc_curves:
                # 显示ROC曲线
                self.visualization_area.display_roc_curve({
                    'roc_curves': roc_curves
                }, f"ROC曲线对比 - {data_name}")
                
                # 显示统计信息
                stats = output.statistics
                if 'n_sources' in stats:
                    # 多个试验来源
                    info_text = f"试验来源数: {stats.get('n_sources', 0)}\n"
                    info_text += f"平均AUC: {stats.get('avg_auc', 0):.3f}\n"
                    info_text += f"总试次数: {stats.get('n_trials', 0)}\n"
                    info_text += f"正类样本: {stats.get('n_positive', 0)}\n"
                    info_text += f"负类样本: {stats.get('n_negative', 0)}\n\n"
                    
                    # 添加每个来源的AUC
                    for source, curve_data in roc_curves.items():
                        short_name = source.split('_')[0] if '_' in source else source
                        info_text += f"{short_name}: AUC={curve_data.get('auc', 0):.3f}\n"
                    
                    QMessageBox.information(self, "ROC分析结果", info_text)
                else:
                    # 单个试验来源
                    QMessageBox.information(
                        self, 
                        "ROC分析结果",
                        f"AUC: {stats.get('auc', 0):.3f}\n"
                        f"总试次数: {stats.get('n_trials', 0)}\n"
                        f"正类样本: {stats.get('n_positive', 0)}\n"
                        f"负类样本: {stats.get('n_negative', 0)}"
                    )
            else:
                QMessageBox.information(self, "分析结果", "无ROC曲线数据")
        
        elif algorithm_name in ["LDADecoder", "SVMClassifier", "RandomForestClassifier"]:
            # 解码/分类结果显示
            # 注意：统计数据在 output.statistics 中，而不是 output.data 中
            from src.algorithms import AlgorithmOutput
            if isinstance(output, AlgorithmOutput):
                stats = output.statistics if output.statistics else {}
                data_dict = output.data if output.data else {}
            else:
                stats = result_data.get('statistics', {})
                data_dict = result_data
            
            test_accuracy = stats.get('test_accuracy', 0)
            cv_accuracy = stats.get('mean_cv_accuracy', 0)
            
            print(f"[DEBUG] Display results - test_accuracy={test_accuracy}, cv_accuracy={cv_accuracy}")
            print(f"[DEBUG] stats keys: {stats.keys() if stats else 'None'}")
            
            # 构建结果信息
            result_info = f"测试集准确率: {test_accuracy:.2%}\n"
            result_info += f"交叉验证准确率: {cv_accuracy:.2%}"
            
            if 'n_support_vectors' in stats:
                result_info += f"\n支持向量数: {stats['n_support_vectors']}"
            if 'n_trees' in stats:
                result_info += f"\n决策树数量: {stats['n_trees']}"
            
            # 获取混淆矩阵和类别信息
            confusion_matrix = data_dict.get('confusion_matrix') if isinstance(data_dict, dict) else None
            classes = data_dict.get('classes') if isinstance(data_dict, dict) else None
            
            print(f"[DEBUG] confusion_matrix shape: {confusion_matrix.shape if confusion_matrix is not None else 'None'}")
            print(f"[DEBUG] classes: {classes}")
            
            self.visualization_area.add_plot(
                f"{algorithm_name} - {data_name}",
                {
                    'data_type': 'decoding_results',
                    'title': f'{algorithm_name} 分类结果',
                    'result_info': result_info,
                    'statistics': stats,
                    'confusion_matrix': confusion_matrix,
                    'classes': classes
                }
            )
        elif algorithm_name == "ViewRawLFPData":
            # 查看原始LFP数据结果显示
            if 'signal_data' in result_data and 'times' in result_data:
                # 获取绘图配置
                plot_config = result_data.get('plot_config', {})
                n_channels = result_data.get('channel_indices', [0])
                duration = result_data.get('times', []).shape[0] / result_data.get('sampling_rate', 1000) if len(result_data.get('times', [])) > 0 else 0
                
                self.visualization_area.add_plot(
                    f"LFP原始信号 - {data_name} - {len(n_channels)}通道 - {duration:.1f}s",
                    {
                        'data_type': 'raw_signal',
                        'signal_data': result_data['signal_data'],
                        'times': result_data['times'],
                        'channel_indices': n_channels,
                        'plot_config': plot_config
                    }
                )
            else:
                QMessageBox.information(self, "分析结果", "无LFP信号数据")
        else:
            # 处理所有其他算法，包括自定义算法
            # 尝试从结果数据中提取可视化数据
            # 首先检查是否有plot_type字段
            plot_type = result_data.get('plot_type', '')
            
            if plot_type == 'spike_raster' or 'spike_times' in result_data:
                # 显示Spike栅格图
                spike_times = result_data['spike_times']
                if isinstance(spike_times, list) and len(spike_times) > 0:
                    self.visualization_area.display_raster({
                        'channel_id': data_name,
                        'trial_ids': list(range(len(spike_times))),
                        'spike_times': spike_times,
                        'ylabel': '试次'
                    }, f"算法结果 - {algorithm_name} - {data_name}")
            elif plot_type == 'raw_signal' or 'signal_data' in result_data:
                # 显示信号波形
                signal_data = result_data['signal_data']
                times = result_data.get('times', [])
                if len(times) == 0 and hasattr(signal_data, 'shape'):
                    # 生成时间轴
                    import numpy as np
                    sampling_rate = result_data.get('sampling_rate', 2000.0)
                    times = np.arange(signal_data.shape[1]) / sampling_rate
                
                self.visualization_area.add_plot(
                    f"算法结果 - {algorithm_name} - {data_name}",
                    {
                        'data_type': 'raw_signal',
                        'signal_data': signal_data,
                        'times': times,
                        'channel_indices': list(range(signal_data.shape[0])) if hasattr(signal_data, 'shape') else [0],
                        'plot_config': result_data.get('plot_config', {})
                    }
                )
            elif plot_type == 'power_spectrum' or ('power' in result_data and 'freqs' in result_data):
                # 显示功率谱
                self.visualization_area.display_power_spectrum({
                    'freqs': result_data['freqs'],
                    'power': result_data['power'],
                    'psd_mean': result_data.get('psd_mean', None)
                }, f"算法结果 - {algorithm_name} - {data_name}")
            elif plot_type == 'spectrogram' or 'spectrogram' in result_data:
                # 显示时频图
                self.visualization_area.display_spectrogram({
                    'spectrogram': result_data['spectrogram'],
                    'times': result_data.get('times', []),
                    'freqs': result_data.get('frequencies', [])
                }, f"算法结果 - {algorithm_name} - {data_name}")
            elif plot_type == 'time_frequency' or 'power_data' in result_data:
                # 显示时频图（MNE算法）
                channel_info = result_data.get('channel_info', '')
                title_suffix = f" - {channel_info}" if channel_info else ""
                self.visualization_area.display_spectrogram({
                    'spectrogram': result_data['power_data'],
                    'times': result_data.get('times', []),
                    'freqs': result_data.get('frequencies', [])
                }, f"算法结果 - {algorithm_name} - {data_name}{title_suffix}")
            elif plot_type == 'psth' or ('psth_counts' in result_data and 'bin_centers' in result_data):
                # 显示PSTH
                self.visualization_area.display_psth({
                    'bins': result_data['bin_centers'],
                    'counts': result_data['psth_counts'],
                    'rates': result_data.get('psth_rate', []),
                    'trial_count': result_data.get('n_trials', len(data_items))
                }, f"算法结果 - {algorithm_name} - {data_name}")
            elif plot_type == 'spike_sorting' or ('labels' in result_data and 'cluster_centers' in result_data):
                # 显示Spike排序结果
                self.visualization_area.add_plot(
                    f"算法结果 - {algorithm_name} - {data_name}",
                    {
                        'data_type': 'spike_sorting',
                        'title': f'聚类结果',
                        'data': result_data
                    }
                )
            elif plot_type == 'tuning_curve' or ('conditions' in result_data and 'mean_responses' in result_data):
                # 显示调谐曲线
                plot_data = {
                    'conditions': result_data['conditions'],
                    'mean_responses': result_data['mean_responses'],
                    'std_responses': result_data.get('std_responses', []),
                    'sem_responses': result_data.get('sem_responses', [])
                }
                self.visualization_area.display_tuning_curve(plot_data, f"算法结果 - {algorithm_name} - {data_name}")
            else:
                # 默认显示
                QMessageBox.information(self, "分析完成", f"{algorithm_name} 分析已完成，但无可视化数据")


def main():
    """主函数"""
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setApplicationName("NeuroPrime")
    app.setApplicationVersion("1.0.0")
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
