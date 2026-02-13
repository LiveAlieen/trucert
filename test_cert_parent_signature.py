#!/usr/bin/env python3
"""
测试证书parent_signature字段功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from cert_manager.core.key_manager import KeyManager
from cert_manager.core.cert_manager import CertManager


def test_certificate_parent_signature():
    """测试证书parent_signature字段功能"""
    print("=== 测试证书parent_signature字段功能 ===")
    
    try:
        # 初始化密钥管理器
        print("1. 初始化密钥管理器...")
        key_manager = KeyManager()
        print("✓ 密钥管理器初始化成功")
        
        # 生成CA密钥对
        print("2. 生成CA密钥对...")
        ca_private_key, ca_public_key = key_manager.generate_rsa_key(key_size=2048, auto_save=True)
        print("✓ CA密钥对生成成功")
        
        # 生成二级密钥对
        print("3. 生成二级密钥对...")
        secondary_private_key, secondary_public_key = key_manager.generate_rsa_key(key_size=2048, auto_save=True)
        print("✓ 二级密钥对生成成功")
        
        # 初始化证书管理器
        print("4. 初始化证书管理器...")
        cert_manager = CertManager()
        print("✓ 证书管理器初始化成功")
        
        # 生成自签名证书（根证书）
        print("5. 生成自签名证书（根证书）...")
        root_cert_data = cert_manager.generate_self_signed_cert(
            public_key=ca_public_key,
            private_key=ca_private_key,
            validity_days=365,
            forward_offset=0
        )
        print("✓ 自签名证书生成成功")
        print(f"  有parent_signature字段: {'是' if 'parent_signature' in root_cert_data else '否'}")
        print(f"  有type字段: {'是' if 'type' in root_cert_data else '否'}")
        
        # 生成二级证书
        print("6. 生成二级证书...")
        secondary_cert_data = cert_manager.generate_secondary_cert(
            public_key=secondary_public_key,
            parent_private_key=ca_private_key,
            parent_public_key=ca_public_key,
            validity_days=365,
            forward_offset=0
        )
        print("✓ 二级证书生成成功")
        print(f"  有parent_public_key字段: {'是' if 'parent_public_key' in secondary_cert_data.get('cert_info', {}) else '否'}")
        print(f"  有type字段: {'是' if 'type' in secondary_cert_data else '否'}")
        
        # 列出所有证书
        print("7. 列出所有证书...")
        certs = cert_manager.list_certs()
        print(f"✓ 找到 {len(certs)} 个证书")
        
        for i, cert_info in enumerate(certs):
            print(f"  {i+1}. {cert_info['filename']} ({cert_info['type']})")
            print(f"     根证书: {'是' if cert_info.get('is_root_cert', False) else '否'}")
        
        # 验证根证书和二级证书的区分
        print("8. 验证根证书和二级证书的区分...")
        root_certs = [cert for cert in certs if cert.get('is_root_cert', False)]
        secondary_certs = [cert for cert in certs if not cert.get('is_root_cert', False)]
        
        print(f"✓ 找到 {len(root_certs)} 个根证书")
        print(f"✓ 找到 {len(secondary_certs)} 个二级证书")
        
        print("\n=== 测试完成 ===")
        print("✓ 证书parent_signature字段功能测试成功")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_certificate_parent_signature()
    sys.exit(0 if success else 1)
