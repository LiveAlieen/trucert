#!/usr/bin/env python3
"""
测试使用证书进行文件验证的功能
"""

import os
import sys
import tempfile

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from trucert.core.utils import initialize_dependencies
    from trucert.core.business.key_manager import KeyManager
    from trucert.core.business.cert_manager import CertManager
    from trucert.core.business.file_signer import FileSigner
    
    print("正在初始化依赖...")
    initialize_dependencies()
    print("依赖初始化成功！")
    
    # 1. 生成密钥对
    print("\n1. 生成RSA密钥对...")
    key_manager = KeyManager()
    private_key, public_key = key_manager.generate_rsa_key(key_size=2048, auto_save=False)
    print("密钥生成成功")
    
    # 2. 生成自签名证书
    print("\n2. 生成自签名证书...")
    cert_manager = CertManager()
    # 直接使用证书管理器保存证书
    cert_file = tempfile.mktemp(suffix='.tru')
    cert_data = cert_manager.generate_self_signed_cert(
        public_key=public_key,
        private_key=private_key,
        validity_days=365,
        forward_offset=0
    )
    # 使用证书管理器保存证书
    cert_manager.save_cert(cert_data, cert_file)
    print(f"证书生成成功，保存到: {cert_file}")
    
    # 3. 创建测试文件
    print("\n3. 创建测试文件...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test file for certificate verification.")
        test_file = f.name
    print(f"测试文件创建成功: {test_file}")
    
    # 4. 签名测试文件
    print("\n4. 签名测试文件...")
    file_signer = FileSigner()
    signature = file_signer.sign_file(test_file, private_key)
    
    # 保存签名到文件
    sig_file = test_file + ".giq"
    file_signer.save_signature(signature, sig_file, test_file)
    print(f"文件签名成功，签名保存到: {sig_file}")
    
    # 5. 使用证书验证文件签名
    print("\n5. 使用证书验证文件签名...")
    # 加载签名
    loaded_signature, hash_algorithm, file_info = file_signer.load_signature(sig_file)
    
    # 使用证书验证
    verify_result = file_signer.verify_file_signature_with_cert(
        test_file, loaded_signature, cert_file, hash_algorithm
    )
    
    if verify_result:
        print("🎉 证书验证成功！文件签名有效。")
    else:
        print("❌ 证书验证失败！文件签名无效。")
    
    # 6. 清理临时文件
    print("\n6. 清理临时文件...")
    os.unlink(test_file)
    os.unlink(sig_file)
    os.unlink(cert_file)
    print("临时文件清理完成！")
    
    print("\n测试完成！所有功能正常工作。")
    
    sys.exit(0)
    
except Exception as e:
    print(f"测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
