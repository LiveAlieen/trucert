#!/usr/bin/env python3
"""
测试签名的保存和加载过程

验证签名在保存和加载过程中是否保持一致
"""

import os
import sys
import tempfile

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cert_manager.core.key_manager import KeyManager
from cert_manager.core.file_signer import FileSigner


def test_signature_save_load():
    """测试签名的保存和加载过程"""
    print("开始测试签名的保存和加载过程...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建KeyManager和FileSigner实例
        key_manager = KeyManager()
        file_signer = FileSigner()
        
        # 生成RSA密钥对
        print("生成RSA密钥对...")
        private_key, public_key = key_manager.generate_rsa_key(key_size=2048, auto_save=False)
        print(f"私钥类型: {type(private_key)}")
        print(f"公钥类型: {type(public_key)}")
        
        # 创建测试文件
        print("创建测试文件...")
        test_content = "test content for signature save/load test"
        test_file = os.path.join(temp_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write(test_content)
        print(f"测试文件路径: {test_file}")
        print(f"测试文件内容: {test_content}")
        
        # 生成签名
        print("生成签名...")
        signature = file_signer.sign_file(test_file, private_key, "sha256")
        print(f"签名长度: {len(signature)}")
        print(f"签名前10字节: {signature[:10]}")
        print(f"签名完整值: {signature}")
        
        # 验证签名
        print("验证签名...")
        verify_result = file_signer.verify_file_signature(test_file, signature, public_key, "sha256")
        print(f"签名验证结果: {verify_result}")
        
        # 保存签名
        print("保存签名...")
        signature_file = os.path.join(temp_dir, "test_signature.sig.json")
        file_signer.save_signature(signature, signature_file, test_file, "sha256")
        print(f"签名文件路径: {signature_file}")
        
        # 查看签名文件内容
        print("查看签名文件内容...")
        with open(signature_file, "r") as f:
            signature_content = f.read()
        print(f"签名文件内容: {signature_content}")
        
        # 加载签名
        print("加载签名...")
        loaded_signature, hash_algorithm, file_info = file_signer.load_signature(signature_file)
        print(f"加载的签名长度: {len(loaded_signature)}")
        print(f"加载的签名前10字节: {loaded_signature[:10]}")
        print(f"加载的签名完整值: {loaded_signature}")
        print(f"加载的哈希算法: {hash_algorithm}")
        print(f"加载的文件信息: {file_info}")
        
        # 比较签名
        print("比较签名...")
        print(f"签名是否相同: {signature == loaded_signature}")
        print(f"签名长度是否相同: {len(signature) == len(loaded_signature)}")
        
        # 验证加载的签名
        print("验证加载的签名...")
        loaded_verify_result = file_signer.verify_file_signature(test_file, loaded_signature, public_key, hash_algorithm)
        print(f"加载的签名验证结果: {loaded_verify_result}")
        
        # 测试批量签名
        print("\n测试批量签名...")
        test_files = [test_file]
        output_dir = os.path.join(temp_dir, "batch_signatures")
        os.makedirs(output_dir, exist_ok=True)
        
        batch_results = file_signer.batch_sign(test_files, private_key, output_dir, "sha256")
        print(f"批量签名结果: {batch_results}")
        
        if batch_results and batch_results[0]["success"]:
            batch_signature_file = batch_results[0]["signature_file"]
            print(f"批量签名文件路径: {batch_signature_file}")
            
            # 查看批量签名文件内容
            print("查看批量签名文件内容...")
            with open(batch_signature_file, "r") as f:
                batch_signature_content = f.read()
            print(f"批量签名文件内容: {batch_signature_content}")
            
            # 加载批量签名
            print("加载批量签名...")
            batch_loaded_signature, batch_hash_algorithm, batch_file_info = file_signer.load_signature(batch_signature_file)
            print(f"批量加载的签名长度: {len(batch_loaded_signature)}")
            print(f"批量加载的签名前10字节: {batch_loaded_signature[:10]}")
            print(f"批量加载的签名完整值: {batch_loaded_signature}")
            print(f"批量加载的哈希算法: {batch_hash_algorithm}")
            
            # 比较批量签名和直接签名
            print("比较批量签名和直接签名...")
            print(f"批量签名与直接签名是否相同: {batch_loaded_signature == signature}")
            print(f"批量签名长度与直接签名长度是否相同: {len(batch_loaded_signature) == len(signature)}")
            
            # 验证批量签名
            print("验证批量签名...")
            batch_verify_result = file_signer.verify_file_signature(test_file, batch_loaded_signature, public_key, batch_hash_algorithm)
            print(f"批量签名验证结果: {batch_verify_result}")


if __name__ == "__main__":
    test_signature_save_load()
