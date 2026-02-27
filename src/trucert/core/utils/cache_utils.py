# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

"""缓存工具模块

提供缓存机制，减少重复计算，提高性能
"""

from typing import Dict, Any, Optional, Callable, TypeVar, Generic
from datetime import datetime, timedelta
import threading

T = TypeVar('T')


class CacheItem(Generic[T]):
    """缓存项类"""
    
    def __init__(self, value: T, expiry: Optional[datetime] = None):
        """初始化缓存项
        
        Args:
            value: 缓存值
            expiry: 过期时间
        """
        self.value = value
        self.expiry = expiry
        self.created_at = datetime.now()
    
    def is_expired(self) -> bool:
        """检查缓存项是否过期
        
        Returns:
            bool: 是否过期
        """
        if self.expiry is None:
            return False
        return datetime.now() > self.expiry


class CacheManager:
    """缓存管理器类"""
    
    def __init__(self):
        """初始化缓存管理器"""
        self._cache: Dict[str, CacheItem] = {}
        self._lock = threading.RLock()
        self._default_ttl = 3600  # 默认过期时间，1小时
    
    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值
        
        Returns:
            缓存值或默认值
        """
        with self._lock:
            if key not in self._cache:
                return default
            
            item = self._cache[key]
            if item.is_expired():
                del self._cache[key]
                return default
            
            return item.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
        """
        with self._lock:
            expiry = None
            if ttl is not None:
                expiry = datetime.now() + timedelta(seconds=ttl)
            self._cache[key] = CacheItem(value, expiry)
    
    def delete(self, key: str) -> bool:
        """删除缓存值
        
        Args:
            key: 缓存键
        
        Returns:
            bool: 是否删除成功
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """清除所有缓存"""
        with self._lock:
            self._cache.clear()
    
    def has(self, key: str) -> bool:
        """检查缓存键是否存在且未过期
        
        Args:
            key: 缓存键
        
        Returns:
            bool: 是否存在且未过期
        """
        with self._lock:
            if key not in self._cache:
                return False
            return not self._cache[key].is_expired()
    
    def get_or_set(self, key: str, func: Callable, ttl: Optional[int] = None) -> Any:
        """获取缓存值，如果不存在则计算并缓存
        
        Args:
            key: 缓存键
            func: 计算缓存值的函数
            ttl: 过期时间（秒）
        
        Returns:
            缓存值
        """
        value = self.get(key)
        if value is None:
            value = func()
            self.set(key, value, ttl)
        return value
    
    def size(self) -> int:
        """获取缓存大小
        
        Returns:
            int: 缓存项数量
        """
        with self._lock:
            # 清理过期项
            self._clean_expired()
            return len(self._cache)
    
    def _clean_expired(self) -> None:
        """清理过期的缓存项"""
        expired_keys = []
        for key, item in self._cache.items():
            if item.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
    
    def set_default_ttl(self, ttl: int) -> None:
        """设置默认过期时间
        
        Args:
            ttl: 默认过期时间（秒）
        """
        self._default_ttl = ttl


# 创建全局缓存管理器实例
cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例
    
    Returns:
        CacheManager: 缓存管理器实例
    """
    return cache_manager


def get_cache(key: str, default: Optional[Any] = None) -> Optional[Any]:
    """获取缓存值
    
    Args:
        key: 缓存键
        default: 默认值
    
    Returns:
        缓存值或默认值
    """
    return cache_manager.get(key, default)


def set_cache(key: str, value: Any, ttl: Optional[int] = None) -> None:
    """设置缓存值
    
    Args:
        key: 缓存键
        value: 缓存值
        ttl: 过期时间（秒）
    """
    cache_manager.set(key, value, ttl)


def delete_cache(key: str) -> bool:
    """删除缓存值
    
    Args:
        key: 缓存键
    
    Returns:
        bool: 是否删除成功
    """
    return cache_manager.delete(key)


def clear_cache() -> None:
    """清除所有缓存"""
    cache_manager.clear()


def has_cache(key: str) -> bool:
    """检查缓存键是否存在且未过期
    
    Args:
        key: 缓存键
    
    Returns:
        bool: 是否存在且未过期
    """
    return cache_manager.has(key)


def get_or_set_cache(key: str, func: Callable, ttl: Optional[int] = None) -> Any:
    """获取缓存值，如果不存在则计算并缓存
    
    Args:
        key: 缓存键
        func: 计算缓存值的函数
        ttl: 过期时间（秒）
    
    Returns:
        缓存值
    """
    return cache_manager.get_or_set(key, func, ttl)


def cache(size: int = 128):
    """缓存装饰器
    
    用于缓存函数的返回值
    
    Args:
        size: 缓存大小
    
    Returns:
        装饰器函数
    """
    def decorator(func):
        cache_dict = {}
        
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key = str(args) + str(kwargs)
            
            # 检查缓存
            if key in cache_dict:
                return cache_dict[key]
            
            # 计算结果
            result = func(*args, **kwargs)
            
            # 更新缓存
            if len(cache_dict) >= size:
                # 简单的缓存淘汰策略
                cache_dict.pop(next(iter(cache_dict)))
            cache_dict[key] = result
            
            return result
        
        return wrapper
    
    return decorator


__all__ = [
    "CacheManager",
    "cache_manager",
    "get_cache_manager",
    "get_cache",
    "set_cache",
    "delete_cache",
    "clear_cache",
    "has_cache",
    "get_or_set_cache",
    "cache"
]
