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
from .utils import get_logger


class KeyManager:
    def __init__(self, config_dir: str = "configs", root_key_dir: str = "root_key"):
        # 初始化日志记录器
        self.logger = get_logger("key_manager")
        
        self.backend = default_backend()
        self.storage_manager = StorageManager()
        self.key_storage = KeyStorage(self.storage_manager)
        # 加载或生成根密钥对
        self.logger.info("Initializing KeyManager")
        self.root_private_key, self.root_public_key = self._load_or_generate_root_key()
        self.logger.info("KeyManager initialized successfully")
    
    def _load_or_generate_root_key(self) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """加载或生成根密钥对"""
        try:
            # 尝试加载现有根密钥对
            self.logger.info("Attempting to load existing root key pair")
            private_key, public_key = self.key_storage.load_root_key_pair()
            self.logger.info("Root key pair loaded successfully")
            return private_key, public_key
        except FileNotFoundError:
            # 生成新根密钥对
            self.logger.info("Root key pair not found, generating new one")
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=self.backend
            )
            public_key = private_key.public_key()
            
            # 保存根密钥对
            self.key_storage.save_root_key_pair(private_key, public_key)
            self.logger.info("New root key pair generated and saved successfully")
            
            return private_key, public_key
        except Exception as e:
            self.logger.error(f"Failed to load or generate root key pair: {str(e)}")
            raise
    
    def generate_rsa_key(self, key_size: int = 2048, auto_save: bool = True) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        try:
            self.logger.info(f"Generating RSA key pair with key size: {key_size}")
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=self.backend
            )
            public_key = private_key.public_key()
            self.logger.info(f"RSA key pair generated successfully with key size: {key_size}")
            
            if auto_save:
                self.logger.info("Auto-saving RSA key pair to config")
                self.save_keys_to_config(private_key, public_key, "RSA")
                self.logger.info("RSA key pair saved to config")
            
            return private_key, public_key
        except Exception as e:
            self.logger.error(f"Failed to generate RSA key pair: {str(e)}")
            raise
    
    def generate_ecc_key(self, curve: str = "SECP256R1", auto_save: bool = True) -> Tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
        try:
            # 确保曲线名称大写
            curve_upper = curve.upper()
            self.logger.info(f"Generating ECC key pair with curve: {curve_upper}")
            curve_obj = getattr(ec, curve_upper)()
            private_key = ec.generate_private_key(
                curve=curve_obj,
                backend=self.backend
            )
            public_key = private_key.public_key()
            self.logger.info(f"ECC key pair generated successfully with curve: {curve_upper}")
            
            if auto_save:
                self.logger.info("Auto-saving ECC key pair to config")
                self.save_keys_to_config(private_key, public_key, "ECC")
                self.logger.info("ECC key pair saved to config")
            
            return private_key, public_key
        except Exception as e:
            self.logger.error(f"Failed to generate ECC key pair: {str(e)}")
            raise
    
    def save_private_key(self, private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey], 
                        filepath: str, password: Optional[str] = None, 
                        format: str = "pem") -> None:
        try:
            if format.lower() == "pem":
                self.logger.info(f"Saving private key to file: {filepath}")
                self.key_storage.save_private_key(private_key, filepath, password)
                self.logger.info(f"Private key saved successfully to file: {filepath}")
            elif format.lower() == "der":
                # DER格式暂不支持，仅支持PEM格式
                self.logger.warning("Attempted to save private key in DER format, which is not supported")
                raise ValueError("Unsupported format. Use 'pem'")
            else:
                self.logger.warning(f"Attempted to save private key in unsupported format: {format}")
                raise ValueError("Unsupported format. Use 'pem'")
        except Exception as e:
            self.logger.error(f"Failed to save private key to file {filepath}: {str(e)}")
            raise
    
    def save_public_key(self, public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey], 
                       filepath: str, format: str = "pem") -> None:
        try:
            if format.lower() == "pem":
                self.logger.info(f"Saving public key to file: {filepath}")
                self.key_storage.save_public_key(public_key, filepath)
                self.logger.info(f"Public key saved successfully to file: {filepath}")
            elif format.lower() == "der":
                # DER格式暂不支持，仅支持PEM格式
                self.logger.warning("Attempted to save public key in DER format, which is not supported")
                raise ValueError("Unsupported format. Use 'pem'")
            else:
                self.logger.warning(f"Attempted to save public key in unsupported format: {format}")
                raise ValueError("Unsupported format. Use 'pem'")
        except Exception as e:
            self.logger.error(f"Failed to save public key to file {filepath}: {str(e)}")
            raise
    
    def load_private_key(self, filepath: str, password: Optional[str] = None) -> Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey]:
        try:
            self.logger.info(f"Loading private key from file: {filepath}")
            private_key = self.key_storage.load_private_key(filepath, password)
            self.logger.info(f"Private key loaded successfully from file: {filepath}")
            return private_key
        except Exception as e:
            self.logger.error(f"Failed to load private key from file {filepath}: {str(e)}")
            raise
    
    def load_public_key(self, filepath: str) -> Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]:
        try:
            self.logger.info(f"Loading public key from file: {filepath}")
            public_key = self.key_storage.load_public_key(filepath)
            self.logger.info(f"Public key loaded successfully from file: {filepath}")
            return public_key
        except Exception as e:
            self.logger.error(f"Failed to load public key from file {filepath}: {str(e)}")
            raise
    
    def get_key_info(self, key: Union[rsa.RSAPrivateKey, rsa.RSAPublicKey, 
                                     ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]) -> dict:
        try:
            info = {}
            
            if isinstance(key, rsa.RSAPrivateKey):
                info["type"] = "RSA Private Key"
                info["key_size"] = key.key_size
                self.logger.debug("Retrieved info for RSA private key")
            elif isinstance(key, rsa.RSAPublicKey):
                info["type"] = "RSA Public Key"
                info["key_size"] = key.key_size
                self.logger.debug("Retrieved info for RSA public key")
            elif isinstance(key, ec.EllipticCurvePrivateKey):
                info["type"] = "ECC Private Key"
                info["curve"] = key.curve.name
                self.logger.debug("Retrieved info for ECC private key")
            elif isinstance(key, ec.EllipticCurvePublicKey):
                info["type"] = "ECC Public Key"
                info["curve"] = key.curve.name
                self.logger.debug("Retrieved info for ECC public key")
            
            return info
        except Exception as e:
            self.logger.error(f"Failed to get key info: {str(e)}")
            return {}
    
    def save_keys_to_config(self, private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey],
                           public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                           key_type: str) -> None:
        """将密钥对安全存储到key文件夹中"""
        try:
            # 生成密钥ID
            import datetime
            now = datetime.datetime.now()
            # 生成简洁的ID格式：类型_时间戳
            key_id = f"{key_type}_{int(now.timestamp())}"
            self.logger.info(f"Saving key pair to config with ID: {key_id}")
            
            # 保存密钥对
            self.key_storage.save_key_pair(private_key, public_key, key_id, key_type)
            self.logger.debug(f"Saved key pair with ID: {key_id}")
            
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
            self.logger.debug(f"Saved metadata for key pair: {metadata_path}")
            
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
            self.logger.debug(f"Saved signature for key pair: {signature_path}")
            self.logger.info(f"Key pair saved to config successfully with ID: {key_id}")
        except Exception as e:
            self.logger.error(f"Failed to save key pair to config: {str(e)}")
            raise
    
    def load_keys_from_config(self, key_id: str) -> Tuple[Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey], Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]]:
        """从key文件夹加载密钥对"""
        try:
            self.logger.info(f"Loading key pair from config with ID: {key_id}")
            private_key, public_key = self.key_storage.load_key_pair(key_id)
            self.logger.info(f"Key pair loaded successfully from config with ID: {key_id}")
            return private_key, public_key
        except Exception as e:
            self.logger.error(f"Failed to load key pair from config with ID {key_id}: {str(e)}")
            raise
    
    def list_keys(self, sort_by_time: bool = True, reverse: bool = True) -> list:
        """列出所有存储的密钥
        
        Args:
            sort_by_time: 是否按时间排序
            reverse: 是否倒序（最新的在前）
        """
        try:
            self.logger.info("Listing all stored keys")
            keys = self.key_storage.list_keys()
            
            # 按时间排序
            if sort_by_time:
                keys.sort(key=lambda x: x.get("created_at", ""), reverse=reverse)
                self.logger.debug(f"Sorted keys by time, reverse={reverse}")
            
            self.logger.info(f"Listed {len(keys)} keys")
            return keys
        except Exception as e:
            self.logger.error(f"Failed to list keys: {str(e)}")
            return []
    
    def delete_key(self, key_id: str) -> bool:
        """从key文件夹中删除指定的密钥"""
        try:
            self.logger.info(f"Attempting to delete key with ID: {key_id}")
            success = self.key_storage.delete_key(key_id)
            if success:
                self.logger.info(f"Key deleted successfully with ID: {key_id}")
            else:
                self.logger.warning(f"Failed to delete key with ID: {key_id}")
            return success
        except Exception as e:
            self.logger.error(f"Error during key deletion with ID {key_id}: {str(e)}")
            return False
    
    def get_root_key_pair(self) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """获取根密钥对"""
        self.logger.debug("Getting root key pair")
        return self.root_private_key, self.root_public_key
