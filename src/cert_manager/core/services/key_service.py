from typing import Optional, Tuple, Union, List, Dict, Any
from cryptography.hazmat.primitives import serialization
from ..utils import get

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
    
    def generate_rsa_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成RSA密钥对
        
        Args:
            params: 包含以下字段的字典：
                - key_size: 密钥大小，默认2048
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，包含私钥信息和公钥信息
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            key_size = params.get('key_size', 2048)
            
            # 验证参数
            if key_size <= 0:
                return {
                    "success": False,
                    "error": "密钥大小必须为正数"
                }
            
            # 调用业务逻辑层
            key_id, private_key, public_key = self.key_manager.generate_rsa_key(key_size)
            private_info = self.key_manager.get_key_info(key_id)
            private_info["type"] = "RSA Private Key"
            public_info = private_info.copy()
            public_info["type"] = "RSA Public Key"
            
            return {
                "success": True,
                "data": {
                    "private_key_info": private_info,
                    "public_key_info": public_info,
                    "key_id": key_id
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_ecc_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成ECC密钥对
        
        Args:
            params: 包含以下字段的字典：
                - curve: 曲线类型，默认"secp256r1"
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，包含私钥信息和公钥信息
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            curve = params.get('curve', "secp256r1")
            
            # 验证参数
            if not curve:
                return {
                    "success": False,
                    "error": "缺少必要的曲线类型参数"
                }
            
            # 调用业务逻辑层
            key_id, private_key, public_key = self.key_manager.generate_ecc_key(curve)
            private_info = self.key_manager.get_key_info(key_id)
            private_info["type"] = "ECC Private Key"
            public_info = private_info.copy()
            public_info["type"] = "ECC Public Key"
            
            return {
                "success": True,
                "data": {
                    "private_key_info": private_info,
                    "public_key_info": public_info,
                    "key_id": key_id
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_keys(self) -> Dict[str, Any]:
        """列出所有存储的密钥
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: List[Dict[str, Any]]，密钥列表
                - error: str，错误信息（如果操作失败）
        """
        try:
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
            
            return {
                "success": True,
                "data": keys_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_key_pair(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """加载密钥对
        
        Args:
            params: 包含以下字段的字典：
                - key_id: 密钥ID
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，包含私钥和公钥
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            key_id = params.get('key_id')
            
            # 验证参数
            if not key_id:
                return {
                    "success": False,
                    "error": "缺少必要的密钥ID参数"
                }
            
            # 调用业务逻辑层
            private_key, public_key, _ = self.key_manager.load_key(key_id)
            
            return {
                "success": True,
                "data": {
                    "private_key": private_key,
                    "public_key": public_key
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """删除密钥
        
        Args:
            params: 包含以下字段的字典：
                - key_id: 密钥ID
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: bool，是否删除成功
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            key_id = params.get('key_id')
            
            # 验证参数
            if not key_id:
                return {
                    "success": False,
                    "error": "缺少必要的密钥ID参数"
                }
            
            # 调用业务逻辑层
            success = self.key_manager.delete_key(key_id)
            
            return {
                "success": True,
                "data": success
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_private_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """保存私钥
        
        Args:
            params: 包含以下字段的字典：
                - private_key: 私钥
                - file_path: 文件路径
                - password: 密码（可选）
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            private_key = params.get('private_key')
            file_path = params.get('file_path')
            password = params.get('password', None)
            
            # 验证参数
            if not private_key or not file_path:
                return {
                    "success": False,
                    "error": "缺少必要的私钥或文件路径参数"
                }
            
            # 调用业务逻辑层
            self.key_manager.save_private_key(private_key, file_path, password)
            
            return {
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_public_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """保存公钥
        
        Args:
            params: 包含以下字段的字典：
                - public_key: 公钥
                - file_path: 文件路径
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            public_key = params.get('public_key')
            file_path = params.get('file_path')
            
            # 验证参数
            if not public_key or not file_path:
                return {
                    "success": False,
                    "error": "缺少必要的公钥或文件路径参数"
                }
            
            # 调用业务逻辑层
            self.key_manager.save_public_key(public_key, file_path)
            
            return {
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_private_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """加载私钥
        
        Args:
            params: 包含以下字段的字典：
                - file_path: 文件路径
                - password: 密码（可选）
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Any，私钥
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            file_path = params.get('file_path')
            password = params.get('password', None)
            
            # 验证参数
            if not file_path:
                return {
                    "success": False,
                    "error": "缺少必要的文件路径参数"
                }
            
            # 调用业务逻辑层
            private_key = self.key_manager.load_private_key(file_path, password)
            
            return {
                "success": True,
                "data": private_key
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_public_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """加载公钥
        
        Args:
            params: 包含以下字段的字典：
                - file_path: 文件路径
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Any，公钥
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            file_path = params.get('file_path')
            
            # 验证参数
            if not file_path:
                return {
                    "success": False,
                    "error": "缺少必要的文件路径参数"
                }
            
            # 调用业务逻辑层
            public_key = self.key_manager.load_public_key(file_path)
            
            return {
                "success": True,
                "data": public_key
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_key_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取密钥信息
        
        Args:
            params: 包含以下字段的字典：
                - key: 密钥
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，密钥信息
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            key = params.get('key')
            
            # 验证参数
            if not key:
                return {
                    "success": False,
                    "error": "缺少必要的密钥参数"
                }
            
            # 从密钥对象中提取信息
            from cryptography.hazmat.primitives.asymmetric import rsa, ec
            key_info = {}
            
            if isinstance(key, rsa.RSAPrivateKey):
                key_info["type"] = "RSA Private Key"
                key_info["key_size"] = key.key_size
            elif isinstance(key, rsa.RSAPublicKey):
                key_info["type"] = "RSA Public Key"
                key_info["key_size"] = key.key_size
            elif isinstance(key, ec.EllipticCurvePrivateKey):
                key_info["type"] = "ECC Private Key"
                key_info["curve"] = key.curve.name
            elif isinstance(key, ec.EllipticCurvePublicKey):
                key_info["type"] = "ECC Public Key"
                key_info["curve"] = key.curve.name
            
            return {
                "success": True,
                "data": key_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
