# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.backends import default_backend
import os
import json
from datetime import datetime
from typing import Optional, Union, Tuple, Any
from ..utils import get_logger, get


class FileSigner:
    """文件签名类，负责文件的哈希计算、签名和验证
    
    提供文件哈希计算、文件签名、签名保存、批量签名等功能，
    是整个系统中文件签名功能的核心组件。
    """
    
    def __init__(self):
        """初始化文件签名器
        
        使用依赖注入获取存储组件，确保与存储层的解耦。
        """
        # 初始化日志记录器
        self.logger = get_logger("file_signer")
        
        self.backend = default_backend()
        # 使用依赖注入获取存储组件
        self.storage_manager = get("storage_manager")
        self.logger.info("FileSigner initialized successfully")
    
    def calculate_file_hash(self, filepath: str, hash_algorithm: str = "sha256") -> bytes:
        """计算文件哈希值"""
        try:
            # 确保使用绝对路径
            absolute_filepath = os.path.abspath(filepath)
            self.logger.info(f"Calculating file hash for: {absolute_filepath} using algorithm: {hash_algorithm}")
            
            # 检查文件是否存在
            if not os.path.exists(absolute_filepath):
                self.logger.error(f"File not found: {absolute_filepath}")
                raise FileNotFoundError(f"File not found: {absolute_filepath}")
            
            # 检查文件大小
            file_size = os.path.getsize(absolute_filepath)
            self.logger.debug(f"File size: {file_size} bytes")
            
            # 使用工具层中的函数计算文件哈希
            from ..utils.hash_utils import calculate_file_hash
            hash_hex = calculate_file_hash(absolute_filepath, hash_algorithm)
            # 转换为字节格式
            file_hash = bytes.fromhex(hash_hex)
            
            self.logger.info(f"File hash calculated successfully for: {absolute_filepath}")
            self.logger.debug(f"File hash: {file_hash}")
            return file_hash
        except Exception as e:
            self.logger.error(f"Failed to calculate file hash for {filepath}: {str(e)}")
            raise
    
    def sign_file(self, filepath: str, private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey],
                 hash_algorithm: str = "sha256") -> bytes:
        """签名文件"""
        try:
            self.logger.info(f"Signing file: {filepath} using algorithm: {hash_algorithm}")
            file_hash = self.calculate_file_hash(filepath, hash_algorithm)
            
            if isinstance(private_key, rsa.RSAPrivateKey):
                signature = private_key.sign(
                    file_hash,
                    padding.PKCS1v15(),
                    getattr(hashes, hash_algorithm.upper())()
                )
                self.logger.debug("Generated RSA signature for file")
            elif isinstance(private_key, ec.EllipticCurvePrivateKey):
                signature = private_key.sign(
                    file_hash,
                    ec.ECDSA(getattr(hashes, hash_algorithm.upper())())
                )
                self.logger.debug("Generated ECC signature for file")
            else:
                raise TypeError("Unsupported private key type")
            
            self.logger.info(f"File signed successfully: {filepath}")
            return signature
        except Exception as e:
            self.logger.error(f"Failed to sign file {filepath}: {str(e)}")
            raise
    
    def save_signature(self, signature: bytes, filepath: str, original_filepath: str = "", hash_algorithm: str = "sha256") -> None:
        """Save signature as JSON format with minimal information
        
        If filepath is not provided or is a directory, the signature will be saved
        in the same directory as the original file with .giq extension.
        """
        try:
            # If filepath is not provided or is a directory, use original_filepath's directory
            if not filepath or os.path.isdir(filepath):
                if not original_filepath:
                    raise ValueError("Either filepath or original_filepath must be provided")
                # Save signature in the same directory as the original file
                signature_dir = os.path.dirname(original_filepath)
                signature_filename = os.path.basename(original_filepath) + ".giq"
                filepath = os.path.join(signature_dir, signature_filename)
            
            self.logger.info(f"Saving signature to file: {filepath}")
            # Create minimal file info with only filename and relative path
            file_info = {}
            if original_filepath:
                # Get filename
                file_info["filename"] = os.path.basename(original_filepath)
                # Get relative path from signature directory to original file
                signature_dir = os.path.dirname(filepath)
                try:
                    relative_path = os.path.relpath(original_filepath, signature_dir)
                    file_info["relative_path"] = relative_path
                except:
                    # If relative path can't be calculated, just store filename
                    pass
            
            # Create signature data with only essential fields
            signature_data = {
                "signature": signature.hex(),
                "hash_algorithm": hash_algorithm,
                "file_info": file_info
            }
            
            # Save as JSON using storage manager
            self.storage_manager.save(signature_data, filepath, "json")
            self.logger.info(f"Signature saved successfully to file: {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save signature to file {filepath}: {str(e)}")
            raise
    
    def load_signature(self, filepath: str) -> tuple[bytes, str, dict]:
        """Load signature from JSON format"""
        try:
            self.logger.info(f"Loading signature from file: {filepath}")
            data = self.storage_manager.load(filepath, "json")
            
            # Check if it's a batch signature
            if "batch_signatures" in data:
                # For batch signatures, return the first signature for verification
                # This is a simplification - in a real implementation, you might want to handle each signature separately
                if data["batch_signatures"]:
                    batch_sig = data["batch_signatures"][0]
                    signature = bytes.fromhex(batch_sig["signature"])
                    hash_algorithm = batch_sig.get("hash_algorithm", data.get("hash_algorithm", "sha256"))
                    file_info = batch_sig.get("file_info", {})
                    # Add batch information to file_info
                    file_info["batch_signature"] = True
                    file_info["total_files"] = len(data["batch_signatures"])
                else:
                    raise ValueError("Batch signature file is empty")
            else:
                # Single signature
                signature = bytes.fromhex(data["signature"])
                hash_algorithm = data.get("hash_algorithm", "sha256")
                file_info = data.get("file_info", {})
            
            self.logger.info(f"Signature loaded successfully from file: {filepath}")
            return signature, hash_algorithm, file_info
        except Exception as e:
            self.logger.error(f"Failed to load signature from file {filepath}: {str(e)}")
            raise
    
    def attach_signature_to_file(self, original_file: str, signature: bytes, 
                                output_file: Optional[str] = None) -> str:
        """将签名附加到文件"""
        try:
            self.logger.info(f"Attaching signature to file: {original_file}")
            if not output_file:
                output_file = original_file + ".signed"
            
            # 读取原始文件内容
            with open(original_file, "rb") as f:
                file_content = f.read()
            
            # 创建签名头部
            signature_header = b"---BEGIN SIGNATURE---\n"
            signature_footer = b"\n---END SIGNATURE---"
            
            # 写入带签名的文件
            with open(output_file, "wb") as f:
                f.write(file_content)
                f.write(signature_header)
                f.write(signature)
                f.write(signature_footer)
            
            self.logger.info(f"Signature attached successfully to file: {output_file}")
            return output_file
        except Exception as e:
            self.logger.error(f"Failed to attach signature to file {original_file}: {str(e)}")
            raise
    
    def extract_signature_from_file(self, signed_file: str) -> Tuple[bytes, bytes]:
        """从文件中提取签名"""
        try:
            self.logger.info(f"Extracting signature from file: {signed_file}")
            with open(signed_file, "rb") as f:
                content = f.read()
            
            # 查找签名头部和尾部
            sig_start = content.find(b"---BEGIN SIGNATURE---\n")
            sig_end = content.find(b"\n---END SIGNATURE---")
            
            if sig_start == -1 or sig_end == -1:
                raise ValueError("No signature found in file")
            
            # 提取文件内容和签名
            file_content = content[:sig_start]
            signature = content[sig_start + len(b"---BEGIN SIGNATURE---\n"):sig_end]
            
            self.logger.info(f"Signature extracted successfully from file: {signed_file}")
            return file_content, signature
        except Exception as e:
            self.logger.error(f"Failed to extract signature from file {signed_file}: {str(e)}")
            raise
    
    def get_file_info(self, filepath: str) -> dict:
        """获取文件信息"""
        try:
            self.logger.info(f"Getting file info for: {filepath}")
            file_info = {
                "file_path": filepath,
                "file_size": os.path.getsize(filepath),
                "file_name": os.path.basename(filepath),
                "file_exists": os.path.exists(filepath)
            }
            self.logger.debug(f"File info retrieved: {file_info}")
            return file_info
        except Exception as e:
            self.logger.error(f"Failed to get file info for {filepath}: {str(e)}")
            raise
    
    def batch_sign(self, filepaths: list, private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey],
                  output_dir: str = None, hash_algorithm: str = "sha256") -> list:
        """批量签名多个文件，生成单个.giqs文件
        
        支持目录级签名：如果提供的路径是目录，会递归处理目录中的所有文件
        
        Args:
            filepaths: 文件或目录路径列表
            private_key: 私钥
            output_dir: 输出目录，默认为None
            hash_algorithm: 哈希算法，默认"sha256"
            
        Returns:
            签名结果列表
        """
        try:
            self.logger.info(f"Starting batch signing of {len(filepaths)} items")
            results = []
            batch_signatures = []
            
            # 确定输出目录
            if not output_dir:
                # 如果没有指定输出目录，使用第一个文件的目录
                # 预处理：处理目录和文件，递归收集所有文件
                valid_filepaths = []
                for path in filepaths:
                    if not os.path.exists(path):
                        results.append({
                            "file": path,
                            "success": False,
                            "reason": "Path does not exist"
                        })
                        self.logger.warning(f"Path does not exist: {path}")
                    elif os.path.isdir(path):
                        # 处理目录，递归收集所有文件
                        self.logger.info(f"Processing directory: {path}")
                        for root, _, files in os.walk(path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                valid_filepaths.append(file_path)
                                self.logger.debug(f"Added file from directory: {file_path}")
                    else:
                        # 处理单个文件
                        valid_filepaths.append(path)
                
                # 如果有有效文件，使用第一个文件的目录作为输出目录
                if valid_filepaths:
                    first_file_dir = os.path.dirname(valid_filepaths[0])
                    output_dir = first_file_dir
                else:
                    # 如果没有有效文件，使用当前目录
                    output_dir = os.getcwd()
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            self.logger.debug(f"Created output directory: {output_dir}")
            
            # 确保valid_filepaths已定义
            if 'valid_filepaths' not in locals():
                # 预处理：处理目录和文件，递归收集所有文件
                valid_filepaths = []
                for path in filepaths:
                    if not os.path.exists(path):
                        results.append({
                            "file": path,
                            "success": False,
                            "reason": "Path does not exist"
                        })
                        self.logger.warning(f"Path does not exist: {path}")
                    elif os.path.isdir(path):
                        # 处理目录，递归收集所有文件
                        self.logger.info(f"Processing directory: {path}")
                        for root, _, files in os.walk(path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                valid_filepaths.append(file_path)
                                self.logger.debug(f"Added file from directory: {file_path}")
                    else:
                        # 处理单个文件
                        valid_filepaths.append(path)
            
            self.logger.info(f"Valid files for signing: {len(valid_filepaths)}")
            
            # 批量处理有效文件
            for filepath in valid_filepaths:
                try:
                    # 直接调用sign_file方法，确保使用完全相同的代码路径
                    self.logger.debug(f"Batch signing file: {filepath}")
                    self.logger.debug(f"Using hash algorithm: {hash_algorithm}")
                    signature = self.sign_file(filepath, private_key, hash_algorithm)
                    self.logger.debug(f"Generated signature for file {filepath}, length: {len(signature)}")
                    
                    # 收集签名信息
                    file_info = {}
                    file_info["filename"] = os.path.basename(filepath)
                    try:
                        relative_path = os.path.relpath(filepath, output_dir)
                        file_info["relative_path"] = relative_path
                    except:
                        pass
                    
                    batch_signatures.append({
                        "file_path": filepath,
                        "file_info": file_info,
                        "signature": signature.hex(),
                        "hash_algorithm": hash_algorithm
                    })
                    
                    results.append({
                        "file": filepath,
                        "success": True
                    })
                    self.logger.info(f"Batch sign completed for file: {filepath}")
                    
                except Exception as e:
                    error_msg = str(e)
                    results.append({
                        "file": filepath,
                        "success": False,
                        "reason": error_msg
                    })
                    self.logger.error(f"Batch sign failed for file {filepath}: {error_msg}")
            
            # 生成单个.giqs文件
            if batch_signatures:
                import uuid
                import datetime
                unique_id = str(uuid.uuid4())[:8]
                timestamp = int(datetime.datetime.now().timestamp())
                signature_filename = f"batch_sign_{timestamp}_{unique_id}.giqs"
                signature_filepath = os.path.join(output_dir, signature_filename)
                
                # 构建批量签名数据
                batch_data = {
                    "batch_signatures": batch_signatures,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "hash_algorithm": hash_algorithm,
                    "total_files": len(valid_filepaths),
                    "successful_files": len([r for r in results if r['success']])
                }
                
                # 保存为JSON格式
                self.storage_manager.save(batch_data, signature_filepath, "json")
                self.logger.info(f"Batch signatures saved to file: {signature_filepath}")
                
                # 添加批量签名文件路径到结果
                for result in results:
                    if result["success"]:
                        result["signature_file"] = signature_filepath
            
            self.logger.info(f"Batch signing completed. {len([r for r in results if r['success']])} succeeded, {len([r for r in results if not r['success']])} failed")
            return results
        except Exception as e:
            self.logger.error(f"Failed to perform batch signing: {str(e)}")
            return []
    
    def verify_file_signature(self, filepath: str, signature: bytes, 
                             public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                             hash_algorithm: str = "sha256") -> bool:
        """验证文件签名"""
        try:
            self.logger.info(f"Verifying file signature for: {filepath}")
            self.logger.debug(f"Signature length: {len(signature)}")
            self.logger.debug(f"Hash algorithm: {hash_algorithm}")
            self.logger.debug(f"Public key type: {type(public_key)}")
            
            file_hash = self.calculate_file_hash(filepath, hash_algorithm)
            self.logger.debug(f"Calculated file hash: {file_hash[:10]}...")
            
            try:
                if isinstance(public_key, rsa.RSAPublicKey):
                    public_key.verify(
                        signature,
                        file_hash,
                        padding.PKCS1v15(),
                        getattr(hashes, hash_algorithm.upper())()
                    )
                elif isinstance(public_key, ec.EllipticCurvePublicKey):
                    public_key.verify(
                        signature,
                        file_hash,
                        ec.ECDSA(getattr(hashes, hash_algorithm.upper())())
                    )
                else:
                    raise TypeError("Unsupported public key type")
                self.logger.info(f"File signature verified successfully for: {filepath}")
                return True
            except Exception as e:
                self.logger.warning(f"File signature verification failed for {filepath}: {str(e)}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to verify file signature for {filepath}: {str(e)}")
            return False
    
    def verify_file_signature_with_cert(self, filepath: str, signature: bytes, 
                                       cert: Union[Any, str],
                                       hash_algorithm: str = "sha256") -> bool:
        """使用证书验证文件签名
        
        Args:
            filepath: 要验证的文件路径
            signature: 签名数据
            cert: 证书对象或证书文件路径
            hash_algorithm: 哈希算法，默认"sha256"
            
        Returns:
            验证是否成功
        """
        try:
            self.logger.info(f"Verifying file signature with certificate for: {filepath}")
            self.logger.debug(f"Signature length: {len(signature)}")
            self.logger.debug(f"Hash algorithm: {hash_algorithm}")
            
            # 加载证书并提取公钥
            from ..utils.verify_utils import load_certificate, extract_public_key_from_certificate
            from ..utils.crypto_utils import load_public_key
            from cryptography.hazmat.primitives import serialization
            
            public_key = None
            
            if isinstance(cert, str):
                # 从文件路径加载证书
                self.logger.debug(f"Loading certificate from file: {cert}")
                try:
                    # 尝试作为PEM证书加载
                    cert_obj = load_certificate(cert)
                    public_key = extract_public_key_from_certificate(cert_obj)
                    self.logger.debug(f"Loaded PEM certificate and extracted public key")
                except Exception as e:
                    # 尝试作为JSON证书加载
                    self.logger.debug(f"Failed to load as PEM certificate, trying JSON format: {str(e)}")
                    import json
                    with open(cert, 'r', encoding='utf-8') as f:
                        cert_data = json.load(f)
                    
                    # 从JSON证书中提取公钥
                    if 'public_key' in cert_data:
                        public_key_hex = cert_data['public_key']
                        public_key_data = bytes.fromhex(public_key_hex)
                        public_key = serialization.load_der_public_key(public_key_data, backend=self.backend)
                        self.logger.debug(f"Loaded JSON certificate and extracted public key")
                    else:
                        raise ValueError("Certificate file does not contain public_key field")
            else:
                # 使用证书对象
                self.logger.debug(f"Using provided certificate object")
                public_key = extract_public_key_from_certificate(cert)
            
            self.logger.debug(f"Extracted public key type: {type(public_key)}")
            
            # 调用现有的验证方法
            return self.verify_file_signature(filepath, signature, public_key, hash_algorithm)
        except Exception as e:
            self.logger.error(f"Failed to verify file signature with certificate for {filepath}: {str(e)}")
            return False