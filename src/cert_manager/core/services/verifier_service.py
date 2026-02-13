from typing import Optional, Dict, Any, List, Union
from src.cert_manager.core.verifier import Verifier

class VerifierService:
    """验证服务类，封装验证功能，作为GUI和核心业务逻辑之间的桥梁"""
    
    def __init__(self):
        self.verifier = Verifier()
    
    def verify_cert_signature(self, cert: Any, parent_cert: Optional[Any] = None) -> Dict[str, Any]:
        """验证X.509证书签名
        
        Args:
            cert: X.509证书
            parent_cert: 上级X.509证书
        
        Returns:
            Dict[str, Any]: 验证结果
        """
        return self.verifier.verify_cert_signature(cert, parent_cert)
    
    def verify_file_signature(self, file_path: str, signature: bytes, public_key: Any, hash_algorithm: str = "sha256") -> Dict[str, Any]:
        """验证文件签名
        
        Args:
            file_path: 文件路径
            signature: 签名
            public_key: 公钥
            hash_algorithm: 哈希算法
        
        Returns:
            Dict[str, Any]: 验证结果
        """
        return self.verifier.verify_file_signature(file_path, signature, public_key, hash_algorithm)
    
    def verify_signed_file(self, signed_file: str, public_key: Any, hash_algorithm: str = "sha256") -> Dict[str, Any]:
        """验证带签名的文件
        
        Args:
            signed_file: 带签名的文件路径
            public_key: 公钥
            hash_algorithm: 哈希算法
        
        Returns:
            Dict[str, Any]: 验证结果
        """
        return self.verifier.verify_signed_file(signed_file, public_key, hash_algorithm)
    
    def verify_cert_chain(self, cert: Any, parent_certs: List[Any]) -> Dict[str, Any]:
        """验证证书链
        
        Args:
            cert: X.509证书
            parent_certs: 上级X.509证书列表
        
        Returns:
            Dict[str, Any]: 验证结果
        """
        return self.verifier.verify_cert_chain(cert, parent_certs)
    
    def verify_json_cert(self, cert_data: Dict[str, Any], parent_cert_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """验证自定义JSON格式证书
        
        Args:
            cert_data: 证书数据
            parent_cert_data: 上级证书数据
        
        Returns:
            Dict[str, Any]: 验证结果
        """
        return self.verifier.verify_json_cert(cert_data, parent_cert_data)
    
    def verify_signed_file_from_json(self, signed_file: str, signature_file: str, public_key: Any) -> Dict[str, Any]:
        """从JSON签名文件验证带签名的文件
        
        Args:
            signed_file: 带签名的文件路径
            signature_file: 签名文件路径
            public_key: 公钥
        
        Returns:
            Dict[str, Any]: 验证结果
        """
        return self.verifier.verify_signed_file_from_json(signed_file, signature_file, public_key)
