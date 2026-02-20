#!/usr/bin/env python3
"""测试模块导入"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing imports...")
print(f"sys.path: {sys.path[:3]}")

try:
    import cert_manager
    print("✓ cert_manager imported")
    
    from cert_manager.core import KeyManager
    print("✓ KeyManager imported")
    
    from cert_manager.core import CertManager
    print("✓ CertManager imported")
    
    from cert_manager.core import FileSigner
    print("✓ FileSigner imported")
    
    from cert_manager.core import Verifier
    print("✓ Verifier imported")
    
    print("\nAll imports successful!")
except Exception as e:
    print(f"\n✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
