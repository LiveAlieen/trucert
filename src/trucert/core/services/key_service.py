from typing import Optional, Tuple, Union, List, Dict, Any
from cryptography.hazmat.primitives import serialization
from ..utils import get
from ..utils.service_utils import ServiceUtils

class KeyService:
    """密钥服务类，封装密钥管理功能，作为GUI和核心业务逻辑之间的桥梁
    
    提供标准化的接口调用，负责从业务层调用和封装密钥管理功能，
    统一GUI和CLI的接口规范，确保接口的一致性和可维护性。
    """
    
    def __init__(self):
        """初始化密钥服务
        
        使用依赖注入获取密钥管理组件，确保与业务层的解耦。
        """
        # 使用依赖注入获取业务层组件
        self.key_manager = get("key_manager")
    
    @ServiceUtils.handle_service_method
    def generate_rsa_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成RSA密钥对
        
        Args:
            params: 包含以下字段的字典：
                - key_size: 密钥大小，默认2048
        
        Returns:
            Dict[str, Any]: 包含私钥信息、公钥信息和密钥ID的字典
        """
        # 提取参数
        extracted = ServiceUtils.extract_params(params, [], {"key_size": 2048})
        key_size = extracted["key_size"]
        
        # 验证参数
        ServiceUtils.validate_positive(key_size, "密钥大小")
        
        # 调用业务逻辑层
        key_id, private_key, public_key = self.key_manager.generate_rsa_key(key_size)
        private_info = self.key_manager.get_key_info(key_id)
        private_info["type"] = "RSA Private Key"
        public_info = private_info.copy()
        public_info["type"] = "RSA Public Key"
        
        return {
            "private_key_info": private_info,
            "public_key_info": public_info,
            "key_id": key_id
        }
    
    @ServiceUtils.handle_service_method
    def generate_ecc_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成ECC密钥对
        
        Args:
            params: 包含以下字段的字典：
                - curve: 曲线类型，默认"secp256r1"
        
        Returns:
            Dict[str, Any]: 包含私钥信息、公钥信息和密钥ID的字典
        """
        # 提取参数
        extracted = ServiceUtils.extract_params(params, [], {"curve": "secp256r1"})
        curve = extracted["curve"]
        
        # 验证参数
        ServiceUtils.validate_not_empty(curve, "曲线类型")
        
        # 调用业务逻辑层
        key_id, private_key, public_key = self.key_manager.generate_ecc_key(curve)
        private_info = self.key_manager.get_key_info(key_id)
        private_info["type"] = "ECC Private Key"
        public_info = private_info.copy()
        public_info["type"] = "ECC Public Key"
        
        return {
            "private_key_info": private_info,
            "public_key_info": public_info,
            "key_id": key_id
        }
    
    @ServiceUtils.handle_service_method
    def generate_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成密钥对（统一接口）
        
        Args:
            params: 包含以下字段的字典：
                - key_type: 密钥类型，"RSA"或"ECC"
                - key_size: 密钥大小，默认2048（仅RSA）
                - curve: 曲线类型，默认"secp256r1"（仅ECC）
        
        Returns:
            Dict[str, Any]: 包含私钥信息、公钥信息和密钥ID的字典
        """
        # 提取参数
        extracted = ServiceUtils.extract_params(params, ["key_type"], {"key_size": 2048, "curve": "secp256r1"})
        key_type = extracted["key_type"].upper()
        key_size = extracted["key_size"]
        curve = extracted["curve"]
        
        # 验证参数
        if key_type not in ["RSA", "ECC"]:
            raise ValueError("密钥类型必须是'RSA'或'ECC'")
        
        if key_type == "RSA":
            ServiceUtils.validate_positive(key_size, "密钥大小")
            key_id, private_key, public_key = self.key_manager.generate_rsa_key(key_size)
            key_type_name = "RSA"
        else:  # ECC
            ServiceUtils.validate_not_empty(curve, "曲线类型")
            key_id, private_key, public_key = self.key_manager.generate_ecc_key(curve)
            key_type_name = "ECC"
        
        private_info = self.key_manager.get_key_info(key_id)
        private_info["type"] = f"{key_type_name} Private Key"
        public_info = private_info.copy()
        public_info["type"] = f"{key_type_name} Public Key"
        
        return {
            "private_key_info": private_info,
            "public_key_info": public_info,
            "key_id": key_id
        }
    
    @ServiceUtils.handle_service_method
    def list_keys(self) -> List[Dict[str, Any]]:
        """列出所有存储的密钥
        
        Returns:
            List[Dict[str, Any]]: 密钥列表
        """
        # 调用业务逻辑层
        key_ids = self.key_manager.list_keys()
        keys_info = []
        for key_id in key_ids:
            try:
                key_info = self.key_manager.get_key_info(key_id)
                key_info["id"] = key_id
                keys_info.append(key_info)
            except Exception:
                pass
        
        return keys_info
    
    @ServiceUtils.handle_service_method
    def load_key_pair(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """加载密钥对
        
        Args:
            params: 包含以下字段的字典：
                - key_id: 密钥ID
        
        Returns:
            Dict[str, Any]: 包含私钥和公钥的字典
        """
        # 提取参数
        extracted = ServiceUtils.extract_params(params, ["key_id"])
        key_id = extracted["key_id"]
        
        # 调用业务逻辑层
        private_key, public_key, _ = self.key_manager.load_key(key_id)
        
        return {
            "private_key": private_key,
            "public_key": public_key
        }
    
    @ServiceUtils.handle_service_method
    def delete_key(self, params: Dict[str, Any]) -> bool:
        """删除密钥
        
        Args:
            params: 包含以下字段的字典：
                - key_id: 密钥ID
        
        Returns:
            bool: 是否删除成功
        """
        # 提取参数
        extracted = ServiceUtils.extract_params(params, ["key_id"])
        key_id = extracted["key_id"]
        
        # 调用业务逻辑层
        return self.key_manager.delete_key(key_id)
    
    @ServiceUtils.handle_service_method
    def save_private_key(self, params: Dict[str, Any]) -> None:
        """保存私钥
        
        Args:
            params: 包含以下字段的字典：
                - private_key: 私钥
                - file_path: 文件路径
                - password: 密码（可选）
        """
        # 提取参数
        extracted = ServiceUtils.extract_params(params, ["private_key", "file_path"], {"password": None})
        private_key = extracted["private_key"]
        file_path = extracted["file_path"]
        password = extracted["password"]
        
        # 调用业务逻辑层
        self.key_manager.save_private_key(private_key, file_path, password)
    
    @ServiceUtils.handle_service_method
    def save_public_key(self, params: Dict[str, Any]) -> None:
        """保存公钥
        
        Args:
            params: 包含以下字段的字典：
                - public_key: 公钥
                - file_path: 文件路径
        """
        # 提取参数
        extracted = ServiceUtils.extract_params(params, ["public_key", "file_path"])
        public_key = extracted["public_key"]
        file_path = extracted["file_path"]
        
        # 调用业务逻辑层
        self.key_manager.save_public_key(public_key, file_path)
    
    @ServiceUtils.handle_service_method
    def load_private_key(self, params: Dict[str, Any]) -> Any:
        """加载私钥
        
        Args:
            params: 包含以下字段的字典：
                - file_path: 文件路径
                - password: 密码（可选）
        
        Returns:
            Any: 私钥
        """
        # 提取参数
        extracted = ServiceUtils.extract_params(params, ["file_path"], {"password": None})
        file_path = extracted["file_path"]
        password = extracted["password"]
        
        # 调用业务逻辑层
        return self.key_manager.load_private_key(file_path, password)
    
    @ServiceUtils.handle_service_method
    def load_public_key(self, params: Dict[str, Any]) -> Any:
        """加载公钥
        
        Args:
            params: 包含以下字段的字典：
                - file_path: 文件路径
        
        Returns:
            Any: 公钥
        """
        # 提取参数
        extracted = ServiceUtils.extract_params(params, ["file_path"])
        file_path = extracted["file_path"]
        
        # 调用业务逻辑层
        return self.key_manager.load_public_key(file_path)
    
    @ServiceUtils.handle_service_method
    def get_key_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取密钥信息
        
        Args:
            params: 包含以下字段的字典：
                - key: 密钥
        
        Returns:
            Dict[str, Any]: 密钥信息
        """
        # 提取参数
        extracted = ServiceUtils.extract_params(params, ["key"])
        key = extracted["key"]
        
        # 调用业务逻辑层
        return self.key_manager.get_key_info_from_key(key)
