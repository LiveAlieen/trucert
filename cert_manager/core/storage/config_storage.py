"""配置存储模块

实现配置的存储和加载功能
"""

import os
from typing import Dict, Any
from .storage_manager import StorageManager


class ConfigStorage:
    """配置存储"""
    
    def __init__(self, storage_manager: StorageManager = None):
        """初始化配置存储
        
        Args:
            storage_manager: 存储管理器实例
        """
        if storage_manager is None:
            self.storage_manager = StorageManager()
        else:
            self.storage_manager = storage_manager
        
        self.config_dir = self.storage_manager.base_dir
    
    def save_config(self, config_name: str, config_data: Dict[str, Any], format: str = "json") -> None:
        """保存配置
        
        Args:
            config_name: 配置名称
            config_data: 配置数据
            format: 文件格式，支持"json"
        """
        filepath = os.path.join(self.config_dir, f"{config_name}.{format}")
        self.storage_manager.save(config_data, filepath, format)
    
    def load_config(self, config_name: str, format: str = "json") -> Dict[str, Any]:
        """加载配置
        
        Args:
            config_name: 配置名称
            format: 文件格式，支持"json"
        
        Returns:
            配置数据
        """
        filepath = os.path.join(self.config_dir, f"{config_name}.{format}")
        return self.storage_manager.load(filepath, format)
    
    def get_config(self, config_name: str, default: Dict[str, Any] = None, format: str = "json") -> Dict[str, Any]:
        """获取配置，如果不存在则返回默认值
        
        Args:
            config_name: 配置名称
            default: 默认配置数据
            format: 文件格式，支持"json"
        
        Returns:
            配置数据
        """
        try:
            return self.load_config(config_name, format)
        except FileNotFoundError:
            if default is not None:
                # 保存默认配置
                self.save_config(config_name, default, format)
                return default
            raise
    
    def update_config(self, config_name: str, updates: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
        """更新配置
        
        Args:
            config_name: 配置名称
            updates: 要更新的配置数据
            format: 文件格式，支持"json"
        
        Returns:
            更新后的配置数据
        """
        try:
            config = self.load_config(config_name, format)
        except FileNotFoundError:
            config = {}
        
        config.update(updates)
        self.save_config(config_name, config, format)
        return config
    
    def delete_config(self, config_name: str, format: str = "json") -> bool:
        """删除配置
        
        Args:
            config_name: 配置名称
            format: 文件格式，支持"json"
        
        Returns:
            是否删除成功
        """
        filepath = os.path.join(self.config_dir, f"{config_name}.{format}")
        return self.storage_manager.delete(filepath)
    
    def list_configs(self, format: str = "json") -> list:
        """列出所有配置
        
        Args:
            format: 文件格式，支持"json"
        
        Returns:
            配置名称列表
        """
        config_files = self.storage_manager.list_files(self.config_dir, f"*.{format}")
        configs = []
        
        for filepath in config_files:
            filename = os.path.basename(filepath)
            config_name = os.path.splitext(filename)[0]
            configs.append(config_name)
        
        return configs
    
    def get_cert_versions(self) -> Dict[str, Any]:
        """获取证书版本配置
        
        Returns:
            证书版本配置
        """
        default_config = {
            "v1": {
                "version": 0,  # x509.Version.v1
                "fields": ["subject", "issuer", "public_key", "serial_number", "not_valid_before", "not_valid_after", "signature_algorithm"]
            },
            "v3": {
                "version": 2,  # x509.Version.v3
                "fields": ["subject", "issuer", "public_key", "serial_number", "not_valid_before", "not_valid_after", "signature_algorithm", "extensions"]
            }
        }
        
        return self.get_config("cert_versions", default_config)
    
    def get_algorithms(self) -> Dict[str, Any]:
        """获取算法配置
        
        Returns:
            算法配置
        """
        default_config = {
            "hash_algorithms": ["sha256", "sha384", "sha512"],
            "rsa_key_sizes": [2048, 3072, 4096],
            "ecc_curves": ["secp256r1", "secp384r1", "secp521r1"]
        }
        
        return self.get_config("algorithms", default_config)
