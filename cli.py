#!/usr/bin/env python3
"""
TruCert CLI 入口文件

提供命令行界面，用于管理密钥、证书、文件签名和验证
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from trucert.cli.main import CLI
    
    if __name__ == '__main__':
        cli = CLI()
        sys.exit(cli.run())
        
except ImportError as e:
    print(f"导入错误: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
