from typing import Optional, Tuple, Union, List, Dict, Any
from cryptography.hazmat.primitives import serialization
from ..business.key_manager import KeyManager

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
        key_id, private_key, public_key = self.key_manager.generate_rsa_key(key_size)
        private_info = self.key_manager.get_key_info(key_id)
        private_info["type"] = "RSA Private Key"
        public_info = private_info.copy()
        public_info["type"] = "RSA Public Key"
        return private_info, public_info
    
    def generate_ecc_key(self, curve: str = "secp256r1") -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """生成ECC密钥对
        
        Args:
            curve: 曲线类型
        
        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: 私钥信息和公钥信息
        """
        key_id, private_key, public_key = self.key_manager.generate_ecc_key(curve)
        private_info = self.key_manager.get_key_info(key_id)
        private_info["type"] = "ECC Private Key"
        public_info = private_info.copy()
        public_info["type"] = "ECC Public Key"
        return private_info, public_info
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """列出所有存储的密钥
        
        Returns:
            List[Dict[str, Any]]: 密钥列表
        """
        key_ids = self.key_manager.list_keys()
        keys_info = []
        for key_id in key_ids:
            try:
                key_info = self.key_manager.get_key_info(key_id)
                key_info["id"] = key_id
                keys_info.append(key_info)
            except Exception:
                pass
        return keys_info
    
    def load_key_pair(self, key_id: str) -> Tuple[Any, Any]:
        """加载密钥对
        
        Args:
            key_id: 密钥ID
        
        Returns:
            Tuple[Any, Any]: 私钥和公钥
        """
        private_key, public_key, _ = self.key_manager.load_key(key_id)
        return private_key, public_key
    
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
        # 简化处理，实际应该调用key_manager的保存方法
        # 由于key_manager.py中没有实现save_private_key方法，这里直接保存
        password_bytes = password.encode('utf-8') if password else None
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(password_bytes) if password_bytes else serialization.NoEncryption()
        )
        with open(file_path, 'wb') as f:
            f.write(pem)
    
    def save_public_key(self, public_key: Any, file_path: str) -> None:
        """保存公钥
        
        Args:
            public_key: 公钥
            file_path: 文件路径
        """
        # 简化处理，实际应该调用key_manager的保存方法
        # 由于key_manager.py中没有实现save_public_key方法，这里直接保存
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(file_path, 'wb') as f:
            f.write(pem)
    
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
        # 从密钥对象中提取信息
        from cryptography.hazmat.primitives.asymmetric import rsa, ec
        key_info = {}
        
        if isinstance(key, rsa.RSAPrivateKey):
            key_info["type"] = "RSA Private Key"
            key_info["key_size"] = key.key_size
        elif isinstance(key, rsa.RSAPublicKey):
            key_info["type"] = "RSA Public Key"
            key_info["key_size"] = key.key_size
        elif isinstance(key, ec.EllipticCurvePrivateKey):
            key_info["type"] = "ECC Private Key"
            key_info["curve"] = key.curve.name
        elif isinstance(key, ec.EllipticCurvePublicKey):
            key_info["type"] = "ECC Public Key"
            key_info["curve"] = key.curve.name
        
        return key_info
