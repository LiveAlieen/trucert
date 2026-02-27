# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

"""算法模块测试"""

import unittest
from trucert.core.algorithms import (
    get_algorithm, list_algorithms, list_algorithm_versions, set_default_version
)


class TestAlgorithms(unittest.TestCase):
    """算法模块测试类"""
    
    def test_algorithm_discovery(self):
        """测试算法自动发现功能"""
        # 列出所有算法
        all_algorithms = list_algorithms()
        
        # 检查是否包含所有类型的算法
        self.assertIn('encryption', all_algorithms)
        self.assertIn('signature', all_algorithms)
        self.assertIn('hashing', all_algorithms)
        
        # 检查具体算法是否存在
        self.assertIn('RSA', all_algorithms['encryption'])
        self.assertIn('ECC', all_algorithms['encryption'])
        self.assertIn('RSA-SIGN', all_algorithms['signature'])
        self.assertIn('ECC-SIGN', all_algorithms['signature'])
        self.assertIn('SHA256', all_algorithms['hashing'])
        self.assertIn('SHA384', all_algorithms['hashing'])
        self.assertIn('SHA512', all_algorithms['hashing'])
    
    def test_encryption_algorithms(self):
        """测试加密算法"""
        # 测试RSA算法
        rsa_algorithm = get_algorithm('encryption', 'RSA')
        rsa_instance = rsa_algorithm()
        
        # 生成密钥对
        private_key, public_key = rsa_instance.generate_key(key_size=1024)
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        
        # 测试加密解密
        test_data = b"Hello, World!"
        encrypted_data = rsa_instance.encrypt(public_key, test_data)
        self.assertIsNotNone(encrypted_data)
        self.assertNotEqual(encrypted_data, test_data)
        
        decrypted_data = rsa_instance.decrypt(private_key, encrypted_data)
        self.assertEqual(decrypted_data, test_data)
        
        # 测试ECC算法
        ecc_algorithm = get_algorithm('encryption', 'ECC')
        ecc_instance = ecc_algorithm()
        
        # 生成密钥对
        private_key, public_key = ecc_instance.generate_key()
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
    
    def test_signature_algorithms(self):
        """测试签名算法"""
        # 测试RSA签名
        rsa_sign_algorithm = get_algorithm('signature', 'RSA-SIGN')
        rsa_sign_instance = rsa_sign_algorithm()
        
        # 生成RSA密钥对
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=1024,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # 测试签名和验证
        test_data = b"Hello, Signature!"
        signature = rsa_sign_instance.sign(private_key, test_data)
        self.assertIsNotNone(signature)
        
        is_valid = rsa_sign_instance.verify(public_key, signature, test_data)
        self.assertTrue(is_valid)
        
        # 测试ECC签名
        ecc_sign_algorithm = get_algorithm('signature', 'ECC-SIGN')
        ecc_sign_instance = ecc_sign_algorithm()
        
        # 生成ECC密钥对
        from cryptography.hazmat.primitives.asymmetric import ec
        private_key = ec.generate_private_key(
            ec.SECP256R1(),
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # 测试签名和验证
        signature = ecc_sign_instance.sign(private_key, test_data)
        self.assertIsNotNone(signature)
        
        is_valid = ecc_sign_instance.verify(public_key, signature, test_data)
        self.assertTrue(is_valid)
    
    def test_hashing_algorithms(self):
        """测试哈希算法"""
        # 测试SHA256
        sha256_algorithm = get_algorithm('hashing', 'SHA256')
        sha256_instance = sha256_algorithm()
        
        test_data = b"Hello, Hash!"
        hash_bytes = sha256_instance.calculate(test_data)
        self.assertEqual(len(hash_bytes), 32)  # SHA256产生32字节哈希
        
        hash_hex = sha256_instance.calculate_hex(test_data)
        self.assertEqual(len(hash_hex), 64)  # 十六进制字符串长度为64
        
        # 测试SHA384
        sha384_algorithm = get_algorithm('hashing', 'SHA384')
        sha384_instance = sha384_algorithm()
        
        hash_bytes = sha384_instance.calculate(test_data)
        self.assertEqual(len(hash_bytes), 48)  # SHA384产生48字节哈希
        
        # 测试SHA512
        sha512_algorithm = get_algorithm('hashing', 'SHA512')
        sha512_instance = sha512_algorithm()
        
        hash_bytes = sha512_instance.calculate(test_data)
        self.assertEqual(len(hash_bytes), 64)  # SHA512产生64字节哈希
    
    def test_version_management(self):
        """测试算法版本管理"""
        # 测试列出算法版本
        versions = list_algorithm_versions('encryption', 'RSA')
        self.assertIn('1.0', versions)
        
        # 测试获取指定版本的算法
        rsa_v1 = get_algorithm('encryption', 'RSA', version='1.0')
        self.assertIsNotNone(rsa_v1)
        
        # 测试获取默认版本的算法
        rsa_default = get_algorithm('encryption', 'RSA')
        self.assertIsNotNone(rsa_default)


if __name__ == '__main__':
    unittest.main()
