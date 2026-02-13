from typing import Optional, Dict, Any, List, Union
from ..business.verifier import Verifier

class VerifierService:
    """验证服务类，封装验证功能，作为GUI和核心业务逻辑之间的桥梁"""
    
    def __init__(self):
        self.verifier = Verifier()
    
    def verify_cert_signature(self, cert_data: Dict[str, Any], public_key: Any) -> bool:
        """验证证书签名
        
        Args:
            cert_data: 证书数据
            public_key: 公钥对象
        
        Returns:
            bool: 是否验证成功
        """
        return self.verifier.verify_cert_signature(cert_data, public_key)
    
    def verify_file_signature(self, file_path: str, signature: bytes, public_key: Any, hash_algorithm: str = "sha256") -> bool:
        """验证文件签名
        
        Args:
            file_path: 文件路径
            signature: 签名
            public_key: 公钥
            hash_algorithm: 哈希算法
        
        Returns:
            bool: 是否验证成功
        """
        return self.verifier.verify_file_signature(file_path, signature, public_key, hash_algorithm)
    
    def verify_signed_file(self, signed_file: str, public_key: Any, hash_algorithm: str = "sha256") -> bool:
        """验证带签名的文件
        
        Args:
            signed_file: 带签名的文件路径
            public_key: 公钥
            hash_algorithm: 哈希算法
        
        Returns:
            bool: 是否验证成功
        """
        return self.verifier.verify_signed_file(signed_file, public_key, hash_algorithm)
    
    def verify_cert_chain(self, cert_data: Dict[str, Any], parent_public_key: Any) -> bool:
        """验证证书链
        
        Args:
            cert_data: 证书数据
            parent_public_key: 父证书公钥
        
        Returns:
            bool: 是否验证成功
        """
        return self.verifier.verify_cert_chain(cert_data, parent_public_key)
    
    def verify_json_cert(self, cert_json_path: str, public_key: Any) -> bool:
        """验证JSON格式的证书
        
        Args:
            cert_json_path: 证书JSON文件路径
            public_key: 公钥对象
        
        Returns:
            bool: 是否验证成功
        """
        return self.verifier.verify_json_cert(cert_json_path, public_key)
    
    def verify_cert_data(self, cert_data: Dict[str, Any], public_key: Any) -> Dict[str, Any]:
        """验证内存中的证书数据
        
        Args:
            cert_data: 证书数据
            public_key: 公钥对象
        
        Returns:
            Dict[str, Any]: 验证结果，包含valid字段
        """
        try:
            # 验证证书签名
            signature_valid = self.verifier.verify_cert_signature(cert_data, public_key)
            
            # 构建验证结果
            result = {
                "valid": signature_valid,
                "details": {
                    "signature_valid": signature_valid
                }
            }
            
            return result
        except Exception as e:
            return {
                "valid": False,
                "details": {
                    "error": str(e)
                }
            }
    
    def verify_signature_from_json(self, signature_json_path: str, file_path: str, public_key: Any) -> bool:
        """从JSON文件验证签名
        
        Args:
            signature_json_path: 签名JSON文件路径
            file_path: 文件路径
            public_key: 公钥对象
        
        Returns:
            bool: 是否验证成功
        """
        return self.verifier.verify_signature_from_json(signature_json_path, file_path, public_key)
