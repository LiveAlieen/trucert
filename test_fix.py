#!/usr/bin/env python3
"""
测试修复脚本

用于验证密钥管理修复是否成功
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cert_manager.core.services import KeyService
from cert_manager.core.business import KeyManager

# 测试KeyManager
def test_key_manager():
    print("测试KeyManager...")
    key_manager = KeyManager()
    
    # 测试列出密钥
    print("测试列出密钥...")
    keys = key_manager.list_keys()
    print(f"找到 {len(keys)} 个密钥")
    
    # 测试生成RSA密钥
    print("测试生成RSA密钥...")
    key_id, private_key, public_key = key_manager.generate_rsa_key(key_size=2048)
    print(f"生成RSA密钥成功，ID: {key_id}")
    
    # 测试获取密钥信息
    print("测试获取密钥信息...")
    key_info = key_manager.get_key_info(key_id)
    print(f"密钥信息: {key_info}")
    
    # 测试删除密钥
    print("测试删除密钥...")
    success = key_manager.delete_key(key_id)
    print(f"删除密钥 {'成功' if success else '失败'}")
    
    # 测试生成ECC密钥
    print("测试生成ECC密钥...")
    key_id, private_key, public_key = key_manager.generate_ecc_key(curve="secp256r1")
    print(f"生成ECC密钥成功，ID: {key_id}")
    
    # 测试获取密钥信息
    print("测试获取密钥信息...")
    key_info = key_manager.get_key_info(key_id)
    print(f"密钥信息: {key_info}")
    
    # 测试删除密钥
    print("测试删除密钥...")
    success = key_manager.delete_key(key_id)
    print(f"删除密钥 {'成功' if success else '失败'}")

# 测试KeyService
def test_key_service():
    print("\n测试KeyService...")
    key_service = KeyService()
    
    # 测试列出密钥
    print("测试列出密钥...")
    keys = key_service.list_keys()
    print(f"找到 {len(keys)} 个密钥")
    
    # 测试生成RSA密钥
    print("测试生成RSA密钥...")
    private_info, public_info = key_service.generate_rsa_key(key_size=2048)
    print(f"生成RSA密钥成功")
    print(f"私钥信息: {private_info}")
    print(f"公钥信息: {public_info}")
    
    # 测试生成ECC密钥
    print("测试生成ECC密钥...")
    private_info, public_info = key_service.generate_ecc_key(curve="secp256r1")
    print(f"生成ECC密钥成功")
    print(f"私钥信息: {private_info}")
    print(f"公钥信息: {public_info}")

if __name__ == "__main__":
    try:
        test_key_manager()
        test_key_service()
        print("\n所有测试成功完成！")
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
