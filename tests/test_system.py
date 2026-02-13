"""系统测试模块

测试整个系统的完整功能，模拟用户实际使用场景
"""

import unittest
import os
from cert_manager.core.key_manager import KeyManager
from cert_manager.core.cert_manager import CertManager
from cert_manager.core.file_signer import FileSigner
from cert_manager.core.verifier import Verifier
from cert_manager.core.config import ConfigManager
from tests.test_utils import create_temp_file, create_temp_directory, cleanup_temp_path


class TestSystem(unittest.TestCase):
    """系统测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录
        self.test_dir = create_temp_directory()
        # 创建各个管理器实例
        self.key_manager = KeyManager()
        self.cert_manager = CertManager()
        self.file_signer = FileSigner()
        self.verifier = Verifier()
        self.config_manager = ConfigManager()
    
    def tearDown(self):
        """清理测试环境"""
        cleanup_temp_path(self.test_dir)
    
    def test_end_to_end_certificate_management(self):
        """测试端到端证书管理流程"""
        # 1. 检查配置
        algorithms = self.config_manager.get_algorithms()
        self.assertIsInstance(algorithms, dict)
        
        # 2. 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 3. 生成自签名证书
        cert_data = self.cert_manager.generate_self_signed_cert(
            public_key=public_key,
            private_key=private_key,
            validity_days=365,
            forward_offset=0
        )
        
        # 4. 保存证书
        cert_file = os.path.join(self.test_dir, "root_cert.json")
        self.cert_manager.save_cert(cert_data, cert_file)
        
        # 5. 列出证书
        certs = self.cert_manager.list_certs()
        self.assertGreaterEqual(len(certs), 0)
        
        # 6. 加载证书
        loaded_cert_data = self.cert_manager.load_cert(cert_file)
        
        # 7. 验证证书
        verify_result = self.verifier.verify_json_cert(loaded_cert_data)
        self.assertTrue(verify_result["valid"])
    
    def test_end_to_end_file_signing(self):
        """测试端到端文件签名流程"""
        # 1. 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 2. 创建测试文件
        test_content = "important document content"
        test_file = create_temp_file(test_content)
        
        try:
            # 3. 签名文件
            signature = self.file_signer.sign_file(test_file, private_key, "sha256")
            
            # 4. 保存签名
            signature_file = os.path.join(self.test_dir, "test_signature.json")
            self.file_signer.save_signature(signature, signature_file, test_file, "sha256")
            
            # 5. 加载签名
            loaded_signature, hash_algorithm, file_info = self.file_signer.load_signature(signature_file)
            
            # 6. 验证文件签名
            verify_result = self.verifier.verify_file_signature(test_file, loaded_signature, public_key, hash_algorithm)
            self.assertTrue(verify_result["valid"])
            
            # 7. 创建带签名的文件
            signed_file = os.path.join(self.test_dir, "test_file.signed")
            self.file_signer.attach_signature_to_file(test_file, signature, signed_file)
            
            # 8. 验证带签名的文件
            verify_signed_result = self.verifier.verify_signed_file(signed_file, public_key, "sha256")
            self.assertTrue(verify_signed_result["valid"])
        finally:
            cleanup_temp_path(test_file)
    
    def test_batch_file_signing_system(self):
        """测试批量文件签名系统功能"""
        # 1. 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 2. 创建多个测试文件
        test_files = []
        for i in range(5):
            test_content = f"document {i} content for batch signing"
            test_file = create_temp_file(test_content)
            test_files.append(test_file)
        
        try:
            # 3. 执行批量签名
            output_dir = os.path.join(self.test_dir, "batch_signatures")
            os.makedirs(output_dir, exist_ok=True)
            
            results = self.file_signer.batch_sign(
                test_files,
                private_key,
                output_dir,
                "sha256"
            )
            
            # 4. 验证批量签名结果
            success_count = sum(1 for result in results if result["success"])
            self.assertEqual(success_count, len(test_files))
            
            # 5. 验证每个签名
            for result in results:
                if result["success"]:
                    # 加载签名
                    loaded_signature, hash_algorithm, file_info = self.file_signer.load_signature(result["signature_file"])
                    
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
    
    def test_certificate_chain_verification(self):
        """测试证书链验证"""
        # 1. 生成根密钥对
        root_private_key, root_public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 2. 生成根证书
        root_cert_data = self.cert_manager.generate_self_signed_cert(
            public_key=root_public_key,
            private_key=root_private_key,
            validity_days=365,
            forward_offset=0
        )
        
        # 3. 保存根证书
        root_cert_file = os.path.join(self.test_dir, "root_cert.json")
        self.cert_manager.save_cert(root_cert_data, root_cert_file)
        
        # 4. 生成二级密钥对
        secondary_private_key, secondary_public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 5. 生成二级证书
        secondary_cert_data = self.cert_manager.generate_secondary_cert(
            public_key=secondary_public_key,
            parent_private_key=root_private_key,
            parent_public_key=root_public_key,
            validity_days=180,
            forward_offset=0
        )
        
        # 6. 保存二级证书
        secondary_cert_file = os.path.join(self.test_dir, "secondary_cert.json")
        self.cert_manager.save_cert(secondary_cert_data, secondary_cert_file)
        
        # 7. 验证二级证书
        loaded_secondary_cert = self.cert_manager.load_cert(secondary_cert_file)
        loaded_root_cert = self.cert_manager.load_cert(root_cert_file)
        
        verify_result = self.verifier.verify_json_cert(loaded_secondary_cert, loaded_root_cert)
        self.assertTrue(verify_result["valid"])


if __name__ == "__main__":
    unittest.main()
