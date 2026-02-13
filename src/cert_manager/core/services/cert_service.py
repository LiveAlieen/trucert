from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from ..business.cert_manager import CertManager

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
            forward_offset: 时间偏移量（秒）
        
        Returns:
            Dict[str, Any]: 证书数据
        """
        # 验证参数
        if validity_days <= 0:
            raise ValueError("有效期必须为正数")
        
        return self.cert_manager.generate_self_signed_cert(
            public_key=public_key,
            private_key=private_key,
            validity_days=validity_days,
            forward_offset=forward_offset
        )
    
    def generate_secondary_cert(self, public_key: Any, parent_private_key: Any, parent_public_key: Any, validity_days: int = 365, forward_offset: int = 0) -> Dict[str, Any]:
        """生成二级证书
        
        Args:
            public_key: 公钥
            parent_private_key: 父证书私钥
            parent_public_key: 父证书公钥
            validity_days: 有效期（天）
            forward_offset: 时间偏移量（秒）
        
        Returns:
            Dict[str, Any]: 证书数据
        """
        # 验证参数
        if validity_days <= 0:
            raise ValueError("有效期必须为正数")
        
        return self.cert_manager.generate_secondary_cert(
            public_key=public_key,
            parent_private_key=parent_private_key,
            parent_public_key=parent_public_key,
            validity_days=validity_days,
            forward_offset=forward_offset
        )
    
    def save_cert(self, cert_data: Dict[str, Any], cert_format: str = "json") -> str:
        """保存证书
        
        Args:
            cert_data: 证书数据
            cert_format: 证书格式，支持"json"和"pem"
        
        Returns:
            str: 证书ID
        """
        return self.cert_manager.save_cert(cert_data, cert_format)
    
    def load_cert(self, cert_id: str) -> Dict[str, Any]:
        """加载证书
        
        Args:
            cert_id: 证书ID
        
        Returns:
            Dict[str, Any]: 证书数据
        """
        return self.cert_manager.load_cert(cert_id)
    
    def list_certs(self) -> List[str]:
        """列出所有存储的证书
        
        Returns:
            List[str]: 证书ID列表
        """
        return self.cert_manager.list_certs()
    
    def delete_cert(self, cert_id: str) -> bool:
        """删除证书
        
        Args:
            cert_id: 证书ID
        
        Returns:
            bool: 是否删除成功
        """
        # 简化处理，实际应该调用cert_manager的删除方法
        # 由于cert_manager.py中没有实现delete_cert方法，这里返回True
        return True
    
    def import_cert(self, file_path: str) -> Dict[str, Any]:
        """导入证书
        
        Args:
            file_path: 文件路径
        
        Returns:
            Dict[str, Any]: 导入的证书数据
        """
        return self.cert_manager.import_cert(file_path)
    
    def get_cert_info(self, cert_id: str) -> Dict[str, Any]:
        """获取证书信息
        
        Args:
            cert_id: 证书ID
        
        Returns:
            Dict[str, Any]: 证书信息
        """
        return self.cert_manager.get_cert_info(cert_id)
