# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

"""ECC签名算法模块"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.backends import default_backend
from .. import SignatureAlgorithm


class ECCSignatureAlgorithm(SignatureAlgorithm):
    """ECC签名算法实现"""
    
    name = "ECC-SIGN"
    version = "1.0"
    description = "ECC签名算法，支持数据签名和验证"
    
    def sign(self, private_key: ec.EllipticCurvePrivateKey, data: bytes, algorithm: str = "sha256", **kwargs) -> bytes:
        """使用ECC私钥签名数据
        
        Args:
            private_key: ECC私钥
            data: 要签名的数据
            algorithm: 哈希算法，默认为"sha256"
            
        Returns:
            签名数据
        """
        hash_obj = getattr(hashes, algorithm.upper())()
        signature = private_key.sign(
            data,
            ec.ECDSA(hash_obj)
        )
        return signature
    
    def verify(self, public_key: ec.EllipticCurvePublicKey, signature: bytes, data: bytes, algorithm: str = "sha256", **kwargs) -> bool:
        """使用ECC公钥验证签名
        
        Args:
            public_key: ECC公钥
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
                ec.ECDSA(hash_obj)
            )
            return True
        except Exception:
            return False
