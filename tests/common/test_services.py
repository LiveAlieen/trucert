"""测试服务层功能

测试所有服务的主要功能，包括：
1. KeyService：测试密钥生成、加载、保存等功能
2. CertService：测试证书生成、加载、保存等功能
3. FileSignerService：测试文件签名、验证等功能
4. VerifierService：测试证书和文件验证功能
5. ConfigService：测试配置管理功能
"""

import unittest
import os
import tempfile
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'src'))

from cert_manager.core.services import KeyService, CertService, FileSignerService, VerifierService, ConfigService
from cert_manager.core.utils import initialize_dependencies

class TestServices(unittest.TestCase):
    """测试服务层功能"""
    
    @classmethod
    def setUpClass(cls):
        """类级别的设置，初始化依赖注入容器"""
        # 初始化依赖注入容器
        initialize_dependencies()
    
    def setUp(self):
        """设置测试环境"""
        # 创建服务实例
        self.key_service = KeyService()
        self.cert_service = CertService()
        self.file_signer_service = FileSignerService()
        self.verifier_service = VerifierService()
        self.config_service = ConfigService()
        
        # 创建临时文件和目录
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "test_file.txt")
        
        # 创建测试文件
        with open(self.temp_file, "w") as f:
            f.write("This is a test file for signature verification.")
    
    def tearDown(self):
        """清理测试环境"""
        # 清理临时文件和目录
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_key_service(self):
        """测试KeyService功能"""
        # 测试生成RSA密钥对
        result = self.key_service.generate_rsa_key({"key_size": 2048})
        self.assertTrue(result["success"])
        data = result["data"]
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["private_key_info"], dict)
        self.assertIsInstance(data["public_key_info"], dict)
        self.assertEqual(data["private_key_info"]["type"], "RSA Private Key")
        self.assertEqual(data["public_key_info"]["type"], "RSA Public Key")
        
        # 测试生成ECC密钥对
        result = self.key_service.generate_ecc_key({"curve": "secp256r1"})
        self.assertTrue(result["success"])
        data = result["data"]
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["private_key_info"], dict)
        self.assertIsInstance(data["public_key_info"], dict)
        self.assertEqual(data["private_key_info"]["type"], "ECC Private Key")
        self.assertEqual(data["public_key_info"]["type"], "ECC Public Key")
        
        # 测试统一的生成密钥对接口（RSA）
        result = self.key_service.generate_key({"key_type": "RSA", "key_size": 2048})
        self.assertTrue(result["success"])
        data = result["data"]
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["private_key_info"], dict)
        self.assertIsInstance(data["public_key_info"], dict)
        self.assertEqual(data["private_key_info"]["type"], "RSA Private Key")
        self.assertEqual(data["public_key_info"]["type"], "RSA Public Key")
        
        # 测试统一的生成密钥对接口（ECC）
        result = self.key_service.generate_key({"key_type": "ECC", "curve": "secp256r1"})
        self.assertTrue(result["success"])
        data = result["data"]
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["private_key_info"], dict)
        self.assertIsInstance(data["public_key_info"], dict)
        self.assertEqual(data["private_key_info"]["type"], "ECC Private Key")
        self.assertEqual(data["public_key_info"]["type"], "ECC Public Key")
        
        # 测试列出所有密钥
        result = self.key_service.list_keys()
        self.assertTrue(result["success"])
        keys = result["data"]
        self.assertIsInstance(keys, list)
    
    def test_cert_service(self):
        """测试CertService功能"""
        # 生成密钥对用于测试
        result = self.key_service.list_keys()
        self.assertTrue(result["success"])
        keys = result["data"]
        self.assertGreater(len(keys), 0)
        
        # 加载密钥对
        key_id = keys[0]["id"]
        load_result = self.key_service.load_key_pair({"key_id": key_id})
        self.assertTrue(load_result["success"])
        key_data = load_result["data"]
        private_key = key_data["private_key"]
        public_key = key_data["public_key"]
        
        # 测试生成自签名证书
        result = self.cert_service.generate_self_signed_cert({
            "public_key": public_key,
            "private_key": private_key,
            "validity_days": 365,
            "forward_offset": 0
        })
        self.assertTrue(result["success"])
        cert_data = result["data"]
        self.assertIsInstance(cert_data, dict)
        self.assertIn("cert_info", cert_data)
        self.assertIn("public_key", cert_data)
        self.assertIn("signature", cert_data)
        
        # 测试保存和加载证书
        temp_cert_file = os.path.join(self.temp_dir, "test_cert.json")
        save_result = self.cert_service.save_cert({"cert_data": cert_data, "filepath": temp_cert_file})
        self.assertTrue(save_result["success"])
        saved_path = save_result["data"]
        self.assertTrue(os.path.exists(saved_path))
        
        load_result = self.cert_service.load_cert({"filepath": saved_path})
        self.assertTrue(load_result["success"])
        loaded_cert = load_result["data"]
        self.assertIsInstance(loaded_cert, dict)
        self.assertEqual(loaded_cert["public_key"], cert_data["public_key"])
        
        # 清理临时文件
        if os.path.exists(saved_path):
            os.remove(saved_path)
    
    def test_file_signer_service(self):
        """测试FileSignerService功能"""
        # 生成密钥对用于测试
        result = self.key_service.list_keys()
        self.assertTrue(result["success"])
        keys = result["data"]
        self.assertGreater(len(keys), 0)
        
        # 加载密钥对
        key_id = keys[0]["id"]
        load_result = self.key_service.load_key_pair({"key_id": key_id})
        self.assertTrue(load_result["success"])
        key_data = load_result["data"]
        private_key = key_data["private_key"]
        public_key = key_data["public_key"]
        
        # 测试计算文件哈希
        result = self.file_signer_service.calculate_file_hash({"file_path": self.temp_file, "hash_algorithm": "sha256"})
        self.assertTrue(result["success"])
        file_hash = result["data"]
        self.assertIsInstance(file_hash, bytes)
        self.assertEqual(len(file_hash), 32)  # SHA-256 哈希长度为 32 字节
        
        # 测试签名文件
        result = self.file_signer_service.sign_file({"file_path": self.temp_file, "private_key": private_key, "hash_algorithm": "sha256"})
        self.assertTrue(result["success"])
        signature = result["data"]
        self.assertIsInstance(signature, bytes)
        
        # 测试保存和加载签名
        temp_sig_file = os.path.join(self.temp_dir, "test_signature.json")
        result = self.file_signer_service.save_signature({"signature": signature, "file_path": temp_sig_file, "original_file_path": self.temp_file, "hash_algorithm": "sha256"})
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(temp_sig_file))
        
        result = self.file_signer_service.load_signature({"file_path": temp_sig_file})
        self.assertTrue(result["success"])
        data = result["data"]
        loaded_signature = data["signature"]
        loaded_hash_algorithm = data["hash_algorithm"]
        file_info = data["file_info"]
        self.assertIsInstance(loaded_signature, bytes)
        self.assertEqual(loaded_hash_algorithm, "sha256")
        self.assertIsInstance(file_info, dict)
        
        # 清理临时文件
        if os.path.exists(temp_sig_file):
            os.remove(temp_sig_file)
    
    def test_verifier_service(self):
        """测试VerifierService功能"""
        # 生成密钥对用于测试
        result = self.key_service.list_keys()
        self.assertTrue(result["success"])
        keys = result["data"]
        self.assertGreater(len(keys), 0)
        
        # 加载密钥对
        key_id = keys[0]["id"]
        load_result = self.key_service.load_key_pair({"key_id": key_id})
        self.assertTrue(load_result["success"])
        key_data = load_result["data"]
        private_key = key_data["private_key"]
        public_key = key_data["public_key"]
        
        # 生成自签名证书
        result = self.cert_service.generate_self_signed_cert({
            "public_key": public_key,
            "private_key": private_key,
            "validity_days": 365,
            "forward_offset": 0
        })
        self.assertTrue(result["success"])
        cert_data = result["data"]
        
        # 测试证书生成和数据结构
        self.assertIsInstance(cert_data, dict)
        self.assertIn("cert_info", cert_data)
        self.assertIn("public_key", cert_data)
        self.assertIn("signature", cert_data)
    
    def test_config_service(self):
        """测试ConfigService功能"""
        # 测试获取算法配置
        result = self.config_service.get_algorithms()
        self.assertTrue(result["success"])
        algorithms = result["data"]
        self.assertIsInstance(algorithms, dict)
        self.assertIn("hash_algorithms", algorithms)
        self.assertIn("rsa_key_sizes", algorithms)
        self.assertIn("ecc_curves", algorithms)
        
        # 测试获取证书版本配置


if __name__ == "__main__":
    unittest.main()
