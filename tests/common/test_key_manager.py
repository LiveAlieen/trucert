"""测试密钥管理模块

测试密钥生成、存储和加载的功能
"""

import unittest
import os
from cert_manager.core.key_manager import KeyManager
from tests.utils.test_utils import create_temp_directory, cleanup_temp_path


class TestKeyManager(unittest.TestCase):
    """测试密钥管理"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录
        self.test_dir = create_temp_directory()
        # 创建密钥管理器实例
        self.key_manager = KeyManager()
    
    def tearDown(self):
        """清理测试环境"""
        cleanup_temp_path(self.test_dir)
    
    def test_generate_rsa_key(self):
        """测试生成RSA密钥对"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 验证密钥对生成成功
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
    
    def test_generate_ecc_key(self):
        """测试生成ECC密钥对"""
        # 生成ECC密钥对
        private_key, public_key = self.key_manager.generate_ecc_key(curve="SECP256R1", auto_save=False)
        
        # 验证密钥对生成成功
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
    
    def test_save_and_load_keys(self):
        """测试保存和加载密钥"""
        # 生成RSA密钥对并自动保存
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=True)
        
        # 测试保存私钥
        private_key_path = os.path.join(self.test_dir, "test_private.pem")
        self.key_manager.save_private_key(private_key, private_key_path)
        self.assertTrue(os.path.exists(private_key_path))
        
        # 测试保存公钥
        public_key_path = os.path.join(self.test_dir, "test_public.pem")
        self.key_manager.save_public_key(public_key, public_key_path)
        self.assertTrue(os.path.exists(public_key_path))
        
        # 测试加载私钥
        loaded_private_key = self.key_manager.load_private_key(private_key_path)
        self.assertIsNotNone(loaded_private_key)
        
        # 测试加载公钥
        loaded_public_key = self.key_manager.load_public_key(public_key_path)
        self.assertIsNotNone(loaded_public_key)
    
    def test_list_keys(self):
        """测试列出所有密钥"""
        # 生成RSA密钥对并自动保存
        self.key_manager.generate_rsa_key(key_size=2048, auto_save=True)
        
        # 生成ECC密钥对并自动保存
        self.key_manager.generate_ecc_key(curve="SECP256R1", auto_save=True)
        
        # 列出所有密钥
        keys = self.key_manager.list_keys()
        
        # 验证至少有两个密钥（RSA和ECC）
        self.assertGreaterEqual(len(keys), 2)
    
    def test_get_key_info(self):
        """测试获取密钥信息"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 获取私钥信息
        private_key_info = self.key_manager.get_key_info(private_key)
        self.assertIsInstance(private_key_info, dict)
        self.assertIn("type", private_key_info)
        self.assertIn("key_size", private_key_info)
        
        # 获取公钥信息
        public_key_info = self.key_manager.get_key_info(public_key)
        self.assertIsInstance(public_key_info, dict)
        self.assertIn("type", public_key_info)
        self.assertIn("key_size", public_key_info)


if __name__ == "__main__":
    unittest.main()
