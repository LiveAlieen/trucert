"""证书存储模块

实现证书的存储和加载功能
"""

import os
from typing import Dict, Any, List
from .storage_manager import StorageManager


class CertStorage:
    """证书存储"""
    
    def __init__(self, storage_manager: StorageManager = None):
        """初始化证书存储
        
        Args:
            storage_manager: 存储管理器实例
        """
        if storage_manager is None:
            self.storage_manager = StorageManager()
        else:
            self.storage_manager = storage_manager
        
        self.trust_dir = self.storage_manager.get_trust_dir()
    
    def save_cert(self, cert_data: Dict[str, Any], filepath: str = None) -> str:
        """保存证书
        
        Args:
            cert_data: 证书数据
            filepath: 文件路径，如果为None则自动生成
        
        Returns:
            保存的文件路径
        """
        if filepath is None:
            # 自动生成文件路径
            import datetime
            timestamp = int(datetime.datetime.now().timestamp())
            cert_type = cert_data.get("cert_info", {}).get("parent_public_key", "")
            if cert_type == "":
                # 根证书
                filename = f"self_signed_{timestamp}.json"
            else:
                # 二级证书
                filename = f"secondary_{timestamp}.json"
            filepath = os.path.join(self.trust_dir, filename)
        
        self.storage_manager.save(cert_data, filepath, "json")
        return filepath
    
    def load_cert(self, filepath: str) -> Dict[str, Any]:
        """加载证书
        
        Args:
            filepath: 文件路径
        
        Returns:
            证书数据
        """
        return self.storage_manager.load(filepath, "json")
    
    def delete_cert(self, filepath: str) -> bool:
        """删除证书
        
        Args:
            filepath: 文件路径
        
        Returns:
            是否删除成功
        """
        return self.storage_manager.delete(filepath)
    
    def list_certs(self) -> List[Dict[str, Any]]:
        """列出所有存储的证书
        
        Returns:
            证书信息列表
        """
        certs = []
        cert_files = self.storage_manager.list_files(self.trust_dir, "*.json")
        
        for filepath in cert_files:
            try:
                cert_data = self.load_cert(filepath)
                filename = os.path.basename(filepath)
                
                # 确定证书类型和是否为根证书
                if "self_signed" in filename:
                    cert_type = "self_signed"
                    is_root_cert = True
                elif "secondary" in filename:
                    cert_type = "secondary"
                    is_root_cert = False
                else:
                    cert_type = "unknown"
                    is_root_cert = False
                
                cert_info = {
                    "filename": filename,
                    "path": filepath,
                    "type": cert_type,
                    "is_root_cert": is_root_cert,
                    "cert_info": cert_data.get("cert_info", {})
                }
                certs.append(cert_info)
            except Exception:
                # 跳过损坏的证书文件
                pass
        
        # 按时间戳排序（最新的在前）
        certs.sort(key=lambda x: x["cert_info"].get("timestamp", ""), reverse=True)
        return certs
    
    def get_cert_by_filename(self, filename: str) -> Dict[str, Any]:
        """根据文件名获取证书
        
        Args:
            filename: 文件名
        
        Returns:
            证书数据
        """
        filepath = os.path.join(self.trust_dir, filename)
        return self.load_cert(filepath)
    
    def import_cert(self, filepath: str) -> Dict[str, Any]:
        """导入证书
        
        Args:
            filepath: 证书文件路径
        
        Returns:
            导入的证书数据
        """
        # 加载证书数据
        cert_data = self.storage_manager.load(filepath, "json")
        
        # 保存到信任存储
        saved_path = self.save_cert(cert_data)
        
        return cert_data
