from typing import Optional, Dict, Any, List
from src.cert_manager.core.cert_manager import CertManager

class CertService:
    """证书服务类，封装证书管理功能，作为GUI和核心业务逻辑之间的桥梁"""
    
    def __init__(self):
        self.cert_manager = CertManager()
    
    def generate_self_signed_cert(self, public_key: Any, private_key: Any, validity_days: int = 365, forward_offset: int = 0) -> Dict[str, Any]:
        """生成自签名证书
        
        Args:
            public_key: 公钥
            private_key: 私钥
            validity_days: 有效期（天）
            forward_offset: 正向偏移量（秒）
        
        Returns:
            Dict[str, Any]: 证书数据
        """
        return self.cert_manager.generate_self_signed_cert(public_key, private_key, validity_days, forward_offset)
    
    def generate_secondary_cert(self, public_key: Any, parent_private_key: Any, parent_public_key: Any, validity_days: int = 365, forward_offset: int = 0) -> Dict[str, Any]:
        """生成二级证书
        
        Args:
            public_key: 公钥
            parent_private_key: 上级私钥
            parent_public_key: 上级公钥
            validity_days: 有效期（天）
            forward_offset: 正向偏移量（秒）
        
        Returns:
            Dict[str, Any]: 证书数据
        """
        return self.cert_manager.generate_secondary_cert(public_key, parent_private_key, parent_public_key, validity_days, forward_offset)
    
    def save_cert(self, cert_data: Dict[str, Any], file_path: Optional[str] = None) -> str:
        """保存证书
        
        Args:
            cert_data: 证书数据
            file_path: 文件路径（可选）
        
        Returns:
            str: 保存的文件路径
        """
        return self.cert_manager.save_cert(cert_data, file_path)
    
    def load_cert(self, file_path: str) -> Dict[str, Any]:
        """加载证书
        
        Args:
            file_path: 文件路径
        
        Returns:
            Dict[str, Any]: 证书数据
        """
        return self.cert_manager.load_cert(file_path)
    
    def list_certs(self) -> List[Dict[str, Any]]:
        """列出所有存储的证书
        
        Returns:
            List[Dict[str, Any]]: 证书列表
        """
        return self.cert_manager.list_certs()
    
    def delete_cert(self, file_path: str) -> bool:
        """删除证书
        
        Args:
            file_path: 文件路径
        
        Returns:
            bool: 是否删除成功
        """
        return self.cert_manager.delete_cert(file_path)
    
    def import_cert(self, file_path: str) -> Dict[str, Any]:
        """导入证书
        
        Args:
            file_path: 文件路径
        
        Returns:
            Dict[str, Any]: 导入的证书数据
        """
        return self.cert_manager.import_cert(file_path)
    
    def get_cert_info(self, cert_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取证书信息
        
        Args:
            cert_data: 证书数据
        
        Returns:
            Dict[str, Any]: 证书信息
        """
        return self.cert_manager.get_cert_info(cert_data)
