"""
Navigator - 左侧导航栏组件

树形结构显示工程/试验/数据层次结构
"""

from typing import Dict, Any, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QMenu, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

# 导入样式
from .styles import Styles

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from project.project_manager import ProjectManager


class Navigator(QWidget):
    """
    导航栏组件
    
    树形结构显示：
    - 工程
      - 试验1
        - 信号数据
        - Spike数据
        - 行为数据
      - 试验2
        ...
    """
    
    item_selected = pyqtSignal(str, dict)  # item_type, item_data
    item_double_clicked = pyqtSignal(str, dict)  # item_type, item_data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.project_manager: Optional[ProjectManager] = None
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # 标题
        title_label = QLabel("Data Browser")
        title_label.setStyleSheet("""
            QLabel {
                font-family: 'Segoe UI';
                font-size: 9pt;
                font-weight: 600;
                padding: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5f7fa, stop:1 #f0f8ff);
                border: 1px solid #e0e0e0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: #333333;
            }
        """)
        layout.addWidget(title_label)
        
        # 树形控件
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # 连接信号
        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        self.tree_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree_widget.customContextMenuRequested.connect(self._on_context_menu)
        
        layout.addWidget(self.tree_widget)
        
        # 应用样式
        self.setStyleSheet(Styles.NAVIGATOR)
        
        self.setMinimumWidth(250)
        self.setMaximumWidth(400)
    
    def set_project_manager(self, project_manager: ProjectManager):
        """设置工程管理器并刷新显示"""
        self.project_manager = project_manager
        self.refresh_tree()
    
    def refresh_tree(self):
        """刷新树形结构"""
        self.tree_widget.clear()
        
        if self.project_manager is None or not self.project_manager.is_project_opened():
            # 显示提示信息
            root = QTreeWidgetItem(self.tree_widget)
            root.setText(0, "No Project Open")
            root.setFlags(root.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            return
        
        # 工程节点
        config = self.project_manager.config
        project_item = QTreeWidgetItem(self.tree_widget)
        project_item.setText(0, config.name)
        project_item.setData(0, Qt.ItemDataRole.UserRole, {
            'type': 'project',
            'name': config.name,
            'path': str(self.project_manager.project_path)
        })
        
        # 试验节点
        for trial in config.trials:
            trial_item = QTreeWidgetItem(project_item)
            trial_item.setText(0, trial.name)
            trial_item.setData(0, Qt.ItemDataRole.UserRole, {
                'type': 'trial',
                'name': trial.name
            })
            
            # 数据类型子节点
            data_types = [
                ('LFP Data', 'signals'),
                ('Spike Data', 'spikes'),
                ('Behavior Data', 'behavior')
            ]
            
            for data_name, data_type in data_types:
                data_item = QTreeWidgetItem(trial_item)
                data_item.setText(0, data_name)
                data_item.setData(0, Qt.ItemDataRole.UserRole, {
                    'type': 'data_category',
                    'trial': trial.name,
                    'category': data_type
                })
        
        # 展开工程节点
        project_item.setExpanded(True)
    
    def refresh_project(self, project_manager: ProjectManager):
        """刷新工程显示（外部调用）"""
        self.set_project_manager(project_manager)
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """处理项目点击"""
        # 切换项目的展开/折叠状态
        item.setExpanded(not item.isExpanded())
        
        # 仍然发送选择信号，以保持其他功能的兼容性
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            item_type = data.get('type', 'unknown')
            self.item_selected.emit(item_type, data)
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """处理项目双击"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            item_type = data.get('type', 'unknown')
            self.item_double_clicked.emit(item_type, data)
    
    def _on_context_menu(self, position):
        """显示右键菜单"""
        try:
            item = self.tree_widget.itemAt(position)
            if item is None:
                return
            
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data is None:
                return
            
            item_type = data.get('type')
            
            menu = QMenu(self)
            
            if item_type == 'project':
                # 工程菜单
                import_action = QAction("Import Trial", self)
                import_action.triggered.connect(lambda: self._import_trial())
                menu.addAction(import_action)
                
                menu.addSeparator()
                
                properties_action = QAction("Project Properties", self)
                properties_action.triggered.connect(lambda: self._show_project_properties())
                menu.addAction(properties_action)
            
            elif item_type == 'trial':
                # 试验菜单
                view_action = QAction("View Data", self)
                view_action.triggered.connect(lambda: self._view_trial_data(data))
                menu.addAction(view_action)
                
                menu.addSeparator()
                
                delete_action = QAction("Delete Trial", self)
                delete_action.triggered.connect(lambda: self._delete_trial(data))
                menu.addAction(delete_action)
            
            elif item_type == 'data_category':
                # 数据类别菜单
                view_action = QAction("View", self)
                view_action.triggered.connect(lambda: self._view_data_category(data))
                menu.addAction(view_action)
                
                menu.addSeparator()
                
                delete_action = QAction("Delete Data", self)
                delete_action.triggered.connect(lambda: self._delete_data_category(data))
                menu.addAction(delete_action)
            
            menu.exec(self.tree_widget.viewport().mapToGlobal(position))
        except Exception as e:
            print(f"Context menu error: {e}")
            import traceback
            traceback.print_exc()
    
    def _import_trial(self):
        """导入试验"""
        # 触发信号，由主窗口处理
        self.item_selected.emit('import_trial', {})
    
    def _show_project_properties(self):
        """显示工程属性"""
        if self.project_manager and self.project_manager.is_project_opened():
            config = self.project_manager.config
            QMessageBox.information(
                self,
                "Project Properties",
                f"Project Name: {config.name}\n"
                f"Project Path: {str(self.project_manager.project_path)}\n"
                f"Creation Time: {config.creation_time}\n"
                f"Number of Trials: {len(config.trials)}"
            )
    
    def _view_trial_data(self, data: dict):
        """查看试验数据"""
        trial_name = data.get('name')
        if trial_name:
            self.item_selected.emit('trial', data)
    
    def _delete_trial(self, data: dict):
        """删除试验"""
        trial_name = data.get('name')
        if not trial_name:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete trial '{trial_name}'?\nThis action will delete all data for this trial and cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.project_manager:
                success = self.project_manager.remove_trial(trial_name)
                if success:
                    self.refresh_tree()
                    QMessageBox.information(self, "成功", f"试验 '{trial_name}' 已删除")
                else:
                    QMessageBox.warning(self, "错误", f"删除试验 '{trial_name}' 失败")
            else:
                QMessageBox.warning(self, "错误", "未打开工程")
    
    def _view_data_category(self, data: dict):
        """查看数据类别"""
        self.item_selected.emit('data_category', data)
    
    def _delete_data_category(self, data: dict):
        """删除数据类别"""
        trial_name = data.get('trial')
        category = data.get('category')
        
        if not trial_name or not category:
            return
        
        # 将category映射为中文名称
        category_names = {
            'signals': 'LFP数据',
            'spikes': 'Spike数据',
            'behavior': '行为数据'
        }
        category_name = category_names.get(category, category)
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除试验 '{trial_name}' 的 {category_name} 吗？\n此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.project_manager:
                success = self.project_manager.remove_trial_data(trial_name, category)
                if success:
                    self.refresh_tree()
                    QMessageBox.information(self, "成功", f"{category_name} 已删除")
                else:
                    QMessageBox.warning(self, "错误", f"删除 {category_name} 失败")
            else:
                QMessageBox.warning(self, "错误", "未打开工程")
    
    def get_selected_item(self) -> Optional[Dict[str, Any]]:
        """获取当前选中的项目"""
        item = self.tree_widget.currentItem()
        if item:
            return item.data(0, Qt.ItemDataRole.UserRole)
        return None
    
    def select_trial(self, trial_name: str):
        """选中指定试验"""
        # 遍历查找试验节点
        root = self.tree_widget.topLevelItem(0)
        if root:
            for i in range(root.childCount()):
                trial_item = root.child(i)
                data = trial_item.data(0, Qt.ItemDataRole.UserRole)
                if data and data.get('name') == trial_name:
                    self.tree_widget.setCurrentItem(trial_item)
                    break


if __name__ == '__main__':
    # 测试代码
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    navigator = Navigator()
    navigator.item_selected.connect(lambda t, d: print(f"Selected: {t}, {d}"))
    navigator.show()
    
    sys.exit(app.exec())
