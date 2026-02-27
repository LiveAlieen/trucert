from typing import Dict, Any, Optional, List, Callable
from ..utils import get_logger

class ServiceUtils:
    """服务工具类，封装服务层通用功能
    
    提供参数提取、验证、异常处理等通用功能，
    减少服务层代码重复，提高可维护性。
    """
    
    @staticmethod
    def extract_params(params: Dict[str, Any], required: List[str], optional: Dict[str, Any] = None) -> Dict[str, Any]:
        """提取并验证参数
        
        Args:
            params: 包含所有参数的字典
            required: 必需参数列表
            optional: 可选参数及其默认值的字典
        
        Returns:
            提取的参数字典
            
        Raises:
            ValueError: 如果缺少必需参数
        """
        if optional is None:
            optional = {}
        
        extracted = {}
        
        # 提取必需参数
        for param_name in required:
            if param_name not in params or params[param_name] is None:
                raise ValueError(f"缺少必要的{param_name}参数")
            extracted[param_name] = params[param_name]
        
        # 提取可选参数
        for param_name, default_value in optional.items():
            extracted[param_name] = params.get(param_name, default_value)
        
        return extracted
    
    @staticmethod
    def handle_service_method(func: Callable) -> Callable:
        """服务方法装饰器，处理异常并返回统一格式的结果
        
        Args:
            func: 服务方法
        
        Returns:
            包装后的服务方法
        """
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger = get_logger(func.__self__.__class__.__name__)
                logger.error(f"{func.__name__} 失败: {str(e)}")
                return {
                    "success": False,
                    "error": str(e)
                }
        return wrapper
    
    @staticmethod
    def validate_positive(value: Any, name: str) -> None:
        """验证值是否为正数
        
        Args:
            value: 要验证的值
            name: 参数名称
        
        Raises:
            ValueError: 如果值不是正数
        """
        if value <= 0:
            raise ValueError(f"{name}必须为正数")
    
    @staticmethod
    def validate_not_empty(value: Any, name: str) -> None:
        """验证值是否非空
        
        Args:
            value: 要验证的值
            name: 参数名称
        
        Raises:
            ValueError: 如果值为空
        """
        if not value:
            raise ValueError(f"{name}不能为空")
