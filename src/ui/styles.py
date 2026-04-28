"""
NeuroPrime UI样式定义

提供现代化的UI设计样式，包括颜色方案、排版和布局样式
"""

from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt

# 颜色方案 - 现代科学风格
class Colors:
    # 主色调
    PRIMARY = QColor(52, 152, 219)  # 蓝色
    PRIMARY_DARK = QColor(41, 128, 185)  # 深蓝色
    PRIMARY_LIGHT = QColor(124, 181, 236)  # 浅蓝色
    
    # 辅助色
    SECONDARY = QColor(46, 204, 113)  # 绿色
    SECONDARY_DARK = QColor(39, 174, 96)  # 深绿色
    SECONDARY_LIGHT = QColor(129, 230, 191)  # 浅绿色
    
    # 强调色
    ACCENT = QColor(155, 89, 182)  # 紫色
    
    # 中性色
    BACKGROUND = QColor(245, 247, 250)  # 浅灰背景
    SURFACE = QColor(255, 255, 255)  # 白色表面
    TEXT = QColor(51, 51, 51)  # 深灰文本
    TEXT_LIGHT = QColor(102, 102, 102)  # 浅灰文本
    BORDER = QColor(204, 204, 204)  # 边框颜色
    
    # 状态颜色
    SUCCESS = QColor(46, 204, 113)  # 成功绿色
    WARNING = QColor(241, 196, 15)  # 警告黄色
    ERROR = QColor(231, 76, 60)  # 错误红色
    INFO = QColor(52, 152, 219)  # 信息蓝色

# 字体方案
class Fonts:
    # 标题字体
    TITLE = QFont("Segoe UI", 14, QFont.Weight.Bold)
    SUBTITLE = QFont("Segoe UI", 12, QFont.Weight.Medium)
    
    # 正文字体
    BODY = QFont("Segoe UI", 10, QFont.Weight.Normal)
    
    # 小字体
    SMALL = QFont("Segoe UI", 9, QFont.Weight.Normal)

