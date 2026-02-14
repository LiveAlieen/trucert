from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
import json
import hashlib
from datetime import datetime
from typing import Optional, Tuple, Union
from ..storage import KeyStorage, StorageManager
from ..utils import get_logger


class KeyManager:
    def __init__(self):
        # 初始化日志记录器
        self.logger = get_logger("key_manager")
        
        self.backend = default_backend()
        self.storage_manager = StorageManager()
        self.key_storage = KeyStorage(self.storage_manager)
        self.logger.info("KeyManager initialized successfully")
    
    def generate_rsa_key(self, key_size: int = 2048, password: Optional[bytes] = None,
                        hash_algorithm: str = "sha256",
                        key_format: str = "json") -> Tuple[str, rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """生成RSA密钥对
        
        Args:
            key_size: 密钥大小
            password: 密码，用于加密私钥
            hash_algorithm: 哈希算法
            key_format: 密钥格式，支持"json"和"pem"
        
        Returns:
            密钥ID, 私钥对象, 公钥对象
        """
        try:
            self.logger.info(f"Generating RSA key with size: {key_size}")
            
            # 生成RSA密钥对
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=self.backend
            )
            
            public_key = private_key.public_key()
            
            # 保存密钥
            import datetime
            key_id = f"RSA_{int(datetime.datetime.now().timestamp())}"
            self.key_storage.save_key_pair(private_key, public_key, key_id, "RSA")
            
            self.logger.info(f"RSA key generated and saved successfully with ID: {key_id}")
            return key_id, private_key, public_key
        except Exception as e:
            self.logger.error(f"Failed to generate RSA key: {str(e)}")
            raise
    
    def generate_ecc_key(self, curve: str = "secp256r1", password: Optional[bytes] = None,
                        hash_algorithm: str = "sha256",
                        key_format: str = "json") -> Tuple[str, ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
        """生成ECC密钥对
        
        Args:
            curve: 椭圆曲线名称
            password: 密码，用于加密私钥
            hash_algorithm: 哈希算法
            key_format: 密钥格式，支持"json"和"pem"
        
        Returns:
            密钥ID, 私钥对象, 公钥对象
        """
        try:
            self.logger.info(f"Generating ECC key with curve: {curve}")
            
            # 获取曲线对象
            curve_obj = getattr(ec, curve.upper())()
            
            # 生成ECC密钥对
            private_key = ec.generate_private_key(
                curve=curve_obj,
                backend=self.backend
            )
            
            public_key = private_key.public_key()
            
            # 保存密钥
            import datetime
            key_id = f"ECC_{int(datetime.datetime.now().timestamp())}"
            self.key_storage.save_key_pair(private_key, public_key, key_id, "ECC")
            
            self.logger.info(f"ECC key generated and saved successfully with ID: {key_id}")
            return key_id, private_key, public_key
        except Exception as e:
            self.logger.error(f"Failed to generate ECC key: {str(e)}")
            raise
    
    def load_private_key(self, key_path: str, password: Optional[bytes] = None) -> Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey]:
        """加载私钥
        
        Args:
            key_path: 私钥文件路径
            password: 密码，用于解密私钥
        
        Returns:
            私钥对象
        """
        try:
            self.logger.info(f"Loading private key from: {key_path}")
            
            # 读取私钥文件
            with open(key_path, "rb") as f:
                key_data = f.read()
            
            # 加载私钥
            private_key = serialization.load_pem_private_key(
                key_data,
                password=password,
                backend=self.backend
            )
            
            self.logger.info(f"Private key loaded successfully from: {key_path}")
            return private_key
        except Exception as e:
            self.logger.error(f"Failed to load private key from {key_path}: {str(e)}")
            raise
    
    def load_public_key(self, key_path: str) -> Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]:
        """加载公钥
        
        Args:
            key_path: 公钥文件路径
        
        Returns:
            公钥对象
        """
        try:
            self.logger.info(f"Loading public key from: {key_path}")
            
            # 读取公钥文件
            with open(key_path, "rb") as f:
                key_data = f.read()
            
            # 加载公钥
            public_key = serialization.load_pem_public_key(
                key_data,
                backend=self.backend
            )
            
            self.logger.info(f"Public key loaded successfully from: {key_path}")
            return public_key
        except Exception as e:
            self.logger.error(f"Failed to load public key from {key_path}: {str(e)}")
            raise
    
    def get_key_info(self, key_identifier: str) -> dict:
        """获取密钥信息
        
        Args:
            key_identifier: 密钥ID
        
        Returns:
            密钥信息字典
        """
        try:
            self.logger.info(f"Getting key info for ID: {key_identifier}")
            # 遍历所有密钥，找到匹配的密钥ID
            all_keys = self.key_storage.list_keys()
            for key_info in all_keys:
                if key_info.get("id") == key_identifier:
                    self.logger.debug(f"Retrieved key info: {key_info}")
                    return key_info
            # 如果没有找到匹配的密钥ID，返回空字典
            self.logger.warning(f"Key with ID {key_identifier} not found")
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get key info for ID {key_identifier}: {str(e)}")
            raise
    
    def delete_key(self, key_id: str) -> bool:
        """删除密钥
        
        Args:
            key_id: 密钥ID
        
        Returns:
            是否删除成功
        """
        try:
            self.logger.info(f"Deleting key with ID: {key_id}")
            success = self.key_storage.delete_key(key_id)
            if success:
                self.logger.info(f"Key with ID {key_id} deleted successfully")
            else:
                self.logger.warning(f"Failed to delete key with ID {key_id}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to delete key with ID {key_id}: {str(e)}")
            return False
    
    def list_keys(self) -> list:
        """列出所有密钥
        
        Returns:
            密钥ID列表
        """
        try:
            self.logger.info("Listing all stored keys")
            keys_info = self.key_storage.list_keys()
            # 提取密钥ID列表
            key_ids = [key_info.get("id") for key_info in keys_info if key_info.get("id")]
            self.logger.info(f"Listed {len(key_ids)} keys")
            return key_ids
        except Exception as e:
            self.logger.error(f"Failed to list keys: {str(e)}")
            raise
    
    def save_key(self, private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey],
                public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                password: Optional[bytes] = None,
                key_type: str = "RSA",
                key_size: Optional[int] = None,
                curve: Optional[str] = None,
                hash_algorithm: str = "sha256",
                key_format: str = "json") -> str:
        """保存密钥
        
        Args:
            private_key: 私钥对象
            public_key: 公钥对象
            password: 密码，用于加密私钥
            key_type: 密钥类型，"RSA"或"ECC"
            key_size: 密钥大小，仅用于RSA
            curve: 椭圆曲线名称，仅用于ECC
            hash_algorithm: 哈希算法
            key_format: 密钥格式，支持"json"和"pem"
        
        Returns:
            密钥ID
        """
        try:
            self.logger.info(f"Saving {key_type} key")
            # 生成密钥ID
            import time
            timestamp = int(time.time())
            key_id = f"{key_type}_{timestamp}"
            
            # 保存密钥对
            self.key_storage.save_key_pair(private_key, public_key, key_id, key_type)
            
            # 保存元数据
            key_folder = os.path.join(self.storage_manager.get_key_dir(), key_id)
            metadata_path = os.path.join(key_folder, f"{key_id}_metadata.json")
            metadata = {
                "created_at": datetime.now().isoformat(),
                "timestamp": f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                "private_info": {
                    "type": f"{key_type} Private Key",
                },
                "public_info": {
                    "type": f"{key_type} Public Key",
                },
                "encrypted": False
            }
            
            # 添加RSA或ECC特定信息
            if key_type == "RSA" and key_size:
                metadata["private_info"]["key_size"] = key_size
                metadata["public_info"]["key_size"] = key_size
            elif key_type == "ECC" and curve:
                metadata["private_info"]["curve"] = curve
                metadata["public_info"]["curve"] = curve
            
            # 保存元数据
            self.storage_manager.save(metadata, metadata_path, "json")
            
            self.logger.info(f"{key_type} key saved successfully with ID: {key_id}")
            return key_id
        except Exception as e:
            self.logger.error(f"Failed to save {key_type} key: {str(e)}")
            raise
    
    def load_key(self, key_id: str, password: Optional[bytes] = None) -> tuple:
        """加载密钥
        
        Args:
            key_id: 密钥ID
            password: 密码，用于解密私钥
        
        Returns:
            (私钥对象, 公钥对象, 密钥信息)
        """
        try:
            self.logger.info(f"Loading key with ID: {key_id}")
            # 加载密钥对
            private_key, public_key = self.key_storage.load_key_pair(key_id)
            # 获取密钥信息
            key_info = self.get_key_info(key_id)
            self.logger.info(f"Key loaded successfully: {key_id}")
            return private_key, public_key, key_info
        except Exception as e:
            self.logger.error(f"Failed to load key with ID {key_id}: {str(e)}")
            raise
    
    def save_private_key(self, private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey], 
                        filepath: str, password: Optional[str] = None) -> None:
        """保存私钥
        
        Args:
            private_key: 私钥对象
            filepath: 文件路径
            password: 密码（可选）
        """
        try:
            self.logger.info(f"Saving private key to file: {filepath}")
            password_bytes = password.encode('utf-8') if password else None
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(password_bytes) if password_bytes else serialization.NoEncryption()
            )
            with open(filepath, 'wb') as f:
                f.write(pem)
            self.logger.info(f"Private key saved successfully to file: {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save private key to file {filepath}: {str(e)}")
            raise
    
    def save_public_key(self, public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey], 
                       filepath: str) -> None:
        """保存公钥
        
        Args:
            public_key: 公钥对象
            filepath: 文件路径
        """
        try:
            self.logger.info(f"Saving public key to file: {filepath}")
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            with open(filepath, 'wb') as f:
                f.write(pem)
            self.logger.info(f"Public key saved successfully to file: {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save public key to file {filepath}: {str(e)}")
            raise