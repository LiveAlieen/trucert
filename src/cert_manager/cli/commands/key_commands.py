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
                private_info, public_info = key_service.generate_rsa_key(args.size)
            else:
                private_info, public_info = key_service.generate_ecc_key(args.curve.upper())
            
            print("密钥生成成功!")
            print(f"私钥信息:")
            for key, value in private_info.items():
                print(f"  {key}: {value}")
            print(f"公钥信息:")
            for key, value in public_info.items():
                print(f"  {key}: {value}")
            
            if args.output:
                os.makedirs(args.output, exist_ok=True)
                # 保存密钥到文件
                key_id = private_info.get('id')
                if key_id:
                    private_key, public_key = key_service.load_key_pair(key_id)
                    private_path = os.path.join(args.output, f"private_{key_id}.pem")
                    public_path = os.path.join(args.output, f"public_{key_id}.pem")
                    key_service.save_private_key(private_key, private_path)
                    key_service.save_public_key(public_key, public_path)
                    print(f"密钥已保存到: {args.output}")
            
            return 0
        except Exception as e:
            print(f"生成密钥失败: {str(e)}")
            return 1
    
    @staticmethod
    def _list_keys(args, key_service):
        """列出存储的密钥"""
        try:
            keys = key_service.list_keys()
            if not keys:
                print("没有存储的密钥")
                return 0
            
            print("存储的密钥:")
            for i, key in enumerate(keys, 1):
                print(f"{i}. ID: {key['id']}")
                print(f"   类型: {key['type']}")
                print(f"   创建时间: {key.get('created_at', '未知')}")
                if 'private_info' in key:
                    private_info = key['private_info']
                    if 'key_size' in private_info:
                        print(f"   密钥大小: {private_info['key_size']}")
                    elif 'curve' in private_info:
                        print(f"   曲线: {private_info['curve']}")
                print()
            return 0
        except Exception as e:
            print(f"列出密钥失败: {str(e)}")
            return 1
    
    @staticmethod
    def _load_key(args, key_service):
        """加载密钥"""
        try:
            private_key, public_key = key_service.load_key_pair(args.key_id)
            private_info = key_service.get_key_info(private_key)
            public_info = key_service.get_key_info(public_key)
            
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
            private_key, public_key = key_service.load_key_pair(args.key_id)
            
            if args.type == 'private':
                key_service.save_private_key(private_key, args.output, args.password)
                print(f"私钥已保存到: {args.output}")
            else:
                key_service.save_public_key(public_key, args.output)
                print(f"公钥已保存到: {args.output}")
            return 0
        except Exception as e:
            print(f"保存密钥失败: {str(e)}")
            return 1
    
    @staticmethod
    def _delete_key(args, key_service):
        """删除密钥"""
        try:
            success = key_service.delete_key(args.key_id)
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
