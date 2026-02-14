"""错误处理工具模块

提供统一的错误类型和异常处理机制
"""

from typing import Optional, Dict, Any
import traceback


class CertManagerError(Exception):
    """证书管理器基础错误类"""
    
    def __init__(self, message: str, error_code: int = 500, details: Optional[Dict[str, Any]] = None):
        """初始化错误
        
        Args:
            message: 错误信息
            error_code: 错误代码
            details: 错误详情
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """将错误转换为字典
        
        Returns:
            错误信息字典
        """
        return {
            "error": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class KeyError(CertManagerError):
    """密钥相关错误"""
    
    def __init__(self, message: str, error_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)


class CertError(CertManagerError):
    """证书相关错误"""
    
    def __init__(self, message: str, error_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)


class FileError(CertManagerError):
    """文件相关错误"""
    
    def __init__(self, message: str, error_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)


class StorageError(CertManagerError):
    """存储相关错误"""
    
    def __init__(self, message: str, error_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)


class ValidationError(CertManagerError):
    """验证相关错误"""
    
    def __init__(self, message: str, error_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)


class ConfigError(CertManagerError):
    """配置相关错误"""
    
    def __init__(self, message: str, error_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)


def handle_error(error: Exception) -> Dict[str, Any]:
    """处理错误，返回统一格式的错误信息
    
    Args:
        error: 异常对象
    
    Returns:
        错误信息字典
    """
    if isinstance(error, CertManagerError):
        return error.to_dict()
    else:
        # 处理未捕获的异常
        return {
            "error": str(error),
            "error_code": 500,
            "details": {
                "traceback": traceback.format_exc()
            }
        }


def raise_error(error_type: type, message: str, **kwargs):
    """抛出错误
    
    Args:
        error_type: 错误类型
        message: 错误信息
        **kwargs: 额外参数
    """
    details = kwargs.pop('details', None)
    error_code = kwargs.pop('error_code', None)
    
    if error_code:
        raise error_type(message, error_code, details)
    else:
        raise error_type(message, details=details)
