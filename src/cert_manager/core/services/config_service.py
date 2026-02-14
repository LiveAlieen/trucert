from typing import Optional, Dict, Any, List
from ..business.config import ConfigManager

class ConfigService:
    """配置服务类，封装配置管理功能，作为GUI和核心业务逻辑之间的桥梁"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
    
    def load_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """加载配置文件
        
        Args:
            params: 包含以下字段的字典：
                - config_name: 配置名称
                - file_format: 文件格式，默认"json"
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，配置数据
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            config_name = params.get('config_name')
            file_format = params.get('file_format', 'json')
            
            # 验证参数
            if not config_name:
                return {
                    "success": False,
                    "error": "缺少必要的配置名称参数"
                }
            
            # 调用业务逻辑层
            config_data = self.config_manager.load_config(config_name, file_format)
            
            return {
                "success": True,
                "data": config_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """保存配置文件
        
        Args:
            params: 包含以下字段的字典：
                - config_name: 配置名称
                - config_data: 配置数据
                - file_format: 文件格式，默认"json"
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            config_name = params.get('config_name')
            config_data = params.get('config_data')
            file_format = params.get('file_format', 'json')
            
            # 验证参数
            if not config_name or config_data is None:
                return {
                    "success": False,
                    "error": "缺少必要的配置名称或配置数据参数"
                }
            
            # 调用业务逻辑层
            self.config_manager.save_config(config_name, config_data, file_format)
            
            return {
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取配置，如果不存在则返回默认值
        
        Args:
            params: 包含以下字段的字典：
                - config_name: 配置名称
                - default: 默认配置数据，默认None
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，配置数据
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            config_name = params.get('config_name')
            default = params.get('default', None)
            
            # 验证参数
            if not config_name:
                return {
                    "success": False,
                    "error": "缺少必要的配置名称参数"
                }
            
            # 调用业务逻辑层
            config_data = self.config_manager.get_config(config_name, default)
            
            return {
                "success": True,
                "data": config_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """更新配置
        
        Args:
            params: 包含以下字段的字典：
                - config_name: 配置名称
                - updates: 要更新的配置数据
                - file_format: 文件格式，默认"json"
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，更新后的配置数据
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            config_name = params.get('config_name')
            updates = params.get('updates')
            file_format = params.get('file_format', 'json')
            
            # 验证参数
            if not config_name or updates is None:
                return {
                    "success": False,
                    "error": "缺少必要的配置名称或更新数据参数"
                }
            
            # 调用业务逻辑层
            updated_config = self.config_manager.update_config(config_name, updates, file_format)
            
            return {
                "success": True,
                "data": updated_config
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_algorithms(self) -> Dict[str, Any]:
        """获取算法配置
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，算法配置
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 调用业务逻辑层
            algorithms = self.config_manager.get_algorithms()
            
            return {
                "success": True,
                "data": algorithms
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def reload_all(self) -> Dict[str, Any]:
        """重新加载所有配置
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 调用业务逻辑层
            self.config_manager.reload_all()
            
            return {
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """删除配置
        
        Args:
            params: 包含以下字段的字典：
                - config_name: 配置名称
                - file_format: 文件格式，默认"json"
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: bool，是否删除成功
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            config_name = params.get('config_name')
            file_format = params.get('file_format', 'json')
            
            # 验证参数
            if not config_name:
                return {
                    "success": False,
                    "error": "缺少必要的配置名称参数"
                }
            
            # 调用业务逻辑层
            success = self.config_manager.delete_config(config_name, file_format)
            
            return {
                "success": True,
                "data": success
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_configs(self) -> Dict[str, Any]:
        """列出所有配置
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: List[str]，配置名称列表
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 调用业务逻辑层
            configs = self.config_manager.list_configs()
            
            return {
                "success": True,
                "data": configs
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
