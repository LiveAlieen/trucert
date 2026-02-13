"""日志工具模块

提供日志配置和管理功能，包括创建日志目录、配置日志格式和级别等
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(name: str = "cert_manager", log_dir: str = None) -> logging.Logger:
    """设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志目录路径，如果为None则使用默认路径
    
    Returns:
        配置好的日志记录器
    """
    # 如果未指定日志目录，使用默认路径
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件路径
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建文件处理器，使用轮转日志
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5  # 保留5个备份文件
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 创建日志格式
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # 添加处理器到日志记录器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "cert_manager") -> logging.Logger:
    """获取日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        日志记录器
    """
    return logging.getLogger(name)


# 导出默认日志记录器
default_logger = setup_logger()
