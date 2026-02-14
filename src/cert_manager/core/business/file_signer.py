from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.backends import default_backend
import os
import json
from datetime import datetime
from typing import Optional, Union, Tuple
from ..storage import StorageManager
from ..utils import get_logger


class FileSigner:
    def __init__(self):
        # 初始化日志记录器
        self.logger = get_logger("file_signer")
        
        self.backend = default_backend()
        self.storage_manager = StorageManager()
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
            
            # 计算文件哈希
            hash_obj = getattr(hashes, hash_algorithm.upper())()
            digest = hashes.Hash(hash_obj, self.backend)
            
            with open(absolute_filepath, "rb") as f:
                while chunk := f.read(8192):
                    digest.update(chunk)
            
            file_hash = digest.finalize()
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
        """Save signature as JSON format with minimal information"""
        try:
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
                  output_dir: str, hash_algorithm: str = "sha256") -> list:
        """批量签名多个文件"""
        try:
            self.logger.info(f"Starting batch signing of {len(filepaths)} files")
            results = []
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            self.logger.debug(f"Created output directory: {output_dir}")
            
            for filepath in filepaths:
                try:
                    # 检查文件是否存在
                    if not os.path.exists(filepath):
                        results.append({
                            "file": filepath,
                            "success": False,
                            "reason": "File does not exist"
                        })
                        self.logger.warning(f"File does not exist: {filepath}")
                        continue
                    
                    # 直接调用sign_file方法，确保使用完全相同的代码路径
                    signature = self.sign_file(filepath, private_key, hash_algorithm)
                    self.logger.debug(f"Generated signature for file {filepath}, length: {len(signature)}")
                    
                    # 生成签名文件路径（保存到output_dir根目录）
                    filename = os.path.basename(filepath)
                    # 为了避免文件名冲突，添加一个唯一标识符
                    import uuid
                    unique_id = str(uuid.uuid4())[:8]
                    signature_filename = f"{os.path.splitext(filename)[0]}_{unique_id}.sig.json"
                    signature_filepath = os.path.join(output_dir, signature_filename)
                    self.logger.debug(f"Signature file path: {signature_filepath}")
                    
                    # 保存签名
                    self.save_signature(signature, signature_filepath, filepath, hash_algorithm)
                    self.logger.debug(f"Signature saved to file: {signature_filepath}")
                    
                    results.append({
                        "file": filepath,
                        "success": True,
                        "signature_file": signature_filepath,
                        "signature": signature  # 添加生成的签名到结果中
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
            file_hash = self.calculate_file_hash(filepath, hash_algorithm)
            
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
                print(f"验证失败详情: {str(e)}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to verify file signature for {filepath}: {str(e)}")
            print(f"验证过程错误: {str(e)}")
            return False