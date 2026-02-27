"""哈希工具模块

提供哈希相关的工具函数，包括数据哈希计算和文件哈希计算，使用模块化算法系统
"""

import hashlib
import os
from typing import Union, Optional
from ..algorithms import get_algorithm


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
    
    # 获取哈希算法实例
    hash_algorithm = get_algorithm('hashing', algorithm.upper())
    hash_instance = hash_algorithm()
    return hash_instance.calculate_hex(data)


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
    
    # 获取哈希算法实例
    hash_algorithm = get_algorithm('hashing', algorithm.upper())
    hash_instance = hash_algorithm()
    
    # 读取文件并计算哈希
    buffer_size = 65536  # 64KB
    with open(filepath, "rb") as f:
        while chunk := f.read(buffer_size):
            # 这里我们需要累积计算哈希，因为文件可能很大
            # 注意：当前实现中，哈希算法类只支持一次性计算，所以我们使用传统方法
            # 后续可以考虑在哈希算法类中添加流式计算支持
            pass
    
    # 为了保持兼容性，这里暂时使用传统方法计算文件哈希
    # 后续可以优化为使用算法模块的流式计算
    if algorithm.lower() == "sha256":
        hash_obj = hashlib.sha256()
    elif algorithm.lower() == "sha384":
        hash_obj = hashlib.sha384()
    elif algorithm.lower() == "sha512":
        hash_obj = hashlib.sha512()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
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