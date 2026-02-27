# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

import os
from typing import Dict, Any, Optional
from ..utils import ConfigError, handle_error, get

class ConfigManager:
    """配置管理类，负责系统配置的加载、保存和管理
    
    提供配置文件的加载、保存、更新、删除等功能，
    是整个系统中配置管理的核心组件。
    """
    
    # 默认配置
    DEFAULT_CONFIGS = {
        "algorithms": {
            "hash_algorithms": ["sha256", "sha384", "sha512"],
            "rsa_key_sizes": [2048, 3072, 4096],
            "ecc_curves": ["secp256r1", "secp384r1", "secp521r1"]
        },
        "storage": {
            "key_dir": "key",
            "trust_dir": "trust",
            "config_dir": "configs"
        },
        "security": {
            "enable_file_integrity": True,
            "enable_memory_protection": True
        },
        "ui": {
            "default_tab": "key",
            "window_size": [1000, 700]
        }
    }
    
    def __init__(self, config_dir: str = None):
        """初始化配置管理器
        
        Args:
            config_dir: 配置目录路径，如果为None则使用默认路径
        """
        self.config_dir = config_dir
        self.configs = {}
        # 使用依赖注入获取配置存储组件
        self.config_storage = get("config_storage")
        # 加载默认配置
        self._load_default_configs()
    
    def _load_default_configs(self):
        """加载默认配置"""
        for config_name, default_config in self.DEFAULT_CONFIGS.items():
            try:
                # 尝试加载配置，如果不存在则使用默认值
                self.configs[config_name] = self.get_config(config_name, default_config)
            except Exception as e:
                # 如果加载失败，使用默认配置
                self.configs[config_name] = default_config
    
    def load_config(self, config_name: str, file_format: str = "json") -> Dict[str, Any]:
        """加载配置文件
        
        Args:
            config_name: 配置名称
            file_format: 文件格式，支持"json"
        
        Returns:
            配置数据
        
        Raises:
            ConfigError: 加载配置失败时抛出
        """
        try:
            config = self.config_storage.load_config(config_name, file_format)
            self.configs[config_name] = config
            return config
        except Exception as e:
            # 如果加载失败，返回默认配置
            if config_name in self.DEFAULT_CONFIGS:
                return self.DEFAULT_CONFIGS[config_name]
            raise ConfigError(f"Failed to load config file: {str(e)}")
    
    def save_config(self, config_name: str, config_data: Dict[str, Any], 
                   file_format: str = "json") -> None:
        """保存配置文件
        
        Args:
            config_name: 配置名称
            config_data: 配置数据
            file_format: 文件格式，支持"json"
        
        Raises:
            ConfigError: 保存配置失败时抛出
        """
        try:
            self.config_storage.save_config(config_name, config_data, file_format)
            self.configs[config_name] = config_data
        except Exception as e:
            raise ConfigError(f"Failed to save config file: {str(e)}")
    
    def get_config(self, config_name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """获取配置，如果不存在则返回默认值
        
        Args:
            config_name: 配置名称
            default: 默认配置数据
        
        Returns:
            配置数据
        """
        if config_name in self.configs:
            return self.configs[config_name]
        
        try:
            return self.load_config(config_name)
        except (FileNotFoundError, ConfigError):
            if default is not None:
                return default
            elif config_name in self.DEFAULT_CONFIGS:
                return self.DEFAULT_CONFIGS[config_name]
            return {}
    
    def update_config(self, config_name: str, updates: Dict[str, Any], 
                     file_format: str = "json") -> Dict[str, Any]:
        """更新配置
        
        Args:
            config_name: 配置名称
            updates: 要更新的配置数据
            file_format: 文件格式，支持"json"
        
        Returns:
            更新后的配置数据
        """
        try:
            config = self.get_config(config_name)
        except (FileNotFoundError, ConfigError):
            config = self.DEFAULT_CONFIGS.get(config_name, {})
        
        config.update(updates)
        self.save_config(config_name, config, file_format)
        return config
    
    def get_algorithms(self) -> Dict[str, Any]:
        """获取算法配置
        
        Returns:
            算法配置
        """
        return self.get_config("algorithms")
    
    def get_storage_config(self) -> Dict[str, Any]:
        """获取存储配置
        
        Returns:
            存储配置
        """
        return self.get_config("storage")
    
    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置
        
        Returns:
            安全配置
        """
        return self.get_config("security")
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置
        
        Returns:
            UI配置
        """
        return self.get_config("ui")
    
    def reload_all(self):
        """重新加载所有配置"""
        try:
            configs = self.config_storage.list_configs()
            for config_name in configs:
                try:
                    self.load_config(config_name)
                except Exception as e:
                    print(f"Warning: Failed to reload config {config_name}: {str(e)}")
        except Exception as e:
            print(f"Warning: Failed to list configs: {str(e)}")
    
    def delete_config(self, config_name: str, file_format: str = "json") -> bool:
        """删除配置
        
        Args:
            config_name: 配置名称
            file_format: 文件格式，支持"json"
        
        Returns:
            是否删除成功
        """
        try:
            if config_name in self.configs:
                del self.configs[config_name]
            # 如果是默认配置，恢复默认值
            if config_name in self.DEFAULT_CONFIGS:
                self.configs[config_name] = self.DEFAULT_CONFIGS[config_name]
            return self.config_storage.delete_config(config_name, file_format)
        except Exception as e:
            print(f"Warning: Failed to delete config {config_name}: {str(e)}")
            return False
    
    def list_configs(self, file_format: str = "json") -> list:
        """列出所有配置
        
        Args:
            file_format: 文件格式，支持"json"
        
        Returns:
            配置名称列表
        """
        try:
            return self.config_storage.list_configs(file_format)
        except Exception as e:
            raise ConfigError(f"Failed to list configs: {str(e)}")