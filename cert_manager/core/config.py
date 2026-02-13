import json
import yaml
import os
from typing import Dict, Any, Optional

class ConfigManager:
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir
        self.configs = {}
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.config_dir)
        if not os.path.exists(config_path):
            os.makedirs(config_path)
    
    def load_config(self, config_name: str, file_format: str = "json") -> Dict[str, Any]:
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 self.config_dir, f"{config_name}.{file_format}")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if file_format.lower() == "json":
                    config = json.load(f)
                elif file_format.lower() == "yaml" or file_format.lower() == "yml":
                    config = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported file format: {file_format}")
            
            self.configs[config_name] = config
            return config
        except Exception as e:
            raise Exception(f"Failed to load config file: {str(e)}")
    
    def save_config(self, config_name: str, config_data: Dict[str, Any], 
                   file_format: str = "json") -> None:
        """保存配置文件"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 self.config_dir, f"{config_name}.{file_format}")
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if file_format.lower() == "json":
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                elif file_format.lower() == "yaml" or file_format.lower() == "yml":
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    raise ValueError(f"Unsupported file format: {file_format}")
            
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
    
    def get_cert_versions(self) -> Dict[str, Any]:
        """获取证书版本配置"""
        try:
            return self.get_config("cert_versions")
        except FileNotFoundError:
            # 返回默认配置
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
            self.save_config("cert_versions", default_config)
            return default_config
    
    def get_algorithms(self) -> Dict[str, Any]:
        """获取算法配置"""
        try:
            return self.get_config("algorithms")
        except FileNotFoundError:
            # 返回默认配置
            default_config = {
                "hash_algorithms": ["sha256", "sha384", "sha512"],
                "rsa_key_sizes": [2048, 3072, 4096],
                "ecc_curves": ["secp256r1", "secp384r1", "secp521r1"]
            }
            self.save_config("algorithms", default_config)
            return default_config
    
    def reload_all(self):
        """重新加载所有配置"""
        config_files = os.listdir(os.path.join(os.path.dirname(os.path.dirname(__file__)), self.config_dir))
        for config_file in config_files:
            if config_file.endswith('.json') or config_file.endswith('.yaml') or config_file.endswith('.yml'):
                config_name = os.path.splitext(config_file)[0]
                file_format = os.path.splitext(config_file)[1][1:]
                try:
                    self.load_config(config_name, file_format)
                except Exception as e:
                    print(f"Warning: Failed to reload config {config_name}: {str(e)}")
