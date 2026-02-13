from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
import json
import hashlib
from typing import Optional, Tuple, Union
from .storage import KeyStorage, StorageManager

class KeyManager:
    def __init__(self, config_dir: str = "configs", root_key_dir: str = "root_key"):
        self.backend = default_backend()
        self.storage_manager = StorageManager()
        self.key_storage = KeyStorage(self.storage_manager)
        # 加载或生成根密钥对
        self.root_private_key, self.root_public_key = self._load_or_generate_root_key()
    
    def _load_or_generate_root_key(self) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """加载或生成根密钥对"""
        try:
            # 尝试加载现有根密钥对
            return self.key_storage.load_root_key_pair()
        except FileNotFoundError:
            # 生成新根密钥对
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=self.backend
            )
            public_key = private_key.public_key()
            
            # 保存根密钥对
            self.key_storage.save_root_key_pair(private_key, public_key)
            
            return private_key, public_key
    
    def generate_rsa_key(self, key_size: int = 2048, auto_save: bool = True) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=self.backend
        )
        public_key = private_key.public_key()
        
        if auto_save:
            self.save_keys_to_config(private_key, public_key, "RSA")
        
        return private_key, public_key
    
    def generate_ecc_key(self, curve: str = "SECP256R1", auto_save: bool = True) -> Tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
        # 确保曲线名称大写
        curve_upper = curve.upper()
        curve_obj = getattr(ec, curve_upper)()
        private_key = ec.generate_private_key(
            curve=curve_obj,
            backend=self.backend
        )
        public_key = private_key.public_key()
        
        if auto_save:
            self.save_keys_to_config(private_key, public_key, "ECC")
        
        return private_key, public_key
    
    def save_private_key(self, private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey], 
                        filepath: str, password: Optional[str] = None, 
                        format: str = "pem") -> None:
        if format.lower() == "pem":
            self.key_storage.save_private_key(private_key, filepath, password)
        elif format.lower() == "der":
            # DER格式暂不支持，仅支持PEM格式
            raise ValueError("Unsupported format. Use 'pem'")
        else:
            raise ValueError("Unsupported format. Use 'pem'")
    
    def save_public_key(self, public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey], 
                       filepath: str, format: str = "pem") -> None:
        if format.lower() == "pem":
            self.key_storage.save_public_key(public_key, filepath)
        elif format.lower() == "der":
            # DER格式暂不支持，仅支持PEM格式
            raise ValueError("Unsupported format. Use 'pem'")
        else:
            raise ValueError("Unsupported format. Use 'pem'")
    
    def load_private_key(self, filepath: str, password: Optional[str] = None) -> Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey]:
        return self.key_storage.load_private_key(filepath, password)
    
    def load_public_key(self, filepath: str) -> Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]:
        return self.key_storage.load_public_key(filepath)
    
    def get_key_info(self, key: Union[rsa.RSAPrivateKey, rsa.RSAPublicKey, 
                                     ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]) -> dict:
        info = {}
        
        if isinstance(key, rsa.RSAPrivateKey):
            info["type"] = "RSA Private Key"
            info["key_size"] = key.key_size
        elif isinstance(key, rsa.RSAPublicKey):
            info["type"] = "RSA Public Key"
            info["key_size"] = key.key_size
        elif isinstance(key, ec.EllipticCurvePrivateKey):
            info["type"] = "ECC Private Key"
            info["curve"] = key.curve.name
        elif isinstance(key, ec.EllipticCurvePublicKey):
            info["type"] = "ECC Public Key"
            info["curve"] = key.curve.name
        
        return info
    
    def save_keys_to_config(self, private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey],
                           public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                           key_type: str) -> None:
        """将密钥对安全存储到key文件夹中"""
        # 生成密钥ID
        import datetime
        now = datetime.datetime.now()
        # 生成简洁的ID格式：类型_时间戳
        key_id = f"{key_type}_{int(now.timestamp())}"
        
        # 保存密钥对
        self.key_storage.save_key_pair(private_key, public_key, key_id, key_type)
        
        # 创建元数据文件
        metadata = {
            "id": key_id,
            "type": key_type,
            "created_at": now.isoformat(),
            "timestamp": now.strftime("%Y%m%d_%H%M%S_%f"),
            "private_info": self.get_key_info(private_key),
            "public_info": self.get_key_info(public_key),
            "encrypted": True
        }
        
        # 保存元数据
        key_folder = os.path.join(self.key_storage.key_dir, key_id)
        metadata_path = os.path.join(key_folder, f"{key_id}_metadata.json")
        self.storage_manager.save(metadata, metadata_path, "json")
        
        # 用根私钥对元数据文件进行签名
        with open(metadata_path, 'rb') as f:
            metadata_data = f.read()
        
        # 计算元数据的哈希值
        metadata_hash = hashlib.sha256(metadata_data).digest()
        
        # 使用根私钥签名
        signature = self.root_private_key.sign(
            metadata_hash,
            PKCS1v15(),
            hashes.SHA256()
        )
        
        signature_path = os.path.join(key_folder, f"{key_id}_signature.txt")
        with open(signature_path, 'w', encoding='utf-8') as f:
            f.write(signature.hex())
    
    def load_keys_from_config(self, key_id: str) -> Tuple[Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey], Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]]:
        """从key文件夹加载密钥对"""
        return self.key_storage.load_key_pair(key_id)
    
    def list_keys(self, sort_by_time: bool = True, reverse: bool = True) -> list:
        """列出所有存储的密钥
        
        Args:
            sort_by_time: 是否按时间排序
            reverse: 是否倒序（最新的在前）
        """
        keys = self.key_storage.list_keys()
        
        # 按时间排序
        if sort_by_time:
            keys.sort(key=lambda x: x.get("created_at", ""), reverse=reverse)
        
        return keys
    
    def delete_key(self, key_id: str) -> bool:
        """从key文件夹中删除指定的密钥"""
        return self.key_storage.delete_key(key_id)
    
    def get_root_key_pair(self) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """获取根密钥对"""
        return self.root_private_key, self.root_public_key
