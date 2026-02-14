from typing import Optional, Dict, Any, List, Tuple
from ..business.file_signer import FileSigner

class FileSignerService:
    """文件签名服务类，封装文件签名功能，作为GUI和核心业务逻辑之间的桥梁"""
    
    def __init__(self):
        self.file_signer = FileSigner()
    
    def sign_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """签名文件
        
        Args:
            params: 包含以下字段的字典：
                - file_path: 文件路径
                - private_key: 私钥
                - hash_algorithm: 哈希算法，默认"sha256"
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: bytes，签名
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            file_path = params.get('file_path')
            private_key = params.get('private_key')
            hash_algorithm = params.get('hash_algorithm', 'sha256')
            
            # 验证参数
            if not file_path or not private_key:
                return {
                    "success": False,
                    "error": "缺少必要的文件路径或私钥参数"
                }
            
            # 调用业务逻辑层
            signature = self.file_signer.sign_file(file_path, private_key, hash_algorithm)
            
            return {
                "success": True,
                "data": signature
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_signature(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """保存签名
        
        Args:
            params: 包含以下字段的字典：
                - signature: 签名
                - file_path: 文件路径
                - original_file_path: 原始文件路径，默认""
                - hash_algorithm: 哈希算法，默认"sha256"
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            signature = params.get('signature')
            file_path = params.get('file_path')
            original_file_path = params.get('original_file_path', '')
            hash_algorithm = params.get('hash_algorithm', 'sha256')
            
            # 验证参数
            if not signature or not file_path:
                return {
                    "success": False,
                    "error": "缺少必要的签名或文件路径参数"
                }
            
            # 调用业务逻辑层
            self.file_signer.save_signature(signature, file_path, original_file_path, hash_algorithm)
            
            return {
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_signature(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """加载签名
        
        Args:
            params: 包含以下字段的字典：
                - file_path: 文件路径
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，包含签名、哈希算法和文件信息
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            file_path = params.get('file_path')
            
            # 验证参数
            if not file_path:
                return {
                    "success": False,
                    "error": "缺少必要的文件路径参数"
                }
            
            # 调用业务逻辑层
            signature, hash_algorithm, file_info = self.file_signer.load_signature(file_path)
            
            return {
                "success": True,
                "data": {
                    "signature": signature,
                    "hash_algorithm": hash_algorithm,
                    "file_info": file_info
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def attach_signature_to_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """将签名附加到文件
        
        Args:
            params: 包含以下字段的字典：
                - original_file: 原始文件路径
                - signature: 签名
                - output_file: 输出文件路径，默认None
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: str，输出文件路径
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            original_file = params.get('original_file')
            signature = params.get('signature')
            output_file = params.get('output_file', None)
            
            # 验证参数
            if not original_file or not signature:
                return {
                    "success": False,
                    "error": "缺少必要的原始文件路径或签名参数"
                }
            
            # 调用业务逻辑层
            output_path = self.file_signer.attach_signature_to_file(original_file, signature, output_file)
            
            return {
                "success": True,
                "data": output_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_signature_from_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """从文件中提取签名
        
        Args:
            params: 包含以下字段的字典：
                - signed_file: 带签名的文件路径
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，包含文件内容和签名
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            signed_file = params.get('signed_file')
            
            # 验证参数
            if not signed_file:
                return {
                    "success": False,
                    "error": "缺少必要的带签名文件路径参数"
                }
            
            # 调用业务逻辑层
            file_content, signature = self.file_signer.extract_signature_from_file(signed_file)
            
            return {
                "success": True,
                "data": {
                    "file_content": file_content,
                    "signature": signature
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_file_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取文件信息
        
        Args:
            params: 包含以下字段的字典：
                - file_path: 文件路径
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，文件信息
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            file_path = params.get('file_path')
            
            # 验证参数
            if not file_path:
                return {
                    "success": False,
                    "error": "缺少必要的文件路径参数"
                }
            
            # 调用业务逻辑层
            file_info = self.file_signer.get_file_info(file_path)
            
            return {
                "success": True,
                "data": file_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """批量签名多个文件
        
        Args:
            params: 包含以下字段的字典：
                - file_paths: 文件路径列表
                - private_key: 私钥
                - output_dir: 输出目录
                - hash_algorithm: 哈希算法，默认"sha256"
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: List[Dict[str, Any]]，签名结果列表
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            file_paths = params.get('file_paths')
            private_key = params.get('private_key')
            output_dir = params.get('output_dir')
            hash_algorithm = params.get('hash_algorithm', 'sha256')
            
            # 验证参数
            if not file_paths or not private_key or not output_dir:
                return {
                    "success": False,
                    "error": "缺少必要的文件路径列表、私钥或输出目录参数"
                }
            
            # 调用业务逻辑层
            results = self.file_signer.batch_sign(file_paths, private_key, output_dir, hash_algorithm)
            
            return {
                "success": True,
                "data": results
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def calculate_file_hash(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """计算文件哈希值
        
        Args:
            params: 包含以下字段的字典：
                - file_path: 文件路径
                - hash_algorithm: 哈希算法，默认"sha256"
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: bytes，哈希值
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            file_path = params.get('file_path')
            hash_algorithm = params.get('hash_algorithm', 'sha256')
            
            # 验证参数
            if not file_path:
                return {
                    "success": False,
                    "error": "缺少必要的文件路径参数"
                }
            
            # 调用业务逻辑层
            hash_value = self.file_signer.calculate_file_hash(file_path, hash_algorithm)
            
            return {
                "success": True,
                "data": hash_value
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_file_signature(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证文件签名
        
        Args:
            params: 包含以下字段的字典：
                - file_path: 文件路径
                - signature: 签名
                - public_key: 公钥
                - hash_algorithm: 哈希算法，默认"sha256"
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: bool，验证是否成功
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            file_path = params.get('file_path')
            signature = params.get('signature')
            public_key = params.get('public_key')
            hash_algorithm = params.get('hash_algorithm', 'sha256')
            
            # 验证参数
            if not file_path or not signature or not public_key:
                return {
                    "success": False,
                    "error": "缺少必要的文件路径、签名或公钥参数"
                }
            
            # 调用业务逻辑层
            result = self.file_signer.verify_file_signature(file_path, signature, public_key, hash_algorithm)
            
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
