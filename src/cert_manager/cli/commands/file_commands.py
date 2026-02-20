#!/usr/bin/env python3
"""
文件签名命令实现
"""

import os
import json
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
            result_key = key_service.load_private_key({"file_path": args.private_key, "password": None})
            if not result_key.get("success"):
                print(f"加载私钥失败: {result_key.get('error', '未知错误')}")
                return 1
            private_key = result_key["data"]
            
            # 签名文件
            result_sign = file_signer_service.sign_file({
                "file_path": args.file_path,
                "private_key": private_key,
                "hash_algorithm": args.hash
            })
            
            if not result_sign.get("success"):
                print(f"签名文件失败: {result_sign.get('error', '未知错误')}")
                return 1
            
            signature = result_sign["data"]
            
            if args.attach:
                # 附加签名到文件
                if args.output:
                    output_path = args.output
                else:
                    output_path = args.file_path + ".signed"
                
                result_attach = file_signer_service.attach_signature_to_file({
                    "original_file": args.file_path,
                    "signature": signature,
                    "output_file": output_path
                })
                
                if not result_attach.get("success"):
                    print(f"附加签名失败: {result_attach.get('error', '未知错误')}")
                    return 1
                
                result_path = result_attach["data"]
                print(f"文件签名成功，签名已附加到文件: {result_path}")
            else:
                # 生成单独的签名文件
                if args.output:
                    # 保存签名
                    result_save = file_signer_service.save_signature({
                        "signature": signature,
                        "file_path": args.output,
                        "original_file_path": args.file_path,
                        "hash_algorithm": args.hash
                    })
                    
                    if not result_save.get("success"):
                        print(f"保存签名失败: {result_save.get('error', '未知错误')}")
                        return 1
                    
                    print(f"文件签名成功，签名保存到: {args.output}")
                else:
                    # 输出签名到控制台
                    print("文件签名成功!")
                    print(f"签名: {signature.hex()}")
            
            return 0
        except Exception as e:
            print(f"签名文件失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1
    
    @staticmethod
    def _verify_file(args, file_signer_service, key_service):
        """验证文件签名"""
        try:
            print(f"验证文件签名: {args.file_path}")
            
            # 加载公钥
            result_key = key_service.load_public_key({"file_path": args.public_key})
            if not result_key.get("success"):
                print(f"加载公钥失败: {result_key.get('error', '未知错误')}")
                return 1
            public_key = result_key["data"]
            
            # 加载签名
            result_load = file_signer_service.load_signature({"file_path": args.signature_path})
            if not result_load.get("success"):
                print(f"加载签名失败: {result_load.get('error', '未知错误')}")
                return 1
            
            signature_data = result_load["data"]
            signature = signature_data["signature"]
            sig_hash_algorithm = signature_data["hash_algorithm"]
            
            # 使用从签名文件中获取的哈希算法
            if sig_hash_algorithm:
                hash_algorithm = sig_hash_algorithm
            else:
                hash_algorithm = args.hash
            
            # 验证签名
            result_verify = file_signer_service.verify_file_signature({
                "file_path": args.file_path,
                "signature": signature,
                "public_key": public_key,
                "hash_algorithm": hash_algorithm
            })
            
            if not result_verify.get("success"):
                print(f"验证文件签名失败: {result_verify.get('error', '未知错误')}")
                return 1
            
            is_valid = result_verify["data"]
            
            if is_valid:
                print("文件签名验证成功!")
                return 0
            else:
                print("文件签名验证失败!")
                return 1
        except Exception as e:
            print(f"验证文件签名失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1
    
    @staticmethod
    def _batch_sign(args, file_signer_service, key_service):
        """批量签名文件"""
        try:
            print(f"批量签名目录: {args.directory}")
            
            # 加载私钥
            result_key = key_service.load_private_key({"file_path": args.private_key, "password": None})
            if not result_key.get("success"):
                print(f"加载私钥失败: {result_key.get('error', '未知错误')}")
                return 1
            private_key = result_key["data"]
            
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
            output_dir = args.output if args.output else os.path.join(args.directory, "signed")
            os.makedirs(output_dir, exist_ok=True)
            
            # 批量签名
            result_batch = file_signer_service.batch_sign({
                "file_paths": files,
                "private_key": private_key,
                "output_dir": output_dir,
                "hash_algorithm": args.hash
            })
            
            if not result_batch.get("success"):
                print(f"批量签名失败: {result_batch.get('error', '未知错误')}")
                return 1
            
            results = result_batch["data"]
            
            # 显示批量签名结果
            success_count = 0
            fail_count = 0
            
            print("批量签名结果:")
            for result in results:
                if result["success"]:
                    print(f"✓ {result['file']} → {result['signature_file']}")
                    success_count += 1
                else:
                    print(f"✗ {result['file']} → {result['reason']}")
                    fail_count += 1
            
            print(f"\n总计: {success_count} 成功, {fail_count} 失败")
            
            return 0
        except Exception as e:
            print(f"批量签名失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1

# 导出处理函数
handle_file_command = FileCommands.handle_file_command
