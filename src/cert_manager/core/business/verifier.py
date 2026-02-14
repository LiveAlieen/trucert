from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from typing import Optional, Union, Dict, Any, Tuple
import os
import json
import datetime
from ..storage import StorageManager
from .file_signer import FileSigner
from ..utils import get_logger


class Verifier:
    def __init__(self):
        # 初始化日志记录器
        self.logger = get_logger("verifier")
        
        self.backend = default_backend()
        self.storage_manager = StorageManager()
        self.file_signer = FileSigner()
        self.logger.info("Verifier initialized successfully")
    
    def verify_cert_signature(self, cert_data: Dict[str, Any], public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]) -> bool:
        """验证证书签名
        
        Args:
            cert_data: 证书数据
            public_key: 公钥对象
        
        Returns:
            是否验证成功
        """
        try:
            self.logger.info("Verifying certificate signature")
            
            # 从证书数据中提取签名和待签名数据
            signature = bytes.fromhex(cert_data.get("signature", ""))
            if not signature:
                self.logger.error("No signature found in certificate data")
                return False
            
            # 构建待签名数据
            data_to_verify = self._build_data_to_verify(cert_data)
            
            # 验证签名
            hash_algorithm = cert_data.get("hash_algorithm", "sha256")
            
            try:
                if isinstance(public_key, rsa.RSAPublicKey):
                    # 使用与cert_manager中相同的PSS填充方案
                    public_key.verify(
                        signature,
                        data_to_verify,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                elif isinstance(public_key, ec.EllipticCurvePublicKey):
                    public_key.verify(
                        signature,
                        data_to_verify,
                        ec.ECDSA(hashes.SHA256())
                    )
                else:
                    self.logger.error("Unsupported public key type")
                    return False
                
                self.logger.info("Certificate signature verified successfully")
                return True
            except Exception as e:
                self.logger.warning(f"Certificate signature verification failed: {str(e)}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to verify certificate signature: {str(e)}")
            return False
    
    def verify_cert_validity(self, cert_data: Dict[str, Any]) -> bool:
        """验证证书有效性
        
        Args:
            cert_data: 证书数据
        
        Returns:
            是否验证成功
        """
        try:
            self.logger.info("Verifying certificate validity")
            
            if "cert_info" in cert_data:
                # 当前格式的证书，暂时跳过有效期验证
                # 因为当前格式的证书没有明确的有效期字段
                self.logger.info("Skipping validity check for current certificate format")
                return True
            else:
                # 旧格式的证书
                # 检查证书是否过期
                not_valid_before = datetime.datetime.fromisoformat(cert_data.get("not_valid_before", ""))
                not_valid_after = datetime.datetime.fromisoformat(cert_data.get("not_valid_after", ""))
                current_time = datetime.datetime.now()
                
                if current_time < not_valid_before:
                    self.logger.warning("Certificate is not yet valid")
                    return False
                
                if current_time > not_valid_after:
                    self.logger.warning("Certificate has expired")
                    return False
            
            self.logger.info("Certificate validity verified successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to verify certificate validity: {str(e)}")
            return False
    
    def verify_cert_chain(self, cert_data: Dict[str, Any], parent_public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]) -> bool:
        """验证证书链
        
        Args:
            cert_data: 证书数据
            parent_public_key: 父证书公钥
        
        Returns:
            是否验证成功
        """
        try:
            self.logger.info("Verifying certificate chain")
            
            # 验证证书签名
            if not self.verify_cert_signature(cert_data, parent_public_key):
                self.logger.error("Certificate chain verification failed: invalid signature")
                return False
            
            # 验证证书有效性
            if not self.verify_cert_validity(cert_data):
                self.logger.error("Certificate chain verification failed: invalid validity")
                return False
            
            self.logger.info("Certificate chain verified successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to verify certificate chain: {str(e)}")
            return False
    
    def verify_file_signature(self, filepath: str, signature: bytes, public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                             hash_algorithm: str = "sha256") -> dict:
        """验证文件签名
        
        Args:
            filepath: 文件路径
            signature: 签名数据
            public_key: 公钥对象
            hash_algorithm: 哈希算法
        
        Returns:
            验证结果字典，包含"valid"字段表示验证是否成功
        """
        result = self.file_signer.verify_file_signature(filepath, signature, public_key, hash_algorithm)
        return {"valid": result}
    
    def verify_signed_file(self, signed_filepath: str, public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey],
                          hash_algorithm: str = "sha256") -> dict:
        """验证带签名的文件
        
        Args:
            signed_filepath: 带签名的文件路径
            public_key: 公钥对象
            hash_algorithm: 哈希算法
        
        Returns:
            验证结果字典，包含"valid"字段表示验证是否成功
        """
        try:
            self.logger.info(f"Verifying signed file: {signed_filepath}")
            
            # 提取文件内容和签名
            file_content, signature = self.file_signer.extract_signature_from_file(signed_filepath)
            
            # 创建临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # 验证签名
                result = self.verify_file_signature(temp_file_path, signature, public_key, hash_algorithm)
                self.logger.info(f"Signed file verification {'successful' if result['valid'] else 'failed'}")
                return result
            finally:
                # 清理临时文件
                os.unlink(temp_file_path)
        except Exception as e:
            self.logger.error(f"Failed to verify signed file {signed_filepath}: {str(e)}")
            return {"valid": False}
    
    def verify_json_cert(self, cert_data: dict, public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey] = None) -> dict:
        """验证JSON格式的证书
        
        Args:
            cert_data: 证书数据字典
            public_key: 公钥对象（可选，如果不提供则使用证书中的公钥）
        
        Returns:
            验证结果字典，包含"valid"字段表示验证是否成功
        """
        try:
            self.logger.info("Verifying JSON certificate")
            
            # 验证证书签名
            if not public_key:
                # 如果没有提供公钥，使用证书中的公钥（自签名证书）
                from cryptography.hazmat.primitives import serialization
                public_key_pem = bytes.fromhex(cert_data.get("public_key", ""))
                public_key = serialization.load_pem_public_key(public_key_pem, backend=self.backend)
            
            if not self.verify_cert_signature(cert_data, public_key):
                self.logger.error("JSON certificate verification failed: invalid signature")
                return {"valid": False}
            
            # 验证证书有效性
            if not self.verify_cert_validity(cert_data):
                self.logger.error("JSON certificate verification failed: invalid validity")
                return {"valid": False}
            
            self.logger.info("JSON certificate verified successfully")
            return {"valid": True}
        except Exception as e:
            self.logger.error(f"Failed to verify JSON certificate: {str(e)}")
            return {"valid": False}
    
    def verify_signature_from_json(self, signature_json_path: str, filepath: str, public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]) -> dict:
        """从JSON文件验证签名
        
        Args:
            signature_json_path: 签名JSON文件路径
            filepath: 文件路径
            public_key: 公钥对象
        
        Returns:
            验证结果字典，包含"valid"字段表示验证是否成功
        """
        try:
            self.logger.info(f"Verifying signature from JSON file: {signature_json_path}")
            
            # 加载签名数据
            signature, hash_algorithm, _ = self.file_signer.load_signature(signature_json_path)
            
            # 验证签名
            result = self.verify_file_signature(filepath, signature, public_key, hash_algorithm)
            self.logger.info(f"Signature verification from JSON {'successful' if result['valid'] else 'failed'}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to verify signature from JSON file {signature_json_path}: {str(e)}")
            return {"valid": False}
    
    def _build_data_to_verify(self, cert_data: Dict[str, Any]) -> bytes:
        """构建待验证数据
        
        Args:
            cert_data: 证书数据
        
        Returns:
            待验证数据
        """
        try:
            # 检查证书数据格式
            if "cert_info" in cert_data:
                # 当前格式的证书 - 与cert_manager中的签名生成方式保持一致
                # 解析时间戳为整数时间戳
                timestamp = datetime.datetime.fromisoformat(cert_data.get("timestamp", "")).timestamp()
                timestamp_bytes = str(int(timestamp)).encode('utf-8')
                offset_bytes = str(cert_data.get("forward_offset", 0)).encode('utf-8')
                public_key_bytes = bytes.fromhex(cert_data.get("public_key", ""))
                
                # 序列化cert_info并排序键以确保确定性
                cert_info = cert_data.get("cert_info", {})
                cert_info_bytes = json.dumps(cert_info, sort_keys=True).encode('utf-8')
                
                # 按与生成签名相同的顺序连接数据
                message = public_key_bytes + timestamp_bytes + offset_bytes + cert_info_bytes
                return message
            else:
                # 旧格式的证书
                data = {
                    "subject": cert_data.get("subject", {}),
                    "issuer": cert_data.get("issuer", {}),
                    "public_key": cert_data.get("public_key", ""),
                    "serial_number": cert_data.get("serial_number", ""),
                    "not_valid_before": cert_data.get("not_valid_before", ""),
                    "not_valid_after": cert_data.get("not_valid_after", ""),
                    "version": cert_data.get("version", ""),
                    "hash_algorithm": cert_data.get("hash_algorithm", "")
                }
            
            # 转换为JSON字符串并编码为字节
            json_data = json.dumps(data, sort_keys=True, ensure_ascii=False)
            return json_data.encode("utf-8")
        except Exception as e:
            self.logger.error(f"Failed to build data to verify: {str(e)}")
            raise