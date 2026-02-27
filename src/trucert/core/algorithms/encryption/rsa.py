# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

"""RSA加密算法模块"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from .. import EncryptionAlgorithm


class RSAAlgorithm(EncryptionAlgorithm):
    """RSA加密算法实现"""
    
    name = "RSA"
    version = "1.0"
    description = "RSA加密算法，支持密钥生成、加密和解密"
    
    def generate_key(self, key_size: int = 2048, **kwargs) -> tuple:
        """生成RSA密钥对
        
        Args:
            key_size: 密钥大小，默认为2048位
            
        Returns:
            (私钥, 公钥)元组
        """
        backend = default_backend()
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=backend
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    def encrypt(self, public_key: rsa.RSAPublicKey, data: bytes) -> bytes:
        """使用RSA公钥加密数据
        
        Args:
            public_key: RSA公钥
            data: 要加密的数据
            
        Returns:
            加密后的数据
        """
        hash_obj = hashes.SHA256()
        encrypted_data = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(hash_obj),
                algorithm=hash_obj,
                label=None
            )
        )
        return encrypted_data
    
    def decrypt(self, private_key: rsa.RSAPrivateKey, encrypted_data: bytes) -> bytes:
        """使用RSA私钥解密数据
        
        Args:
            private_key: RSA私钥
            encrypted_data: 加密的数据
            
        Returns:
            解密后的数据
        """
        hash_obj = hashes.SHA256()
        decrypted_data = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(hash_obj),
                algorithm=hash_obj,
                label=None
            )
        )
        return decrypted_data
