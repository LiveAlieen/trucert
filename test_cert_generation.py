#!/usr/bin/env python3
"""
测试证书生成功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from cert_manager.core.key_manager import KeyManager
from cert_manager.core.cert_manager import CertManager


def test_certificate_generation():
    """测试证书生成功能"""
    print("=== 测试证书生成功能 ===")
    
    try:
        # 初始化密钥管理器
        print("1. 初始化密钥管理器...")
        key_manager = KeyManager()
        print("✓ 密钥管理器初始化成功")
        
        # 生成RSA密钥对
        print("2. 生成RSA密钥对...")
        private_key, public_key = key_manager.generate_rsa_key(key_size=2048, auto_save=True)
        print("✓ RSA密钥对生成成功")
        
        # 初始化证书管理器
        print("3. 初始化证书管理器...")
        cert_manager = CertManager()
        print("✓ 证书管理器初始化成功")
        
        # 生成自签名证书
        print("4. 生成自签名证书...")
        cert_data = cert_manager.generate_self_signed_cert(
            public_key=public_key,
            private_key=private_key,
            validity_days=365,
            forward_offset=0
        )
        print("✓ 自签名证书生成成功")
        print(f"  算法: {cert_data['cert_info']['algorithm']}")
        print(f"  签名算法: {cert_data['cert_info']['signature_algorithm']}")
        print(f"  上级公钥: {cert_data['cert_info']['parent_public_key']}")
        
        # 检查trust文件夹是否创建
        print("5. 检查trust文件夹...")
        trust_dir = os.path.join('cert_manager', 'configs', 'trust')
        if os.path.exists(trust_dir):
            print("✓ trust文件夹存在")
            # 列出trust文件夹中的证书
            cert_files = [f for f in os.listdir(trust_dir) if f.endswith('.json')]
            if cert_files:
                print(f"  找到 {len(cert_files)} 个证书文件:")
                for cert_file in cert_files:
                    print(f"    - {cert_file}")
            else:
                print("  trust文件夹为空")
        else:
            print("✗ trust文件夹不存在")
        
        print("\n=== 测试完成 ===")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_certificate_generation()
    sys.exit(0 if success else 1)
