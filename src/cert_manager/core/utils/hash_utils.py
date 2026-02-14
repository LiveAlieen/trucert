"""哈希工具模块

提供哈希相关的工具函数，包括数据哈希计算和文件哈希计算
"""

import hashlib
import os
from typing import Union, Optional


# 文件哈希缓存，避免重复计算
_file_hash_cache = {}


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
    # 生成缓存键
    cache_key = f"{filepath}:{algorithm}:{os.path.getmtime(filepath)}:{os.path.getsize(filepath)}"
    
    # 检查缓存
    if cache_key in _file_hash_cache:
        return _file_hash_cache[cache_key]
    
    # 选择哈希算法
    if algorithm.lower() == "sha256":
        hash_obj = hashlib.sha256()
    elif algorithm.lower() == "sha384":
        hash_obj = hashlib.sha384()
    elif algorithm.lower() == "sha512":
        hash_obj = hashlib.sha512()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    # 使用更大的缓冲区，减少I/O操作次数
    buffer_size = 65536  # 64KB
    with open(filepath, "rb") as f:
        while chunk := f.read(buffer_size):
            hash_obj.update(chunk)
    
    # 计算哈希值并缓存
    hash_hex = hash_obj.hexdigest()
    _file_hash_cache[cache_key] = hash_hex
    
    # 限制缓存大小，避免内存占用过高
    if len(_file_hash_cache) > 100:
        # 删除最旧的缓存项
        oldest_key = next(iter(_file_hash_cache))
        del _file_hash_cache[oldest_key]
    
    return hash_hex


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