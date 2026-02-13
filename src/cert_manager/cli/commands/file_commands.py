#!/usr/bin/env python3
"""
文件签名命令实现
"""

import os
from typing import Optional

class FileCommands:
    """文件签名命令类"""
    
    @staticmethod
    def handle_file_command(args, file_signer_service, key_service):
        """处理文件签名相关命令"""
        if not args.file_command:
            print("请指定文件子命令，使用 --help 查看帮助")
            return 1
        
        if args.file_command == 'sign':
            return FileCommands._sign_file(args, file_signer_service, key_service)
        elif args.file_command == 'verify':
            return FileCommands._verify_file(args, file_signer_service, key_service)
        elif args.file_command == 'batch':
            return FileCommands._batch_sign(args, file_signer_service, key_service)
        else:
            print(f"未知的文件子命令: {args.file_command}")
            return 1
    
    @staticmethod
    def _sign_file(args, file_signer_service, key_service):
        """签名文件"""
        try:
            print(f"签名文件: {args.file_path}")
            
            # 加载私钥
            private_key = key_service.load_private_key(args.private_key)
            
            # 签名文件
            if args.attach:
                # 附加签名到文件
                result = file_signer_service.sign_file_attach(args.file_path, private_key, hash_algorithm=args.hash)
                print(f"文件签名成功，签名已附加到文件: {args.file_path}")
            else:
                # 生成单独的签名文件
                signature = file_signer_service.sign_file(args.file_path, private_key, hash_algorithm=args.hash)
                
                if args.output:
                    with open(args.output, 'wb') as f:
                        f.write(signature)
                    print(f"文件签名成功，签名保存到: {args.output}")
                else:
                    # 输出签名到控制台
                    print("文件签名成功!")
                    print(f"签名: {signature.hex()}")
            
            return 0
        except Exception as e:
            print(f"签名文件失败: {str(e)}")
            return 1
    
    @staticmethod
    def _verify_file(args, file_signer_service, key_service):
        """验证文件签名"""
        try:
            print(f"验证文件签名: {args.file_path}")
            
            # 加载公钥
            public_key = key_service.load_public_key(args.public_key)
            
            # 读取签名
            with open(args.signature_path, 'rb') as f:
                signature = f.read()
            
            # 验证签名
            is_valid = file_signer_service.verify_file(args.file_path, signature, public_key, hash_algorithm=args.hash)
            
            if is_valid:
                print("文件签名验证成功!")
                return 0
            else:
                print("文件签名验证失败!")
                return 1
        except Exception as e:
            print(f"验证文件签名失败: {str(e)}")
            return 1
    
    @staticmethod
    def _batch_sign(args, file_signer_service, key_service):
        """批量签名文件"""
        try:
            print(f"批量签名目录: {args.directory}")
            
            # 加载私钥
            private_key = key_service.load_private_key(args.private_key)
            
            # 获取目录中的文件
            files = []
            for root, _, filenames in os.walk(args.directory):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    files.append(file_path)
            
            if not files:
                print("目录中没有文件")
                return 0
            
            # 创建输出目录
            if args.output:
                os.makedirs(args.output, exist_ok=True)
            
            # 批量签名
            signed_count = 0
            for file_path in files:
                try:
                    print(f"签名文件: {file_path}")
                    signature = file_signer_service.sign_file(file_path, private_key, hash_algorithm=args.hash)
                    
                    if args.output:
                        # 保存签名到输出目录
                        filename = os.path.basename(file_path)
                        signature_path = os.path.join(args.output, f"{filename}.sig")
                        with open(signature_path, 'wb') as f:
                            f.write(signature)
                        print(f"签名保存到: {signature_path}")
                    signed_count += 1
                except Exception as e:
                    print(f"签名文件 {file_path} 失败: {str(e)}")
            
            print(f"批量签名完成，成功签名 {signed_count} 个文件")
            return 0
        except Exception as e:
            print(f"批量签名失败: {str(e)}")
            return 1

# 导出处理函数
handle_file_command = FileCommands.handle_file_command