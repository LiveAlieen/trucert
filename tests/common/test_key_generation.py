from cert_manager.core.key_manager import KeyManager

# 测试密钥生成
key_manager = KeyManager()

# 生成RSA密钥
print("生成RSA密钥...")
private_key, public_key = key_manager.generate_rsa_key(key_size=2048, auto_save=True)

# 生成ECC密钥
print("生成ECC密钥...")
private_key_ecc, public_key_ecc = key_manager.generate_ecc_key(curve="SECP256R1", auto_save=True)

# 列出所有密钥
print("\n所有存储的密钥:")
keys = key_manager.list_keys()
for key in keys:
    print(f"ID: {key.get('id', 'N/A')}")
    print(f"Type: {key.get('type', 'N/A')}")
    print(f"Created At: {key.get('created_at', 'N/A')}")
    print(f"Encrypted: {key.get('encrypted', 'N/A')}")
    print("---")

print("测试完成")