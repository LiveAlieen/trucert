"""存储管理器

实现统一的存储接口，管理不同类型的数据存储
"""

import os
import json
from typing import Optional, Union, Dict, Any, List
from ..utils import get_logger, calculate_hash


class StorageManager:
    """存储管理器"""
    
    def __init__(self, base_dir: str = None):
        """初始化存储管理器
        
        Args:
            base_dir: 基础目录路径，如果为None则使用默认路径
        """
        # 初始化日志记录器
        self.logger = get_logger("storage_manager")
        
        if base_dir is None:
            self.base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "configs")
        else:
            self.base_dir = base_dir
        
        # 确保基础目录存在
        os.makedirs(self.base_dir, exist_ok=True)
        self.logger.info(f"Base directory initialized: {self.base_dir}")
        
        # 初始化子目录
        self.key_dir = os.path.join(self.base_dir, "key")
        self.trust_dir = os.path.join(self.base_dir, "trust")
        
        # 确保子目录存在
        os.makedirs(self.key_dir, exist_ok=True)
        os.makedirs(self.trust_dir, exist_ok=True)
        self.logger.info(f"Subdirectories initialized: key={self.key_dir}, trust={self.trust_dir}")
    
    def save(self, data: Union[Dict[str, Any], bytes], filepath: str, format: str = "json") -> None:
        """保存数据到文件
        
        Args:
            data: 要保存的数据
            filepath: 文件路径
            format: 文件格式，支持"json"和"binary"
        """
        try:
            # 确保目录存在
            dir_path = os.path.dirname(filepath)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
                self.logger.debug(f"Created directory: {dir_path}")
            
            # 保存主文件
            if format.lower() == "json":
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Saved JSON data to file: {filepath}")
            elif format.lower() == "binary":
                with open(filepath, "wb") as f:
                    f.write(data)
                self.logger.info(f"Saved binary data to file: {filepath}")
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # 生成并保存文件哈希值
            self._save_file_hash(filepath)
        except Exception as e:
            self.logger.error(f"Failed to save data to file {filepath}: {str(e)}")
            raise
    
    def _save_file_hash(self, filepath: str) -> None:
        """保存文件的哈希值
        
        Args:
            filepath: 文件路径
        """
        try:
            # 读取文件内容
            with open(filepath, "rb") as f:
                content = f.read()
            
            # 计算哈希值
            file_hash = calculate_hash(content, "sha256")
            
            # 保存哈希值到 .hash 文件
            hash_filepath = f"{filepath}.hash"
            with open(hash_filepath, "w", encoding="utf-8") as f:
                json.dump({"hash": file_hash, "algorithm": "sha256"}, f, indent=2)
            
            self.logger.debug(f"Saved hash for file: {filepath}")
        except Exception as e:
            self.logger.warning(f"Failed to save file hash: {str(e)}")
    
    def load(self, filepath: str, format: str = "json") -> Union[Dict[str, Any], bytes]:
        """从文件加载数据
        
        Args:
            filepath: 文件路径
            format: 文件格式，支持"json"和"binary"
        
        Returns:
            加载的数据
        """
        try:
            if not os.path.exists(filepath):
                self.logger.warning(f"File not found: {filepath}")
                raise FileNotFoundError(f"File not found: {filepath}")
            
            # 验证文件完整性
            self._verify_file_integrity(filepath)
            
            if format.lower() == "json":
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.logger.info(f"Loaded JSON data from file: {filepath}")
                return data
            elif format.lower() == "binary":
                with open(filepath, "rb") as f:
                    data = f.read()
                self.logger.info(f"Loaded binary data from file: {filepath}")
                return data
            else:
                raise ValueError(f"Unsupported format: {format}")
        except Exception as e:
            self.logger.error(f"Failed to load data from file {filepath}: {str(e)}")
            raise
    
    def _verify_file_integrity(self, filepath: str) -> bool:
        """验证文件完整性
        
        Args:
            filepath: 文件路径
        
        Returns:
            bool: 文件是否完整
        """
        try:
            hash_filepath = f"{filepath}.hash"
            if not os.path.exists(hash_filepath):
                self.logger.warning(f"Hash file not found for {filepath}, skipping integrity check")
                return True
            
            # 读取存储的哈希值
            with open(hash_filepath, "r", encoding="utf-8") as f:
                hash_data = json.load(f)
            
            # 读取文件内容
            with open(filepath, "rb") as f:
                content = f.read()
            
            # 计算当前哈希值
            current_hash = calculate_hash(content, "sha256")
            
            # 验证哈希值
            if current_hash != hash_data["hash"]:
                self.logger.error(f"File integrity check failed for {filepath}")
                raise ValueError(f"File integrity check failed for {filepath}")
            
            self.logger.debug(f"File integrity check passed for {filepath}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to verify file integrity: {str(e)}")
            # 允许加载文件，但记录警告
            return True
    
    def delete(self, filepath: str) -> bool:
        """删除文件
        
        Args:
            filepath: 文件路径
        
        Returns:
            是否删除成功
        """
        try:
            # 删除主文件
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    self.logger.info(f"Deleted file: {filepath}")
                except Exception as e:
                    self.logger.error(f"Failed to delete file {filepath}: {str(e)}")
                    return False
            else:
                self.logger.warning(f"File not found for deletion: {filepath}")
            
            # 删除对应的哈希文件
            hash_filepath = f"{filepath}.hash"
            if os.path.exists(hash_filepath):
                try:
                    os.remove(hash_filepath)
                    self.logger.info(f"Deleted hash file: {hash_filepath}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete hash file {hash_filepath}: {str(e)}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error during file deletion: {str(e)}")
            return False
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """列出目录中的文件
        
        Args:
            directory: 目录路径
            pattern: 文件匹配模式
        
        Returns:
            文件路径列表
        """
        try:
            import glob
            if not os.path.exists(directory):
                self.logger.warning(f"Directory not found: {directory}")
                return []
            
            search_path = os.path.join(directory, pattern)
            files = glob.glob(search_path)
            self.logger.info(f"Listed {len(files)} files in directory {directory} with pattern {pattern}")
            return files
        except Exception as e:
            self.logger.error(f"Failed to list files in directory {directory}: {str(e)}")
            return []
    
    def get_key_dir(self) -> str:
        """获取密钥存储目录
        
        Returns:
            密钥存储目录路径
        """
        self.logger.debug(f"Getting key directory: {self.key_dir}")
        return self.key_dir
    
    def get_trust_dir(self) -> str:
        """获取证书信任存储目录
        
        Returns:
            证书信任存储目录路径
        """
        self.logger.debug(f"Getting trust directory: {self.trust_dir}")
        return self.trust_dir
    
    def get_root_key_dir(self) -> str:
        """获取根密钥存储目录
        
        Returns:
            根密钥存储目录路径
        """
        # 根密钥存储在base_dir下
        root_key_dir = self.base_dir
        self.logger.debug(f"Getting root key directory: {root_key_dir}")
        return root_key_dir
    
    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """获取文件信息
        
        Args:
            filepath: 文件路径
        
        Returns:
            文件信息字典
        """
        try:
            if not os.path.exists(filepath):
                self.logger.debug(f"File not found: {filepath}")
                return {
                    "exists": False,
                    "path": filepath
                }
            
            info = {
                "exists": True,
                "path": filepath,
                "size": os.path.getsize(filepath),
                "mtime": os.path.getmtime(filepath),
                "is_dir": os.path.isdir(filepath)
            }
            self.logger.debug(f"Retrieved file info: {info}")
            return info
        except Exception as e:
            self.logger.error(f"Failed to get file info for {filepath}: {str(e)}")
            return {
                "exists": False,
                "path": filepath,
                "error": str(e)
            }
