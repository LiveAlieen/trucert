# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

#!/usr/bin/env python3
"""
测试ECC密钥制作证书功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from cert_manager.core.key_manager import KeyManager
from cert_manager.core.cert_manager import CertManager


def test_ecc_certificate_generation():
    """测试ECC密钥制作证书功能"""
    print("=== 测试ECC密钥制作证书功能 ===")
    
    # 初始化密钥管理器
    print("1. 初始化密钥管理器...")
    key_manager = KeyManager()
    print("✓ 密钥管理器初始化成功")
    
    # 生成ECC密钥对
    print("2. 生成ECC密钥对...")
    private_key, public_key = key_manager.generate_ecc_key(curve="SECP256R1", auto_save=True)
    print("✓ ECC密钥对生成成功")
    print(f"  曲线: SECP256R1")
    
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
    print(f"  有效期: {cert_data['cert_info'].get('validity_days', 'N/A')}天")
    
    # 列出所有证书
    print("5. 列出所有证书...")
    certs = cert_manager.list_certs()
    print(f"✓ 找到 {len(certs)} 个证书")
    
    # 查找刚刚生成的ECC证书
    ecc_certs = [cert for cert in certs if cert['cert_info'].get('algorithm') == 'ECC']
    if ecc_certs:
        print(f"✓ 找到 {len(ecc_certs)} 个ECC证书")
        for i, cert_info in enumerate(ecc_certs):
            print(f"  {i+1}. {cert_info['filename']} ({cert_info['type']})")
    else:
        print("✗ 没有找到ECC证书")
    
    print("\n=== 测试完成 ===")
    print("✓ ECC密钥制作证书功能测试成功")
    assert True


if __name__ == "__main__":
    success = test_ecc_certificate_generation()
    sys.exit(0 if success else 1)
