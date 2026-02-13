from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.backends import default_backend
from datetime import datetime
from typing import Optional, Union, Dict, Any
import json
import os
import hashlib
from src.cert_manager.core.storage import CertStorage, StorageManager

class CertManager:
    def __init__(self):
        self.backend = default_backend()
        self.storage_manager = StorageManager()
        self.cert_storage = CertStorage(self.storage_manager)
    
    def _calculate_hash(self, data: bytes) -> bytes:
        """计算数据的哈希值"""
        return hashlib.sha256(data).digest()
    
    def _generate_signature(self, private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey],
                          public_key_data: bytes,
                          timestamp: bytes,
                          offset: bytes,
                          cert_info: bytes) -> bytes:
        """Generate signature using standard algorithm with automatic hashing"""
        # Concatenate raw input components in deterministic order
        # This follows industry best practices for combining multiple inputs
        message = public_key_data + timestamp + offset + cert_info
        
        # Use private key to sign the message
        # The cryptography library automatically handles hashing as part of the standard signature process
        if isinstance(private_key, rsa.RSAPrivateKey):
            return private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        elif isinstance(private_key, ec.EllipticCurvePrivateKey):
            return private_key.sign(
                message,
                ec.ECDSA(hashes.SHA256())
            )
    
    def generate_self_signed_cert(self, public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                                   private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey],
                                   validity_days: int = 365,
                                   forward_offset: int = 0) -> Dict[str, Any]:
        """生成自签名证书"""
        # 计算时间戳
        now = datetime.utcnow()
        timestamp_str = now.isoformat()
        
        # 生成证书信息
        cert_info = {
            "algorithm": "RSA" if isinstance(private_key, rsa.RSAPrivateKey) else "ECC",
            "signature_algorithm": "RSA-PSS-SHA256" if isinstance(private_key, rsa.RSAPrivateKey) else "ECDSA-SHA256",
            "storage_formats": {
                "public_key": "DER_HEX",
                "signature": "HEX",
                "parent_public_key": "DER_HEX"
            },
            "parent_public_key": ""
        }
        
        # 转换为字节
        public_key_data = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        timestamp = str(int(now.timestamp())).encode('utf-8')
        offset = str(forward_offset).encode('utf-8')
        cert_info_bytes = json.dumps(cert_info, sort_keys=True).encode('utf-8')
        
        # 生成签名
        signature = self._generate_signature(
            private_key,
            public_key_data,
            timestamp,
            offset,
            cert_info_bytes
        )
        signature_hex = signature.hex()
        
        # 构建证书数据
        cert_data = {
            "timestamp": timestamp_str,
            "forward_offset": forward_offset,
            "cert_info": cert_info,
            "public_key": public_key_data.hex(),
            "signature": signature_hex
        }
        
        # 自动保存到trust文件夹
        self.cert_storage.save_cert(cert_data)
        
        return cert_data
    
    def generate_secondary_cert(self, public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                              parent_private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey],
                              parent_public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                              validity_days: int = 365,
                              forward_offset: int = 0) -> Dict[str, Any]:
        """生成二级证书"""
        # 计算时间戳
        now = datetime.utcnow()
        timestamp_str = now.isoformat()
        
        # 生成证书信息
        cert_info = {
            "algorithm": "RSA" if isinstance(public_key, rsa.RSAPublicKey) else "ECC",
            "signature_algorithm": "RSA-PSS-SHA256" if isinstance(parent_private_key, rsa.RSAPrivateKey) else "ECDSA-SHA256",
            "storage_formats": {
                "public_key": "DER_HEX",
                "signature": "HEX",
                "parent_public_key": "DER_HEX"
            }
        }
        
        # 转换为字节
        public_key_data = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        timestamp = str(int(now.timestamp())).encode('utf-8')
        offset = str(forward_offset).encode('utf-8')
        cert_info_bytes = json.dumps(cert_info, sort_keys=True).encode('utf-8')
        
        # 生成签名
        signature = self._generate_signature(
            parent_private_key,
            public_key_data,
            timestamp,
            offset,
            cert_info_bytes
        )
        signature_hex = signature.hex()
        
        # 获取上级证书公钥的字节表示
        parent_public_key_data = parent_public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        parent_public_key_hex = parent_public_key_data.hex()
        
        # 添加parent_public_key到cert_info
        cert_info["parent_public_key"] = parent_public_key_hex
        
        # 构建证书数据
        cert_data = {
            "timestamp": timestamp_str,
            "forward_offset": forward_offset,
            "cert_info": cert_info,
            "public_key": public_key_data.hex(),
            "signature": signature_hex
        }
        
        # 自动保存到trust文件夹
        self.cert_storage.save_cert(cert_data)
        
        return cert_data
    
    def save_cert(self, cert_data: Dict[str, Any], filepath: str = None) -> str:
        """保存证书"""
        return self.cert_storage.save_cert(cert_data, filepath)
    
    def load_cert(self, filepath: str) -> Dict[str, Any]:
        """加载证书"""
        return self.cert_storage.load_cert(filepath)
    
    def get_cert_info(self, cert_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取证书信息"""
        return cert_data["cert_info"]
    
    def list_certs(self) -> list:
        """列出所有存储的证书"""
        return self.cert_storage.list_certs()
    
    def delete_cert(self, filepath: str) -> bool:
        """删除证书"""
        return self.cert_storage.delete_cert(filepath)
    
    def import_cert(self, filepath: str) -> Dict[str, Any]:
        """导入证书"""
        return self.cert_storage.import_cert(filepath)
    
    def get_cert_by_filename(self, filename: str) -> Dict[str, Any]:
        """根据文件名获取证书"""
        return self.cert_storage.get_cert_by_filename(filename)
