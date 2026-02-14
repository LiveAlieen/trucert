"""日志工具模块

提供集中式日志配置和管理功能，包括创建日志目录、配置日志格式和级别等
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional, Dict, Any


class LogManager:
    """日志管理器类，提供集中式日志管理功能"""
    
    def __init__(self):
        """初始化日志管理器"""
        self.loggers = {}
        self.default_config = {
            "log_dir": None,
            "log_level": logging.DEBUG,
            "console_level": logging.INFO,
            "file_level": logging.DEBUG,
            "max_bytes": 10 * 1024 * 1024,  # 10MB
            "backup_count": 5,
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    
    def _get_default_log_dir(self) -> str:
        """获取默认日志目录"""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    
    def setup_logger(self, name: str = "cert_manager", config: Optional[Dict[str, Any]] = None) -> logging.Logger:
        """设置日志记录器
        
        Args:
            name: 日志记录器名称
            config: 日志配置字典
        
        Returns:
            配置好的日志记录器
        """
        # 合并配置
        merged_config = self.default_config.copy()
        if config:
            merged_config.update(config)
        
        # 获取日志目录
        log_dir = merged_config["log_dir"] or self._get_default_log_dir()
        
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志文件路径
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")
        
        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(merged_config["log_level"])
        
        # 避免重复添加处理器
        if not logger.handlers:
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(merged_config["console_level"])
            
            # 创建文件处理器，使用轮转日志
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=merged_config["max_bytes"],
                backupCount=merged_config["backup_count"]
            )
            file_handler.setLevel(merged_config["file_level"])
            
            # 创建日志格式
            formatter = logging.Formatter(merged_config["log_format"])
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            # 添加处理器到日志记录器
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
        
        # 保存日志记录器
        self.loggers[name] = logger
        
        return logger
    
    def get_logger(self, name: str = "cert_manager") -> logging.Logger:
        """获取日志记录器
        
        Args:
            name: 日志记录器名称
        
        Returns:
            日志记录器
        """
        if name not in self.loggers:
            self.setup_logger(name)
        return self.loggers[name]
    
    def set_log_level(self, name: str, level: int) -> None:
        """设置日志级别
        
        Args:
            name: 日志记录器名称
            level: 日志级别
        """
        logger = self.get_logger(name)
        logger.setLevel(level)
    
    def set_console_level(self, name: str, level: int) -> None:
        """设置控制台日志级别
        
        Args:
            name: 日志记录器名称
            level: 日志级别
        """
        logger = self.get_logger(name)
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(level)
    
    def set_file_level(self, name: str, level: int) -> None:
        """设置文件日志级别
        
        Args:
            name: 日志记录器名称
            level: 日志级别
        """
        logger = self.get_logger(name)
        for handler in logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                handler.setLevel(level)
    
    def get_all_loggers(self) -> Dict[str, logging.Logger]:
        """获取所有日志记录器
        
        Returns:
            日志记录器字典
        """
        return self.loggers


# 创建全局日志管理器实例
log_manager = LogManager()


# 导出常用函数
def setup_logger(name: str = "cert_manager", config: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """设置日志记录器
    
    Args:
        name: 日志记录器名称
        config: 日志配置字典
    
    Returns:
        配置好的日志记录器
    """
    return log_manager.setup_logger(name, config)


def get_logger(name: str = "cert_manager") -> logging.Logger:
    """获取日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        日志记录器
    """
    return log_manager.get_logger(name)


def set_log_level(name: str, level: int) -> None:
    """设置日志级别
    
    Args:
        name: 日志记录器名称
        level: 日志级别
    """
    log_manager.set_log_level(name, level)


def set_console_level(name: str, level: int) -> None:
    """设置控制台日志级别
    
    Args:
        name: 日志记录器名称
        level: 日志级别
    """
    log_manager.set_console_level(name, level)


def set_file_level(name: str, level: int) -> None:
    """设置文件日志级别
    
    Args:
        name: 日志记录器名称
        level: 日志级别
    """
    log_manager.set_file_level(name, level)


# 导出默认日志记录器
default_logger = setup_logger()
