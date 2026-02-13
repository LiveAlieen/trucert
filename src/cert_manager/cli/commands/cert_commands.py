#!/usr/bin/env python3
"""
证书管理命令实现
"""

import os
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
            
            # 加载密钥
            private_key = key_service.load_private_key(args.private_key)
            public_key = key_service.load_public_key(args.public_key)
            
            # 生成证书
            cert_data = cert_service.generate_self_signed_cert(public_key, private_key, validity_days=args.validity, forward_offset=args.offset)
            
            print("自签名证书生成成功!")
            print(f"证书时间戳: {cert_data['timestamp']}")
            print(f"算法: {cert_data['cert_info']['algorithm']}")
            print(f"签名算法: {cert_data['cert_info']['signature_algorithm']}")
            print(f"存储格式: {cert_data['cert_info']['storage_formats']}")
            
            if args.output:
                # 保存证书到文件
                with open(args.output, 'w') as f:
                    import json
                    json.dump(cert_data, f, ensure_ascii=False, indent=2)
                print(f"证书已保存到: {args.output}")
            
            return 0
        except Exception as e:
            print(f"生成自签名证书失败: {str(e)}")
            return 1
    
    @staticmethod
    def _generate_secondary(args, cert_service, key_service):
        """生成二级证书"""
        try:
            print("生成二级证书...")
            
            # 加载密钥
            parent_private_key = key_service.load_private_key(args.parent_private_key)
            parent_public_key = key_service.load_public_key(args.parent_public_key)
            secondary_public_key = key_service.load_public_key(args.secondary_public_key)
            
            # 生成证书
            cert_data = cert_service.generate_secondary_cert(
                secondary_public_key, parent_private_key, parent_public_key,
                validity_days=args.validity, forward_offset=args.offset
            )
            
            print("二级证书生成成功!")
            print(f"证书时间戳: {cert_data['timestamp']}")
            print(f"算法: {cert_data['cert_info']['algorithm']}")
            print(f"签名算法: {cert_data['cert_info']['signature_algorithm']}")
            print(f"存储格式: {cert_data['cert_info']['storage_formats']}")
            print(f"是否有父证书: {'是' if cert_data['cert_info']['parent_public_key'] else '否'}")
            
            if args.output:
                # 保存证书到文件
                with open(args.output, 'w') as f:
                    import json
                    json.dump(cert_data, f, ensure_ascii=False, indent=2)
                print(f"证书已保存到: {args.output}")
            
            return 0
        except Exception as e:
            print(f"生成二级证书失败: {str(e)}")
            return 1
    
    @staticmethod
    def _list_certs(args, cert_service):
        """列出存储的证书"""
        try:
            certs = cert_service.list_certs()
            if not certs:
                print("没有存储的证书")
                return 0
            
            print("存储的证书:")
            for i, cert in enumerate(certs, 1):
                print(f"{i}. ID: {cert['id']}")
                print(f"   类型: {'自签名' if cert['issuer'] == cert['subject'] else '二级'}")
                print(f"   颁发者: {cert['issuer']}")
                print(f"   主体: {cert['subject']}")
                print(f"   有效期: {cert['valid_from']} 至 {cert['valid_to']}")
                print(f"   签名算法: {cert['signature_algorithm']}")
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
            
            cert_data = cert_service.import_cert(args.file_path)
            
            print("证书导入成功!")
            print(f"证书ID: {cert_data['id']}")
            print(f"颁发者: {cert_data['issuer']}")
            print(f"主体: {cert_data['subject']}")
            print(f"有效期: {cert_data['valid_from']} 至 {cert_data['valid_to']}")
            
            return 0
        except Exception as e:
            print(f"导入证书失败: {str(e)}")
            return 1
    
    @staticmethod
    def _export_cert(args, cert_service):
        """导出证书"""
        try:
            print(f"导出证书: {args.cert_id}")
            
            cert_data = cert_service.get_cert(args.cert_id)
            cert_service.export_cert(cert_data, args.output)
            
            print(f"证书导出成功，保存到: {args.output}")
            return 0
        except Exception as e:
            print(f"导出证书失败: {str(e)}")
            return 1
    
    @staticmethod
    def _delete_cert(args, cert_service):
        """删除证书"""
        try:
            success = cert_service.delete_cert(args.cert_id)
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