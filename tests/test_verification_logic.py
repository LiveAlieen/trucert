#!/usr/bin/env python3
"""
测试验证逻辑
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from cert_manager.core.key_manager import KeyManager
from cert_manager.core.cert_manager import CertManager
from cert_manager.core.verifier import Verifier


def test_verification_logic():
    """测试验证逻辑"""
    print("=== 测试验证逻辑 ===")
    
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
    print(f"  根证书parent_public_key字段: '{root_cert_data['cert_info'].get('parent_public_key', 'N/A')}'")
    
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
    print(f"  二级证书parent_public_key字段: '{secondary_cert_data['cert_info'].get('parent_public_key', 'N/A')}'")
    
    # 初始化验证器
    print("7. 初始化验证器...")
    verifier = Verifier()
    print("✓ 验证器初始化成功")
    
    # 验证根证书
    print("8. 验证根证书...")
    root_verification_result = verifier.verify_json_cert(root_cert_data)
    print(f"  根证书验证结果: {'有效' if root_verification_result['valid'] else '无效'}")
    print(f"  验证原因: {root_verification_result['reason']}")
    assert root_verification_result['valid'], "根证书验证失败"
    print("✓ 根证书验证成功")
    
    # 验证二级证书（使用parent_public_key字段）
    print("9. 验证二级证书（使用parent_public_key字段）...")
    secondary_verification_result = verifier.verify_json_cert(secondary_cert_data)
    print(f"  二级证书验证结果: {'有效' if secondary_verification_result['valid'] else '无效'}")
    print(f"  验证原因: {secondary_verification_result['reason']}")
    assert secondary_verification_result['valid'], "二级证书验证失败"
    print("✓ 二级证书验证成功")
    
    # 验证二级证书（使用上级证书）
    print("10. 验证二级证书（使用上级证书）...")
    secondary_verification_with_parent_result = verifier.verify_json_cert(secondary_cert_data, root_cert_data)
    print(f"  二级证书验证结果: {'有效' if secondary_verification_with_parent_result['valid'] else '无效'}")
    print(f"  验证原因: {secondary_verification_with_parent_result['reason']}")
    assert secondary_verification_with_parent_result['valid'], "二级证书验证失败（使用上级证书）"
    print("✓ 二级证书验证成功（使用上级证书）")
    
    print("\n=== 测试完成 ===")
    print("✓ 验证逻辑测试成功")
    assert True


if __name__ == "__main__":
    success = test_verification_logic()
    sys.exit(0 if success else 1)
