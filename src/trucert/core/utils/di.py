"""依赖注入工具模块

提供依赖注入容器和相关功能，用于管理模块间的依赖关系，降低耦合度
"""

from typing import Dict, Any, Optional, Type, Callable, TypeVar, cast
from functools import wraps
import inspect

T = TypeVar('T')


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
    
    def get(self, name: str, default: Optional[Any] = None) -> Any:
        """获取依赖项
        
        Args:
            name: 依赖项名称
            default: 默认值，如果依赖项不存在则返回
        
        Returns:
            依赖项对象
        
        Raises:
            KeyError: 依赖项不存在且没有默认值时抛出
        """
        # 首先检查单例
        if name in self.singletons:
            return self.singletons[name]
        
        # 然后检查工厂
        if name in self.factories:
            try:
                # 创建实例并缓存为单例
                instance = self.factories[name]()
                self.singletons[name] = instance
                return instance
            except Exception as e:
                if default is not None:
                    return default
                raise RuntimeError(f"Failed to create instance for dependency '{name}': {str(e)}")
        
        # 最后检查直接注册的依赖项
        if name in self.dependencies:
            return self.dependencies[name]
        
        # 如果都不存在，返回默认值或抛出异常
        if default is not None:
            return default
        raise KeyError(f"Dependency '{name}' not found")
    
    def get_typed(self, name: str, type_: Type[T], default: Optional[T] = None) -> T:
        """获取指定类型的依赖项
        
        Args:
            name: 依赖项名称
            type_: 依赖项类型
            default: 默认值，如果依赖项不存在则返回
        
        Returns:
            指定类型的依赖项对象
        
        Raises:
            KeyError: 依赖项不存在且没有默认值时抛出
            TypeError: 依赖项类型不匹配时抛出
        """
        dependency = self.get(name, default)
        if dependency is not None and not isinstance(dependency, type_):
            raise TypeError(f"Dependency '{name}' is not of type {type_.__name__}")
        return cast(T, dependency)
    
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
                        try:
                            kwargs[param_name] = self.get(dep_name)
                        except KeyError as e:
                            # 获取函数签名，提供更详细的错误信息
                            sig = inspect.signature(func)
                            raise RuntimeError(
                                f"Failed to inject dependency '{dep_name}' for parameter '{param_name}' in function '{func.__name__}': {str(e)}"
                            ) from e
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def inject_class(self, **dependencies: str):
        """类依赖注入装饰器
        
        用于自动注入依赖项到类的__init__方法中
        
        Args:
            **dependencies: 依赖项映射，键为参数名，值为依赖项名称
        
        Returns:
            装饰器函数
        """
        def decorator(cls: Type) -> Type:
            original_init = cls.__init__
            
            @wraps(original_init)
            def new_init(self, *args, **kwargs):
                # 注入依赖项
                for param_name, dep_name in dependencies.items():
                    if param_name not in kwargs:
                        try:
                            kwargs[param_name] = self.get(dep_name)
                        except KeyError as e:
                            raise RuntimeError(
                                f"Failed to inject dependency '{dep_name}' for parameter '{param_name}' in class '{cls.__name__}': {str(e)}"
                            ) from e
                original_init(self, *args, **kwargs)
            
            cls.__init__ = new_init
            return cls
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


def get(name: str, default: Optional[Any] = None) -> Any:
    """获取依赖项
    
    Args:
        name: 依赖项名称
        default: 默认值，如果依赖项不存在则返回
    
    Returns:
        依赖项对象
    """
    return di_container.get(name, default)


def get_typed(name: str, type_: Type[T], default: Optional[T] = None) -> T:
    """获取指定类型的依赖项
    
    Args:
        name: 依赖项名称
        type_: 依赖项类型
        default: 默认值，如果依赖项不存在则返回
    
    Returns:
        指定类型的依赖项对象
    """
    return di_container.get_typed(name, type_, default)


def has(name: str) -> bool:
    """检查依赖项是否存在
    
    Args:
        name: 依赖项名称
    
    Returns:
        是否存在
    """
    return di_container.has(name)


def remove(name: str) -> None:
    """移除依赖项
    
    Args:
        name: 依赖项名称
    """
    di_container.remove(name)


def inject(**dependencies: str):
    """依赖注入装饰器
    
    用于自动注入依赖项到函数或方法中
    
    Args:
        **dependencies: 依赖项映射，键为参数名，值为依赖项名称
    
    Returns:
        装饰器函数
    """
    return di_container.inject(**dependencies)


def inject_class(**dependencies: str):
    """类依赖注入装饰器
    
    用于自动注入依赖项到类的__init__方法中
    
    Args:
        **dependencies: 依赖项映射，键为参数名，值为依赖项名称
    
    Returns:
        装饰器函数
    """
    return di_container.inject_class(**dependencies)


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
    "get_typed",
    "has",
    "remove",
    "inject",
    "inject_class",
    "clear"
]