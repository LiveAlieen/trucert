# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

#!/usr/bin/env python3
"""
验证命令实现
"""

import os
import json
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
            result_key = key_service.load_public_key({"file_path": args.public_key})
            if not result_key.get("success"):
                print(f"加载公钥失败: {result_key.get('error', '未知错误')}")
                return 1
            public_key = result_key["data"]
            
            # 验证证书
            result_verify = verifier_service.verify_json_cert({
                "cert_json_path": args.cert_path,
                "public_key": public_key
            })
            
            if not result_verify.get("success"):
                print(f"验证证书失败: {result_verify.get('error', '未知错误')}")
                return 1
            
            is_valid = result_verify["data"]
            
            if is_valid:
                print("证书验证成功!")
                return 0
            else:
                print("证书验证失败!")
                return 1
        except Exception as e:
            print(f"验证证书失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1
    
    @staticmethod
    def _verify_chain(args, verifier_service, key_service, cert_service):
        """验证证书链"""
        try:
            print(f"验证证书链: {args.cert_path}")
            
            # 加载父证书公钥
            result_parent_key = key_service.load_public_key({"file_path": args.parent_public_key})
            if not result_parent_key.get("success"):
                print(f"加载父证书公钥失败: {result_parent_key.get('error', '未知错误')}")
                return 1
            parent_public_key = result_parent_key["data"]
            
            # 加载证书数据
            result_cert = cert_service.load_cert({"filepath": args.cert_path})
            if not result_cert.get("success"):
                print(f"加载证书失败: {result_cert.get('error', '未知错误')}")
                return 1
            cert_data = result_cert["data"]
            
            # 验证证书链
            result_verify = verifier_service.verify_cert_chain({
                "cert_data": cert_data,
                "parent_public_key": parent_public_key
            })
            
            if not result_verify.get("success"):
                print(f"验证证书链失败: {result_verify.get('error', '未知错误')}")
                return 1
            
            is_valid = result_verify["data"]
            
            if is_valid:
                print("证书链验证成功!")
                return 0
            else:
                print("证书链验证失败!")
                return 1
        except Exception as e:
            print(f"验证证书链失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1

# 导出处理函数
handle_verify_command = VerifyCommands.handle_verify_command
