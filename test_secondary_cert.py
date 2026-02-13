#!/usr/bin/env python3
"""
测试二级证书生成功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from cert_manager.core.key_manager import KeyManager
from cert_manager.core.cert_manager import CertManager


def test_secondary_certificate_generation():
    """测试二级证书生成功能"""
    print("=== 测试二级证书生成功能 ===")
    
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
        
        # 生成二级证书（只使用二级公钥和CA私钥，不使用二级私钥）
        print("5. 生成二级证书...")
        cert_data = cert_manager.generate_secondary_cert(
            public_key=secondary_public_key,
            parent_private_key=ca_private_key,
            parent_public_key=ca_public_key,
            validity_days=365,
            forward_offset=0
        )
        print("✓ 二级证书生成成功")
        print(f"  算法: {cert_data['cert_info']['algorithm']}")
        print(f"  签名算法: {cert_data['cert_info']['signature_algorithm']}")
        print(f"  上级公钥: {cert_data['cert_info']['parent_public_key'][:20]}...")
        
        # 检查trust文件夹是否创建了二级证书
        print("6. 检查trust文件夹...")
        trust_dir = os.path.join('cert_manager', 'configs', 'trust')
        if os.path.exists(trust_dir):
            print("✓ trust文件夹存在")
            # 列出trust文件夹中的二级证书
            secondary_cert_files = [f for f in os.listdir(trust_dir) if f.startswith('secondary_') and f.endswith('.json')]
            if secondary_cert_files:
                print(f"  找到 {len(secondary_cert_files)} 个二级证书文件:")
                for cert_file in secondary_cert_files[-3:]:  # 只显示最近的3个
                    print(f"    - {cert_file}")
            else:
                print("  trust文件夹中没有二级证书文件")
        else:
            print("✗ trust文件夹不存在")
        
        print("\n=== 测试完成 ===")
        print("✓ 成功验证：二级证书生成不再需要二级私钥")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_secondary_certificate_generation()
    sys.exit(0 if success else 1)
