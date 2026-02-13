"""测试验证模块

测试证书验证和文件验证的功能
"""

import unittest
import os
from cert_manager.core.verifier import Verifier
from cert_manager.core.key_manager import KeyManager
from cert_manager.core.cert_manager import CertManager
from cert_manager.core.file_signer import FileSigner
from tests.test_utils import create_temp_file, create_temp_directory, cleanup_temp_path


class TestVerifier(unittest.TestCase):
    """测试验证"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建验证器实例
        self.verifier = Verifier()
        # 创建密钥管理器实例
        self.key_manager = KeyManager()
        # 创建证书管理器实例
        self.cert_manager = CertManager()
        # 创建文件签名器实例
        self.file_signer = FileSigner()
    
    def tearDown(self):
        """清理测试环境"""
        pass
    
    def test_verify_json_cert(self):
        """测试验证JSON格式证书"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 生成自签名证书
        cert_data = self.cert_manager.generate_self_signed_cert(
            public_key=public_key,
            private_key=private_key,
            validity_days=365,
            forward_offset=0
        )
        
        # 验证证书
        result = self.verifier.verify_json_cert(cert_data)
        
        # 验证证书验证成功
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertTrue(result["valid"])
    
    def test_verify_file_signature(self):
        """测试验证文件签名"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 创建测试文件
        test_content = "test file content"
        test_file = create_temp_file(test_content)
        
        try:
            # 签名文件
            signature = self.file_signer.sign_file(test_file, private_key, "sha256")
            
            # 验证文件签名
            result = self.verifier.verify_file_signature(test_file, signature, public_key, "sha256")
            
            # 验证签名验证成功
            self.assertIsInstance(result, dict)
            self.assertIn("valid", result)
            self.assertTrue(result["valid"])
        finally:
            cleanup_temp_path(test_file)
    
    def test_verify_signed_file(self):
        """测试验证带签名的文件"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 创建测试文件
        test_content = "test file content"
        test_file = create_temp_file(test_content)
        
        try:
            # 签名文件
            signature = self.file_signer.sign_file(test_file, private_key, "sha256")
            
            # 附加签名到文件
            signed_file = create_temp_file(suffix=".signed")
            self.file_signer.attach_signature_to_file(test_file, signature, signed_file)
            
            # 验证带签名的文件
            result = self.verifier.verify_signed_file(signed_file, public_key, "sha256")
            
            # 验证签名验证成功
            self.assertIsInstance(result, dict)
            self.assertIn("valid", result)
            self.assertTrue(result["valid"])
        finally:
            cleanup_temp_path(test_file)
            cleanup_temp_path(signed_file)
    
    def test_verify_signature_from_json(self):
        """测试从JSON文件验证签名"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 创建测试文件
        test_content = "test file content"
        test_file = create_temp_file(test_content)
        
        try:
            # 签名文件
            signature = self.file_signer.sign_file(test_file, private_key, "sha256")
            
            # 保存签名为JSON文件
            signature_file = create_temp_file(suffix=".json")
            self.file_signer.save_signature(signature, signature_file, test_file, "sha256")
            
            # 加载签名
            loaded_signature, hash_algorithm, file_info = self.file_signer.load_signature(signature_file)
            
            # 验证文件签名
            result = self.verifier.verify_file_signature(test_file, loaded_signature, public_key, hash_algorithm)
            
            # 验证签名验证成功
            self.assertIsInstance(result, dict)
            self.assertIn("valid", result)
            self.assertTrue(result["valid"])
        finally:
            cleanup_temp_path(test_file)
            cleanup_temp_path(signature_file)


if __name__ == "__main__":
    unittest.main()
