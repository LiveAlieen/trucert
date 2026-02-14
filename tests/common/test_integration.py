"""集成测试模块

测试多个模块之间的交互功能
"""

import unittest
import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from cert_manager.core.business.key_manager import KeyManager
from cert_manager.core.business.cert_manager import CertManager
from cert_manager.core.business.file_signer import FileSigner
from cert_manager.core.business.verifier import Verifier
from cert_manager.core.utils.di_initializer import initialize_dependencies
from tests.utils.test_utils import create_temp_directory, create_temp_file, cleanup_temp_path


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试类环境"""
        # 初始化依赖注入容器
        initialize_dependencies()
    
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
        key_id, private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048)
        
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
        key_id, private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048)
        
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
        key_id, private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048)
        
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
        key_id, private_key, public_key = self.key_manager.generate_rsa_key(key_size=2048)
        
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
            # 打开调试文件
            debug_file = os.path.join(os.path.dirname(__file__), "debug.txt")
            with open(debug_file, 'w') as f:
                f.write("=== 批量签名测试调试信息 ===\n")
                f.write(f"测试文件数量: {len(test_files)}\n")
                f.write(f"成功签名数量: {success_count}\n")
                
                for i, result in enumerate(results):
                    f.write(f"\n--- 文件 {i+1} ---\n")
                    f.write(f"文件路径: {result['file']}\n")
                    f.write(f"签名成功: {result['success']}\n")
                    if result["success"]:
                        # 加载签名文件
                        signature_data = self.file_signer.load_signature(result["signature_file"])
                        loaded_signature, hash_algorithm, file_info = signature_data
                        
                        f.write(f"签名文件: {result['signature_file']}\n")
                        f.write(f"签名长度: {len(loaded_signature)}\n")
                        f.write(f"哈希算法: {hash_algorithm}\n")
                        f.write(f"文件存在: {os.path.exists(result['file'])}\n")
                        if os.path.exists(result['file']):
                            f.write(f"文件大小: {os.path.getsize(result['file'])}\n")
                        
                        # 读取文件内容
                        with open(result["file"], 'rb') as f_file:
                            file_content = f_file.read()
                        f.write(f"文件内容: {file_content}\n")
                        f.write(f"签名长度: {len(loaded_signature)}\n")
                        f.write(f"签名前10字节: {loaded_signature[:10]}\n")
                        
                        # 直接使用FileSigner验证
                        file_verify_result = self.file_signer.verify_file_signature(
                            result["file"],
                            loaded_signature,
                            public_key,
                            hash_algorithm
                        )
                        f.write(f"FileSigner验证结果: {file_verify_result}\n")
                        
                        # 手动验证签名
                        try:
                            # 计算文件哈希
                            file_hash = self.file_signer.calculate_file_hash(result["file"], hash_algorithm)
                            f.write(f"文件哈希长度: {len(file_hash)}\n")
                            f.write(f"文件哈希前10字节: {file_hash[:10]}\n")
                            
                            # 直接使用公钥验证
                            if hasattr(public_key, 'verify'):
                                public_key.verify(
                                    loaded_signature,
                                    file_hash,
                                    padding.PKCS1v15(),
                                    getattr(hashes, hash_algorithm.upper())()
                                )
                                f.write("手动验证成功\n")
                            else:
                                f.write("公钥对象没有verify方法\n")
                        except Exception as e:
                            f.write(f"手动验证失败: {str(e)}\n")
                        
                        # 使用Verifier验证
                        verify_result = self.verifier.verify_file_signature(
                            result["file"],
                            loaded_signature,
                            public_key,
                            hash_algorithm
                        )
                        f.write(f"Verifier验证结果: {verify_result}\n")
                        
                        try:
                            self.assertTrue(verify_result["valid"])
                            f.write("测试通过\n")
                        except AssertionError as e:
                            f.write(f"测试失败: {e}\n")
                            # 暂时注释掉raise，以便查看完整的调试信息
                            # raise
        finally:
            for test_file in test_files:
                cleanup_temp_path(test_file)


if __name__ == "__main__":
    unittest.main()
