from typing import Optional, Dict, Any, List
from ..business.config import ConfigManager

class ConfigService:
    """配置服务类，封装配置管理功能，作为GUI和核心业务逻辑之间的桥梁"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
    
    def load_config(self, config_name: str, file_format: str = "json") -> Dict[str, Any]:
        """加载配置文件
        
        Args:
            config_name: 配置名称
            file_format: 文件格式
        
        Returns:
            Dict[str, Any]: 配置数据
        """
        return self.config_manager.load_config(config_name, file_format)
    
    def save_config(self, config_name: str, config_data: Dict[str, Any], file_format: str = "json") -> None:
        """保存配置文件
        
        Args:
            config_name: 配置名称
            config_data: 配置数据
            file_format: 文件格式
        """
        self.config_manager.save_config(config_name, config_data, file_format)
    
    def get_config(self, config_name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """获取配置，如果不存在则返回默认值
        
        Args:
            config_name: 配置名称
            default: 默认配置数据
        
        Returns:
            Dict[str, Any]: 配置数据
        """
        return self.config_manager.get_config(config_name, default)
    
    def update_config(self, config_name: str, updates: Dict[str, Any], file_format: str = "json") -> Dict[str, Any]:
        """更新配置
        
        Args:
            config_name: 配置名称
            updates: 要更新的配置数据
            file_format: 文件格式
        
        Returns:
            Dict[str, Any]: 更新后的配置数据
        """
        return self.config_manager.update_config(config_name, updates, file_format)
    

    
    def get_algorithms(self) -> Dict[str, Any]:
        """获取算法配置
        
        Returns:
            Dict[str, Any]: 算法配置
        """
        return self.config_manager.get_algorithms()
    
    def reload_all(self) -> None:
        """重新加载所有配置"""
        self.config_manager.reload_all()
    
    def delete_config(self, config_name: str, file_format: str = "json") -> bool:
        """删除配置
        
        Args:
            config_name: 配置名称
            file_format: 文件格式
        
        Returns:
            bool: 是否删除成功
        """
        return self.config_manager.delete_config(config_name, file_format)
    
    def list_configs(self) -> List[str]:
        """列出所有配置
        
        Returns:
            List[str]: 配置名称列表
        """
        return self.config_manager.list_configs()