# 样式表
class Styles:
    # 主窗口样式
    MAIN_WINDOW = """
    QMainWindow {
        background-color: %s;
        font-family: 'Segoe UI';
        font-size: 9pt;
    }
    
    * {
        font-family: 'Segoe UI';
        font-size: 9pt;
    }
    
    QMenuBar, QMenu, QAction {
        font-family: 'Segoe UI';
        font-size: 9pt;
    }
    
    QStatusBar {
        font-family: 'Segoe UI';
        font-size: 8pt;
    }
    
    QTabBar::tab {
        font-family: 'Segoe UI';
        font-size: 9pt;
    }
    
    QToolButton {
        font-family: 'Segoe UI';
        font-size: 9pt;
    }
    
    QGroupBox {
        font-family: 'Segoe UI';
        font-size: 9pt;
    }
    
    QGroupBox::title {
        font-family: 'Segoe UI';
        font-size: 9pt;
    }
    
    QLabel {
        font-family: 'Segoe UI';
        font-size: 9pt;
    }
    
    QPushButton {
        font-family: 'Segoe UI';
        font-size: 9pt;
    }
    
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
        font-family: 'Segoe UI';
        font-size: 9pt;
    }
    """ % Colors.BACKGROUND.name()
    
    # RibbonBar样式
    RIBBON_BAR = """
    QTabWidget::pane {
        border: 1px solid %s;
        background: %s;
    }
    QTabBar::tab {
        padding: 8px 16px;
        margin-right: 2px;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %s, stop:1 %s);
        border: 1px solid %s;
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        font-family: 'Segoe UI';
        font-size: 9pt;
        font-weight: 500;
        color: %s;
        min-width: 80px;
    }
    QTabBar::tab:selected {
        background: %s;
        border-bottom: 2px solid %s;
        color: %s;
        font-weight: 600;
    }
    QTabBar::tab:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f8ff, stop:1 #e0f2fe);
        border: 1px solid %s;
    }
    QTabBar::tab:disabled {
        background: %s;
        color: %s;
    }
    """ % (
        Colors.BORDER.name(),
        Colors.SURFACE.name(),
        Colors.BACKGROUND.name(),
        "#e8f4fd",
        Colors.BORDER.name(),
        Colors.TEXT.name(),
        Colors.SURFACE.name(),
        Colors.PRIMARY.name(),
        Colors.PRIMARY.name(),
        Colors.PRIMARY_LIGHT.name(),
        Colors.BACKGROUND.name(),
        Colors.TEXT_LIGHT.name()
    )
    
    # 工具按钮样式
    TOOL_BUTTON = """
    QToolButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %s, stop:1 #f0f0f0);
        border: 1px solid %s;
        border-radius: 6px;
        padding: 4px 8px;
        font-family: 'Segoe UI';
        font-size: 9pt;
        font-weight: 500;
        color: %s;
        min-width: 80px;
        min-height: 50px;
        max-height: 55px;
    }
    QToolButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f8ff, stop:1 #e0f2fe);
        border: 1px solid %s;
    }
    QToolButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %s, stop:1 %s);
        border: 1px solid %s;
    }
    QToolButton:disabled {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5f5f5, stop:1 #e8e8e8);
        color: %s;
        border: 1px solid %s;
    }
    """ % (
        Colors.SURFACE.name(),
        Colors.BORDER.name(),
        Colors.TEXT.name(),
        Colors.PRIMARY.name(),
        Colors.PRIMARY_LIGHT.name(),
        Colors.PRIMARY_DARK.name(),
        Colors.PRIMARY.name(),
        Colors.TEXT_LIGHT.name(),
        Colors.BORDER.name()
    )
    
    # 分割器样式
    SPLITTER = """
    QSplitter::handle {
        background-color: %s;
        width: 4px;
        height: 4px;
    }
    QSplitter::handle:hover {
        background-color: %s;
    }
    QSplitter::handle:pressed {
        background-color: %s;
    }
    """ % (
        Colors.BORDER.name(),
        Colors.PRIMARY_LIGHT.name(),
        Colors.PRIMARY.name()
    )
    
    # 导航栏样式
    NAVIGATOR = """
    QWidget {
        background-color: %s;
    }
    QTreeWidget {
        background-color: %s;
        border: 1px solid %s;
        border-top: none;
        border-bottom-left-radius: 6px;
        border-bottom-right-radius: 6px;
        font-family: 'Segoe UI';
        font-size: 9pt;
    }
    QTreeWidget::item {
        padding: 4px;
    }
    QTreeWidget::item:hover {
        background-color: %s;
    }
    QTreeWidget::item:selected {
        background-color: %s;
        color: white;
    }
    QTreeWidget::branch {
        background: %s;
    }
    """ % (
        Colors.BACKGROUND.name(),
        Colors.BACKGROUND.name(),
        Colors.BORDER.name(),
        Colors.BACKGROUND.name(),
        Colors.PRIMARY.name(),
        Colors.BACKGROUND.name()
    )
    
    # 参数面板样式
    PARAMETER_PANEL = """
    QWidget {
        background-color: %s;
        font-family: 'Segoe UI';
    }
    QGroupBox {
        font-family: 'Segoe UI';
        font-size: 10pt;
        font-weight: 600;
        color: %s;
        border: 1px solid %s;
        border-radius: 8px;
        margin-top: 15px;
        padding: 10px;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %s, stop:1 %s);
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        top: 0px;
        padding: 0 10px;
        background: %s;
        border-radius: 4px;
        color: %s;
    }
    QLabel {
        font-family: 'Segoe UI';
        font-size: 9pt;
        color: %s;
    }
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
        padding: 6px 8px;
        border: 1px solid %s;
        border-radius: 6px;
        font-family: 'Segoe UI';
        font-size: 9pt;
        background-color: %s;
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
        border: 2px solid %s;
        background-color: white;
    }
    QComboBox QAbstractItemView {
        border: 1px solid %s;
        border-radius: 6px;
        background: white;
        font-family: 'Segoe UI';
        font-size: 9pt;
        color: %s;
    }
    QComboBox QAbstractItemView::item {
        padding: 6px 8px;
    }
    QComboBox QAbstractItemView::item:hover {
        background: %s;
        color: white;
    }
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f0f0f0);
        border: 1px solid %s;
        border-radius: 6px;
        padding: 8px 16px;
        font-family: 'Segoe UI';
        font-size: 9pt;
        font-weight: 500;
        color: %s;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f8ff, stop:1 #e0f2fe);
        border: 1px solid %s;
    }
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e3f2fd, stop:1 #bbdefb);
        border: 1px solid %s;
    }
    QPushButton:disabled {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5f5f5, stop:1 #e8e8e8);
        color: %s;
        border: 1px solid %s;
    }
    QPushButton#runButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %s, stop:1 %s);
        border: 1px solid %s;
        color: white;
        font-weight: 600;
    }
    QPushButton#runButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %s, stop:1 %s);
        border: 1px solid %s;
    }
    QPushButton#runButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %s, stop:1 %s);
        border: 1px solid %s;
    }
    """ % (
        Colors.BACKGROUND.name(),
        Colors.TEXT.name(),
        Colors.BORDER.name(),
        Colors.BACKGROUND.name(),
        "#f0f8ff",
        Colors.BACKGROUND.name(),
        Colors.TEXT.name(),
        Colors.TEXT.name(),
        Colors.BORDER.name(),
        Colors.BACKGROUND.name(),
        Colors.PRIMARY.name(),
        Colors.BORDER.name(),
        Colors.TEXT.name(),
        Colors.PRIMARY.name(),
        Colors.BORDER.name(),
        Colors.TEXT.name(),
        Colors.PRIMARY.name(),
        Colors.BORDER.name(),
        Colors.TEXT.name(),
        Colors.PRIMARY.name(),
        Colors.BORDER.name(),
        Colors.TEXT.name(),
        Colors.BORDER.name(),
        Colors.PRIMARY.name(),
        Colors.PRIMARY.name(),
        Colors.BORDER.name(),
        Colors.SECONDARY.name(),
        Colors.SECONDARY_DARK.name(),
        Colors.SECONDARY.name()
    )
    
    # 可视化区域样式
    VISUALIZATION_AREA = """
    QWidget {
        background-color: %s;
        font-family: 'Segoe UI';
    }
    QTabWidget {
        background-color: %s;
        border: none;
    }
    QTabWidget::pane {
        border: 1px solid %s;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %s, stop:1 #f0f8ff);
        border-radius: 6px;
    }
    QTabBar {
        height: 30px;
    }
    QTabBar::tab {
        padding: 4px 16px;
        margin-right: 2px;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %s, stop:1 #e8f4fd);
        border: 1px solid %s;
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        font-family: 'Segoe UI';
        font-size: 9pt;
        font-weight: 500;
        color: %s;
        min-width: 80px;
        min-height: 28px;
    }
    QTabBar::tab:selected {
        background: %s;
        border-bottom: 2px solid %s;
        color: %s;
        font-weight: 600;
    }
    QTabBar::tab:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f8ff, stop:1 #e0f2fe);
        border: 1px solid %s;
    }
    """ % (
        Colors.BACKGROUND.name(),
        Colors.BACKGROUND.name(),
        Colors.BORDER.name(),
        Colors.BACKGROUND.name(),
        Colors.BACKGROUND.name(),
        Colors.BORDER.name(),
        Colors.TEXT.name(),
        Colors.BACKGROUND.name(),
        Colors.PRIMARY.name(),
        Colors.PRIMARY.name(),
        Colors.PRIMARY_LIGHT.name()
    )
    
    # 状态栏样式
    STATUS_BAR = """
    QStatusBar {
        background-color: %s;
        border-top: 1px solid %s;
        font-family: 'Segoe UI';
        font-size: 8pt;
        color: %s;
    }
    QProgressBar {
        border: 1px solid %s;
        border-radius: 4px;
        background-color: %s;
    }
    QProgressBar::chunk {
        background-color: %s;
    }
    """ % (
        Colors.SURFACE.name(),
        Colors.BORDER.name(),
        Colors.TEXT_LIGHT.name(),
        Colors.BORDER.name(),
        Colors.BACKGROUND.name(),
        Colors.PRIMARY.name()
    )
    
    # 对话框样式
    DIALOG = """
    QDialog {
        background-color: %s;
        font-family: 'Segoe UI';
    }
    QDialogButtonBox QPushButton {
        background-color: %s;
        border: 1px solid %s;
        border-radius: 4px;
        padding: 6px 12px;
        font-family: 'Segoe UI';
        font-size: 9pt;
        font-weight: 500;
        color: %s;
    }
    QDialogButtonBox QPushButton:hover {
        background-color: %s;
        border: 1px solid %s;
    }
    QDialogButtonBox QPushButton:pressed {
        background-color: %s;
    }
    """ % (
        Colors.SURFACE.name(),
        Colors.SURFACE.name(),
        Colors.BORDER.name(),
        Colors.TEXT.name(),
        Colors.BACKGROUND.name(),
        Colors.PRIMARY.name(),
        Colors.PRIMARY_LIGHT.name()
    )
