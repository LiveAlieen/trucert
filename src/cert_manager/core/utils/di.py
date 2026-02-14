"""依赖注入工具模块

提供依赖注入容器和相关功能，用于管理模块间的依赖关系，降低耦合度
"""

from typing import Dict, Any, Optional, Type, Callable
from functools import wraps


class DependencyInjector:
    """依赖注入容器类
    
    用于管理和注入依赖项，支持单例模式和工厂模式
    """
    
    def __init__(self):
        """初始化依赖注入容器"""
        self.dependencies: Dict[str, Any] = {}
        self.factories: Dict[str, Callable] = {}
        self.singletons: Dict[str, Any] = {}
    
    def register(self, name: str, dependency: Any) -> None:
        """注册依赖项
        
        Args:
            name: 依赖项名称
            dependency: 依赖项对象
        """
        self.dependencies[name] = dependency
    
    def register_factory(self, name: str, factory: Callable) -> None:
        """注册依赖项工厂
        
        Args:
            name: 依赖项名称
            factory: 用于创建依赖项的工厂函数
        """
        self.factories[name] = factory
    
    def register_singleton(self, name: str, singleton: Any) -> None:
        """注册单例依赖项
        
        Args:
            name: 依赖项名称
            singleton: 单例对象
        """
        self.singletons[name] = singleton
    
    def get(self, name: str) -> Any:
        """获取依赖项
        
        Args:
            name: 依赖项名称
        
        Returns:
            依赖项对象
        
        Raises:
            KeyError: 依赖项不存在时抛出
        """
        # 首先检查单例
        if name in self.singletons:
            return self.singletons[name]
        
        # 然后检查工厂
        if name in self.factories:
            # 创建实例并缓存为单例
            instance = self.factories[name]()
            self.singletons[name] = instance
            return instance
        
        # 最后检查直接注册的依赖项
        if name in self.dependencies:
            return self.dependencies[name]
        
        # 如果都不存在，抛出异常
        raise KeyError(f"Dependency '{name}' not found")
    
    def has(self, name: str) -> bool:
        """检查依赖项是否存在
        
        Args:
            name: 依赖项名称
        
        Returns:
            是否存在
        """
        return name in self.singletons or name in self.factories or name in self.dependencies
    
    def remove(self, name: str) -> None:
        """移除依赖项
        
        Args:
            name: 依赖项名称
        """
        if name in self.singletons:
            del self.singletons[name]
        if name in self.factories:
            del self.factories[name]
        if name in self.dependencies:
            del self.dependencies[name]
    
    def clear(self) -> None:
        """清除所有依赖项"""
        self.singletons.clear()
        self.factories.clear()
        self.dependencies.clear()
    
    def inject(self, **dependencies: str):
        """依赖注入装饰器
        
        用于自动注入依赖项到函数或方法中
        
        Args:
            **dependencies: 依赖项映射，键为参数名，值为依赖项名称
        
        Returns:
            装饰器函数
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 注入依赖项
                for param_name, dep_name in dependencies.items():
                    if param_name not in kwargs:
                        kwargs[param_name] = self.get(dep_name)
                return func(*args, **kwargs)
            return wrapper
        return decorator


# 创建全局依赖注入容器实例
di_container = DependencyInjector()


# 导出常用函数
def register(name: str, dependency: Any) -> None:
    """注册依赖项
    
    Args:
        name: 依赖项名称
        dependency: 依赖项对象
    """
    di_container.register(name, dependency)


def register_factory(name: str, factory: Callable) -> None:
    """注册依赖项工厂
    
    Args:
        name: 依赖项名称
        factory: 用于创建依赖项的工厂函数
    """
    di_container.register_factory(name, factory)


def register_singleton(name: str, singleton: Any) -> None:
    """注册单例依赖项
    
    Args:
        name: 依赖项名称
        singleton: 单例对象
    """
    di_container.register_singleton(name, singleton)


def get(name: str) -> Any:
    """获取依赖项
    
    Args:
        name: 依赖项名称
    
    Returns:
        依赖项对象
    """
    return di_container.get(name)


def has(name: str) -> bool:
    """检查依赖项是否存在
    
    Args:
        name: 依赖项名称
    
    Returns:
        是否存在
    """
    return di_container.has(name)


def inject(**dependencies: str):
    """依赖注入装饰器
    
    用于自动注入依赖项到函数或方法中
    
    Args:
        **dependencies: 依赖项映射，键为参数名，值为依赖项名称
    
    Returns:
        装饰器函数
    """
    return di_container.inject(**dependencies)


def clear() -> None:
    """清除所有依赖项"""
    di_container.clear()


__all__ = [
    "DependencyInjector",
    "di_container",
    "register",
    "register_factory",
    "register_singleton",
    "get",
    "has",
    "inject",
    "clear"
]