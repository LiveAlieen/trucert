from typing import Optional, Dict, Any, List, Tuple
from src.cert_manager.core.file_signer import FileSigner

class FileSignerService:
    """文件签名服务类，封装文件签名功能，作为GUI和核心业务逻辑之间的桥梁"""
    
    def __init__(self):
        self.file_signer = FileSigner()
    
    def sign_file(self, file_path: str, private_key: Any, hash_algorithm: str = "sha256") -> bytes:
        """签名文件
        
        Args:
            file_path: 文件路径
            private_key: 私钥
            hash_algorithm: 哈希算法
        
        Returns:
            bytes: 签名
        """
        return self.file_signer.sign_file(file_path, private_key, hash_algorithm)
    
    def save_signature(self, signature: bytes, file_path: str, original_file_path: str = "", hash_algorithm: str = "sha256") -> None:
        """保存签名
        
        Args:
            signature: 签名
            file_path: 文件路径
            original_file_path: 原始文件路径
            hash_algorithm: 哈希算法
        """
        self.file_signer.save_signature(signature, file_path, original_file_path, hash_algorithm)
    
    def load_signature(self, file_path: str) -> Tuple[bytes, str, Dict[str, Any]]:
        """加载签名
        
        Args:
            file_path: 文件路径
        
        Returns:
            Tuple[bytes, str, Dict[str, Any]]: 签名、哈希算法和文件信息
        """
        return self.file_signer.load_signature(file_path)
    
    def attach_signature_to_file(self, original_file: str, signature: bytes, output_file: Optional[str] = None) -> str:
        """将签名附加到文件
        
        Args:
            original_file: 原始文件路径
            signature: 签名
            output_file: 输出文件路径
        
        Returns:
            str: 输出文件路径
        """
        return self.file_signer.attach_signature_to_file(original_file, signature, output_file)
    
    def extract_signature_from_file(self, signed_file: str) -> Tuple[bytes, bytes]:
        """从文件中提取签名
        
        Args:
            signed_file: 带签名的文件路径
        
        Returns:
            Tuple[bytes, bytes]: 文件内容和签名
        """
        return self.file_signer.extract_signature_from_file(signed_file)
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """获取文件信息
        
        Args:
            file_path: 文件路径
        
        Returns:
            Dict[str, Any]: 文件信息
        """
        return self.file_signer.get_file_info(file_path)
    
    def batch_sign(self, file_paths: List[str], private_key: Any, output_dir: str, hash_algorithm: str = "sha256") -> List[Dict[str, Any]]:
        """批量签名多个文件
        
        Args:
            file_paths: 文件路径列表
            private_key: 私钥
            output_dir: 输出目录
            hash_algorithm: 哈希算法
        
        Returns:
            List[Dict[str, Any]]: 签名结果列表
        """
        return self.file_signer.batch_sign(file_paths, private_key, output_dir, hash_algorithm)
    
    def calculate_file_hash(self, file_path: str, hash_algorithm: str = "sha256") -> bytes:
        """计算文件哈希值
        
        Args:
            file_path: 文件路径
            hash_algorithm: 哈希算法
        
        Returns:
            bytes: 哈希值
        """
        return self.file_signer.calculate_file_hash(file_path, hash_algorithm)
