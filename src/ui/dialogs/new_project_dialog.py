"""
New Project Dialog - 新建工程对话框

用于创建新的工程项目
"""

from pathlib import Path
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QFileDialog, QMessageBox,
    QFormLayout, QWidget
)
from PyQt6.QtCore import Qt


class NewProjectDialog(QDialog):
    """
    新建工程对话框
    
    收集工程信息：
    - 工程名称
    - 工程路径
    - 工程描述
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("新建工程")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # 工程名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入工程名称")
        form_layout.addRow("工程名称*:", self.name_edit)
        
        # 工程路径
        path_widget = QWidget()
        path_layout = QHBoxLayout(path_widget)
        path_layout.setContentsMargins(0, 0, 0, 0)
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("选择工程保存路径")
        self.path_edit.setReadOnly(True)
        path_layout.addWidget(self.path_edit)
        
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(self.browse_btn)
        
        form_layout.addRow("工程路径*:", path_widget)
        
        # 工程描述
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("输入工程描述（可选）")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("工程描述:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # 提示信息
        info_label = QLabel("* 为必填项")
        info_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.ok_btn = QPushButton("确定")
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self._on_ok)
        btn_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLineEdit, QTextEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #0078d4;
            }
            QPushButton {
                padding: 6px 16px;
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
    
    def _browse_path(self):
        """浏览路径"""
        # 获取软件根目录
        default_path = Path(__file__).parent.parent.parent.parent
        
        path = QFileDialog.getExistingDirectory(
            self,
            "选择工程保存路径",
            str(default_path)
        )
        
        if path:
            self.path_edit.setText(path)
    
    def _on_ok(self):
        """确定按钮点击"""
        # 验证输入
        name = self.name_edit.text().strip()
        path = self.path_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "警告", "请输入工程名称")
            return
        
        if not path:
            QMessageBox.warning(self, "警告", "请选择工程路径")
            return
        
        # 检查路径是否存在
        if not Path(path).exists():
            QMessageBox.warning(self, "警告", "所选路径不存在")
            return
        
        # 检查工程文件夹是否已存在
        project_path = Path(path) / name
        if project_path.exists():
            reply = QMessageBox.question(
                self,
                "确认",
                f"工程文件夹 '{name}' 已存在，是否覆盖？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.accept()
    
    def get_project_info(self) -> Dict[str, Any]:
        """
        获取工程信息
        
        Returns:
            工程信息字典
        """
        return {
            'name': self.name_edit.text().strip(),
            'path': self.path_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip()
        }


if __name__ == '__main__':
    # 测试代码
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = NewProjectDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        print(f"Project info: {dialog.get_project_info()}")
    
    sys.exit(app.exec())
