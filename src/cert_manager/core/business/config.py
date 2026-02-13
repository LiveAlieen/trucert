import os
from typing import Dict, Any, Optional
from ..storage import ConfigStorage

class ConfigManager:
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir
        self.configs = {}
        # 使用新的存储模块
        self.config_storage = ConfigStorage()
    
    def load_config(self, config_name: str, file_format: str = "json") -> Dict[str, Any]:
        """加载配置文件"""
        try:
            config = self.config_storage.load_config(config_name, file_format)
            self.configs[config_name] = config
            return config
        except Exception as e:
            raise Exception(f"Failed to load config file: {str(e)}")
    
    def save_config(self, config_name: str, config_data: Dict[str, Any], 
                   file_format: str = "json") -> None:
        """保存配置文件"""
        try:
            self.config_storage.save_config(config_name, config_data, file_format)
            self.configs[config_name] = config_data
        except Exception as e:
            raise Exception(f"Failed to save config file: {str(e)}")
    
    def get_config(self, config_name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """获取配置，如果不存在则返回默认值"""
        if config_name in self.configs:
            return self.configs[config_name]
        
        try:
            return self.load_config(config_name)
        except FileNotFoundError:
            if default is not None:
                return default
            raise
    
    def update_config(self, config_name: str, updates: Dict[str, Any], 
                     file_format: str = "json") -> Dict[str, Any]:
        """更新配置"""
        try:
            config = self.get_config(config_name)
        except FileNotFoundError:
            config = {}
        
        config.update(updates)
        self.save_config(config_name, config, file_format)
        return config
    

    
    def get_algorithms(self) -> Dict[str, Any]:
        """获取算法配置"""
        return self.config_storage.get_algorithms()
    
    def reload_all(self):
        """重新加载所有配置"""
        configs = self.config_storage.list_configs()
        for config_name in configs:
            try:
                self.load_config(config_name)
            except Exception as e:
                print(f"Warning: Failed to reload config {config_name}: {str(e)}")
    
    def delete_config(self, config_name: str, file_format: str = "json") -> bool:
        """删除配置"""
        try:
            if config_name in self.configs:
                del self.configs[config_name]
            return self.config_storage.delete_config(config_name, file_format)
        except Exception:
            return False
    
    def list_configs(self) -> list:
        """列出所有配置"""
        return self.config_storage.list_configs()