"""密钥存储模块

实现密钥的存储和加载功能
"""

import os
from typing import Dict, Any, List, Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from .storage_manager import StorageManager


class KeyStorage:
    """密钥存储"""
    
    def __init__(self, storage_manager: StorageManager = None):
        """初始化密钥存储
        
        Args:
            storage_manager: 存储管理器实例
        """
        if storage_manager is None:
            self.storage_manager = StorageManager()
        else:
            self.storage_manager = storage_manager
        
        self.key_dir = self.storage_manager.get_key_dir()
        self.root_key_dir = self.storage_manager.get_root_key_dir()
        self.backend = default_backend()
    
    def save_private_key(self, private_key, filepath: str, password: str = None) -> None:
        """保存私钥
        
        Args:
            private_key: 私钥对象
            filepath: 文件路径
            password: 密码，可选
        """
        if password:
            encryption_algorithm = serialization.BestAvailableEncryption(password.encode())
        else:
            encryption_algorithm = serialization.NoEncryption()
        
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
        
        self.storage_manager.save(pem, filepath, "binary")
    
    def save_public_key(self, public_key, filepath: str) -> None:
        """保存公钥
        
        Args:
            public_key: 公钥对象
            filepath: 文件路径
        """
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        self.storage_manager.save(pem, filepath, "binary")
    
    def load_private_key(self, filepath: str, password: str = None):
        """加载私钥
        
        Args:
            filepath: 文件路径
            password: 密码，可选
        
        Returns:
            私钥对象
        """
        key_data = self.storage_manager.load(filepath, "binary")
        
        if password:
            password_bytes = password.encode()
        else:
            password_bytes = None
        
        private_key = serialization.load_pem_private_key(
            key_data,
            password=password_bytes,
            backend=self.backend
        )
        
        return private_key
    
    def load_public_key(self, filepath: str):
        """加载公钥
        
        Args:
            filepath: 文件路径
        
        Returns:
            公钥对象
        """
        key_data = self.storage_manager.load(filepath, "binary")
        
        public_key = serialization.load_pem_public_key(
            key_data,
            backend=self.backend
        )
        
        return public_key
    
    def save_key_pair(self, private_key, public_key, key_id: str, key_type: str) -> Dict[str, str]:
        """保存密钥对
        
        Args:
            private_key: 私钥对象
            public_key: 公钥对象
            key_id: 密钥ID
            key_type: 密钥类型
        
        Returns:
            保存的文件路径
        """
        # 创建密钥目录
        key_folder = os.path.join(self.key_dir, key_id)
        os.makedirs(key_folder, exist_ok=True)
        
        # 保存私钥
        private_key_path = os.path.join(key_folder, f"{key_id}_private.pem")
        self.save_private_key(private_key, private_key_path)
        
        # 保存公钥
        public_key_path = os.path.join(key_folder, f"{key_id}_public.pem")
        self.save_public_key(public_key, public_key_path)
        
        return {
            "private_key": private_key_path,
            "public_key": public_key_path
        }
    
    def load_key_pair(self, key_id: str) -> Tuple:
        """加载密钥对
        
        Args:
            key_id: 密钥ID
        
        Returns:
            (私钥对象, 公钥对象)
        """
        key_folder = os.path.join(self.key_dir, key_id)
        
        # 加载私钥
        private_key_path = os.path.join(key_folder, f"{key_id}_private.pem")
        private_key = self.load_private_key(private_key_path)
        
        # 加载公钥
        public_key_path = os.path.join(key_folder, f"{key_id}_public.pem")
        public_key = self.load_public_key(public_key_path)
        
        return private_key, public_key
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """列出所有存储的密钥
        
        Returns:
            密钥信息列表
        """
        keys = []
        
        # 遍历密钥目录
        if os.path.exists(self.key_dir):
            for key_id in os.listdir(self.key_dir):
                key_folder = os.path.join(self.key_dir, key_id)
                if os.path.isdir(key_folder):
                    # 检查密钥文件是否存在
                    private_key_path = os.path.join(key_folder, f"{key_id}_private.pem")
                    public_key_path = os.path.join(key_folder, f"{key_id}_public.pem")
                    metadata_path = os.path.join(key_folder, f"{key_id}_metadata.json")
                    
                    if os.path.exists(private_key_path) and os.path.exists(public_key_path):
                        key_info = {
                            "id": key_id,
                            "type": key_id.split("_")[0],
                            "private_key_path": private_key_path,
                            "public_key_path": public_key_path
                        }
                        
                        # 加载元数据
                        if os.path.exists(metadata_path):
                            try:
                                metadata = self.storage_manager.load(metadata_path, "json")
                                key_info.update(metadata)
                            except Exception:
                                pass
                        
                        keys.append(key_info)
        
        # 按创建时间排序
        keys.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return keys
    
    def delete_key(self, key_id: str) -> bool:
        """删除密钥
        
        Args:
            key_id: 密钥ID
        
        Returns:
            是否删除成功
        """
        key_folder = os.path.join(self.key_dir, key_id)
        
        if os.path.exists(key_folder):
            import shutil
            try:
                shutil.rmtree(key_folder)
                return True
            except Exception:
                return False
        
        return False
    
    def save_root_key_pair(self, private_key, public_key) -> Dict[str, str]:
        """保存根密钥对
        
        Args:
            private_key: 根私钥对象
            public_key: 根公钥对象
        
        Returns:
            保存的文件路径
        """
        # 保存根私钥
        private_key_path = os.path.join(self.root_key_dir, "root_private.pem")
        self.save_private_key(private_key, private_key_path)
        
        # 保存根公钥
        public_key_path = os.path.join(self.root_key_dir, "root_public.pem")
        self.save_public_key(public_key, public_key_path)
        
        return {
            "private_key": private_key_path,
            "public_key": public_key_path
        }
    
    def load_root_key_pair(self) -> Tuple:
        """加载根密钥对
        
        Returns:
            (根私钥对象, 根公钥对象)
        """
        # 加载根私钥
        private_key_path = os.path.join(self.root_key_dir, "root_private.pem")
        private_key = self.load_private_key(private_key_path)
        
        # 加载根公钥
        public_key_path = os.path.join(self.root_key_dir, "root_public.pem")
        public_key = self.load_public_key(public_key_path)
        
        return private_key, public_key
