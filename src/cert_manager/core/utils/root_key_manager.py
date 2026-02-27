"""根密钥管理模块

用于生成、存储和管理根密钥，为私钥加密提供基础密钥
"""

import os
import json
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional, Union, Dict, Any
import base64


class RootKeyManager:
    """根密钥管理器"""
    
    def __init__(self, root_key_path: str = None):
        """初始化根密钥管理器
        
        Args:
            root_key_path: 根密钥存储路径，如果为None则使用默认路径
        """
        if root_key_path is None:
            self.root_key_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "..", "configs", "root_key.json"
            )
        else:
            self.root_key_path = root_key_path
        
        self.backend = default_backend()
        self.root_key = None
        self.salt = None
        self.iterations = 100000
        
    def _ensure_directory(self, path: str):
        """确保目录存在"""
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
    
    def generate_root_key(self) -> bytes:
        """生成根密钥
        
        Returns:
            bytes: 生成的根密钥
        """
        # 生成随机盐值
        self.salt = os.urandom(16)
        
        # 生成随机主密钥
        master_key = os.urandom(32)  # 256位密钥
        
        # 使用PBKDF2派生根密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=self.iterations,
            backend=self.backend
        )
        
        self.root_key = kdf.derive(master_key)
        return self.root_key
    
    def save_root_key(self) -> None:
        """保存根密钥到文件
        
        注意：根密钥将以加密形式存储
        """
        if not self.root_key:
            raise ValueError("根密钥未生成")
        
        # 生成临时加密密钥（用于加密根密钥）
        temp_key = os.urandom(32)
        iv = os.urandom(16)
        
        # 加密根密钥
        cipher = Cipher(
            algorithms.AES(temp_key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # 对根密钥进行填充
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(self.root_key) + padder.finalize()
        
        # 加密数据
        encrypted_root_key = encryptor.update(padded_data) + encryptor.finalize()
        
        # 生成验证哈希
        h = hashes.Hash(hashes.SHA256(), backend=self.backend)
        h.update(self.root_key)
        key_hash = h.finalize()
        
        # 保存到文件
        self._ensure_directory(self.root_key_path)
        with open(self.root_key_path, 'w', encoding='utf-8') as f:
            json.dump({
                "salt": base64.b64encode(self.salt).decode('utf-8'),
                "iterations": self.iterations,
                "temp_key": base64.b64encode(temp_key).decode('utf-8'),
                "iv": base64.b64encode(iv).decode('utf-8'),
                "encrypted_root_key": base64.b64encode(encrypted_root_key).decode('utf-8'),
                "key_hash": base64.b64encode(key_hash).decode('utf-8')
            }, f, indent=2, ensure_ascii=False)
    
    def load_root_key(self) -> Optional[bytes]:
        """从文件加载根密钥
        
        Returns:
            Optional[bytes]: 加载的根密钥，如果加载失败返回None
        """
        try:
            if not os.path.exists(self.root_key_path):
                return None
            
            with open(self.root_key_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取数据
            self.salt = base64.b64decode(data['salt'])
            self.iterations = data['iterations']
            temp_key = base64.b64decode(data['temp_key'])
            iv = base64.b64decode(data['iv'])
            encrypted_root_key = base64.b64decode(data['encrypted_root_key'])
            key_hash = base64.b64decode(data['key_hash'])
            
            # 解密根密钥
            cipher = Cipher(
                algorithms.AES(temp_key),
                modes.CBC(iv),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(encrypted_root_key) + decryptor.finalize()
            
            # 移除填充
            unpadder = padding.PKCS7(128).unpadder()
            self.root_key = unpadder.update(padded_data) + unpadder.finalize()
            
            # 验证哈希
            h = hashes.Hash(hashes.SHA256(), backend=self.backend)
            h.update(self.root_key)
            computed_hash = h.finalize()
            
            if computed_hash != key_hash:
                raise ValueError("根密钥哈希验证失败")
            
            return self.root_key
        except Exception as e:
            print(f"加载根密钥失败: {str(e)}")
            return None
    
    def get_root_key(self) -> bytes:
        """获取根密钥
        
        如果根密钥未加载，则尝试从文件加载；如果文件不存在，则生成新的根密钥
        
        Returns:
            bytes: 根密钥
        """
        if not self.root_key:
            # 尝试从文件加载
            if not self.load_root_key():
                # 生成新的根密钥
                self.generate_root_key()
                self.save_root_key()
        return self.root_key
    
    def encrypt_data(self, data: bytes) -> Dict[str, str]:
        """使用根密钥加密数据
        
        Args:
            data: 要加密的数据
        
        Returns:
            Dict[str, str]: 包含加密数据、IV和盐值的字典
        """
        root_key = self.get_root_key()
        
        # 生成随机IV
        iv = os.urandom(16)
        
        # 加密数据
        cipher = Cipher(
            algorithms.AES(root_key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # 对数据进行填充
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # 加密数据
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        return {
            "iv": base64.b64encode(iv).decode('utf-8'),
            "encrypted_data": base64.b64encode(encrypted_data).decode('utf-8')
        }
    
    def decrypt_data(self, encrypted_data: Dict[str, str]) -> bytes:
        """使用根密钥解密数据
        
        Args:
            encrypted_data: 包含加密数据、IV和盐值的字典
        
        Returns:
            bytes: 解密后的数据
        """
        root_key = self.get_root_key()
        
        # 提取数据
        iv = base64.b64decode(encrypted_data['iv'])
        encrypted_data_bytes = base64.b64decode(encrypted_data['encrypted_data'])
        
        # 解密数据
        cipher = Cipher(
            algorithms.AES(root_key),
            modes.CBC(iv),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data_bytes) + decryptor.finalize()
        
        # 移除填充
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data
    
    def backup_root_key(self, backup_path: str) -> bool:
        """备份根密钥
        
        Args:
            backup_path: 备份路径
        
        Returns:
            bool: 备份是否成功
        """
        try:
            if not os.path.exists(self.root_key_path):
                return False
            
            # 确保备份目录存在
            self._ensure_directory(backup_path)
            
            # 复制根密钥文件
            with open(self.root_key_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            return True
        except Exception as e:
            print(f"备份根密钥失败: {str(e)}")
            return False
    
    def restore_root_key(self, backup_path: str) -> bool:
        """从备份恢复根密钥
        
        Args:
            backup_path: 备份路径
        
        Returns:
            bool: 恢复是否成功
        """
        try:
            if not os.path.exists(backup_path):
                return False
            
            # 确保目标目录存在
            self._ensure_directory(self.root_key_path)
            
            # 复制备份文件
            with open(backup_path, 'r', encoding='utf-8') as src:
                with open(self.root_key_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            # 重新加载根密钥
            self.root_key = None
            return self.load_root_key() is not None
        except Exception as e:
            print(f"恢复根密钥失败: {str(e)}")
            return False


# 导出根密钥管理器实例
root_key_manager = RootKeyManager()


def get_root_key_manager() -> RootKeyManager:
    """获取根密钥管理器实例
    
    Returns:
        RootKeyManager: 根密钥管理器实例
    """
    return root_key_manager


def get_root_key() -> bytes:
    """获取根密钥
    
    Returns:
        bytes: 根密钥
    """
    return root_key_manager.get_root_key()


def encrypt_with_root_key(data: bytes) -> Dict[str, str]:
    """使用根密钥加密数据
    
    Args:
        data: 要加密的数据
    
    Returns:
        Dict[str, str]: 包含加密数据、IV和盐值的字典
    """
    return root_key_manager.encrypt_data(data)


def decrypt_with_root_key(encrypted_data: Dict[str, str]) -> bytes:
    """使用根密钥解密数据
    
    Args:
        encrypted_data: 包含加密数据、IV和盐值的字典
    
    Returns:
        bytes: 解密后的数据
    """
    return root_key_manager.decrypt_data(encrypted_data)


__all__ = [
    "RootKeyManager",
    "root_key_manager",
    "get_root_key_manager",
    "get_root_key",
    "encrypt_with_root_key",
    "decrypt_with_root_key"
]
