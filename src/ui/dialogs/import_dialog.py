"""
Import Dialog - 导入数据对话框

用于导入试验数据文件
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import re

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QFormLayout,
    QWidget, QProgressBar, QGroupBox, QCheckBox,
    QComboBox, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from project.project_manager import ProjectManager
from parsers.ns3_parser import parse_ns3
from parsers.nev_parser import parse_nev
from parsers.mbm_parser import parse_mbm
from data.hdf5_writer import convert_ns3_to_hdf5, convert_nev_to_hdf5


class ImportWorker(QThread):
    """导入工作线程"""
    
    progress_updated = pyqtSignal(int, str)  # 进度百分比, 状态信息
    import_completed = pyqtSignal(bool, str)  # 是否成功, 消息
    
    def __init__(self, ns3_file: str, nev_file: str, mbm_file: Optional[str],
                 output_dir: str, trial_name: str):
        super().__init__()
        
        self.ns3_file = ns3_file
        self.nev_file = nev_file
        self.mbm_file = mbm_file
        self.output_dir = output_dir
        self.trial_name = trial_name
    
    def run(self):
        """执行导入"""
        try:
            print(f"ImportWorker: Starting import for {self.trial_name}")
            
            # 1. 解析NS3文件
            self.progress_updated.emit(10, "解析NS3文件...")
            print(f"ImportWorker: Parsing NS3 file: {self.ns3_file}")
            ns3_result = parse_ns3(self.ns3_file)
            if ns3_result is None:
                print("ImportWorker: NS3 parsing failed")
                self.import_completed.emit(False, "NS3文件解析失败")
                return
            print(f"ImportWorker: NS3 parsing successful")
            
            # 2. 解析NEV文件
            self.progress_updated.emit(30, "解析NEV文件...")
            print(f"ImportWorker: Parsing NEV file: {self.nev_file}")
            nev_result = parse_nev(self.nev_file)
            if nev_result is None:
                print("ImportWorker: NEV parsing failed")
                self.import_completed.emit(False, "NEV文件解析失败")
                return
            print(f"ImportWorker: NEV parsing successful")
            
            # 3. 创建HDF5文件
            self.progress_updated.emit(50, "创建HDF5文件...")
            hdf5_path = Path(self.output_dir) / f"{self.trial_name}.h5"
            print(f"ImportWorker: Creating HDF5 file: {hdf5_path}")
            
            success = convert_ns3_to_hdf5(
                self.ns3_file,
                str(hdf5_path),
                experiment_name="NeuroPrime Experiment",
                trial_name=self.trial_name
            )
            
            if not success:
                print("ImportWorker: HDF5 creation failed")
                self.import_completed.emit(False, "HDF5文件创建失败")
                return
            print(f"ImportWorker: HDF5 creation successful")
            
            # 4. 添加NEV数据
            self.progress_updated.emit(70, "添加Spike数据...")
            print(f"ImportWorker: Adding NEV data to HDF5")
            # 自动查找同名的.log文件
            log_file = Path(self.nev_file).with_suffix('.log')
            log_file_str = str(log_file) if log_file.exists() else None
            success = convert_nev_to_hdf5(self.nev_file, str(hdf5_path), log_file_str)
            
            if not success:
                print("ImportWorker: NEV conversion failed")
                self.import_completed.emit(False, "NEV数据添加失败")
                return
            print(f"ImportWorker: NEV conversion successful")
            
            # 5. 解析MBM文件（如果有）
            if self.mbm_file and Path(self.mbm_file).exists():
                self.progress_updated.emit(85, "解析行为数据...")
                print(f"ImportWorker: Parsing MBM file: {self.mbm_file}")
                mbm_result = parse_mbm(self.mbm_file)
                if mbm_result:
                    # TODO: 将MBM数据添加到HDF5
                    pass
            
            self.progress_updated.emit(100, "导入完成")
            print(f"ImportWorker: Import completed successfully")
            self.import_completed.emit(True, self.trial_name)
        
        except Exception as e:
            import traceback
            error_msg = f"导入失败: {str(e)}"
            print(f"ImportWorker ERROR: {error_msg}")
            traceback.print_exc()
            self.import_completed.emit(False, error_msg)


class ImportDialog(QDialog):
    """
    导入数据对话框
    
    用于导入试验数据文件（.ns3, .nev, .mbm）
    """
    
    import_completed = pyqtSignal(str)  # trial_name
    
    def __init__(self, parent=None, project_manager: Optional[ProjectManager] = None):
        super().__init__(parent)
        
        self.project_manager = project_manager
        self.worker: Optional[ImportWorker] = None
        
        self.setWindowTitle("导入试验数据")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 文件选择组
        file_group = QGroupBox("数据文件")
        file_layout = QFormLayout(file_group)
        
        # NS3文件
        ns3_widget = self._create_file_selector("选择NS3文件", "ns3")
        file_layout.addRow("NS3文件*:", ns3_widget)
        
        # NEV文件
        nev_widget = self._create_file_selector("选择NEV文件", "nev")
        file_layout.addRow("NEV文件*:", nev_widget)
        
        # MBM文件
        mbm_widget = self._create_file_selector("选择MBM文件（可选）", "mbm", optional=True)
        file_layout.addRow("MBM文件:", mbm_widget)
        
        layout.addWidget(file_group)
        
        # 试验信息组
        info_group = QGroupBox("试验信息")
        info_layout = QFormLayout(info_group)
        
        # 试验名称
        self.trial_name_edit = QLineEdit()
        self.trial_name_edit.setPlaceholderText("输入试验名称")
        info_layout.addRow("试验名称*:", self.trial_name_edit)
        
        # 试验描述
        self.trial_desc_edit = QTextEdit()
        self.trial_desc_edit.setPlaceholderText("输入试验描述（可选）")
        self.trial_desc_edit.setMaximumHeight(80)
        info_layout.addRow("试验描述:", self.trial_desc_edit)
        
        layout.addWidget(info_group)
        
        # 选项组
        options_group = QGroupBox("导入选项")
        options_layout = QVBoxLayout(options_group)
        
        self.auto_detect_check = QCheckBox("自动检测配套文件")
        self.auto_detect_check.setChecked(True)
        self.auto_detect_check.stateChanged.connect(self._on_auto_detect_changed)
        options_layout.addWidget(self.auto_detect_check)
        
        layout.addWidget(options_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.import_btn = QPushButton("导入")
        self.import_btn.setDefault(True)
        self.import_btn.clicked.connect(self._on_import)
        btn_layout.addWidget(self.import_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLineEdit, QTextEdit, QComboBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
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
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
    
    def _create_file_selector(self, title: str, file_type: str, optional: bool = False) -> QWidget:
        """创建文件选择器"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        line_edit = QLineEdit()
        line_edit.setReadOnly(True)
        line_edit.setObjectName(f"{file_type}_edit")
        layout.addWidget(line_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(lambda: self._browse_file(file_type, title))
        layout.addWidget(browse_btn)
        
        return widget
    
    def _browse_file(self, file_type: str, title: str):
        """浏览文件"""
        filters = {
            "ns3": "NS3文件 (*.ns3)",
            "nev": "NEV文件 (*.nev)",
            "mbm": "MBM文件 (*.mbm)"
        }
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            title,
            "",
            filters.get(file_type, "所有文件 (*)")
        )
        
        if file_path:
            # 更新对应的line edit
            edit = self.findChild(QLineEdit, f"{file_type}_edit")
            if edit:
                edit.setText(file_path)
            
            # 自动检测配套文件
            if self.auto_detect_check.isChecked():
                self._auto_detect_files(file_path, file_type)
            
            # 自动填充试验名称
            if file_type == "ns3":
                self._auto_fill_trial_name(file_path)
    
    def _auto_detect_files(self, selected_file: str, file_type: str):
        """自动检测配套文件"""
        selected_path = Path(selected_file)
        base_name = selected_path.stem
        parent_dir = selected_path.parent
        
        # 检测其他文件
        for ext in ["ns3", "nev", "mbm"]:
            if ext != file_type:
                potential_file = parent_dir / f"{base_name}.{ext}"
                if potential_file.exists():
                    edit = self.findChild(QLineEdit, f"{ext}_edit")
                    if edit and not edit.text():
                        edit.setText(str(potential_file))
    
    def _auto_fill_trial_name(self, ns3_file: str):
        """自动填充试验名称"""
        if not self.trial_name_edit.text():
            base_name = Path(ns3_file).stem
            self.trial_name_edit.setText(base_name)
    
    def _on_auto_detect_changed(self, state):
        """自动检测选项改变"""
        # 如果启用，尝试检测文件
        if state == Qt.CheckState.Checked.value:
            ns3_edit = self.findChild(QLineEdit, "ns3_edit")
            if ns3_edit and ns3_edit.text():
                self._auto_detect_files(ns3_edit.text(), "ns3")
    
    def _on_import(self):
        """导入按钮点击"""
        # 获取文件路径
        ns3_edit = self.findChild(QLineEdit, "ns3_edit")
        nev_edit = self.findChild(QLineEdit, "nev_edit")
        mbm_edit = self.findChild(QLineEdit, "mbm_edit")
        
        ns3_file = ns3_edit.text() if ns3_edit else ""
        nev_file = nev_edit.text() if nev_edit else ""
        mbm_file = mbm_edit.text() if mbm_edit else None
        
        # 验证输入
        if not ns3_file:
            QMessageBox.warning(self, "警告", "请选择NS3文件")
            return
        
        if not nev_file:
            QMessageBox.warning(self, "警告", "请选择NEV文件")
            return
        
        trial_name = self.trial_name_edit.text().strip()
        if not trial_name:
            QMessageBox.warning(self, "警告", "请输入试验名称")
            return
        
        # 检查文件是否存在
        if not Path(ns3_file).exists():
            QMessageBox.warning(self, "警告", "NS3文件不存在")
            return
        
        if not Path(nev_file).exists():
            QMessageBox.warning(self, "警告", "NEV文件不存在")
            return
        
        # 确定输出目录
        if self.project_manager and self.project_manager.is_project_opened():
            output_dir = str(self.project_manager.project_path / "data" / "processed")
        else:
            output_dir = str(Path(ns3_file).parent)
        
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        print(f"ImportDialog: Output directory: {output_dir}")
        
        # 禁用按钮
        self.import_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        # 启动导入线程
        self.worker = ImportWorker(
            ns3_file, nev_file, mbm_file,
            output_dir, trial_name
        )
        self.worker.progress_updated.connect(self._on_progress_updated)
        self.worker.import_completed.connect(self._on_import_completed)
        self.worker.start()
    
    def _on_progress_updated(self, progress: int, message: str):
        """进度更新"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
    
    def _on_import_completed(self, success: bool, message: str):
        """导入完成"""
        self.import_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "成功", f"试验 '{message}' 导入成功")
            self.import_completed.emit(message)
            self.accept()
        else:
            QMessageBox.critical(self, "错误", message)
            self.progress_bar.setVisible(False)
            self.status_label.setText("")


if __name__ == '__main__':
    # 测试代码
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = ImportDialog()
    dialog.import_completed.connect(lambda name: print(f"Imported: {name}"))
    dialog.exec()
    
    sys.exit(app.exec())
