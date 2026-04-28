"""
ManageAlgorithmsDialog - 管理自定义算法对话框

显示已集成的算法列表，允许用户删除已集成的算法或添加custom_algorithms文件夹中的脚本。
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal


class ManageAlgorithmsDialog(QDialog):
    """管理自定义算法对话框"""
    
    algorithms_updated = pyqtSignal(str)  # 算法更新信号，传递更新的文件路径
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("管理自定义算法")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self._init_ui()
        self._load_algorithms()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("已集成的算法")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 算法列表
        self.algorithm_list = QListWidget()
        layout.addWidget(self.algorithm_list)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 添加拉伸空间
        button_layout.addStretch()
        
        # 删除算法按钮
        self.delete_button = QPushButton("删除算法")
        self.delete_button.clicked.connect(self._on_delete_algorithm)
        self.delete_button.setFixedWidth(100)
        button_layout.addWidget(self.delete_button)
        
        # 关闭按钮
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        self.close_button.setFixedWidth(100)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _load_algorithms(self):
        """加载已集成的算法"""
        self.algorithm_list.clear()
        
        try:
            # 清除模块缓存，确保删除的算法不会被重新加载
            import sys
            import importlib
            # 清除所有可能的自定义算法模块
            modules_to_remove = []
            for module_name in list(sys.modules.keys()):
                if (module_name in ['aaaa', 'bbbb', 'cccc', 'CustomAlgorithm', 'CustomAlgorithmTest', 'New', 'newnew', 'newnewnew', 'newnewnewnewnewn', 'ViewRawLFPData'] or 
                    module_name.startswith('customalgorithm') or 
                    module_name.startswith('new') or 
                    module_name.startswith('view_raw')):
                    modules_to_remove.append(module_name)
            
            # 清除所有pycache文件
            import shutil
            import os
            pycache_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'custom_algorithms', '__pycache__')
            if os.path.exists(pycache_dir):
                shutil.rmtree(pycache_dir)
                print(f"已删除pycache目录: {pycache_dir}")
            
            # 清除所有与自定义算法相关的模块
            for module_name in modules_to_remove:
                if module_name in sys.modules:
                    del sys.modules[module_name]
                    print(f"已从缓存中移除模块: {module_name}")
            
            # 强制重新加载scheduler模块
            if 'src.algorithms.scheduler' in sys.modules:
                del sys.modules['src.algorithms.scheduler']
                print("已从缓存中移除scheduler模块")
            
            # 导入AlgorithmScheduler
            from src.algorithms.scheduler import AlgorithmScheduler
            scheduler = AlgorithmScheduler()
            
            # 注册内置算法和加载自定义算法
            scheduler.register_builtin_algorithms()
            
            # 获取所有算法
            algorithms = scheduler.get_algorithms()
            
            # 筛选自定义算法
            custom_algorithms = []
            for algo_name, algo_class in algorithms.items():
                if hasattr(algo_class, 'category') and algo_class.category == "自定义算法":
                    custom_algorithms.append((algo_name, algo_class))
            
            # 添加到列表
            for algo_name, algo_class in custom_algorithms:
                item = QListWidgetItem(algo_name)
                item.setData(Qt.ItemDataRole.UserRole, algo_name)
                self.algorithm_list.addItem(item)
            
            # 显示算法数量
            self.setWindowTitle(f"管理自定义算法 (共 {len(custom_algorithms)} 个算法)")
            
        except Exception as e:
            print(f"加载算法列表错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_add_algorithm(self):
        """添加算法"""
        # 打开文件对话框，选择算法脚本
        default_dir = Path(__file__).parent.parent.parent.parent / "custom_algorithms"
        if not default_dir.exists():
            default_dir = Path(__file__).parent.parent.parent.parent
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择算法脚本", str(default_dir), "Python Files (*.py)"
        )
        
        if file_path:
            try:
                # 导入算法
                from src.algorithms.scheduler import AlgorithmScheduler
                scheduler = AlgorithmScheduler()
                
                # 加载算法
                scheduler._load_custom_algorithms()
                
                # 刷新列表
                self._load_algorithms()
                
                # 发送更新信号
                self.algorithms_updated.emit(file_path)
                
                QMessageBox.information(self, "成功", f"算法已添加: {Path(file_path).name}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加算法失败: {str(e)}")
                print(f"添加算法错误: {e}")
                import traceback
                traceback.print_exc()
    
    def _on_delete_algorithm(self):
        """删除算法"""
        selected_items = self.algorithm_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请选择要删除的算法")
            return
        
        # 获取选中的算法名称
        algo_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除算法 '{algo_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 查找并删除算法文件
                import os
                custom_algorithms_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'custom_algorithms')
                print(f"自定义算法目录: {custom_algorithms_dir}")
                
                file_deleted = False
                if os.path.exists(custom_algorithms_dir):
                    # 查找匹配的文件
                    for file_name in os.listdir(custom_algorithms_dir):
                        if file_name.endswith('.py') and not file_name.startswith('__'):
                            file_path = os.path.join(custom_algorithms_dir, file_name)
                            # 读取文件内容，检查是否包含算法名称
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    # 更灵活的匹配方式
                                    if (f"class {algo_name}" in content or 
                                        f"'name': '{algo_name}'" in content or 
                                        f'"name": "{algo_name}"' in content or
                                        f"self.name = '{algo_name}'" in content or
                                        algo_name in content):
                                        # 删除文件
                                        os.remove(file_path)
                                        print(f"已删除算法文件: {file_path}")
                                        file_deleted = True
                                        break
                            except Exception as e:
                                print(f"读取文件错误: {e}")
                
                if not file_deleted:
                    # 尝试根据文件名直接删除
                    possible_file_names = [
                        f"{algo_name.lower()}.py",
                        f"{algo_name}.py",
                        f"custom{algo_name.lower()}.py"
                    ]
                    
                    for file_name in possible_file_names:
                        file_path = os.path.join(custom_algorithms_dir, file_name)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f"已根据文件名删除算法文件: {file_path}")
                            file_deleted = True
                            break
                
                # 清除所有pycache文件
                import shutil
                pycache_dir = os.path.join(custom_algorithms_dir, '__pycache__')
                if os.path.exists(pycache_dir):
                    shutil.rmtree(pycache_dir)
                    print(f"已删除pycache目录: {pycache_dir}")
                
                # 清除模块缓存
                import sys
                # 清除所有可能的自定义算法模块
                modules_to_remove = []
                for module_name in list(sys.modules.keys()):
                    if (module_name in ['aaaa', 'bbbb', 'cccc', 'CustomAlgorithm', 'CustomAlgorithmTest', 'New', 'newnew', 'newnewnew', 'newnewnewnewnewn', 'ViewRawLFPData'] or 
                        module_name.startswith('customalgorithm') or 
                        module_name.startswith('new') or 
                        module_name.startswith('view_raw') or
                        module_name == algo_name or
                        module_name.endswith('algorithm') or
                        module_name.startswith('src.algorithms') or
                        module_name.startswith('custom_algorithms')):
                        modules_to_remove.append(module_name)
                
                # 清除所有与自定义算法相关的模块
                for module_name in modules_to_remove:
                    if module_name in sys.modules:
                        del sys.modules[module_name]
                        print(f"已从缓存中移除模块: {module_name}")
                
                # 强制重新加载所有相关模块
                modules_to_reload = [
                    'src.algorithms.scheduler',
                    'src.algorithms.base',
                    'src.algorithms.spike_detection',
                    'src.algorithms.lfp_analysis',
                    'src.algorithms.behavior_analysis',
                    'src.algorithms.decoding'
                ]
                
                for module_name in modules_to_reload:
                    if module_name in sys.modules:
                        del sys.modules[module_name]
                        print(f"已从缓存中移除模块: {module_name}")
                
                # 重新加载算法
                from src.algorithms.scheduler import AlgorithmScheduler
                
                # 重新创建调度器并加载算法
                scheduler = AlgorithmScheduler()
                scheduler.register_builtin_algorithms()
                
                # 刷新列表
                self._load_algorithms()
                
                # 发送更新信号
                self.algorithms_updated.emit("")
                
                QMessageBox.information(self, "成功", f"算法已删除: {algo_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除算法失败: {str(e)}")
                print(f"删除算法错误: {e}")
                import traceback
                traceback.print_exc()
