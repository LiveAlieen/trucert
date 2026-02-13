"""存储管理器

实现统一的存储接口，管理不同类型的数据存储
"""

import os
from typing import Optional, Union, Dict, Any, List


class StorageManager:
    """存储管理器"""
    
    def __init__(self, base_dir: str = None):
        """初始化存储管理器
        
        Args:
            base_dir: 基础目录路径，如果为None则使用默认路径
        """
        if base_dir is None:
            self.base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "configs")
        else:
            self.base_dir = base_dir
        
        # 确保基础目录存在
        os.makedirs(self.base_dir, exist_ok=True)
        
        # 初始化子目录
        self.key_dir = os.path.join(self.base_dir, "key")
        self.trust_dir = os.path.join(self.base_dir, "trust")
        self.root_key_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "root_key")
        
        # 确保子目录存在
        os.makedirs(self.key_dir, exist_ok=True)
        os.makedirs(self.trust_dir, exist_ok=True)
        os.makedirs(self.root_key_dir, exist_ok=True)
    
    def save(self, data: Union[Dict[str, Any], bytes], filepath: str, format: str = "json") -> None:
        """保存数据到文件
        
        Args:
            data: 要保存的数据
            filepath: 文件路径
            format: 文件格式，支持"json"和"binary"
        """
        # 确保目录存在
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        if format.lower() == "json":
            import json
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif format.lower() == "binary":
            with open(filepath, "wb") as f:
                f.write(data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def load(self, filepath: str, format: str = "json") -> Union[Dict[str, Any], bytes]:
        """从文件加载数据
        
        Args:
            filepath: 文件路径
            format: 文件格式，支持"json"和"binary"
        
        Returns:
            加载的数据
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if format.lower() == "json":
            import json
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        elif format.lower() == "binary":
            with open(filepath, "rb") as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def delete(self, filepath: str) -> bool:
        """删除文件
        
        Args:
            filepath: 文件路径
        
        Returns:
            是否删除成功
        """
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except Exception:
                return False
        return False
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """列出目录中的文件
        
        Args:
            directory: 目录路径
            pattern: 文件匹配模式
        
        Returns:
            文件路径列表
        """
        import glob
        if not os.path.exists(directory):
            return []
        
        search_path = os.path.join(directory, pattern)
        return glob.glob(search_path)
    
    def get_key_dir(self) -> str:
        """获取密钥存储目录
        
        Returns:
            密钥存储目录路径
        """
        return self.key_dir
    
    def get_trust_dir(self) -> str:
        """获取证书信任存储目录
        
        Returns:
            证书信任存储目录路径
        """
        return self.trust_dir
    
    def get_root_key_dir(self) -> str:
        """获取根密钥存储目录
        
        Returns:
            根密钥存储目录路径
        """
        return self.root_key_dir
    
    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """获取文件信息
        
        Args:
            filepath: 文件路径
        
        Returns:
            文件信息字典
        """
        if not os.path.exists(filepath):
            return {
                "exists": False,
                "path": filepath
            }
        
        return {
            "exists": True,
            "path": filepath,
            "size": os.path.getsize(filepath),
            "mtime": os.path.getmtime(filepath),
            "is_dir": os.path.isdir(filepath)
        }
