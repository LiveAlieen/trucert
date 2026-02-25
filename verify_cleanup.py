#!/usr/bin/env python3
"""
验证删除根密钥相关代码后系统功能是否正常
"""

import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("正在验证核心模块导入...")
    
    # 导入核心模块
    from cert_manager.core.storage.key_storage import KeyStorage
    from cert_manager.core.storage.storage_manager import StorageManager
    
    print("✓ 核心模块导入成功")
    
    # 测试StorageManager初始化
    print("\n正在测试StorageManager初始化...")
    storage_manager = StorageManager()
    print(f"✓ StorageManager初始化成功，基础目录: {storage_manager.base_dir}")
    print(f"✓ 密钥目录: {storage_manager.get_key_dir()}")
    print(f"✓ 信任目录: {storage_manager.get_trust_dir()}")
    
    # 测试KeyStorage初始化
    print("\n正在测试KeyStorage初始化...")
    key_storage = KeyStorage(storage_manager)
    print("✓ KeyStorage初始化成功")
    
    # 测试密钥存储功能
    print("\n正在测试密钥存储功能...")
    # 列出当前存储的密钥
    keys = key_storage.list_keys()
    print(f"✓ 密钥列表功能正常，当前存储的密钥数量: {len(keys)}")
    
    print("\n🎉 核心存储模块验证通过，删除根密钥相关代码后系统功能正常！")
    
    # 检查根密钥目录是否存在
    root_key_dir = os.path.join(os.path.dirname(__file__), 'src', 'cert_manager', 'root_key')
    if os.path.exists(root_key_dir):
        print(f"\n⚠️  注意：根密钥目录仍然存在: {root_key_dir}")
        files = os.listdir(root_key_dir)
        if files:
            print(f"⚠️  根密钥目录中存在文件: {files}")
    else:
        print("\n✓ 根密钥目录不存在，符合预期")
        
except Exception as e:
    print(f"✗ 验证失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n验证完成！")
