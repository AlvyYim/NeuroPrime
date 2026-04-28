"""
Batch Import Dialog - 批量导入对话框

用于批量导入多个试验数据文件
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import re

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QFormLayout,
    QWidget, QProgressBar, QGroupBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from project.project_manager import ProjectManager
from parsers.ns3_parser import parse_ns3
from parsers.nev_parser import parse_nev
from parsers.mbm_parser import parse_mbm
from data.hdf5_writer import convert_ns3_to_hdf5, convert_nev_to_hdf5


class BatchImportWorker(QThread):
    """批量导入工作线程"""
    
    progress_updated = pyqtSignal(int, str)  # 当前进度, 状态信息
    trial_completed = pyqtSignal(str, bool, str)  # 试验名称, 是否成功, 消息
    batch_completed = pyqtSignal(int, int, list)  # 成功数量, 失败数量, 成功试验信息列表
    
    def __init__(self, trials_to_import: List[Dict], output_dir: str):
        super().__init__()
        self.trials_to_import = trials_to_import
        self.output_dir = output_dir
        self._is_running = True
        self.successful_trials: List[Dict] = []
    
    def run(self):
        """执行批量导入"""
        success_count = 0
        fail_count = 0
        total = len(self.trials_to_import)
        
        for i, trial_info in enumerate(self.trials_to_import):
            if not self._is_running:
                break
            
            trial_name = trial_info['name']
            ns3_file = trial_info['ns3_file']
            nev_file = trial_info['nev_file']
            mbm_file = trial_info.get('mbm_file')
            
            progress = int((i / total) * 100)
            self.progress_updated.emit(progress, f"正在导入: {trial_name} ({i+1}/{total})")
            
            try:
                # 1. 解析NS3文件
                ns3_result = parse_ns3(ns3_file)
                if ns3_result is None:
                    self.trial_completed.emit(trial_name, False, "NS3文件解析失败")
                    fail_count += 1
                    continue
                
                # 2. 解析NEV文件
                nev_result = parse_nev(nev_file)
                if nev_result is None:
                    self.trial_completed.emit(trial_name, False, "NEV文件解析失败")
                    fail_count += 1
                    continue
                
                # 3. 创建HDF5文件
                hdf5_path = Path(self.output_dir) / f"{trial_name}.h5"
                
                success = convert_ns3_to_hdf5(
                    ns3_file,
                    str(hdf5_path),
                    experiment_name="NeuroPrime Experiment",
                    trial_name=trial_name
                )
                
                if not success:
                    self.trial_completed.emit(trial_name, False, "HDF5文件创建失败")
                    fail_count += 1
                    continue
                
                # 4. 添加NEV数据
                success = convert_nev_to_hdf5(nev_file, str(hdf5_path))
                
                if not success:
                    self.trial_completed.emit(trial_name, False, "NEV数据添加失败")
                    fail_count += 1
                    continue
                
                # 5. 解析MBM文件（如果有）
                if mbm_file and Path(mbm_file).exists():
                    mbm_result = parse_mbm(mbm_file)
                    if mbm_result:
                        # TODO: 将MBM数据添加到HDF5
                        pass
                
                # 记录成功导入的试验信息
                successful_trial = {
                    'name': trial_name,
                    'ns3_file': ns3_file,
                    'nev_file': nev_file,
                    'mbm_file': mbm_file,
                    'hdf5_file': str(hdf5_path.name)
                }
                self.successful_trials.append(successful_trial)
                
                self.trial_completed.emit(trial_name, True, "导入成功")
                success_count += 1
                
            except Exception as e:
                self.trial_completed.emit(trial_name, False, f"导入失败: {str(e)}")
                fail_count += 1
        
        self.progress_updated.emit(100, "批量导入完成")
        self.batch_completed.emit(success_count, fail_count, self.successful_trials)
    
    def stop(self):
        """停止导入"""
        self._is_running = False


class BatchImportDialog(QDialog):
    """
    批量导入数据对话框
    
    用于批量导入多个试验数据文件
    """
    
    import_completed = pyqtSignal(list)  # 成功导入的试验名称列表
    
    def __init__(self, parent=None, project_manager: Optional[ProjectManager] = None):
        super().__init__(parent)
        
        self.project_manager = project_manager
        self.worker: Optional[BatchImportWorker] = None
        self.detected_trials: List[Dict] = []
        
        self.setWindowTitle("批量导入试验数据")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 文件夹选择组
        folder_group = QGroupBox("数据文件夹")
        folder_layout = QHBoxLayout(folder_group)
        
        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        self.folder_edit.setPlaceholderText("选择包含数据文件的文件夹")
        folder_layout.addWidget(self.folder_edit)
        
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self._browse_folder)
        folder_layout.addWidget(self.browse_btn)
        
        self.scan_btn = QPushButton("扫描文件")
        self.scan_btn.clicked.connect(self._scan_files)
        self.scan_btn.setEnabled(False)
        folder_layout.addWidget(self.scan_btn)
        
        layout.addWidget(folder_group)
        
        # 试验列表组
        trials_group = QGroupBox("检测到的试验")
        trials_layout = QVBoxLayout(trials_group)
        
        # 试验表格
        self.trials_table = QTableWidget()
        self.trials_table.setColumnCount(5)
        self.trials_table.setHorizontalHeaderLabels([
            "导入", "试验名称", "NS3文件", "NEV文件", "MBM文件"
        ])
        self.trials_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.trials_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.trials_table.setAlternatingRowColors(True)
        trials_layout.addWidget(self.trials_table)
        
        # 全选/取消全选按钮
        select_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self._select_all)
        select_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("取消全选")
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        select_layout.addWidget(self.deselect_all_btn)
        
        select_layout.addStretch()
        trials_layout.addLayout(select_layout)
        
        layout.addWidget(trials_group)
        
        # 选项组
        options_group = QGroupBox("导入选项")
        options_layout = QVBoxLayout(options_group)
        
        self.skip_existing_check = QCheckBox("跳过已存在的试验")
        self.skip_existing_check.setChecked(True)
        options_layout.addWidget(self.skip_existing_check)
        
        self.compress_check = QCheckBox("压缩HDF5文件")
        self.compress_check.setChecked(True)
        options_layout.addWidget(self.compress_check)
        
        layout.addWidget(options_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.import_btn = QPushButton("开始导入")
        self.import_btn.setDefault(True)
        self.import_btn.clicked.connect(self._on_import)
        self.import_btn.setEnabled(False)
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
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
    
    def _browse_folder(self):
        """浏览文件夹"""
        try:
            folder_path = QFileDialog.getExistingDirectory(
                self,
                "选择数据文件夹",
                "",
                QFileDialog.Option.ShowDirsOnly
            )
            
            if folder_path:
                self.folder_edit.setText(folder_path)
                self.scan_btn.setEnabled(True)
                self._scan_files()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"选择文件夹失败: {str(e)}")
    
    def _scan_files(self):
        """扫描文件夹中的试验文件"""
        try:
            folder_path = self.folder_edit.text()
            if not folder_path or not Path(folder_path).exists():
                QMessageBox.warning(self, "警告", "请选择有效的文件夹")
                return
            
            self.detected_trials.clear()
            folder = Path(folder_path)
            
            # 获取已存在的试验名称列表
            existing_trials = set()
            if self.project_manager and self.project_manager.is_project_opened():
                existing_trials = set(self.project_manager.get_trial_names())
            
            # 查找所有NS3文件
            ns3_files = list(folder.glob("*.ns3"))
            
            skipped_count = 0
            for ns3_file in ns3_files:
                base_name = ns3_file.stem
                
                # 检查是否已存在（如果启用了跳过选项）
                if self.skip_existing_check.isChecked() and base_name in existing_trials:
                    skipped_count += 1
                    continue
                
                # 查找配套的NEV和MBM文件
                nev_file = folder / f"{base_name}.nev"
                mbm_file = folder / f"{base_name}.mbm"
                
                # 只添加有NEV文件的试验
                if nev_file.exists():
                    trial_info = {
                        'name': base_name,
                        'ns3_file': str(ns3_file),
                        'nev_file': str(nev_file),
                        'mbm_file': str(mbm_file) if mbm_file.exists() else None
                    }
                    self.detected_trials.append(trial_info)
            
            # 更新表格
            self._update_trials_table()
            
            if self.detected_trials:
                self.import_btn.setEnabled(True)
                status_text = f"检测到 {len(self.detected_trials)} 个试验"
                if skipped_count > 0:
                    status_text += f"（已跳过 {skipped_count} 个已存在试验）"
                self.status_label.setText(status_text)
            else:
                if skipped_count > 0:
                    QMessageBox.information(self, "提示", f"所有试验都已存在，已跳过 {skipped_count} 个试验")
                else:
                    QMessageBox.information(self, "提示", "未检测到有效的试验文件\n\n请确保文件夹中包含配套的.ns3和.nev文件")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"扫描文件失败: {str(e)}")
    
    def _update_trials_table(self):
        """更新试验表格"""
        self.trials_table.setRowCount(len(self.detected_trials))
        
        for i, trial in enumerate(self.detected_trials):
            # 导入复选框
            checkbox = QTableWidgetItem()
            checkbox.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            checkbox.setCheckState(Qt.CheckState.Checked)
            self.trials_table.setItem(i, 0, checkbox)
            
            # 试验名称
            name_item = QTableWidgetItem(trial['name'])
            self.trials_table.setItem(i, 1, name_item)
            
            # NS3文件
            ns3_item = QTableWidgetItem("✓")
            ns3_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.trials_table.setItem(i, 2, ns3_item)
            
            # NEV文件
            nev_item = QTableWidgetItem("✓")
            nev_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.trials_table.setItem(i, 3, nev_item)
            
            # MBM文件
            mbm_text = "✓" if trial['mbm_file'] else "-"
            mbm_item = QTableWidgetItem(mbm_text)
            mbm_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.trials_table.setItem(i, 4, mbm_item)
        
        self.trials_table.resizeColumnsToContents()
    
    def _select_all(self):
        """全选"""
        for i in range(self.trials_table.rowCount()):
            item = self.trials_table.item(i, 0)
            if item:
                item.setCheckState(Qt.CheckState.Checked)
    
    def _deselect_all(self):
        """取消全选"""
        for i in range(self.trials_table.rowCount()):
            item = self.trials_table.item(i, 0)
            if item:
                item.setCheckState(Qt.CheckState.Unchecked)
    
    def _get_selected_trials(self) -> List[Dict]:
        """获取选中的试验列表"""
        selected = []
        for i in range(self.trials_table.rowCount()):
            checkbox_item = self.trials_table.item(i, 0)
            if checkbox_item and checkbox_item.checkState() == Qt.CheckState.Checked:
                selected.append(self.detected_trials[i])
        return selected
    
    def _on_import(self):
        """开始导入"""
        try:
            selected_trials = self._get_selected_trials()
            
            if not selected_trials:
                QMessageBox.warning(self, "警告", "请至少选择一个试验")
                return
            
            # 确定输出目录
            if self.project_manager and self.project_manager.is_project_opened():
                output_dir = self.project_manager.project_path / "data" / "processed"
                # 确保目录存在
                output_dir.mkdir(parents=True, exist_ok=True)
            else:
                output_dir = Path(self.folder_edit.text())
            
            # 禁用按钮
            self.import_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
            self.browse_btn.setEnabled(False)
            self.scan_btn.setEnabled(False)
            
            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            
            # 启动导入线程
            self.worker = BatchImportWorker(selected_trials, str(output_dir))
            self.worker.progress_updated.connect(self._on_progress_updated)
            self.worker.trial_completed.connect(self._on_trial_completed)
            self.worker.batch_completed.connect(self._on_batch_completed)
            self.worker.start()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动导入失败: {str(e)}")
            # 恢复按钮状态
            self.import_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
            self.browse_btn.setEnabled(True)
            self.scan_btn.setEnabled(True)
    
    def _on_progress_updated(self, progress: int, message: str):
        """进度更新"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
    
    def _on_trial_completed(self, trial_name: str, success: bool, message: str):
        """单个试验导入完成"""
        # 更新表格中的状态
        for i in range(self.trials_table.rowCount()):
            name_item = self.trials_table.item(i, 1)
            if name_item and name_item.text() == trial_name:
                status_text = "✓ 成功" if success else f"✗ {message}"
                name_item.setText(f"{trial_name} - {status_text}")
                if not success:
                    name_item.setForeground(Qt.GlobalColor.red)
                break
    
    def _on_batch_completed(self, success_count: int, fail_count: int, successful_trials: list):
        """批量导入完成"""
        try:
            self.import_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
            self.browse_btn.setEnabled(True)
            self.scan_btn.setEnabled(True)
            
            # 等待线程完全结束
            if self.worker:
                self.worker.wait(1000)  # 等待1秒
                self.worker = None
            
            QMessageBox.information(
                self,
                "导入完成",
                f"批量导入完成！\n\n"
                f"成功: {success_count} 个\n"
                f"失败: {fail_count} 个"
            )
            
            # 发射成功导入的试验信息列表
            self.import_completed.emit(successful_trials)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"完成导入处理失败: {str(e)}")
            self.accept()


if __name__ == '__main__':
    # 测试代码
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = BatchImportDialog()
    dialog.import_completed.connect(lambda names: print(f"Imported trials: {names}"))
    dialog.exec()
    
    sys.exit(app.exec())
