#!/usr/bin/env python3
"""
验证命令实现
"""

import os
from typing import Optional

class VerifyCommands:
    """验证命令类"""
    
    @staticmethod
    def handle_verify_command(args, verifier_service, key_service, cert_service):
        """处理验证相关命令"""
        if not args.verify_command:
            print("请指定验证子命令，使用 --help 查看帮助")
            return 1
        
        if args.verify_command == 'cert':
            return VerifyCommands._verify_cert(args, verifier_service, key_service)
        elif args.verify_command == 'chain':
            return VerifyCommands._verify_chain(args, verifier_service, key_service, cert_service)
        else:
            print(f"未知的验证子命令: {args.verify_command}")
            return 1
    
    @staticmethod
    def _verify_cert(args, verifier_service, key_service):
        """验证证书"""
        try:
            print(f"验证证书: {args.cert_path}")
            
            # 加载公钥
            public_key = key_service.load_public_key(args.public_key)
            
            # 验证证书
            is_valid, errors = verifier_service.verify_cert(args.cert_path, public_key)
            
            if is_valid:
                print("证书验证成功!")
                return 0
            else:
                print("证书验证失败!")
                for error in errors:
                    print(f"  - {error}")
                return 1
        except Exception as e:
            print(f"验证证书失败: {str(e)}")
            return 1
    
    @staticmethod
    def _verify_chain(args, verifier_service, key_service, cert_service):
        """验证证书链"""
        try:
            print(f"验证证书链: {args.cert_path}")
            
            # 加载父证书公钥
            parent_public_key = key_service.load_public_key(args.parent_public_key)
            
            # 加载证书
            with open(args.cert_path, 'rb') as f:
                cert_data = f.read()
            
            # 验证证书链
            is_valid, errors = verifier_service.verify_cert_chain(args.cert_path, parent_public_key)
            
            if is_valid:
                print("证书链验证成功!")
                return 0
            else:
                print("证书链验证失败!")
                for error in errors:
                    print(f"  - {error}")
                return 1
        except Exception as e:
            print(f"验证证书链失败: {str(e)}")
            return 1

# 导出处理函数
handle_verify_command = VerifyCommands.handle_verify_command