from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec
from cryptography.hazmat.backends import default_backend
import os
import json
from datetime import datetime
from typing import Optional, Union, Tuple

class FileSigner:
    def __init__(self):
        self.backend = default_backend()
    
    def calculate_file_hash(self, filepath: str, hash_algorithm: str = "sha256") -> bytes:
        hash_obj = getattr(hashes, hash_algorithm.upper())()
        digest = hashes.Hash(hash_obj, self.backend)
        
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                digest.update(chunk)
        
        return digest.finalize()
    
    def sign_file(self, filepath: str, private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey],
                 hash_algorithm: str = "sha256") -> bytes:
        file_hash = self.calculate_file_hash(filepath, hash_algorithm)
        
        if isinstance(private_key, rsa.RSAPrivateKey):
            signature = private_key.sign(
                file_hash,
                padding.PKCS1v15(),
                getattr(hashes, hash_algorithm.upper())()
            )
        elif isinstance(private_key, ec.EllipticCurvePrivateKey):
            signature = private_key.sign(
                file_hash,
                ec.ECDSA(getattr(hashes, hash_algorithm.upper())())
            )
        else:
            raise TypeError("Unsupported private key type")
        
        return signature
    
    def save_signature(self, signature: bytes, filepath: str, original_filepath: str = "", hash_algorithm: str = "sha256") -> None:
        """Save signature as JSON format with minimal information"""
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
        
        # Save as JSON
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(signature_data, f, indent=2, ensure_ascii=False)
    
    def load_signature(self, filepath: str) -> tuple[bytes, str, dict]:
        """Load signature from JSON format"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        signature = bytes.fromhex(data["signature"])
        hash_algorithm = data.get("hash_algorithm", "sha256")
        file_info = data.get("file_info", {})
        
        return signature, hash_algorithm, file_info
    
    def attach_signature_to_file(self, original_file: str, signature: bytes, 
                                output_file: Optional[str] = None) -> str:
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
        
        return output_file
    
    def extract_signature_from_file(self, signed_file: str) -> Tuple[bytes, bytes]:
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
        
        return file_content, signature
    
    def get_file_info(self, filepath: str) -> dict:
        return {
            "file_path": filepath,
            "file_size": os.path.getsize(filepath),
            "file_name": os.path.basename(filepath),
            "file_exists": os.path.exists(filepath)
        }
    
    def batch_sign(self, filepaths: list, private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey],
                  output_dir: str, hash_algorithm: str = "sha256") -> list:
        """批量签名多个文件"""
        results = []
        
        for filepath in filepaths:
            try:
                # 检查文件是否存在
                if not os.path.exists(filepath):
                    results.append({
                        "file": filepath,
                        "success": False,
                        "reason": "File does not exist"
                    })
                    continue
                
                # 生成签名
                signature = self.sign_file(filepath, private_key, hash_algorithm)
                
                # 生成签名文件路径（保存到output_dir根目录）
                filename = os.path.basename(filepath)
                signature_filename = f"{os.path.splitext(filename)[0]}.sig.json"
                signature_filepath = os.path.join(output_dir, signature_filename)
                
                # 保存签名
                self.save_signature(signature, signature_filepath, filepath, hash_algorithm)
                
                results.append({
                    "file": filepath,
                    "success": True,
                    "signature_file": signature_filepath
                })
                
            except Exception as e:
                results.append({
                    "file": filepath,
                    "success": False,
                    "reason": str(e)
                })
        
        return results
