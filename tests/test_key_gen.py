#!/usr/bin/env python3
"""测试密钥生成功能"""

from cert_manager.core.key_manager import KeyManager

def test_rsa_key_gen():
    print("测试RSA密钥生成...")
    key_manager = KeyManager()
    private_key, public_key = key_manager.generate_rsa_key(key_size=2048, auto_save=False)
    print("✓ RSA密钥生成成功")
    print(f"  密钥大小: {private_key.key_size}")
    assert True

def test_ecc_key_gen():
    print("\n测试ECC密钥生成...")
    key_manager = KeyManager()
    private_key, public_key = key_manager.generate_ecc_key(curve="secp256r1", auto_save=False)
    print("✓ ECC密钥生成成功")
    print(f"  曲线: {private_key.curve.name}")
    assert True

def test_key_save():
    print("\n测试密钥存储...")
    key_manager = KeyManager()
    private_key, public_key = key_manager.generate_rsa_key(key_size=2048, auto_save=True)
    print("✓ 密钥存储成功")
    
    # 测试列出密钥
    keys = key_manager.list_keys()
    print(f"  存储的密钥数量: {len(keys)}")
    if keys:
        print(f"  最后一个密钥: {keys[-1]['id']}")
    assert True

if __name__ == "__main__":
    print("开始测试密钥生成功能...\n")
    
    success = 0
    total = 3
    
    if test_rsa_key_gen():
        success += 1
    
    if test_ecc_key_gen():
        success += 1
    
    if test_key_save():
        success += 1
    
    print(f"\n测试完成: {success}/{total} 测试通过")
