from typing import Optional, Dict, Any, List, Union
from ..business.verifier import Verifier

class VerifierService:
    """验证服务类，封装验证功能，作为GUI和核心业务逻辑之间的桥梁"""
    
    def __init__(self):
        self.verifier = Verifier()
    
    def verify_cert_signature(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证证书签名
        
        Args:
            params: 包含以下字段的字典：
                - cert_data: 证书数据
                - public_key: 公钥对象
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: bool，是否验证成功
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            cert_data = params.get('cert_data')
            public_key = params.get('public_key')
            
            # 验证参数
            if not cert_data or not public_key:
                return {
                    "success": False,
                    "error": "缺少必要的证书数据或公钥参数"
                }
            
            # 调用业务逻辑层
            result = self.verifier.verify_cert_signature(cert_data, public_key)
            
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_file_signature(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证文件签名
        
        Args:
            params: 包含以下字段的字典：
                - file_path: 文件路径
                - signature: 签名
                - public_key: 公钥
                - hash_algorithm: 哈希算法，默认"sha256"
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，验证结果
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            file_path = params.get('file_path')
            signature = params.get('signature')
            public_key = params.get('public_key')
            hash_algorithm = params.get('hash_algorithm', 'sha256')
            
            # 验证参数
            if not file_path or not signature or not public_key:
                return {
                    "success": False,
                    "error": "缺少必要的文件路径、签名或公钥参数"
                }
            
            # 调用业务逻辑层
            result = self.verifier.verify_file_signature(file_path, signature, public_key, hash_algorithm)
            
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_signed_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证带签名的文件
        
        Args:
            params: 包含以下字段的字典：
                - signed_file: 带签名的文件路径
                - public_key: 公钥
                - hash_algorithm: 哈希算法，默认"sha256"
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，验证结果
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            signed_file = params.get('signed_file')
            public_key = params.get('public_key')
            hash_algorithm = params.get('hash_algorithm', 'sha256')
            
            # 验证参数
            if not signed_file or not public_key:
                return {
                    "success": False,
                    "error": "缺少必要的带签名文件路径或公钥参数"
                }
            
            # 调用业务逻辑层
            result = self.verifier.verify_signed_file(signed_file, public_key, hash_algorithm)
            
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_cert_chain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证证书链
        
        Args:
            params: 包含以下字段的字典：
                - cert_data: 证书数据
                - parent_public_key: 父证书公钥
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: bool，是否验证成功
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            cert_data = params.get('cert_data')
            parent_public_key = params.get('parent_public_key')
            
            # 验证参数
            if not cert_data or not parent_public_key:
                return {
                    "success": False,
                    "error": "缺少必要的证书数据或父证书公钥参数"
                }
            
            # 调用业务逻辑层
            result = self.verifier.verify_cert_chain(cert_data, parent_public_key)
            
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_json_cert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证JSON格式的证书
        
        Args:
            params: 包含以下字段的字典：
                - cert_json_path: 证书JSON文件路径
                - public_key: 公钥对象
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: bool，是否验证成功
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            cert_json_path = params.get('cert_json_path')
            public_key = params.get('public_key')
            
            # 验证参数
            if not cert_json_path or not public_key:
                return {
                    "success": False,
                    "error": "缺少必要的证书JSON文件路径或公钥参数"
                }
            
            # 加载证书数据
            cert_data = self.verifier.load_json_cert(cert_json_path)
            
            # 验证证书
            result = self.verifier.verify_json_cert(cert_data, public_key)
            
            return {
                "success": True,
                "data": result['valid']
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_cert_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证内存中的证书数据
        
        Args:
            params: 包含以下字段的字典：
                - cert_data: 证书数据
                - public_key: 公钥对象
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，验证结果
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            cert_data = params.get('cert_data')
            public_key = params.get('public_key')
            
            # 验证参数
            if not cert_data or not public_key:
                return {
                    "success": False,
                    "error": "缺少必要的证书数据或公钥参数"
                }
            
            # 验证证书签名
            signature_valid = self.verifier.verify_cert_signature(cert_data, public_key)
            
            # 构建验证结果
            result = {
                "valid": signature_valid,
                "details": {
                    "signature_valid": signature_valid
                }
            }
            
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_signature_from_json(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """从JSON文件验证签名
        
        Args:
            params: 包含以下字段的字典：
                - signature_json_path: 签名JSON文件路径
                - file_path: 文件路径
                - public_key: 公钥对象
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，验证结果
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            signature_json_path = params.get('signature_json_path')
            file_path = params.get('file_path')
            public_key = params.get('public_key')
            
            # 验证参数
            if not signature_json_path or not file_path or not public_key:
                return {
                    "success": False,
                    "error": "缺少必要的签名JSON文件路径、文件路径或公钥参数"
                }
            
            # 调用业务逻辑层
            result = self.verifier.verify_signature_from_json(signature_json_path, file_path, public_key)
            
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_json_cert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """加载JSON格式的证书
        
        Args:
            params: 包含以下字段的字典：
                - cert_json_path: 证书JSON文件路径
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，证书数据
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            cert_json_path = params.get('cert_json_path')
            
            # 验证参数
            if not cert_json_path:
                return {
                    "success": False,
                    "error": "缺少必要的证书JSON文件路径参数"
                }
            
            # 调用业务逻辑层
            cert_data = self.verifier.load_json_cert(cert_json_path)
            
            return {
                "success": True,
                "data": cert_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
