"""RSA签名算法模块"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from src.cert_manager.core.algorithms import SignatureAlgorithm


class RSASignatureAlgorithm(SignatureAlgorithm):
    """RSA签名算法实现"""
    
    name = "RSA-SIGN"
    version = "1.0"
    description = "RSA签名算法，支持数据签名和验证"
    
    def sign(self, private_key: rsa.RSAPrivateKey, data: bytes, algorithm: str = "sha256", **kwargs) -> bytes:
        """使用RSA私钥签名数据
        
        Args:
            private_key: RSA私钥
            data: 要签名的数据
            algorithm: 哈希算法，默认为"sha256"
            
        Returns:
            签名数据
        """
        hash_obj = getattr(hashes, algorithm.upper())()
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hash_obj),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hash_obj
        )
        return signature
    
    def verify(self, public_key: rsa.RSAPublicKey, signature: bytes, data: bytes, algorithm: str = "sha256", **kwargs) -> bool:
        """使用RSA公钥验证签名
        
        Args:
            public_key: RSA公钥
            signature: 签名数据
            data: 原始数据
            algorithm: 哈希算法，默认为"sha256"
            
        Returns:
            签名是否有效
        """
        hash_obj = getattr(hashes, algorithm.upper())()
        
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hash_obj),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hash_obj
            )
            return True
        except Exception:
            return False
