"""
Time Alignment Dialog - 时间对齐对话框

用于配置多数据项的时间对齐参数
支持从真实数据读取时间范围
"""

from pathlib import Path
from typing import Dict, Any, Optional, List

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QFormLayout, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from visualization.time_alignment import TimeAlignmentConfig


class TimeAlignmentDialog(QDialog):
    """
    时间对齐对话框
    
    功能：
    - 显示各数据项的原始时间范围（从真实数据读取）
    - 编辑初始时间和持续时间
    - 自动同步功能
    """
    
    def __init__(self, parent=None, data_items: Optional[List[Dict[str, Any]]] = None):
        """
        初始化时间对齐对话框
        
        Args:
            parent: 父窗口
            data_items: 数据项列表，每个数据项包含id, name, trial_name, time_range等信息
        """
        super().__init__(parent)
        
        self.data_items = data_items or []
        self.alignment_config = TimeAlignmentConfig()
        
        self.setWindowTitle("时间对齐")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        self._init_ui()
        self._populate_data_items()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 说明标签
        info_label = QLabel(
            "配置各数据项的时间对齐参数。修改初始时间或持续时间后，"
            "其他数据项将自动同步（使用全局对齐模式）。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(info_label)
        
        # 数据项表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "试验", "数据项", "原始起始(s)", "原始结束(s)", "对齐起始(s)", "持续时间(s)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        
        # 连接单元格编辑信号
        self.table.cellChanged.connect(self._on_cell_changed)
        
        layout.addWidget(self.table)
        
        # 全局设置组
        global_group = QGroupBox("全局设置")
        global_layout = QFormLayout(global_group)
        
        self.global_start_edit = QLineEdit("0.0")
        self.global_start_edit.setPlaceholderText("全局起始时间（秒）")
        global_layout.addRow("全局起始时间:", self.global_start_edit)
        
        self.global_duration_edit = QLineEdit("10.0")
        self.global_duration_edit.setPlaceholderText("全局持续时间（秒）")
        global_layout.addRow("全局持续时间:", self.global_duration_edit)
        
        # 按钮行 - 应用到所有 和 最长时间对齐
        btn_layout = QHBoxLayout()
        
        self.apply_global_btn = QPushButton("应用到所有")
        self.apply_global_btn.setFixedWidth(100)
        self.apply_global_btn.clicked.connect(self._apply_global_settings)
        btn_layout.addWidget(self.apply_global_btn)
        
        self.suggest_btn = QPushButton("最长时间对齐")
        self.suggest_btn.setToolTip("使用所有数据项的共同时间范围（最长时间）")
        self.suggest_btn.setFixedWidth(100)
        self.suggest_btn.clicked.connect(self._apply_suggested_alignment)
        btn_layout.addWidget(self.suggest_btn)
        
        btn_layout.addStretch()
        global_layout.addRow(btn_layout)
        
        layout.addWidget(global_group)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 按钮
        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.addStretch()
        
        self.ok_btn = QPushButton("确定")
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self._on_ok)
        bottom_btn_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        bottom_btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(bottom_btn_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLineEdit {
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
            QTableWidget {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #e5f3ff;
                color: black;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
    
    def _populate_data_items(self):
        """填充数据项 - 从真实数据读取时间范围"""
        if not self.data_items:
            # 没有数据项时显示提示
            self.table.setRowCount(1)
            item = QTableWidgetItem("请先选择数据项")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(0, 0, item)
            self.status_label.setText("请先选择数据项")
            self.status_label.setStyleSheet("color: orange;")
            return
        
        self.table.setRowCount(len(self.data_items))
        
        # 计算所有数据项的共同时间范围
        all_starts = []
        all_ends = []
        
        for i, item in enumerate(self.data_items):
            # 确保item是字典类型
            if not isinstance(item, dict):
                print(f"警告: time_alignment_dialog中包含非字典类型: {type(item)}")
                continue
            
            # 获取数据项信息
            trial_name = item.get('trial_name', 'Unknown')
            data_id = item.get('id', '')
            display_name = item.get('display_name', data_id)
            time_range = item.get('time_range', None)
            
            # 解析时间范围
            if time_range and isinstance(time_range, (list, tuple)) and len(time_range) >= 2:
                start_time = float(time_range[0])
                end_time = float(time_range[1])
            else:
                # 没有时间范围信息，使用默认值
                start_time = 0.0
                end_time = 0.0
            
            all_starts.append(start_time)
            all_ends.append(end_time)
            
            # 试验名称
            trial_item = QTableWidgetItem(trial_name)
            trial_item.setFlags(trial_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            trial_item.setData(Qt.ItemDataRole.UserRole, data_id)
            self.table.setItem(i, 0, trial_item)
            
            # 数据项名称
            name_item = QTableWidgetItem(display_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, name_item)
            
            # 原始起始
            start_item = QTableWidgetItem(f"{start_time:.3f}")
            start_item.setFlags(start_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, start_item)
            
            # 原始结束
            end_item = QTableWidgetItem(f"{end_time:.3f}")
            end_item.setFlags(end_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, end_item)
            
            # 对齐起始（可编辑，默认为原始起始）
            align_start_item = QTableWidgetItem(f"{start_time:.3f}")
            self.table.setItem(i, 4, align_start_item)
            
            # 持续时间（可编辑，默认为原始持续时间）
            duration = end_time - start_time
            duration_item = QTableWidgetItem(f"{duration:.3f}")
            self.table.setItem(i, 5, duration_item)
            
            # 添加到配置
            self.alignment_config.add_data_item(
                data_id,
                (start_time, end_time)
            )
        
        # 计算并显示建议的全局时间范围
        if all_starts and all_ends:
            # 计算最长时间范围（并集）
            min_start = min(all_starts)
            max_end = max(all_ends)
            max_duration = max_end - min_start
            
            # 计算共同时间范围（交集）
            max_start = max(all_starts)
            min_end = min(all_ends)
            common_duration = max(0, min_end - max_start)
            
            # 使用最长时间范围作为默认值
            if max_duration > 0:
                self.global_start_edit.setText(f"{min_start:.3f}")
                self.global_duration_edit.setText(f"{max_duration:.3f}")
                
                if common_duration > 0:
                    self.status_label.setText(
                        f"检测到 {len(self.data_items)} 个数据项，"
                        f"最长时间范围: {min_start:.3f}s - {max_end:.3f}s ({max_duration:.3f}s)，"
                        f"共同时间范围: {max_start:.3f}s - {min_end:.3f}s ({common_duration:.3f}s)"
                    )
                else:
                    self.status_label.setText(
                        f"检测到 {len(self.data_items)} 个数据项，"
                        f"最长时间范围: {min_start:.3f}s - {max_end:.3f}s ({max_duration:.3f}s)，"
                        f"时间范围无重叠"
                    )
                self.status_label.setStyleSheet("color: green;")
            else:
                self.status_label.setText(f"检测到 {len(self.data_items)} 个数据项，时间范围无效")
                self.status_label.setStyleSheet("color: orange;")
    
    def _on_cell_changed(self, row: int, column: int):
        """单元格内容改变"""
        # 只处理对齐起始和持续时间列
        if column not in [4, 5]:
            return
        
        # 获取数据项ID
        trial_item = self.table.item(row, 0)
        if not trial_item:
            return
        
        data_id = trial_item.data(Qt.ItemDataRole.UserRole)
        
        try:
            # 确保单元格存在
            start_item = self.table.item(row, 4)
            duration_item = self.table.item(row, 5)
            
            if not start_item or not duration_item:
                return
            
            start_value = float(start_item.text())
            duration_value = float(duration_item.text())
            
            self.alignment_config.set_individual_time_window(
                data_id, start_value, duration_value
            )
            
            # 验证对齐
            self._validate_alignment()
        
        except ValueError:
            self.status_label.setText("请输入有效的数字")
            self.status_label.setStyleSheet("color: red;")
    
    def _validate_alignment(self):
        """验证对齐配置"""
        is_valid, error_msg = self.alignment_config.validate_alignment()
        
        if is_valid:
            self.status_label.setText("")
            return True
        else:
            self.status_label.setText(f"✗ {error_msg}")
            self.status_label.setStyleSheet("color: red;")
            return False
    
    def _apply_global_settings(self):
        """应用全局设置"""
        try:
            global_start = float(self.global_start_edit.text())
            global_duration = float(self.global_duration_edit.text())
            
            # 更新配置
            self.alignment_config.set_global_time_window(global_start, global_duration)
            
            # 更新表格
            for row in range(self.table.rowCount()):
                # 对齐起始
                self.table.item(row, 4).setText(f"{global_start:.3f}")
                # 持续时间
                self.table.item(row, 5).setText(f"{global_duration:.3f}")
            
            # 验证
            self._validate_alignment()
        
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的数字")
    
    def _apply_suggested_alignment(self):
        """应用建议的对齐"""
        start, duration = self.alignment_config.suggest_alignment()
        
        # 更新全局设置
        self.global_start_edit.setText(f"{start:.3f}")
        self.global_duration_edit.setText(f"{duration:.3f}")
        
        # 应用
        self._apply_global_settings()
    
    def _on_ok(self):
        """确定按钮点击"""
        # 验证对齐
        if not self._validate_alignment():
            reply = QMessageBox.question(
                self,
                "确认",
                "对齐配置无效，是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # 显示成功提示
        QMessageBox.information(
            self,
            "时间对齐配置",
            "时间对齐配置已生效！\n\n"
            f"全局起始时间: {self.global_start_edit.text()} 秒\n"
            f"全局持续时间: {self.global_duration_edit.text()} 秒\n\n"
            "配置已应用到所有选中的数据项。"
        )
        
        self.accept()
    
    def get_alignment_config(self) -> TimeAlignmentConfig:
        """
        获取时间对齐配置
        
        Returns:
            TimeAlignmentConfig对象
        """
        return self.alignment_config


if __name__ == '__main__':
    # 测试代码
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 测试数据
    test_data = [
        {
            'id': 'trial1_lfp',
            'display_name': 'LFP Channel 1',
            'trial_name': 'Trial_001',
            'time_range': [0.0, 120.5]
        },
        {
            'id': 'trial1_spike',
            'display_name': 'Spike Unit 1',
            'trial_name': 'Trial_001',
            'time_range': [0.0, 120.5]
        },
        {
            'id': 'trial2_lfp',
            'display_name': 'LFP Channel 1',
            'trial_name': 'Trial_002',
            'time_range': [5.2, 95.8]
        },
    ]
    
    dialog = TimeAlignmentDialog(data_items=test_data)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        config = dialog.get_alignment_config()
        print(f"Alignment config: {config.to_dict()}")
    
    sys.exit(app.exec())
