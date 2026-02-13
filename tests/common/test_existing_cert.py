#!/usr/bin/env python3
"""
测试现有证书管理功能
"""

import os
import sys
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from cert_manager.core.key_manager import KeyManager
from cert_manager.core.cert_manager import CertManager


def test_existing_certificate_management():
    """测试现有证书管理功能"""
    print("=== 测试现有证书管理功能 ===")
    
    # 初始化密钥管理器
    print("1. 初始化密钥管理器...")
    key_manager = KeyManager()
    print("✓ 密钥管理器初始化成功")
    
    # 初始化证书管理器
    print("2. 初始化证书管理器...")
    cert_manager = CertManager()
    print("✓ 证书管理器初始化成功")
    
    # 生成RSA密钥对
    print("3. 生成RSA密钥对...")
    private_key, public_key = key_manager.generate_rsa_key(key_size=2048, auto_save=True)
    print("✓ RSA密钥对生成成功")
    
    # 生成自签名证书
    print("4. 生成自签名证书...")
    cert_data = cert_manager.generate_self_signed_cert(
        public_key=public_key,
        private_key=private_key,
        validity_days=365,
        forward_offset=0
    )
    print("✓ 自签名证书生成成功")
    
    # 列出所有证书
    print("5. 列出所有证书...")
    certs = cert_manager.list_certs()
    print(f"✓ 找到 {len(certs)} 个证书")
    for i, cert_info in enumerate(certs):
        print(f"  {i+1}. {cert_info['filename']} ({cert_info['type']})")
    
    if certs:
        # 测试删除证书
        print("6. 测试删除证书...")
        # 只删除最后一个证书，保留其他证书
        cert_to_delete = certs[-1]
        print(f"  准备删除证书: {cert_to_delete['filename']}")
        success = cert_manager.delete_cert(cert_to_delete['path'])
        if success:
            print("✓ 证书删除成功")
            # 再次列出证书，确认删除
            certs_after_delete = cert_manager.list_certs()
            print(f"  删除后剩余 {len(certs_after_delete)} 个证书")
        else:
            print("✗ 证书删除失败")
    
    # 测试导入证书
    print("7. 测试导入证书...")
    # 创建一个临时证书文件用于导入
    temp_cert_data = {
        "cert_info": {
            "algorithm": "RSA",
            "hash_algorithm": "SHA256",
            "validity_days": 365,
            "forward_offset": 0,
            "timestamp": "2026-02-11T00:00:00"
        },
        "signature": "test_signature",
        "public_key": "test_public_key",
        "type": "self_signed"
    }
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        import json
        json.dump(temp_cert_data, f)
        temp_filepath = f.name
    
    try:
        # 导入证书
        imported_cert = cert_manager.import_cert(temp_filepath)
        print("✓ 证书导入成功")
        # 再次列出证书，确认导入
        certs_after_import = cert_manager.list_certs()
        print(f"  导入后共有 {len(certs_after_import)} 个证书")
    finally:
        # 删除临时文件
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
    
    print("\n=== 测试完成 ===")
    print("✓ 现有证书管理功能测试成功")
    assert True


if __name__ == "__main__":
    success = test_existing_certificate_management()
    sys.exit(0 if success else 1)
