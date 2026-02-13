#!/usr/bin/env python3
"""
测试证书格式功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from cert_manager.core.key_manager import KeyManager
from cert_manager.core.cert_manager import CertManager


def test_certificate_format():
    """测试证书格式功能"""
    print("=== 测试证书格式功能 ===")
    
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
        
        # 验证证书格式
        print("5. 验证证书格式...")
        required_fields = ["timestamp", "forward_offset", "cert_info", "public_key", "signature"]
        for field in required_fields:
            if field in cert_data:
                print(f"  ✓ 包含字段: {field}")
            else:
                print(f"  ✗ 缺少字段: {field}")
        
        # 验证cert_info格式
        if "cert_info" in cert_data:
            cert_info_fields = ["algorithm", "hash_algorithm", "parent_signature"]
            for field in cert_info_fields:
                if field in cert_data["cert_info"]:
                    print(f"  ✓ cert_info包含字段: {field}")
                else:
                    print(f"  ✗ cert_info缺少字段: {field}")
        
        # 显示证书结构
        print("6. 证书结构:")
        print(f"  时间戳: {cert_data['timestamp']}")
        print(f"  正向偏移: {cert_data['forward_offset']}")
        print(f"  算法: {cert_data['cert_info']['algorithm']}")
        print(f"  哈希算法: {cert_data['cert_info']['hash_algorithm']}")
        print(f"  父签名: {cert_data['cert_info']['parent_signature'][:20]}...")
        print(f"  公钥: {cert_data['public_key'][:20]}...")
        print(f"  签名: {cert_data['signature'][:20]}...")
        print(f"  签名是否与父签名相同: {'是' if cert_data['signature'] == cert_data['cert_info']['parent_signature'] else '否'}")
        
        print("\n=== 测试完成 ===")
        print("✓ 证书格式功能测试成功")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_certificate_format()
    sys.exit(0 if success else 1)
