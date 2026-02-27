#!/usr/bin/env python3
"""
CLI主入口文件

实现命令行参数解析和命令分发
"""

import argparse
import sys
import os
from typing import Optional

# 添加src目录到Python路径
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
src_dir = os.path.join(os.path.dirname(grandparent_dir), 'src')
sys.path.insert(0, src_dir)

try:
    from trucert.core.services import KeyService, CertService, FileSignerService, VerifierService, ConfigService
    from trucert.cli.commands import key_commands, cert_commands, file_commands, verify_commands
    from trucert.core.utils import initialize_dependencies
except ImportError as e:
    print(f"Import error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

class CLI:
    """CLI主类"""
    
    def __init__(self):
        # 初始化依赖注入容器
        initialize_dependencies()
        
        self.parser = argparse.ArgumentParser(
            prog='cert-cli',
            description='证书管理工具命令行界面',
            epilog='使用 --help 查看子命令的详细信息'
        )
        self.subparsers = self.parser.add_subparsers(
            dest='command',
            title='子命令',
            description='可用的子命令',
            help='子命令帮助'
        )
        self.key_service = KeyService()
        self.cert_service = CertService()
        self.file_signer_service = FileSignerService()
        self.verifier_service = VerifierService()
        self.config_service = ConfigService()
        self._setup_commands()
    
    def _setup_commands(self):
        """设置命令解析器"""
        # 密钥管理命令
        key_parser = self.subparsers.add_parser('key', help='密钥管理相关命令')
        key_subparsers = key_parser.add_subparsers(
            dest='key_command',
            title='密钥子命令',
            description='密钥管理相关子命令'
        )
        
        # 生成密钥
        generate_key_parser = key_subparsers.add_parser('generate', help='生成密钥对')
        generate_key_parser.add_argument('type', choices=['rsa', 'ecc'], help='密钥类型')
        generate_key_parser.add_argument('--size', type=int, default=2048, help='RSA密钥大小')
        generate_key_parser.add_argument('--curve', type=str, default='secp256r1', help='ECC曲线类型')
        generate_key_parser.add_argument('--output', type=str, help='输出目录')
        
        # 列出密钥
        list_key_parser = key_subparsers.add_parser('list', help='列出存储的密钥')
        
        # 加载密钥
        load_key_parser = key_subparsers.add_parser('load', help='加载密钥')
        load_key_parser.add_argument('key_id', help='密钥ID')
        
        # 保存密钥
        save_key_parser = key_subparsers.add_parser('save', help='保存密钥到文件')
        save_key_parser.add_argument('key_id', help='密钥ID')
        save_key_parser.add_argument('output', help='输出文件路径')
        save_key_parser.add_argument('--type', choices=['private', 'public'], default='private', help='密钥类型')
        save_key_parser.add_argument('--password', type=str, help='私钥密码')
        
        # 删除密钥
        delete_key_parser = key_subparsers.add_parser('delete', help='删除密钥')
        delete_key_parser.add_argument('key_id', help='密钥ID')
        
        # 证书管理命令
        cert_parser = self.subparsers.add_parser('cert', help='证书管理相关命令')
        cert_subparsers = cert_parser.add_subparsers(
            dest='cert_command',
            title='证书子命令',
            description='证书管理相关子命令'
        )
        
        # 生成自签名证书
        self_signed_parser = cert_subparsers.add_parser('self-signed', help='生成自签名证书')
        self_signed_parser.add_argument('private_key', help='私钥文件路径')
        self_signed_parser.add_argument('public_key', help='公钥文件路径')
        self_signed_parser.add_argument('--validity', type=int, default=365, help='有效期（天）')
        self_signed_parser.add_argument('--offset', type=int, default=0, help='时间偏移（秒）')
        self_signed_parser.add_argument('--output', type=str, help='输出文件路径')
        
        # 生成二级证书
        secondary_parser = cert_subparsers.add_parser('secondary', help='生成二级证书')
        secondary_parser.add_argument('parent_private_key', help='上级私钥文件路径')
        secondary_parser.add_argument('parent_public_key', help='上级公钥文件路径')
        secondary_parser.add_argument('secondary_public_key', help='二级公钥文件路径')
        secondary_parser.add_argument('--validity', type=int, default=365, help='有效期（天）')
        secondary_parser.add_argument('--offset', type=int, default=0, help='时间偏移（秒）')
        secondary_parser.add_argument('--output', type=str, help='输出文件路径')
        
        # 列出证书
        list_cert_parser = cert_subparsers.add_parser('list', help='列出存储的证书')
        
        # 导入证书
        import_cert_parser = cert_subparsers.add_parser('import', help='导入证书')
        import_cert_parser.add_argument('file_path', help='证书文件路径')
        
        # 导出证书
        export_cert_parser = cert_subparsers.add_parser('export', help='导出证书')
        export_cert_parser.add_argument('cert_id', help='证书ID')
        export_cert_parser.add_argument('output', help='输出文件路径')
        
        # 删除证书
        delete_cert_parser = cert_subparsers.add_parser('delete', help='删除证书')
        delete_cert_parser.add_argument('cert_id', help='证书ID')
        
        # 文件签名命令
        file_parser = self.subparsers.add_parser('file', help='文件签名相关命令')
        file_subparsers = file_parser.add_subparsers(
            dest='file_command',
            title='文件子命令',
            description='文件签名相关子命令'
        )
        
        # 签名文件
        sign_file_parser = file_subparsers.add_parser('sign', help='签名文件')
        sign_file_parser.add_argument('file_path', help='文件路径')
        sign_file_parser.add_argument('private_key', help='私钥文件路径')
        sign_file_parser.add_argument('--hash', type=str, default='sha256', help='哈希算法')
        sign_file_parser.add_argument('--output', type=str, help='签名输出文件路径')
        sign_file_parser.add_argument('--attach', action='store_true', help='将签名附加到文件')
        
        # 验证文件签名
        verify_file_parser = file_subparsers.add_parser('verify', help='验证文件签名')
        verify_file_parser.add_argument('file_path', help='文件路径')
        verify_file_parser.add_argument('signature_path', help='签名文件路径')
        verify_file_parser.add_argument('--public-key', dest='public_key', help='公钥文件路径')
        verify_file_parser.add_argument('--certificate', dest='certificate', help='证书文件路径')
        verify_file_parser.add_argument('--hash', type=str, default='sha256', help='哈希算法')
        
        # 批量签名
        batch_sign_parser = file_subparsers.add_parser('batch', help='批量签名文件')
        batch_sign_parser.add_argument('directory', help='文件目录')
        batch_sign_parser.add_argument('private_key', help='私钥文件路径')
        batch_sign_parser.add_argument('--output', type=str, help='输出目录')
        batch_sign_parser.add_argument('--hash', type=str, default='sha256', help='哈希算法')
        
        # 验证命令
        verify_parser = self.subparsers.add_parser('verify', help='验证相关命令')
        verify_subparsers = verify_parser.add_subparsers(
            dest='verify_command',
            title='验证子命令',
            description='验证相关子命令'
        )
        
        # 验证证书
        verify_cert_parser = verify_subparsers.add_parser('cert', help='验证证书')
        verify_cert_parser.add_argument('cert_path', help='证书文件路径')
        verify_cert_parser.add_argument('public_key', help='公钥文件路径')
        
        # 验证证书链
        verify_chain_parser = verify_subparsers.add_parser('chain', help='验证证书链')
        verify_chain_parser.add_argument('cert_path', help='证书文件路径')
        verify_chain_parser.add_argument('parent_public_key', help='父证书公钥文件路径')
    
    def run(self):
        """运行CLI命令"""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return 1
        
        try:
            if args.command == 'key':
                return key_commands.handle_key_command(args, self.key_service)
            elif args.command == 'cert':
                return cert_commands.handle_cert_command(args, self.cert_service, self.key_service)
            elif args.command == 'file':
                return file_commands.handle_file_command(args, self.file_signer_service, self.key_service)
            elif args.command == 'verify':
                return verify_commands.handle_verify_command(args, self.verifier_service, self.key_service, self.cert_service)
            else:
                print(f"未知命令: {args.command}")
                return 1
        except Exception as e:
            print(f"错误: {str(e)}")
            return 1

if __name__ == '__main__':
    cli = CLI()
    sys.exit(cli.run())
