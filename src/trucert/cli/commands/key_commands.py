# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

#!/usr/bin/env python3
"""
密钥管理命令实现
"""

import os
from typing import Optional

class KeyCommands:
    """密钥管理命令类"""
    
    @staticmethod
    def handle_key_command(args, key_service):
        """处理密钥相关命令"""
        if not args.key_command:
            print("请指定密钥子命令，使用 --help 查看帮助")
            return 1
        
        if args.key_command == 'generate':
            return KeyCommands._generate_key(args, key_service)
        elif args.key_command == 'list':
            return KeyCommands._list_keys(args, key_service)
        elif args.key_command == 'load':
            return KeyCommands._load_key(args, key_service)
        elif args.key_command == 'save':
            return KeyCommands._save_key(args, key_service)
        elif args.key_command == 'delete':
            return KeyCommands._delete_key(args, key_service)
        else:
            print(f"未知的密钥子命令: {args.key_command}")
            return 1
    
    @staticmethod
    def _generate_key(args, key_service):
        """生成密钥对"""
        try:
            print(f"生成{args.type.upper()}密钥对...")
            
            if args.type == 'rsa':
                result = key_service.generate_rsa_key({"key_size": args.size})
            else:
                result = key_service.generate_ecc_key({"curve": args.curve.upper()})
            
            if not result.get("success"):
                print(f"生成密钥失败: {result.get('error', '未知错误')}")
                return 1
            
            data = result["data"]
            private_info = data["private_key_info"]
            public_info = data["public_key_info"]
            key_id = data["key_id"]
            
            print("密钥生成成功!")
            print(f"私钥信息:")
            for key, value in private_info.items():
                print(f"  {key}: {value}")
            print(f"公钥信息:")
            for key, value in public_info.items():
                print(f"  {key}: {value}")
            print(f"密钥ID: {key_id}")
            
            if args.output:
                os.makedirs(args.output, exist_ok=True)
                # 保存密钥到文件
                result_load = key_service.load_key_pair({"key_id": key_id})
                if not result_load.get("success"):
                    print(f"加载密钥失败: {result_load.get('error', '未知错误')}")
                    return 1
                
                private_key = result_load["data"]["private_key"]
                public_key = result_load["data"]["public_key"]
                
                private_path = os.path.join(args.output, f"private_{key_id}.pem")
                public_path = os.path.join(args.output, f"public_{key_id}.pem")
                
                result_save_private = key_service.save_private_key({"private_key": private_key, "file_path": private_path, "password": None})
                if not result_save_private.get("success"):
                    print(f"保存私钥失败: {result_save_private.get('error', '未知错误')}")
                    return 1
                
                result_save_public = key_service.save_public_key({"public_key": public_key, "file_path": public_path})
                if not result_save_public.get("success"):
                    print(f"保存公钥失败: {result_save_public.get('error', '未知错误')}")
                    return 1
                
                print(f"密钥已保存到: {args.output}")
            
            return 0
        except Exception as e:
            print(f"生成密钥失败: {str(e)}")
            return 1
    
    @staticmethod
    def _list_keys(args, key_service):
        """列出存储的密钥"""
        try:
            result = key_service.list_keys()
            if not result.get("success"):
                print(f"列出密钥失败: {result.get('error', '未知错误')}")
                return 1
            
            keys = result["data"]
            if not keys:
                print("没有存储的密钥")
                return 0
            
            print("存储的密钥:")
            for i, key in enumerate(keys, 1):
                print(f"{i}. ID: {key['id']}")
                print(f"   类型: {key.get('type', '未知')}")
                print(f"   创建时间: {key.get('created_at', '未知')}")
                if 'key_size' in key:
                    print(f"   密钥大小: {key['key_size']}")
                elif 'curve' in key:
                    print(f"   曲线: {key['curve']}")
                print()
            return 0
        except Exception as e:
            print(f"列出密钥失败: {str(e)}")
            return 1
    
    @staticmethod
    def _load_key(args, key_service):
        """加载密钥"""
        try:
            result_load = key_service.load_key_pair({"key_id": args.key_id})
            if not result_load.get("success"):
                print(f"加载密钥失败: {result_load.get('error', '未知错误')}")
                return 1
            
            private_key = result_load["data"]["private_key"]
            public_key = result_load["data"]["public_key"]
            
            result_private_info = key_service.get_key_info({"key": private_key})
            if not result_private_info.get("success"):
                print(f"获取私钥信息失败: {result_private_info.get('error', '未知错误')}")
                return 1
            private_info = result_private_info["data"]
            
            result_public_info = key_service.get_key_info({"key": public_key})
            if not result_public_info.get("success"):
                print(f"获取公钥信息失败: {result_public_info.get('error', '未知错误')}")
                return 1
            public_info = result_public_info["data"]
            
            print(f"密钥加载成功: {args.key_id}")
            print("私钥信息:")
            for key, value in private_info.items():
                print(f"  {key}: {value}")
            print("公钥信息:")
            for key, value in public_info.items():
                print(f"  {key}: {value}")
            return 0
        except Exception as e:
            print(f"加载密钥失败: {str(e)}")
            return 1
    
    @staticmethod
    def _save_key(args, key_service):
        """保存密钥到文件"""
        try:
            result_load = key_service.load_key_pair({"key_id": args.key_id})
            if not result_load.get("success"):
                print(f"加载密钥失败: {result_load.get('error', '未知错误')}")
                return 1
            
            private_key = result_load["data"]["private_key"]
            public_key = result_load["data"]["public_key"]
            
            if args.type == 'private':
                result_save = key_service.save_private_key({"private_key": private_key, "file_path": args.output, "password": args.password})
                if not result_save.get("success"):
                    print(f"保存私钥失败: {result_save.get('error', '未知错误')}")
                    return 1
                print(f"私钥已保存到: {args.output}")
            else:
                result_save = key_service.save_public_key({"public_key": public_key, "file_path": args.output})
                if not result_save.get("success"):
                    print(f"保存公钥失败: {result_save.get('error', '未知错误')}")
                    return 1
                print(f"公钥已保存到: {args.output}")
            return 0
        except Exception as e:
            print(f"保存密钥失败: {str(e)}")
            return 1
    
    @staticmethod
    def _delete_key(args, key_service):
        """删除密钥"""
        try:
            result = key_service.delete_key({"key_id": args.key_id})
            if not result.get("success"):
                print(f"删除密钥失败: {result.get('error', '未知错误')}")
                return 1
            
            success = result["data"]
            if success:
                print(f"密钥删除成功: {args.key_id}")
                return 0
            else:
                print(f"密钥删除失败: {args.key_id}")
                return 1
        except Exception as e:
            print(f"删除密钥失败: {str(e)}")
            return 1

# 导出处理函数
handle_key_command = KeyCommands.handle_key_command
