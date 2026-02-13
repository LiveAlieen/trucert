from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
import json
import os
import hashlib

class CertManager:
    def __init__(self):
        self.backend = default_backend()
        # 初始化trust文件夹路径
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs")
        self.trust_dir = os.path.join(self.config_dir, "trust")
        # 创建trust文件夹
        os.makedirs(self.trust_dir, exist_ok=True)
    
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
        timestamp = int(now.timestamp())
        cert_filename = f"self_signed_{timestamp}.json"
        cert_path = os.path.join(self.trust_dir, cert_filename)
        self.save_cert(cert_data, cert_path)
        
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
        timestamp = int(now.timestamp())
        cert_filename = f"secondary_{timestamp}.json"
        cert_path = os.path.join(self.trust_dir, cert_filename)
        self.save_cert(cert_data, cert_path)
        
        return cert_data
    
    def save_cert(self, cert_data: Dict[str, Any], filepath: str) -> None:
        """保存证书"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cert_data, f, indent=2, ensure_ascii=False)
    
    def load_cert(self, filepath: str) -> Dict[str, Any]:
        """加载证书"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_cert_info(self, cert_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取证书信息"""
        return cert_data["cert_info"]
    
    def list_certs(self) -> list:
        """列出所有存储的证书"""
        certs = []
        if not os.path.exists(self.trust_dir):
            return certs
        
        for filename in os.listdir(self.trust_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.trust_dir, filename)
                try:
                    cert_data = self.load_cert(filepath)
                    # 添加文件名和路径信息
                    # 根据文件名判断证书类型和是否为根证书
                    if "self_signed" in filename:
                        cert_type = "self_signed"
                        is_root_cert = True
                    elif "secondary" in filename:
                        cert_type = "secondary"
                        is_root_cert = False
                    else:
                        cert_type = "unknown"
                        is_root_cert = False
                    
                    cert_info = {
                        "filename": filename,
                        "path": filepath,
                        "type": cert_type,
                        "is_root_cert": is_root_cert,
                        "cert_info": cert_data.get("cert_info", {})
                    }
                    certs.append(cert_info)
                except Exception as e:
                    print(f"加载证书文件 {filename} 失败: {str(e)}")
        
        # 按时间戳排序（最新的在前）
        certs.sort(key=lambda x: x["cert_info"].get("timestamp", ""), reverse=True)
        return certs
    
    def delete_cert(self, filepath: str) -> bool:
        """删除证书"""
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except Exception as e:
                print(f"删除证书文件 {filepath} 失败: {str(e)}")
                return False
        return False
    
    def import_cert(self, filepath: str) -> Dict[str, Any]:
        """导入证书"""
        # 加载证书数据
        cert_data = self.load_cert(filepath)
        
        # 生成新的文件名（基于时间戳）
        timestamp = int(datetime.utcnow().timestamp())
        cert_type = cert_data.get("type", "unknown")
        new_filename = f"{cert_type}_{timestamp}.json"
        new_filepath = os.path.join(self.trust_dir, new_filename)
        
        # 保存到trust文件夹
        self.save_cert(cert_data, new_filepath)
        
        return cert_data
