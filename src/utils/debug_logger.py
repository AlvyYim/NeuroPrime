"""
Debug Logger - 调试日志记录器

用于将调试信息写入文件，解决控制台输出不可见的问题
"""

import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class DebugLogger:
    """调试日志记录器"""
    
    _instance = None
    _log_file = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger()
        return cls._instance
    
    def _init_logger(self):
        """初始化日志记录器"""
        # 日志文件路径 - 放在软件根目录下
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = log_dir / f"debug_{timestamp}.log"
        
        # 打开日志文件
        self._log_file = open(self.log_path, 'w', encoding='utf-8')
        
        # 写入启动信息
        self.log("=" * 60)
        self.log("NeuroPrime 调试日志")
        self.log(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"Python版本: {sys.version}")
        self.log(f"日志文件: {self.log_path}")
        self.log("=" * 60)
    
    def log(self, message: str, level: str = "INFO"):
        """
        记录日志
        
        Args:
            message: 日志消息
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if self._log_file:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log_line = f"[{timestamp}] [{level}] {message}\n"
            self._log_file.write(log_line)
            self._log_file.flush()
    
    def debug(self, message: str):
        """记录DEBUG级别日志"""
        self.log(message, "DEBUG")
    
    def info(self, message: str):
        """记录INFO级别日志"""
        self.log(message, "INFO")
    
    def warning(self, message: str):
        """记录WARNING级别日志"""
        self.log(message, "WARNING")
    
    def error(self, message: str):
        """记录ERROR级别日志"""
        self.log(message, "ERROR")
    
    def exception(self, e: Exception, message: str = ""):
        """
        记录异常信息
        
        Args:
            e: 异常对象
            message: 附加消息
        """
        self.error(f"{message} 异常: {str(e)}")
        self.error("异常堆栈:")
        for line in traceback.format_exc().split('\n'):
            self.error(f"  {line}")
    
    def log_vars(self, **kwargs):
        """
        记录变量值
        
        用法: logger.log_vars(var1=value1, var2=value2)
        """
        for name, value in kwargs.items():
            self.debug(f"{name} = {value} (type: {type(value).__name__})")
    
    def close(self):
        """关闭日志文件"""
        if self._log_file:
            self.log("=" * 60)
            self.log("日志记录结束")
            self.log("=" * 60)
            self._log_file.close()
            self._log_file = None
    
    def __del__(self):
        """析构时关闭日志文件"""
        self.close()


# 全局日志实例
_logger = None

def get_logger() -> DebugLogger:
    """获取日志记录器实例"""
    global _logger
    if _logger is None:
        _logger = DebugLogger()
    return _logger


def log(message: str, level: str = "INFO"):
    """快捷记录日志"""
    get_logger().log(message, level)


def debug(message: str):
    """快捷记录DEBUG日志"""
    get_logger().debug(message)


def info(message: str):
    """快捷记录INFO日志"""
    get_logger().info(message)


def warning(message: str):
    """快捷记录WARNING日志"""
    get_logger().warning(message)


def error(message: str):
    """快捷记录ERROR日志"""
    get_logger().error(message)


def exception(e: Exception, message: str = ""):
    """快捷记录异常"""
    get_logger().exception(e, message)


def log_vars(**kwargs):
    """快捷记录变量"""
    get_logger().log_vars(**kwargs)
