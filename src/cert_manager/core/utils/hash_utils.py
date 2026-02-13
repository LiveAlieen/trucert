"""哈希工具模块

提供哈希相关的工具函数
"""

import hashlib
from typing import Union, Optional


def calculate_hash(data: Union[str, bytes], algorithm: str = "sha256") -> str:
    """计算数据的哈希值
    
    Args:
        data: 要计算哈希的数据
        algorithm: 哈希算法，支持"sha256", "sha384", "sha512"
    
    Returns:
        哈希值的十六进制字符串
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    if algorithm.lower() == "sha256":
        hash_obj = hashlib.sha256()
    elif algorithm.lower() == "sha384":
        hash_obj = hashlib.sha384()
    elif algorithm.lower() == "sha512":
        hash_obj = hashlib.sha512()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    hash_obj.update(data)
    return hash_obj.hexdigest()


def calculate_file_hash(filepath: str, algorithm: str = "sha256") -> str:
    """计算文件的哈希值
    
    Args:
        filepath: 文件路径
        algorithm: 哈希算法，支持"sha256", "sha384", "sha512"
    
    Returns:
        哈希值的十六进制字符串
    """
    if algorithm.lower() == "sha256":
        hash_obj = hashlib.sha256()
    elif algorithm.lower() == "sha384":
        hash_obj = hashlib.sha384()
    elif algorithm.lower() == "sha512":
        hash_obj = hashlib.sha512()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def verify_hash(data: Union[str, bytes], expected_hash: str, algorithm: str = "sha256") -> bool:
    """验证数据的哈希值
    
    Args:
        data: 要验证的数据
        expected_hash: 预期的哈希值
        algorithm: 哈希算法，支持"sha256", "sha384", "sha512"
    
    Returns:
        哈希值是否匹配
    """
    calculated_hash = calculate_hash(data, algorithm)
    return calculated_hash == expected_hash


def verify_file_hash(filepath: str, expected_hash: str, algorithm: str = "sha256") -> bool:
    """验证文件的哈希值
    
    Args:
        filepath: 文件路径
        expected_hash: 预期的哈希值
        algorithm: 哈希算法，支持"sha256", "sha384", "sha512"
    
    Returns:
        哈希值是否匹配
    """
    calculated_hash = calculate_file_hash(filepath, algorithm)
    return calculated_hash == expected_hash