# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

#!/usr/bin/env python3
"""
证书管理命令实现
"""

import os
import json
from typing import Optional

class CertCommands:
    """证书管理命令类"""
    
    @staticmethod
    def handle_cert_command(args, cert_service, key_service):
        """处理证书相关命令"""
        if not args.cert_command:
            print("请指定证书子命令，使用 --help 查看帮助")
            return 1
        
        if args.cert_command == 'self-signed':
            return CertCommands._generate_self_signed(args, cert_service, key_service)
        elif args.cert_command == 'secondary':
            return CertCommands._generate_secondary(args, cert_service, key_service)
        elif args.cert_command == 'list':
            return CertCommands._list_certs(args, cert_service)
        elif args.cert_command == 'import':
            return CertCommands._import_cert(args, cert_service)
        elif args.cert_command == 'export':
            return CertCommands._export_cert(args, cert_service)
        elif args.cert_command == 'delete':
            return CertCommands._delete_cert(args, cert_service)
        else:
            print(f"未知的证书子命令: {args.cert_command}")
            return 1
    
    @staticmethod
    def _generate_self_signed(args, cert_service, key_service):
        """生成自签名证书"""
        try:
            print("生成自签名证书...")
            
            # 加载私钥
            result_private = key_service.load_private_key({"file_path": args.private_key, "password": None})
            if not result_private.get("success"):
                print(f"加载私钥失败: {result_private.get('error', '未知错误')}")
                return 1
            private_key = result_private["data"]
            
            # 加载公钥
            result_public = key_service.load_public_key({"file_path": args.public_key})
            if not result_public.get("success"):
                print(f"加载公钥失败: {result_public.get('error', '未知错误')}")
                return 1
            public_key = result_public["data"]
            
            # 生成证书
            result_cert = cert_service.generate_self_signed_cert({
                "public_key": public_key,
                "private_key": private_key,
                "validity_days": args.validity,
                "forward_offset": args.offset
            })
            
            if not result_cert.get("success"):
                print(f"生成自签名证书失败: {result_cert.get('error', '未知错误')}")
                return 1
            
            cert_data = result_cert["data"]
            
            print("自签名证书生成成功!")
            
            # 获取证书信息
            result_info = cert_service.get_cert_info({"cert_data": cert_data})
            if result_info.get("success"):
                cert_info = result_info["data"]
                for key, value in cert_info.items():
                    print(f"{key}: {value}")
            
            if args.output:
                # 保存证书到文件
                with open(args.output, 'w') as f:
                    json.dump(cert_data, f, ensure_ascii=False, indent=2)
                print(f"证书已保存到: {args.output}")
            
            return 0
        except Exception as e:
            print(f"生成自签名证书失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1
    
    @staticmethod
    def _generate_secondary(args, cert_service, key_service):
        """生成二级证书"""
        try:
            print("生成二级证书...")
            
            # 加载上级私钥
            result_parent_private = key_service.load_private_key({"file_path": args.parent_private_key, "password": None})
            if not result_parent_private.get("success"):
                print(f"加载上级私钥失败: {result_parent_private.get('error', '未知错误')}")
                return 1
            parent_private_key = result_parent_private["data"]
            
            # 加载上级公钥
            result_parent_public = key_service.load_public_key({"file_path": args.parent_public_key})
            if not result_parent_public.get("success"):
                print(f"加载上级公钥失败: {result_parent_public.get('error', '未知错误')}")
                return 1
            parent_public_key = result_parent_public["data"]
            
            # 加载二级公钥
            result_secondary_public = key_service.load_public_key({"file_path": args.secondary_public_key})
            if not result_secondary_public.get("success"):
                print(f"加载二级公钥失败: {result_secondary_public.get('error', '未知错误')}")
                return 1
            secondary_public_key = result_secondary_public["data"]
            
            # 生成证书
            result_cert = cert_service.generate_secondary_cert({
                "public_key": secondary_public_key,
                "parent_private_key": parent_private_key,
                "parent_public_key": parent_public_key,
                "validity_days": args.validity,
                "forward_offset": args.offset
            })
            
            if not result_cert.get("success"):
                print(f"生成二级证书失败: {result_cert.get('error', '未知错误')}")
                return 1
            
            cert_data = result_cert["data"]
            
            print("二级证书生成成功!")
            
            # 获取证书信息
            result_info = cert_service.get_cert_info({"cert_data": cert_data})
            if result_info.get("success"):
                cert_info = result_info["data"]
                for key, value in cert_info.items():
                    print(f"{key}: {value}")
            
            if args.output:
                # 保存证书到文件
                with open(args.output, 'w') as f:
                    json.dump(cert_data, f, ensure_ascii=False, indent=2)
                print(f"证书已保存到: {args.output}")
            
            return 0
        except Exception as e:
            print(f"生成二级证书失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1
    
    @staticmethod
    def _list_certs(args, cert_service):
        """列出存储的证书"""
        try:
            result = cert_service.list_certs()
            if not result.get("success"):
                print(f"列出证书失败: {result.get('error', '未知错误')}")
                return 1
            
            certs = result["data"]
            if not certs:
                print("没有存储的证书")
                return 0
            
            print("存储的证书:")
            for i, cert in enumerate(certs, 1):
                print(f"{i}. 文件名: {cert.get('filename', '未知')}")
                print(f"   路径: {cert.get('path', '未知')}")
                print(f"   类型: {cert.get('type', '未知')}")
                print()
            return 0
        except Exception as e:
            print(f"列出证书失败: {str(e)}")
            return 1
    
    @staticmethod
    def _import_cert(args, cert_service):
        """导入证书"""
        try:
            print(f"导入证书: {args.file_path}")
            
            result = cert_service.import_cert({"filepath": args.file_path})
            
            if not result.get("success"):
                print(f"导入证书失败: {result.get('error', '未知错误')}")
                return 1
            
            cert_data = result["data"]
            print("证书导入成功!")
            
            return 0
        except Exception as e:
            print(f"导入证书失败: {str(e)}")
            return 1
    
    @staticmethod
    def _export_cert(args, cert_service):
        """导出证书"""
        try:
            print(f"导出证书: {args.cert_id}")
            
            # 加载证书
            result_load = cert_service.load_cert({"filepath": args.cert_id})
            if not result_load.get("success"):
                print(f"加载证书失败: {result_load.get('error', '未知错误')}")
                return 1
            
            cert_data = result_load["data"]
            
            # 保存到输出文件
            result_save = cert_service.save_cert({"cert_data": cert_data, "filepath": args.output})
            if not result_save.get("success"):
                print(f"保存证书失败: {result_save.get('error', '未知错误')}")
                return 1
            
            print(f"证书导出成功，保存到: {args.output}")
            return 0
        except Exception as e:
            print(f"导出证书失败: {str(e)}")
            return 1
    
    @staticmethod
    def _delete_cert(args, cert_service):
        """删除证书"""
        try:
            result = cert_service.delete_cert({"filepath": args.cert_id})
            if not result.get("success"):
                print(f"删除证书失败: {result.get('error', '未知错误')}")
                return 1
            
            success = result["data"]
            if success:
                print(f"证书删除成功: {args.cert_id}")
                return 0
            else:
                print(f"证书删除失败: {args.cert_id}")
                return 1
        except Exception as e:
            print(f"删除证书失败: {str(e)}")
            return 1

# 导出处理函数
handle_cert_command = CertCommands.handle_cert_command
