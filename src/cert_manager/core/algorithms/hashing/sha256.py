"""SHA256哈希算法模块"""

import hashlib
from src.cert_manager.core.algorithms import HashingAlgorithm


class SHA256Algorithm(HashingAlgorithm):
    """SHA256哈希算法实现"""
    
    name = "SHA256"
    version = "1.0"
    description = "SHA256哈希算法，生成256位哈希值"
    
    def calculate(self, data: bytes) -> bytes:
        """计算SHA256哈希值
        
        Args:
            data: 要计算哈希的数据
            
        Returns:
            哈希值（字节形式）
        """
        hash_obj = hashlib.sha256()
        hash_obj.update(data)
        return hash_obj.digest()
    
    def calculate_hex(self, data: bytes) -> str:
        """计算SHA256哈希值（十六进制字符串）
        
        Args:
            data: 要计算哈希的数据
            
        Returns:
            哈希值的十六进制字符串
        """
        hash_obj = hashlib.sha256()
        hash_obj.update(data)
        return hash_obj.hexdigest()
