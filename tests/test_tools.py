"""测试工具模块

测试哈希、加密、文件和验证工具的功能
"""

import unittest
import os
from cert_manager.utils import (
    calculate_hash, calculate_file_hash, verify_hash, verify_file_hash,
    generate_rsa_key, generate_ecc_key, sign_data, verify_signature,
    save_private_key, save_public_key, load_private_key, load_public_key,
    read_file, write_file, read_binary_file, write_binary_file,
    read_json_file, write_json_file, file_exists, directory_exists
)
from tests.test_utils import create_temp_file, cleanup_temp_path


class TestHashUtils(unittest.TestCase):
    """测试哈希工具"""
    
    def test_calculate_hash(self):
        """测试计算哈希值"""
        data = "test data"
        hash_value = calculate_hash(data)
        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 64)  # SHA-256 长度
        
        # 测试不同哈希算法
        sha384_hash = calculate_hash(data, "sha384")
        self.assertEqual(len(sha384_hash), 96)  # SHA-384 长度
        
        sha512_hash = calculate_hash(data, "sha512")
        self.assertEqual(len(sha512_hash), 128)  # SHA-512 长度
    
    def test_calculate_file_hash(self):
        """测试计算文件哈希值"""
        test_content = "test file content"
        temp_file = create_temp_file(test_content)
        
        try:
            hash_value = calculate_file_hash(temp_file)
            self.assertIsInstance(hash_value, str)
            self.assertEqual(len(hash_value), 64)  # SHA-256 长度
        finally:
            cleanup_temp_path(temp_file)
    
    def test_verify_hash(self):
        """测试验证哈希值"""
        data = "test data"
        hash_value = calculate_hash(data)
        self.assertTrue(verify_hash(data, hash_value))
        self.assertFalse(verify_hash(data, "wrong_hash"))
    
    def test_verify_file_hash(self):
        """测试验证文件哈希值"""
        test_content = "test file content"
        temp_file = create_temp_file(test_content)
        
        try:
            hash_value = calculate_file_hash(temp_file)
            self.assertTrue(verify_file_hash(temp_file, hash_value))
            self.assertFalse(verify_file_hash(temp_file, "wrong_hash"))
        finally:
            cleanup_temp_path(temp_file)


class TestCryptoUtils(unittest.TestCase):
    """测试加密工具"""
    
    def test_generate_rsa_key(self):
        """测试生成RSA密钥对"""
        private_key, public_key = generate_rsa_key()
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
    
    def test_generate_ecc_key(self):
        """测试生成ECC密钥对"""
        private_key, public_key = generate_ecc_key()
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
    
    def test_sign_and_verify_data(self):
        """测试签名和验证数据"""
        # 生成RSA密钥对
        private_key, public_key = generate_rsa_key()
        
        # 测试数据
        test_data = b"test data"
        
        # 签名数据
        signature = sign_data(private_key, test_data)
        self.assertIsInstance(signature, bytes)
        
        # 验证签名
        self.assertTrue(verify_signature(public_key, signature, test_data))
        # 验证失败的情况
        self.assertFalse(verify_signature(public_key, signature, b"wrong data"))
    
    def test_save_and_load_keys(self):
        """测试保存和加载密钥"""
        # 生成RSA密钥对
        private_key, public_key = generate_rsa_key()
        
        # 创建临时文件
        private_key_file = create_temp_file(suffix=".pem")
        public_key_file = create_temp_file(suffix=".pem")
        
        try:
            # 保存密钥
            save_private_key(private_key, private_key_file)
            save_public_key(public_key, public_key_file)
            
            # 验证文件存在
            self.assertTrue(os.path.exists(private_key_file))
            self.assertTrue(os.path.exists(public_key_file))
            
            # 加载密钥
            loaded_private_key = load_private_key(private_key_file)
            loaded_public_key = load_public_key(public_key_file)
            
            self.assertIsNotNone(loaded_private_key)
            self.assertIsNotNone(loaded_public_key)
        finally:
            cleanup_temp_path(private_key_file)
            cleanup_temp_path(public_key_file)


class TestFileUtils(unittest.TestCase):
    """测试文件工具"""
    
    def test_read_write_file(self):
        """测试读取和写入文件"""
        temp_file = create_temp_file(suffix=".txt")
        test_content = "test content"
        
        try:
            # 写入文件
            write_file(temp_file, test_content)
            
            # 读取文件
            read_content = read_file(temp_file)
            self.assertEqual(read_content, test_content)
        finally:
            cleanup_temp_path(temp_file)
    
    def test_read_write_binary_file(self):
        """测试读取和写入二进制文件"""
        temp_file = create_temp_file(suffix=".bin")
        test_content = b"test binary content"
        
        try:
            # 写入文件
            write_binary_file(temp_file, test_content)
            
            # 读取文件
            read_content = read_binary_file(temp_file)
            self.assertEqual(read_content, test_content)
        finally:
            cleanup_temp_path(temp_file)
    
    def test_read_write_json_file(self):
        """测试读取和写入JSON文件"""
        temp_file = create_temp_file(suffix=".json")
        test_data = {"key": "value", "number": 123}
        
        try:
            # 写入文件
            write_json_file(temp_file, test_data)
            
            # 读取文件
            read_data = read_json_file(temp_file)
            self.assertEqual(read_data, test_data)
        finally:
            cleanup_temp_path(temp_file)
    
    def test_file_exists(self):
        """测试文件存在检查"""
        temp_file = create_temp_file()
        
        try:
            self.assertTrue(file_exists(temp_file))
            self.assertFalse(file_exists("non_existent_file.txt"))
        finally:
            cleanup_temp_path(temp_file)
    
    def test_directory_exists(self):
        """测试目录存在检查"""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        try:
            self.assertTrue(directory_exists(temp_dir))
            self.assertFalse(directory_exists("non_existent_directory"))
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
