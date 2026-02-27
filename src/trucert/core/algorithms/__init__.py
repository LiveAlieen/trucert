# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

"""算法模块初始化文件

提供算法注册和管理功能
"""

from abc import ABC, abstractmethod
from typing import Dict, Type, Any


class Algorithm(ABC):
    """算法基类
    
    所有算法模块必须继承此类并实现相应的方法
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """算法名称"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """算法版本"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """算法描述"""
        pass


class EncryptionAlgorithm(Algorithm):
    """加密算法基类"""
    
    @abstractmethod
    def generate_key(self, **kwargs) -> tuple:
        """生成密钥对
        
        Returns:
            (私钥, 公钥)元组
        """
        pass
    
    @abstractmethod
    def encrypt(self, public_key: Any, data: bytes) -> bytes:
        """加密数据
        
        Args:
            public_key: 公钥
            data: 要加密的数据
            
        Returns:
            加密后的数据
        """
        pass
    
    @abstractmethod
    def decrypt(self, private_key: Any, encrypted_data: bytes) -> bytes:
        """解密数据
        
        Args:
            private_key: 私钥
            encrypted_data: 加密的数据
            
        Returns:
            解密后的数据
        """
        pass


class SignatureAlgorithm(Algorithm):
    """签名算法基类"""
    
    @abstractmethod
    def sign(self, private_key: Any, data: bytes, **kwargs) -> bytes:
        """签名数据
        
        Args:
            private_key: 私钥
            data: 要签名的数据
            
        Returns:
            签名数据
        """
        pass
    
    @abstractmethod
    def verify(self, public_key: Any, signature: bytes, data: bytes, **kwargs) -> bool:
        """验证签名
        
        Args:
            public_key: 公钥
            signature: 签名数据
            data: 原始数据
            
        Returns:
            签名是否有效
        """
        pass


class HashingAlgorithm(Algorithm):
    """哈希算法基类"""
    
    @abstractmethod
    def calculate(self, data: bytes) -> bytes:
        """计算哈希值
        
        Args:
            data: 要计算哈希的数据
            
        Returns:
            哈希值（字节形式）
        """
        pass
    
    @abstractmethod
    def calculate_hex(self, data: bytes) -> str:
        """计算哈希值（十六进制字符串）
        
        Args:
            data: 要计算哈希的数据
            
        Returns:
            哈希值的十六进制字符串
        """
        pass


# 算法注册表，结构为：{算法类型: {算法名称: {版本: 算法类}}}
_algorithm_registry: Dict[str, Dict[str, Dict[str, Type[Algorithm]]]] = {
    'encryption': {},
    'signature': {},
    'hashing': {}
}

# 默认版本映射
_default_versions: Dict[str, Dict[str, str]] = {
    'encryption': {},
    'signature': {},
    'hashing': {}
}


def register_algorithm(algorithm_type: str, algorithm_class: Type[Algorithm], set_default: bool = True) -> None:
    """注册算法
    
    Args:
        algorithm_type: 算法类型，可选值：'encryption', 'signature', 'hashing'
        algorithm_class: 算法类
        set_default: 是否将此版本设置为默认版本，默认为True
    """
    if algorithm_type not in _algorithm_registry:
        raise ValueError(f"Unknown algorithm type: {algorithm_type}")
    
    algorithm_name = algorithm_class.name
    algorithm_version = algorithm_class.version
    
    # 初始化算法名称的版本字典
    if algorithm_name not in _algorithm_registry[algorithm_type]:
        _algorithm_registry[algorithm_type][algorithm_name] = {}
    
    # 注册算法版本
    _algorithm_registry[algorithm_type][algorithm_name][algorithm_version] = algorithm_class
    
    # 设置默认版本
    if set_default:
        _default_versions[algorithm_type][algorithm_name] = algorithm_version


def discover_algorithms() -> None:
    """自动发现并注册算法模块
    
    扫描algorithms目录下的所有子目录，自动注册算法模块
    """
    import os
    import importlib
    from pathlib import Path
    
    # 获取algorithms目录的绝对路径
    algorithms_dir = Path(__file__).parent
    
    # 定义算法类型与目录的映射
    algorithm_types = {
        'encryption': 'encryption',
        'signature': 'signature',
        'hashing': 'hashing'
    }
    
    for algo_type, directory in algorithm_types.items():
        algo_dir = algorithms_dir / directory
        if algo_dir.exists() and algo_dir.is_dir():
            # 扫描目录下的所有Python文件
            for file_path in algo_dir.glob('*.py'):
                if file_path.name == '__init__.py':
                    continue
                
                # 构建模块路径
                module_name = f"cert_manager.core.algorithms.{directory}.{file_path.stem}"
                
                try:
                    # 导入模块
                    module = importlib.import_module(module_name)
                    
                    # 查找模块中的算法类
                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        # 检查是否是算法类的子类且不是抽象基类
                        if (isinstance(item, type) and 
                            issubclass(item, Algorithm) and 
                            not item.__abstractmethods__):
                            # 注册算法
                            register_algorithm(algo_type, item)
                except Exception as e:
                    print(f"Error importing algorithm module {module_name}: {e}")


# 自动发现算法
discover_algorithms()


def get_algorithm(algorithm_type: str, algorithm_name: str, version: str = None) -> Type[Algorithm]:
    """获取算法类
    
    Args:
        algorithm_type: 算法类型
        algorithm_name: 算法名称
        version: 算法版本，若为None则使用默认版本
        
    Returns:
        算法类
    """
    if algorithm_type not in _algorithm_registry:
        raise ValueError(f"Unknown algorithm type: {algorithm_type}")
    
    if algorithm_name not in _algorithm_registry[algorithm_type]:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")
    
    # 确定使用的版本
    if version is None:
        if algorithm_name not in _default_versions[algorithm_type]:
            # 如果没有默认版本，使用最新版本
            versions = list(_algorithm_registry[algorithm_type][algorithm_name].keys())
            if not versions:
                raise ValueError(f"No versions available for algorithm: {algorithm_name}")
            version = versions[-1]
        else:
            version = _default_versions[algorithm_type][algorithm_name]
    
    if version not in _algorithm_registry[algorithm_type][algorithm_name]:
        raise ValueError(f"Unknown version {version} for algorithm: {algorithm_name}")
    
    return _algorithm_registry[algorithm_type][algorithm_name][version]


def set_default_version(algorithm_type: str, algorithm_name: str, version: str) -> None:
    """设置算法的默认版本
    
    Args:
        algorithm_type: 算法类型
        algorithm_name: 算法名称
        version: 要设置为默认的版本
    """
    if algorithm_type not in _algorithm_registry:
        raise ValueError(f"Unknown algorithm type: {algorithm_type}")
    
    if algorithm_name not in _algorithm_registry[algorithm_type]:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")
    
    if version not in _algorithm_registry[algorithm_type][algorithm_name]:
        raise ValueError(f"Unknown version {version} for algorithm: {algorithm_name}")
    
    _default_versions[algorithm_type][algorithm_name] = version


def list_algorithm_versions(algorithm_type: str, algorithm_name: str) -> list:
    """列出算法的所有版本
    
    Args:
        algorithm_type: 算法类型
        algorithm_name: 算法名称
        
    Returns:
        版本列表
    """
    if algorithm_type not in _algorithm_registry:
        raise ValueError(f"Unknown algorithm type: {algorithm_type}")
    
    if algorithm_name not in _algorithm_registry[algorithm_type]:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")
    
    return list(_algorithm_registry[algorithm_type][algorithm_name].keys())


def list_algorithms(algorithm_type: str = None) -> Dict:
    """列出所有算法
    
    Args:
        algorithm_type: 算法类型，若为None则返回所有类型的算法
        
    Returns:
        算法注册表
    """
    if algorithm_type:
        if algorithm_type not in _algorithm_registry:
            raise ValueError(f"Unknown algorithm type: {algorithm_type}")
        return {algorithm_type: _algorithm_registry[algorithm_type]}
    return _algorithm_registry
