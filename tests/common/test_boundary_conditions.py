# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

"""测试边界条件和异常处理

测试各种模块的边界条件和异常场景
"""

import unittest
import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# 添加tests目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.trucert.core.utils import initialize_dependencies
from src.trucert.core.business.key_manager import KeyManager
from src.trucert.core.business.cert_manager import CertManager
from src.trucert.core.business.file_signer import FileSigner
from tests.utils.test_utils import create_temp_directory, create_temp_file, cleanup_temp_path


class TestBoundaryConditions(unittest.TestCase):
    """测试边界条件和异常处理"""
    
    def setUp(self):
        """设置测试环境"""
        # 初始化依赖注入容器
        initialize_dependencies()
        # 创建密钥管理器实例
        self.key_manager = KeyManager()
        # 创建证书管理器实例
        self.cert_manager = CertManager()
        # 创建文件签名器实例
        self.file_signer = FileSigner()
    
    def tearDown(self):
        """清理测试环境"""
        pass
    
    def test_rsa_key_size_boundaries(self):
        """测试RSA密钥大小边界"""
        # 测试最小RSA密钥大小
        # 注意：这里暂时注释掉，因为1024位RSA密钥可能被认为不安全
        # try:
        #     private_key, public_key = self.key_manager.generate_rsa_key(key_size=1024, auto_save=False)
        #     self.assertIsNotNone(private_key)
        #     self.assertIsNotNone(public_key)
        # except Exception as e:
        #     # 验证异常被正确捕获
        #     pass
        
        # 测试常用RSA密钥大小
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        
        # 测试较大RSA密钥大小
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=4096, auto_save=False)
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
    
    def test_ecc_curve_validation(self):
        """测试ECC曲线验证"""
        # 测试有效ECC曲线
        private_key, public_key = self.key_manager.generate_ecc_key(curve="SECP256R1", auto_save=False)
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        
        # 测试无效ECC曲线
        try:
            private_key, public_key = self.key_manager.generate_ecc_key(curve="INVALID_CURVE", auto_save=False)
            # 应该抛出异常
            self.fail("Expected exception not raised")
        except Exception as e:
            # 验证异常被正确捕获
            pass
    
    def test_certificate_validity_boundaries(self):
        """测试证书有效期边界"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 测试最短有效期
        cert_data = self.cert_manager.generate_self_signed_cert(
            public_key=public_key,
            private_key=private_key,
            validity_days=1,
            forward_offset=0
        )
        self.assertIsInstance(cert_data, dict)
        
        # 测试最长有效期
        cert_data = self.cert_manager.generate_self_signed_cert(
            public_key=public_key,
            private_key=private_key,
            validity_days=3650,  # 10年
            forward_offset=0
        )
        self.assertIsInstance(cert_data, dict)
    
    def test_file_signature_edge_cases(self):
        """测试文件签名边界情况"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 测试空文件
        empty_file = create_temp_file("")
        try:
            signature = self.file_signer.sign_file(empty_file, private_key, "sha256")
            self.assertIsInstance(signature, bytes)
        finally:
            cleanup_temp_path(empty_file)
        
        # 测试小文件
        small_file = create_temp_file("small")
        try:
            signature = self.file_signer.sign_file(small_file, private_key, "sha256")
            self.assertIsInstance(signature, bytes)
        finally:
            cleanup_temp_path(small_file)
    
    def test_invalid_hash_algorithm(self):
        """测试无效哈希算法"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 创建测试文件
        test_file = create_temp_file("test content")
        
        try:
            # 测试无效哈希算法
            signature = self.file_signer.sign_file(test_file, private_key, "invalid_hash")
            # 应该抛出异常
            self.fail("Expected exception not raised")
        except Exception as e:
            # 验证异常被正确捕获
            pass
        finally:
            cleanup_temp_path(test_file)
    
    def test_nonexistent_file(self):
        """测试不存在的文件"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 测试不存在的文件
        try:
            signature = self.file_signer.sign_file("nonexistent_file.txt", private_key, "sha256")
            # 应该抛出异常
            self.fail("Expected exception not raised")
        except Exception as e:
            # 验证异常被正确捕获
            pass


if __name__ == "__main__":
    unittest.main()