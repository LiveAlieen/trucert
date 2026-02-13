"""测试文件签名模块

测试文件签名和验证的功能
"""

import unittest
import os
from cert_manager.core.file_signer import FileSigner
from cert_manager.core.key_manager import KeyManager
from tests.test_utils import create_temp_file, create_temp_directory, cleanup_temp_path


class TestFileSigner(unittest.TestCase):
    """测试文件签名"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建文件签名器实例
        self.file_signer = FileSigner()
        # 创建密钥管理器实例
        self.key_manager = KeyManager()
    
    def tearDown(self):
        """清理测试环境"""
        pass
    
    def test_sign_file(self):
        """测试签名文件"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 创建测试文件
        test_content = "test file content"
        test_file = create_temp_file(test_content)
        
        try:
            # 签名文件
            signature = self.file_signer.sign_file(test_file, private_key, "sha256")
            
            # 验证签名生成成功
            self.assertIsInstance(signature, bytes)
            self.assertGreater(len(signature), 0)
        finally:
            cleanup_temp_path(test_file)
    
    def test_save_and_load_signature(self):
        """测试保存和加载签名"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 创建测试文件
        test_content = "test file content"
        test_file = create_temp_file(test_content)
        
        try:
            # 签名文件
            signature = self.file_signer.sign_file(test_file, private_key, "sha256")
            
            # 保存签名
            signature_file = create_temp_file(suffix=".json")
            self.file_signer.save_signature(signature, signature_file, test_file, "sha256")
            
            # 验证签名文件存在
            self.assertTrue(os.path.exists(signature_file))
            
            # 加载签名
            loaded_signature, hash_algorithm, file_info = self.file_signer.load_signature(signature_file)
            
            # 验证签名加载成功
            self.assertIsInstance(loaded_signature, bytes)
            self.assertEqual(hash_algorithm, "sha256")
            self.assertIsInstance(file_info, dict)
        finally:
            cleanup_temp_path(test_file)
            cleanup_temp_path(signature_file)
    
    def test_attach_signature_to_file(self):
        """测试将签名附加到文件"""
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
            result_path = self.file_signer.attach_signature_to_file(test_file, signature, signed_file)
            
            # 验证签名文件存在
            self.assertTrue(os.path.exists(result_path))
            
            # 提取签名
            file_content, extracted_signature = self.file_signer.extract_signature_from_file(result_path)
            
            # 验证签名提取成功
            self.assertEqual(file_content, test_content.encode())
            self.assertIsInstance(extracted_signature, bytes)
        finally:
            cleanup_temp_path(test_file)
            cleanup_temp_path(signed_file)
    
    def test_batch_sign(self):
        """测试批量签名"""
        # 生成RSA密钥对
        private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        
        # 创建多个测试文件
        test_files = []
        for i in range(3):
            test_content = f"test file {i}"
            test_file = create_temp_file(test_content)
            test_files.append(test_file)
        
        # 创建输出目录
        output_dir = create_temp_directory()
        
        try:
            # 执行批量签名
            results = self.file_signer.batch_sign(
                test_files,
                private_key,
                output_dir,
                "sha256"
            )
            
            # 验证批量签名结果
            self.assertEqual(len(results), len(test_files))
            success_count = sum(1 for result in results if result["success"])
            self.assertEqual(success_count, len(test_files))
            
            # 验证签名文件存在
            for result in results:
                if result["success"]:
                    self.assertTrue(os.path.exists(result["signature_file"]))
        finally:
            for test_file in test_files:
                cleanup_temp_path(test_file)
            cleanup_temp_path(output_dir)


if __name__ == "__main__":
    unittest.main()
