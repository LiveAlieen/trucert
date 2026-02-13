"""集成测试模块

测试多个模块之间的交互功能
"""

import unittest
import os
from cert_manager.core.key_manager import KeyManager
from cert_manager.core.cert_manager import CertManager
from cert_manager.core.file_signer import FileSigner
from cert_manager.core.verifier import Verifier
from tests.test_utils import create_temp_file, create_temp_directory, cleanup_temp_path


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录
        self.test_dir = create_temp_directory()
        # 创建各个管理器实例
        self.key_manager = KeyManager()
        self.cert_manager = CertManager()
        self.file_signer = FileSigner()
        self.verifier = Verifier()
    
    def tearDown(self):
        """清理测试环境"""
        cleanup_temp_path(self.test_dir)
    
    def test_full_certificate_lifecycle(self):
        """测试完整的证书生命周期"""
        # 1. 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 2. 生成自签名证书
        cert_data = self.cert_manager.generate_self_signed_cert(
            public_key=public_key,
            private_key=private_key,
            validity_days=365,
            forward_offset=0
        )
        
        # 3. 保存证书
        cert_file = os.path.join(self.test_dir, "test_cert.json")
        self.cert_manager.save_cert(cert_data, cert_file)
        
        # 4. 加载证书
        loaded_cert_data = self.cert_manager.load_cert(cert_file)
        
        # 5. 验证证书
        verify_result = self.verifier.verify_json_cert(loaded_cert_data)
        self.assertTrue(verify_result["valid"])
    
    def test_file_signing_and_verification(self):
        """测试文件签名和验证"""
        # 1. 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 2. 创建测试文件
        test_content = "test file content for signing"
        test_file = create_temp_file(test_content)
        
        try:
            # 3. 签名文件
            signature = self.file_signer.sign_file(test_file, private_key, "sha256")
            
            # 4. 验证文件签名
            verify_result = self.verifier.verify_file_signature(test_file, signature, public_key, "sha256")
            self.assertTrue(verify_result["valid"])
        finally:
            cleanup_temp_path(test_file)
    
    def test_signed_file_creation_and_verification(self):
        """测试创建和验证带签名的文件"""
        # 1. 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 2. 创建测试文件
        test_content = "test file content for signed file"
        test_file = create_temp_file(test_content)
        
        try:
            # 3. 签名文件
            signature = self.file_signer.sign_file(test_file, private_key, "sha256")
            
            # 4. 创建带签名的文件
            signed_file = os.path.join(self.test_dir, "test_file.signed")
            self.file_signer.attach_signature_to_file(test_file, signature, signed_file)
            
            # 5. 验证带签名的文件
            verify_result = self.verifier.verify_signed_file(signed_file, public_key, "sha256")
            self.assertTrue(verify_result["valid"])
        finally:
            cleanup_temp_path(test_file)
    
    def test_batch_signing(self):
        """测试批量签名"""
        # 1. 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 2. 创建多个测试文件
        test_files = []
        for i in range(3):
            test_content = f"test file {i} content"
            test_file = create_temp_file(test_content)
            test_files.append(test_file)
        
        try:
            # 3. 执行批量签名
            output_dir = os.path.join(self.test_dir, "signatures")
            os.makedirs(output_dir, exist_ok=True)
            
            results = self.file_signer.batch_sign(
                test_files,
                private_key,
                output_dir,
                "sha256"
            )
            
            # 4. 验证所有文件都签名成功
            success_count = sum(1 for result in results if result["success"])
            self.assertEqual(success_count, len(test_files))
            
            # 5. 验证每个签名文件
            for result in results:
                if result["success"]:
                    # 加载签名文件
                    signature_data = self.file_signer.load_signature(result["signature_file"])
                    loaded_signature, hash_algorithm, file_info = signature_data
                    
                    # 验证签名
                    verify_result = self.verifier.verify_file_signature(
                        result["file"],
                        loaded_signature,
                        public_key,
                        hash_algorithm
                    )
                    self.assertTrue(verify_result["valid"])
        finally:
            for test_file in test_files:
                cleanup_temp_path(test_file)


if __name__ == "__main__":
    unittest.main()
