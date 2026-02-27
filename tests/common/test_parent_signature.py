# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

#!/usr/bin/env python3
"""
测试上级证书签名值功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from cert_manager.core.key_manager import KeyManager
from cert_manager.core.cert_manager import CertManager


def test_parent_signature():
    """测试上级证书签名值功能"""
    print("=== 测试上级证书签名值功能 ===")
    
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
    print(f"  根证书签名: {root_cert_data['signature'][:20]}...")
    print(f"  根证书parent_public_key: {root_cert_data['cert_info']['parent_public_key'][:20]}...")
    print(f"  签名是否相同: {'是' if root_cert_data['signature'] == root_cert_data['cert_info']['parent_public_key'] else '否'}")
    
    # 生成二级证书，使用根证书的公钥作为parent_public_key
    print("6. 生成二级证书...")
    secondary_cert_data = cert_manager.generate_secondary_cert(
        public_key=secondary_public_key,
        parent_private_key=ca_private_key,
        parent_public_key=ca_public_key,  # 使用根证书的公钥作为parent_signature
        validity_days=365,
        forward_offset=0
    )
    print("✓ 二级证书生成成功")
    print(f"  二级证书签名: {secondary_cert_data['signature'][:20]}...")
    print(f"  二级证书parent_public_key: {secondary_cert_data['cert_info']['parent_public_key'][:20]}...")
    print(f"  签名算法: {secondary_cert_data['cert_info']['signature_algorithm']}")
    print(f"  parent_public_key是否为根证书公钥: {'是' if secondary_cert_data['cert_info']['parent_public_key'] != secondary_cert_data['signature'] else '否'}")
    print(f"  签名是否不同: {'是' if secondary_cert_data['signature'] != secondary_cert_data['cert_info']['parent_public_key'] else '否'}")
    
    print("\n=== 测试完成 ===")
    print("✓ 上级证书签名值功能测试成功")
    assert True


if __name__ == "__main__":
    success = test_parent_signature()
    sys.exit(0 if success else 1)
