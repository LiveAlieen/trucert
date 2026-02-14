"""测试证书管理模块

测试证书生成、存储和加载的功能
"""

import unittest
import os
from cert_manager.core.cert_manager import CertManager
from cert_manager.core.key_manager import KeyManager
from tests.utils.test_utils import create_temp_directory, cleanup_temp_path


class TestCertManager(unittest.TestCase):
    """测试证书管理"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录
        self.test_dir = create_temp_directory()
        # 创建证书管理器实例
        self.cert_manager = CertManager()
        # 创建密钥管理器实例
        self.key_manager = KeyManager()
    
    def tearDown(self):
        """清理测试环境"""
        cleanup_temp_path(self.test_dir)
    
    def test_generate_self_signed_cert(self):
        """测试生成自签名证书"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 生成自签名证书
        cert_data = self.cert_manager.generate_self_signed_cert(
            public_key=public_key,
            private_key=private_key,
            validity_days=365,
            forward_offset=0
        )
        
        # 验证证书数据生成成功
        self.assertIsInstance(cert_data, dict)
        self.assertIn("timestamp", cert_data)
        self.assertIn("forward_offset", cert_data)
        self.assertIn("cert_info", cert_data)
        self.assertIn("public_key", cert_data)
        self.assertIn("signature", cert_data)
    
    def test_save_and_load_cert(self):
        """测试保存和加载证书"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 生成自签名证书
        cert_data = self.cert_manager.generate_self_signed_cert(
            public_key=public_key,
            private_key=private_key,
            validity_days=365,
            forward_offset=0
        )
        
        # 保存证书
        cert_file = os.path.join(self.test_dir, "test_cert.json")
        self.cert_manager.save_cert(cert_data, cert_file)
        
        # 验证证书文件存在
        self.assertTrue(os.path.exists(cert_file))
        
        # 加载证书
        loaded_cert_data = self.cert_manager.load_cert(cert_file)
        
        # 验证证书加载成功
        self.assertIsInstance(loaded_cert_data, dict)
        self.assertIn("timestamp", loaded_cert_data)
        self.assertIn("forward_offset", loaded_cert_data)
        self.assertIn("cert_info", loaded_cert_data)
        self.assertIn("public_key", loaded_cert_data)
        self.assertIn("signature", loaded_cert_data)
    
    def test_get_cert_info(self):
        """测试获取证书信息"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 生成自签名证书
        cert_data = self.cert_manager.generate_self_signed_cert(
            public_key=public_key,
            private_key=private_key,
            validity_days=365,
            forward_offset=0
        )
        
        # 获取证书信息
        cert_info = self.cert_manager.get_cert_info(cert_data)
        
        # 验证证书信息获取成功
        self.assertIsInstance(cert_info, dict)
        self.assertIn("algorithm", cert_info)
        self.assertIn("signature_algorithm", cert_info)
        self.assertIn("storage_formats", cert_info)
    
    def test_list_certs(self):
        """测试列出所有证书"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 生成自签名证书
        cert_data = self.cert_manager.generate_self_signed_cert(
            public_key=public_key,
            private_key=private_key,
            validity_days=365,
            forward_offset=0
        )
        
        # 保存证书
        cert_file = os.path.join(self.test_dir, "test_cert.json")
        self.cert_manager.save_cert(cert_data, cert_file)
        
        # 列出所有证书
        certs = self.cert_manager.list_certs()
        
        # 验证至少有一个证书
        self.assertGreaterEqual(len(certs), 1)


if __name__ == "__main__":
    unittest.main()
