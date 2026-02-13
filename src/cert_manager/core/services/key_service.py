from typing import Optional, Tuple, Union, List, Dict, Any
from ..key_manager import KeyManager

class KeyService:
    """密钥服务类，封装密钥管理功能，作为GUI和核心业务逻辑之间的桥梁"""
    
    def __init__(self):
        self.key_manager = KeyManager()
    
    def generate_rsa_key(self, key_size: int = 2048) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """生成RSA密钥对
        
        Args:
            key_size: 密钥大小
        
        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: 私钥信息和公钥信息
        """
        private_key, public_key = self.key_manager.generate_rsa_key(key_size, auto_save=True)
        private_info = self.key_manager.get_key_info(private_key)
        public_info = self.key_manager.get_key_info(public_key)
        return private_info, public_info
    
    def generate_ecc_key(self, curve: str = "SECP256R1") -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """生成ECC密钥对
        
        Args:
            curve: 曲线类型
        
        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: 私钥信息和公钥信息
        """
        private_key, public_key = self.key_manager.generate_ecc_key(curve, auto_save=True)
        private_info = self.key_manager.get_key_info(private_key)
        public_info = self.key_manager.get_key_info(public_key)
        return private_info, public_info
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """列出所有存储的密钥
        
        Returns:
            List[Dict[str, Any]]: 密钥列表
        """
        return self.key_manager.list_keys(sort_by_time=True, reverse=True)
    
    def load_key_pair(self, key_id: str) -> Tuple[Any, Any]:
        """加载密钥对
        
        Args:
            key_id: 密钥ID
        
        Returns:
            Tuple[Any, Any]: 私钥和公钥
        """
        return self.key_manager.load_keys_from_config(key_id)
    
    def delete_key(self, key_id: str) -> bool:
        """删除密钥
        
        Args:
            key_id: 密钥ID
        
        Returns:
            bool: 是否删除成功
        """
        return self.key_manager.delete_key(key_id)
    
    def save_private_key(self, private_key: Any, file_path: str, password: Optional[str] = None) -> None:
        """保存私钥
        
        Args:
            private_key: 私钥
            file_path: 文件路径
            password: 密码（可选）
        """
        self.key_manager.save_private_key(private_key, file_path, password)
    
    def save_public_key(self, public_key: Any, file_path: str) -> None:
        """保存公钥
        
        Args:
            public_key: 公钥
            file_path: 文件路径
        """
        self.key_manager.save_public_key(public_key, file_path)
    
    def load_private_key(self, file_path: str, password: Optional[str] = None) -> Any:
        """加载私钥
        
        Args:
            file_path: 文件路径
            password: 密码（可选）
        
        Returns:
            Any: 私钥
        """
        return self.key_manager.load_private_key(file_path, password)
    
    def load_public_key(self, file_path: str) -> Any:
        """加载公钥
        
        Args:
            file_path: 文件路径
        
        Returns:
            Any: 公钥
        """
        return self.key_manager.load_public_key(file_path)
    
    def get_key_info(self, key: Any) -> Dict[str, Any]:
        """获取密钥信息
        
        Args:
            key: 密钥
        
        Returns:
            Dict[str, Any]: 密钥信息
        """
        return self.key_manager.get_key_info(key)
