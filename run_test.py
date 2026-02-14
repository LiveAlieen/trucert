#!/usr/bin/env python3
"""
运行单个测试的脚本
"""

import sys
import os
import unittest

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

# 导入相关类
from cert_manager.core.key_manager import KeyManager
from cert_manager.core.file_signer import FileSigner
from cert_manager.core.verifier import Verifier
from tests.utils.test_utils import create_temp_directory, create_temp_file, cleanup_temp_path

# 调试测试
if __name__ == '__main__':
    # 模拟测试环境
    test_dir = create_temp_directory()
    key_manager = KeyManager()
    file_signer = FileSigner()
    verifier = Verifier()
    
    try:
        # 生成RSA密钥对
        print("1. 生成RSA密钥对...")
        private_key, public_key = key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        print(f"   私钥类型: {type(private_key)}")
        print(f"   公钥类型: {type(public_key)}")
        
        # 创建测试文件
        print("\n2. 创建测试文件...")
        test_content = "test file content"
        test_file = create_temp_file(test_content)
        print(f"   测试文件: {test_file}")
        
        # 签名文件
        print("\n3. 签名文件...")
        signature = file_signer.sign_file(test_file, private_key, "sha256")
        print(f"   签名长度: {len(signature)}")
        
        # 保存签名
        print("\n4. 保存签名...")
        output_dir = os.path.join(test_dir, "signatures")
        os.makedirs(output_dir, exist_ok=True)
        signature_file = os.path.join(output_dir, "test_file.sig.json")
        file_signer.save_signature(signature, signature_file, test_file, "sha256")
        print(f"   签名文件: {signature_file}")
        
        # 加载签名
        print("\n5. 加载签名...")
        loaded_signature, hash_algorithm, file_info = file_signer.load_signature(signature_file)
        print(f"   加载的签名长度: {len(loaded_signature)}")
        print(f"   哈希算法: {hash_algorithm}")
        print(f"   文件信息: {file_info}")
        
        # 验证签名
        print("\n6. 验证签名...")
        verify_result = verifier.verify_file_signature(test_file, loaded_signature, public_key, hash_algorithm)
        print(f"   验证结果: {verify_result}")
        
        # 直接使用FileSigner验证
        print("\n7. 直接使用FileSigner验证...")
        file_verify_result = file_signer.verify_file_signature(test_file, loaded_signature, public_key, hash_algorithm)
        print(f"   FileSigner验证结果: {file_verify_result}")
        
    finally:
        cleanup_temp_path(test_dir)
        cleanup_temp_path(test_file)
        print("\n测试完成，清理临时文件")
