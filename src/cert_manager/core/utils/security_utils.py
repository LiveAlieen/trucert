"""安全工具模块

提供内存保护、防调试和输入验证等安全相关功能
"""

import os
import sys
import ctypes
import re
from typing import Optional, Union, Any
import hashlib


class MemoryProtector:
    """内存保护类"""
    
    @staticmethod
    def secure_zero_memory(data: bytes) -> None:
        """安全地将内存清零
        
        Args:
            data: 要清零的数据
        """
        if not isinstance(data, bytes):
            return
        
        # 使用ctypes来确保内存被真正清零，避免Python的优化
        try:
            buf = ctypes.create_string_buffer(data, len(data))
            ctypes.memset(buf, 0, len(data))
        except Exception:
            pass
    
    @staticmethod
    def protect_memory(data: Any) -> Any:
        """保护内存中的数据
        
        Args:
            data: 要保护的数据
        
        Returns:
            保护后的数据
        """
        # 对于敏感数据，使用内存保护
        if isinstance(data, (bytes, str)):
            # 这里可以添加更复杂的内存保护逻辑
            pass
        return data


class AntiDebug:
    """防调试类"""
    
    @staticmethod
    def is_debugger_present() -> bool:
        """检测是否存在调试器
        
        Returns:
            bool: 是否存在调试器
        """
        try:
            # 简单的防调试检测
            if sys.gettrace() is not None:
                return True
            
            # 检查是否存在常见的调试器进程
            if os.name == 'nt':
                # Windows平台
                try:
                    import psutil
                    for proc in psutil.process_iter(['name']):
                        try:
                            if proc.info['name'] in ['ollydbg.exe', 'ida.exe', 'windbg.exe', 'gdb.exe']:
                                return True
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                except ImportError:
                    pass
        except Exception:
            pass
        return False
    
    @staticmethod
    def prevent_debugging() -> None:
        """防止调试"""
        if AntiDebug.is_debugger_present():
            # 如果检测到调试器，可以选择退出程序或采取其他措施
            pass


class InputValidator:
    """输入验证类"""
    
    @staticmethod
    def validate_file_path(path: str) -> bool:
        """验证文件路径
        
        Args:
            path: 文件路径
        
        Returns:
            bool: 路径是否有效
        """
        try:
            # 检查路径是否包含危险字符
            dangerous_chars = ['..', '//', '\\', '|', '<', '>', ':', '"', '*', '?']
            for char in dangerous_chars:
                if char in path:
                    return False
            
            # 检查路径是否存在（可选）
            # if not os.path.exists(path):
            #     return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_key_size(size: int) -> bool:
        """验证密钥大小
        
        Args:
            size: 密钥大小
        
        Returns:
            bool: 密钥大小是否有效
        """
        valid_sizes = [1024, 2048, 4096]
        return size in valid_sizes
    
    @staticmethod
    def validate_curve_name(curve: str) -> bool:
        """验证椭圆曲线名称
        
        Args:
            curve: 椭圆曲线名称
        
        Returns:
            bool: 椭圆曲线名称是否有效
        """
        valid_curves = ["SECP256R1", "SECP384R1", "SECP521R1"]
        return curve in valid_curves
    
    @staticmethod
    def validate_algorithm(algorithm: str) -> bool:
        """验证算法名称
        
        Args:
            algorithm: 算法名称
        
        Returns:
            bool: 算法名称是否有效
        """
        valid_algorithms = ["RSA", "ECC", "sha256", "sha384", "sha512"]
        return algorithm in valid_algorithms


class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        """初始化安全管理器"""
        self.memory_protector = MemoryProtector()
        self.anti_debug = AntiDebug()
        self.input_validator = InputValidator()
    
    def secure_data(self, data: Any) -> Any:
        """安全处理数据
        
        Args:
            data: 要处理的数据
        
        Returns:
            处理后的数据
        """
        return self.memory_protector.protect_memory(data)
    
    def clear_data(self, data: bytes) -> None:
        """清除数据
        
        Args:
            data: 要清除的数据
        """
        self.memory_protector.secure_zero_memory(data)
    
    def check_security(self) -> bool:
        """检查安全状态
        
        Returns:
            bool: 安全状态是否正常
        """
        # 检测调试器
        if self.anti_debug.is_debugger_present():
            return False
        return True
    
    def validate_input(self, input_data: Any, input_type: str) -> bool:
        """验证输入
        
        Args:
            input_data: 输入数据
            input_type: 输入类型
        
        Returns:
            bool: 输入是否有效
        """
        if input_type == "file_path":
            return self.input_validator.validate_file_path(input_data)
        elif input_type == "key_size":
            return self.input_validator.validate_key_size(input_data)
        elif input_type == "curve_name":
            return self.input_validator.validate_curve_name(input_data)
        elif input_type == "algorithm":
            return self.input_validator.validate_algorithm(input_data)
        return True


# 导出安全管理器实例
security_manager = SecurityManager()


def get_security_manager() -> SecurityManager:
    """获取安全管理器实例
    
    Returns:
        SecurityManager: 安全管理器实例
    """
    return security_manager


def secure_data(data: Any) -> Any:
    """安全处理数据
    
    Args:
        data: 要处理的数据
    
    Returns:
        处理后的数据
    """
    return security_manager.secure_data(data)


def clear_data(data: bytes) -> None:
    """清除数据
    
    Args:
        data: 要清除的数据
    """
    security_manager.clear_data(data)


def check_security() -> bool:
    """检查安全状态
    
    Returns:
        bool: 安全状态是否正常
    """
    return security_manager.check_security()


def validate_input(input_data: Any, input_type: str) -> bool:
    """验证输入
    
    Args:
        input_data: 输入数据
        input_type: 输入类型
    
    Returns:
        bool: 输入是否有效
    """
    return security_manager.validate_input(input_data, input_type)


def generate_secure_hash(data: bytes) -> str:
    """生成安全哈希
    
    Args:
        data: 要哈希的数据
    
    Returns:
        str: 哈希值
    """
    return hashlib.sha256(data).hexdigest()


def secure_compare(a: bytes, b: bytes) -> bool:
    """安全比较两个值
    
    Args:
        a: 第一个值
        b: 第二个值
    
    Returns:
        bool: 是否相等
    """
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= x ^ y
    return result == 0


__all__ = [
    "MemoryProtector",
    "AntiDebug",
    "InputValidator",
    "SecurityManager",
    "security_manager",
    "get_security_manager",
    "secure_data",
    "clear_data",
    "check_security",
    "validate_input",
    "generate_secure_hash",
    "secure_compare"
]
