from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from typing import Optional, Union, Dict, Any, Tuple
import os
import json
import datetime
from .storage import StorageManager
from .file_signer import FileSigner

class Verifier:
    def __init__(self):
        self.backend = default_backend()
        self.storage_manager = StorageManager()
        self.file_signer = FileSigner()
    
    def verify_cert_signature(self, cert: x509.Certificate, 
                            parent_cert: Optional[x509.Certificate] = None) -> Dict[str, Any]:
        """验证X.509证书签名"""
        try:
            # 如果没有提供上级证书，则验证自签名
            if not parent_cert:
                public_key = cert.public_key()
                issuer_name = cert.issuer
                subject_name = cert.subject
                
                # 检查是否是自签名证书
                if issuer_name != subject_name:
                    return {
                        "valid": False,
                        "reason": "Certificate is not self-signed and no parent certificate provided"
                    }
            else:
                public_key = parent_cert.public_key()
            
            # 验证签名
            signature = cert.signature
            tbs_certificate = cert.tbs_certificate_bytes
            signature_algorithm = cert.signature_algorithm_oid
            
            if isinstance(public_key, rsa.RSAPublicKey):
                public_key.verify(
                    signature,
                    tbs_certificate,
                    padding.PKCS1v15(),
                    cert.signature_hash_algorithm
                )
            elif isinstance(public_key, ec.EllipticCurvePublicKey):
                public_key.verify(
                    signature,
                    tbs_certificate,
                    ec.ECDSA(cert.signature_hash_algorithm)
                )
            else:
                return {
                    "valid": False,
                    "reason": "Unsupported public key type"
                }
            
            # 检查证书有效期
            now = datetime.datetime.utcnow()
            if now < cert.not_valid_before:
                return {
                    "valid": False,
                    "reason": "Certificate is not yet valid"
                }
            if now > cert.not_valid_after:
                return {
                    "valid": False,
                    "reason": "Certificate has expired"
                }
            
            return {
                "valid": True,
                "reason": "Certificate signature is valid",
                "cert_info": {
                    "subject": cert.subject.rfc4514_string(),
                    "issuer": cert.issuer.rfc4514_string(),
                    "not_valid_before": cert.not_valid_before.isoformat(),
                    "not_valid_after": cert.not_valid_after.isoformat(),
                    "serial_number": cert.serial_number
                }
            }
            
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Verification failed: {str(e)}"
            }
    
    def verify_file_signature(self, filepath: str, signature: bytes, 
                             public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                             hash_algorithm: str = "sha256") -> Dict[str, Any]:
        """验证文件签名"""
        try:
            # 使用FileSigner来计算文件哈希和验证签名
            if self.file_signer.verify_file_signature(filepath, signature, public_key, hash_algorithm):
                return {
                    "valid": True,
                    "reason": "File signature is valid",
                    "file_info": {
                        "file_path": filepath,
                        "file_size": os.path.getsize(filepath),
                        "hash_algorithm": hash_algorithm
                    }
                }
            else:
                return {
                    "valid": False,
                    "reason": "File signature verification failed"
                }
            
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Verification failed: {str(e)}"
            }
    
    def verify_signed_file(self, signed_file: str, 
                          public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                          hash_algorithm: str = "sha256") -> Dict[str, Any]:
        """验证带签名的文件"""
        try:
            # 从文件中提取签名
            file_content, signature = self.file_signer.extract_signature_from_file(signed_file)
            
            # 创建临时文件来验证
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as temp:
                temp.write(file_content)
                temp_filepath = temp.name
            
            try:
                # 验证签名
                result = self.verify_file_signature(temp_filepath, signature, public_key, hash_algorithm)
                return result
            finally:
                os.unlink(temp_filepath)
                
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Verification failed: {str(e)}"
            }
    
    def verify_cert_chain(self, cert: x509.Certificate, 
                         parent_certs: list) -> Dict[str, Any]:
        """验证证书链"""
        try:
            # 构建证书链
            cert_chain = [cert]
            current_cert = cert
            
            # 尝试构建完整的证书链
            while True:
                issuer_name = current_cert.issuer
                subject_name = current_cert.subject
                
                # 如果是自签名证书，链结束
                if issuer_name == subject_name:
                    break
                
                # 查找颁发者证书
                found = False
                for parent_cert in parent_certs:
                    if parent_cert.subject == issuer_name:
                        cert_chain.append(parent_cert)
                        current_cert = parent_cert
                        found = True
                        break
                
                if not found:
                    return {
                        "valid": False,
                        "reason": "Certificate chain incomplete - issuer certificate not found"
                    }
            
            # 验证链中的每个证书
            for i in range(len(cert_chain) - 1):
                cert_to_verify = cert_chain[i]
                parent_cert = cert_chain[i + 1]
                
                result = self.verify_cert_signature(cert_to_verify, parent_cert)
                if not result["valid"]:
                    return result
            
            # 验证根证书
            root_cert = cert_chain[-1]
            result = self.verify_cert_signature(root_cert)
            if not result["valid"]:
                return result
            
            return {
                "valid": True,
                "reason": "Certificate chain is valid",
                "chain_length": len(cert_chain)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Chain verification failed: {str(e)}"
            }
    
    def verify_json_cert(self, cert_data: Dict[str, Any], 
                        parent_cert_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """验证自定义JSON格式证书"""
        try:
            # 检查证书数据结构
            if "cert_info" not in cert_data or "public_key" not in cert_data or "signature" not in cert_data:
                return {
                    "valid": False,
                    "reason": "Invalid certificate structure: Missing required fields"
                }
            
            # 获取公钥数据
            try:
                public_key_hex = cert_data["public_key"]
                public_key_data = bytes.fromhex(public_key_hex)
            except Exception as e:
                return {
                    "valid": False,
                    "reason": f"Failed to process public key: {str(e)}"
                }
            
            # 获取签名
            try:
                signature_hex = cert_data["signature"]
                signature = bytes.fromhex(signature_hex)
            except Exception as e:
                return {
                    "valid": False,
                    "reason": f"Failed to process signature: {str(e)}"
                }
            
            # 重建签名时使用的消息
            try:
                # 提取时间戳和正向偏移量
                timestamp_str = cert_data.get("timestamp", "")
                if not timestamp_str:
                    return {
                        "valid": False,
                        "reason": "Missing timestamp"
                    }
                
                forward_offset = cert_data.get("forward_offset", 0)
                
                # 提取证书信息
                cert_info = cert_data["cert_info"]
                
                # 检查是否为根证书
                parent_public_key = cert_info.get("parent_public_key", "")
                is_root_cert = parent_public_key == ""
                
                # 重建cert_info以匹配签名时的状态
                if is_root_cert:
                    # 根证书：签名时包含parent_public_key（为空字符串）和storage_formats
                    cert_info_for_signature = cert_info.copy()
                else:
                    # 二级证书：签名时不包含parent_public_key，但包含storage_formats
                    cert_info_for_signature = {k: v for k, v in cert_info.items() if k != "parent_public_key"}
                
                # 确保排序一致，与生成时完全相同
                cert_info_json = json.dumps(cert_info_for_signature, sort_keys=True)
                cert_info_bytes = cert_info_json.encode('utf-8')
                
                # 转换为字节，与生成时完全相同
                timestamp_obj = datetime.datetime.fromisoformat(timestamp_str)
                timestamp_int = int(timestamp_obj.timestamp())
                timestamp_bytes = str(timestamp_int).encode('utf-8')
                offset_bytes = str(forward_offset).encode('utf-8')
                
                # 重建消息，顺序与生成时完全相同
                message = public_key_data + timestamp_bytes + offset_bytes + cert_info_bytes
            except Exception as e:
                return {
                    "valid": False,
                    "reason": f"Failed to reconstruct message: {str(e)}"
                }
            
            # 确定使用哪个公钥进行验证
            try:
                if is_root_cert:
                    # 根证书：使用自身公钥验证
                    verifying_key = serialization.load_der_public_key(
                        public_key_data,
                        backend=self.backend
                    )
                else:
                    # 二级证书：使用上级证书公钥验证
                    if not parent_cert_data:
                        # 尝试从parent_public_key字段获取上级公钥
                        if not parent_public_key:
                            return {
                                "valid": False,
                                "reason": "Secondary certificate requires parent certificate or parent_public_key field"
                            }
                        try:
                            parent_public_key_data = bytes.fromhex(parent_public_key)
                            verifying_key = serialization.load_der_public_key(
                                parent_public_key_data,
                                backend=self.backend
                            )
                        except Exception as e:
                            return {
                                "valid": False,
                                "reason": f"Failed to load parent public key: {str(e)}"
                            }
                    else:
                        # 使用提供的上级证书公钥验证
                        parent_public_key_hex = parent_cert_data.get("public_key", "")
                        if not parent_public_key_hex:
                            return {
                                "valid": False,
                                "reason": "Parent certificate missing public key"
                            }
                        parent_public_key_data = bytes.fromhex(parent_public_key_hex)
                        verifying_key = serialization.load_der_public_key(
                            parent_public_key_data,
                            backend=self.backend
                        )
            except Exception as e:
                return {
                    "valid": False,
                    "reason": f"Failed to load verifying key: {str(e)}"
                }
            
            # 验证签名
            try:
                if isinstance(verifying_key, rsa.RSAPublicKey):
                    verifying_key.verify(
                        signature,
                        message,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                elif isinstance(verifying_key, ec.EllipticCurvePublicKey):
                    verifying_key.verify(
                        signature,
                        message,
                        ec.ECDSA(hashes.SHA256())
                    )
                else:
                    return {
                        "valid": False,
                        "reason": "Unsupported public key type"
                    }
            except Exception as e:
                return {
                    "valid": False,
                    "reason": f"Failed to verify signature: {str(e)}"
                }
            
            return {
                "valid": True,
                "reason": "Certificate signature is valid",
                "cert_info": cert_info,
                "is_root_cert": is_root_cert
            }
            
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Verification failed with unexpected error: {str(e)}"
            }
    
    def verify_signed_file_from_json(self, signed_file: str, signature_file: str, 
                                   public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]) -> Dict[str, Any]:
        """从JSON签名文件验证带签名的文件"""
        try:
            # 加载签名数据
            signature, hash_algorithm, file_info = self.file_signer.load_signature(signature_file)
            
            # 验证文件签名
            return self.verify_file_signature(signed_file, signature, public_key, hash_algorithm)
            
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Verification failed: {str(e)}"
            }
