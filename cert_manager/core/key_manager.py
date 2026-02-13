from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import os
import json
import hashlib
from typing import Optional, Tuple, Union

class KeyManager:
    def __init__(self, config_dir: str = "configs", root_key_dir: str = "root_key"):
        self.backend = default_backend()
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), config_dir)
        self.root_key_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), root_key_dir)
        self.keys_dir = os.path.join(self.config_dir, "key")
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.root_key_dir, exist_ok=True)
        os.makedirs(self.keys_dir, exist_ok=True)
        self.keys_file = os.path.join(self.config_dir, "keys.json")
        # 加载或生成根密钥对
        self.root_private_key, self.root_public_key = self._load_or_generate_root_key()
    
    def _load_or_generate_root_key(self) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """加载或生成根密钥对"""
        # 根私钥和公钥文件路径
        root_private_key_file = os.path.join(self.root_key_dir, "root_private.pem")
        root_public_key_file = os.path.join(self.root_key_dir, "root_public.pem")
        
        if os.path.exists(root_private_key_file) and os.path.exists(root_public_key_file):
            # 加载现有根密钥对
            with open(root_private_key_file, 'rb') as f:
                private_key_data = f.read()
            
            with open(root_public_key_file, 'rb') as f:
                public_key_data = f.read()
            
            private_key = serialization.load_pem_private_key(
                private_key_data,
                password=None,
                backend=self.backend
            )
            
            public_key = serialization.load_pem_public_key(
                public_key_data,
                backend=self.backend
            )
            
            return private_key, public_key
        else:
            # 生成新根密钥对
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=self.backend
            )
            public_key = private_key.public_key()
            
            # 保存根密钥对
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            with open(root_private_key_file, 'wb') as f:
                f.write(private_pem)
            
            with open(root_public_key_file, 'wb') as f:
                f.write(public_pem)
            
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
        if password:
            encryption_algorithm = serialization.BestAvailableEncryption(password.encode())
        else:
            encryption_algorithm = serialization.NoEncryption()
        
        if format.lower() == "pem":
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption_algorithm
            )
            with open(filepath, "wb") as f:
                f.write(pem)
        elif format.lower() == "der":
            der = private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption_algorithm
            )
            with open(filepath, "wb") as f:
                f.write(der)
        else:
            raise ValueError("Unsupported format. Use 'pem' or 'der'")
    
    def save_public_key(self, public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey], 
                       filepath: str, format: str = "pem") -> None:
        if format.lower() == "pem":
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            with open(filepath, "wb") as f:
                f.write(pem)
        elif format.lower() == "der":
            der = public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            with open(filepath, "wb") as f:
                f.write(der)
        else:
            raise ValueError("Unsupported format. Use 'pem' or 'der'")
    
    def load_private_key(self, filepath: str, password: Optional[str] = None) -> Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey]:
        with open(filepath, "rb") as f:
            key_data = f.read()
        
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
    
    def load_public_key(self, filepath: str) -> Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]:
        with open(filepath, "rb") as f:
            key_data = f.read()
        
        public_key = serialization.load_pem_public_key(
            key_data,
            backend=self.backend
        )
        return public_key
    
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
        # 准备密钥数据 - 使用无加密方式（根密钥会统一加密）
        encryption_algorithm = serialization.NoEncryption()
        
        # 私钥转PEM
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
        
        # 公钥转PEM
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # 获取密钥信息
        private_info = self.get_key_info(private_key)
        public_info = self.get_key_info(public_key)
        
        # 生成密钥ID
        import datetime
        now = datetime.datetime.now()
        # 生成简洁的ID格式：类型_时间戳
        key_id = f"{key_type}_{int(now.timestamp())}"
        # 生成详细时间戳，格式：YYYYMMDD_HHMMSS_ffffff
        timestamp = now.strftime("%Y%m%d_%H%M%S_%f")
        
        # 在key文件夹中保存密钥对
        key_folder = os.path.join(self.keys_dir, key_id)
        os.makedirs(key_folder, exist_ok=True)
        
        # 保存私钥
        private_key_path = os.path.join(key_folder, f"{key_id}_private.pem")
        with open(private_key_path, 'wb') as f:
            f.write(private_pem)
        
        # 保存公钥
        public_key_path = os.path.join(key_folder, f"{key_id}_public.pem")
        with open(public_key_path, 'wb') as f:
            f.write(public_pem)
        
        # 创建元数据文件
        metadata = {
            "id": key_id,
            "type": key_type,
            "created_at": now.isoformat(),
            "timestamp": timestamp,
            "private_info": private_info,
            "public_info": public_info,
            "encrypted": True
        }
        
        metadata_path = os.path.join(key_folder, f"{key_id}_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
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
        # 检查key文件夹是否存在
        key_folder = os.path.join(self.keys_dir, key_id)
        if not os.path.exists(key_folder):
            raise FileNotFoundError(f"Key folder for id {key_id} not found")
        
        # 检查密钥文件是否存在
        private_key_path = os.path.join(key_folder, f"{key_id}_private.pem")
        public_key_path = os.path.join(key_folder, f"{key_id}_public.pem")
        
        if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
            raise FileNotFoundError(f"Key files for id {key_id} not found")
        
        # 加载私钥
        private_key = self.load_private_key(private_key_path, None)
        
        # 加载公钥
        public_key = self.load_public_key(public_key_path)
        
        # 验证签名
        metadata_path = os.path.join(key_folder, f"{key_id}_metadata.json")
        signature_path = os.path.join(key_folder, f"{key_id}_signature.txt")
        
        if os.path.exists(metadata_path) and os.path.exists(signature_path):
            # 读取签名
            with open(signature_path, 'r', encoding='utf-8') as f:
                signature_hex = f.read()
            signature = bytes.fromhex(signature_hex)
            
            # 读取元数据
            with open(metadata_path, 'rb') as f:
                metadata_data = f.read()
            
            # 计算元数据的哈希值
            metadata_hash = hashlib.sha256(metadata_data).digest()
            
            # 使用根公钥验证签名
            try:
                self.root_public_key.verify(
                    signature,
                    metadata_hash,
                    PKCS1v15(),
                    hashes.SHA256()
                )
            except Exception as e:
                raise ValueError(f"Failed to verify signature for key {key_id}: {str(e)}")
        
        return private_key, public_key
    
    def list_keys(self, sort_by_time: bool = True, reverse: bool = True) -> list:
        """列出所有存储的密钥
        
        Args:
            sort_by_time: 是否按时间排序
            reverse: 是否倒序（最新的在前）
        """
        if not os.path.exists(self.keys_dir):
            return []
        
        # 返回密钥列表，不包含实际密钥数据
        key_list = []
        
        # 遍历key文件夹中的所有子文件夹
        for key_folder in os.listdir(self.keys_dir):
            key_path = os.path.join(self.keys_dir, key_folder)
            if os.path.isdir(key_path):
                # 读取元数据文件
                metadata_path = os.path.join(key_path, f"{key_folder}_metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        key_list.append({
                            "id": metadata["id"],
                            "type": metadata["type"],
                            "private_info": metadata["private_info"],
                            "created_at": metadata["created_at"],
                            "encrypted": metadata.get("encrypted", False)
                        })
                    except Exception:
                        # 如果元数据文件损坏，跳过
                        pass
        
        # 按时间排序
        if sort_by_time:
            key_list.sort(key=lambda x: x["created_at"], reverse=reverse)
        
        return key_list
    
    def delete_key(self, key_id: str) -> bool:
        """从key文件夹中删除指定的密钥"""
        # 检查key文件夹是否存在
        key_folder = os.path.join(self.keys_dir, key_id)
        if not os.path.exists(key_folder):
            return False
        
        # 删除对应的key文件夹
        import shutil
        shutil.rmtree(key_folder)
        
        return True
