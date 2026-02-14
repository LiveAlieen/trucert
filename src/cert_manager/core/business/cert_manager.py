from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.backends import default_backend
from datetime import datetime
from typing import Optional, Union, Dict, Any
import json
import os
from ..storage import CertStorage, StorageManager
from ..utils import get_logger


class CertManager:
    def __init__(self):
        # 初始化日志记录器
        self.logger = get_logger("cert_manager")
        
        self.backend = default_backend()
        self.storage_manager = StorageManager()
        self.cert_storage = CertStorage(self.storage_manager)
        self.logger.info("CertManager initialized successfully")
    
    def _calculate_hash(self, data: bytes) -> bytes:
        """计算数据的哈希值"""
        try:
            self.logger.debug("Calculating hash for data")
            from ..utils.hash_utils import calculate_hash
            # 使用hash_utils中的函数计算哈希值，然后转换为字节格式
            hash_hex = calculate_hash(data, "sha256")
            hash_value = bytes.fromhex(hash_hex)
            self.logger.debug("Hash calculation completed")
            return hash_value
        except Exception as e:
            self.logger.error(f"Failed to calculate hash: {str(e)}")
            raise
    
    def _generate_signature(self, private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey],
                          public_key_data: bytes,
                          timestamp: bytes,
                          offset: bytes,
                          cert_info: bytes) -> bytes:
        """Generate signature using standard algorithm with automatic hashing"""
        try:
            self.logger.debug("Generating signature for certificate")
            # Concatenate raw input components in deterministic order
            # This follows industry best practices for combining multiple inputs
            message = public_key_data + timestamp + offset + cert_info
            
            # Use private key to sign the message
            # The cryptography library automatically handles hashing as part of the standard signature process
            if isinstance(private_key, rsa.RSAPrivateKey):
                signature = private_key.sign(
                    message,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                self.logger.debug("Generated RSA signature")
            elif isinstance(private_key, ec.EllipticCurvePrivateKey):
                signature = private_key.sign(
                    message,
                    ec.ECDSA(hashes.SHA256())
                )
                self.logger.debug("Generated ECC signature")
            else:
                raise ValueError("Unsupported private key type")
            
            self.logger.debug("Signature generation completed")
            return signature
        except Exception as e:
            self.logger.error(f"Failed to generate signature: {str(e)}")
            raise
    
    def generate_self_signed_cert(self, public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                                   private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey],
                                   validity_days: int = 365,
                                   forward_offset: int = 0) -> Dict[str, Any]:
        """生成自签名证书"""
        try:
            self.logger.info("Generating self-signed certificate")
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
            self.logger.info("Self-signed certificate generated and saved successfully")
            
            return cert_data
        except Exception as e:
            self.logger.error(f"Failed to generate self-signed certificate: {str(e)}")
            raise
    
    def generate_secondary_cert(self, public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                              parent_private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey],
                              parent_public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                              validity_days: int = 365,
                              forward_offset: int = 0) -> Dict[str, Any]:
        """生成二级证书"""
        try:
            self.logger.info("Generating secondary certificate")
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
            self.logger.info("Secondary certificate generated and saved successfully")
            
            return cert_data
        except Exception as e:
            self.logger.error(f"Failed to generate secondary certificate: {str(e)}")
            raise
    
    def save_cert(self, cert_data: Dict[str, Any], filepath: str = None) -> str:
        """保存证书"""
        try:
            self.logger.info(f"Saving certificate to file: {filepath or 'default location'}")
            saved_path = self.cert_storage.save_cert(cert_data, filepath)
            self.logger.info(f"Certificate saved successfully to file: {saved_path}")
            return saved_path
        except Exception as e:
            self.logger.error(f"Failed to save certificate: {str(e)}")
            raise
    
    def load_cert(self, filepath: str) -> Dict[str, Any]:
        """加载证书"""
        try:
            self.logger.info(f"Loading certificate from file: {filepath}")
            cert_data = self.cert_storage.load_cert(filepath)
            self.logger.info(f"Certificate loaded successfully from file: {filepath}")
            return cert_data
        except Exception as e:
            self.logger.error(f"Failed to load certificate from file {filepath}: {str(e)}")
            raise
    
    def get_cert_info(self, cert_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取证书信息"""
        try:
            self.logger.debug("Getting certificate info")
            cert_info = cert_data["cert_info"]
            self.logger.debug(f"Retrieved certificate info: {cert_info}")
            return cert_info
        except Exception as e:
            self.logger.error(f"Failed to get certificate info: {str(e)}")
            raise
    
    def list_certs(self) -> list:
        """列出所有存储的证书"""
        try:
            self.logger.info("Listing all stored certificates")
            certs = self.cert_storage.list_certs()
            self.logger.info(f"Listed {len(certs)} certificates")
            return certs
        except Exception as e:
            self.logger.error(f"Failed to list certificates: {str(e)}")
            return []
    
    def delete_cert(self, filepath: str) -> bool:
        """删除证书"""
        try:
            self.logger.info(f"Attempting to delete certificate: {filepath}")
            success = self.cert_storage.delete_cert(filepath)
            if success:
                self.logger.info(f"Certificate deleted successfully: {filepath}")
            else:
                self.logger.warning(f"Failed to delete certificate: {filepath}")
            return success
        except Exception as e:
            self.logger.error(f"Error during certificate deletion: {str(e)}")
            return False
    
    def import_cert(self, filepath: str) -> Dict[str, Any]:
        """导入证书"""
        try:
            self.logger.info(f"Importing certificate from file: {filepath}")
            cert_data = self.cert_storage.import_cert(filepath)
            self.logger.info(f"Certificate imported successfully from file: {filepath}")
            return cert_data
        except Exception as e:
            self.logger.error(f"Failed to import certificate from file {filepath}: {str(e)}")
            raise
    
    def get_cert_by_filename(self, filename: str) -> Dict[str, Any]:
        """根据文件名获取证书"""
        try:
            self.logger.info(f"Getting certificate by filename: {filename}")
            cert_data = self.cert_storage.get_cert_by_filename(filename)
            self.logger.info(f"Certificate retrieved successfully by filename: {filename}")
            return cert_data
        except Exception as e:
            self.logger.error(f"Failed to get certificate by filename {filename}: {str(e)}")
            raise