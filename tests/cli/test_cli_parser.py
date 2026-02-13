#!/usr/bin/env python3
"""
CLI命令行参数解析测试

测试CLI命令行参数解析功能的正确性和完整性
"""

import unittest
import sys
import os
from unittest.mock import patch
from cert_manager.cli.main import CLI


class TestCLIParser(unittest.TestCase):
    """测试CLI命令行参数解析"""
    
    def setUp(self):
        """设置测试环境"""
        self.cli = CLI()
    
    def test_main_help(self):
        """测试主帮助信息"""
        with patch('sys.stdout', new_callable=lambda: None):
            with self.assertRaises(SystemExit) as cm:
                sys.argv = ['cert-cli', '--help']
                self.cli.run()
            self.assertEqual(cm.exception.code, 0)
    
    def test_key_command_help(self):
        """测试密钥命令帮助信息"""
        with patch('sys.stdout', new_callable=lambda: None):
            with self.assertRaises(SystemExit) as cm:
                sys.argv = ['cert-cli', 'key', '--help']
                self.cli.run()
            self.assertEqual(cm.exception.code, 0)
    
    def test_cert_command_help(self):
        """测试证书命令帮助信息"""
        with patch('sys.stdout', new_callable=lambda: None):
            with self.assertRaises(SystemExit) as cm:
                sys.argv = ['cert-cli', 'cert', '--help']
                self.cli.run()
            self.assertEqual(cm.exception.code, 0)
    
    def test_file_command_help(self):
        """测试文件命令帮助信息"""
        with patch('sys.stdout', new_callable=lambda: None):
            with self.assertRaises(SystemExit) as cm:
                sys.argv = ['cert-cli', 'file', '--help']
                self.cli.run()
            self.assertEqual(cm.exception.code, 0)
    
    def test_verify_command_help(self):
        """测试验证命令帮助信息"""
        with patch('sys.stdout', new_callable=lambda: None):
            with self.assertRaises(SystemExit) as cm:
                sys.argv = ['cert-cli', 'verify', '--help']
                self.cli.run()
            self.assertEqual(cm.exception.code, 0)
    
    def test_key_generate_args(self):
        """测试密钥生成命令参数"""
        # 测试RSA密钥生成参数
        test_args = ['cert-cli', 'key', 'generate', 'rsa', '--size', '2048']
        with patch('sys.argv', test_args):
            # 这里我们只是测试参数解析，不实际执行命令
            # 所以我们需要mock掉实际的命令执行
            with patch('cert_manager.cli.commands.key_commands.handle_key_command', return_value=0):
                result = self.cli.run()
                self.assertEqual(result, 0)
    
    def test_key_generate_ecc_args(self):
        """测试ECC密钥生成命令参数"""
        test_args = ['cert-cli', 'key', 'generate', 'ecc', '--curve', 'secp256r1']
        with patch('sys.argv', test_args):
            with patch('cert_manager.cli.commands.key_commands.handle_key_command', return_value=0):
                result = self.cli.run()
                self.assertEqual(result, 0)
    
    def test_cert_self_signed_args(self):
        """测试自签名证书命令参数"""
        test_args = ['cert-cli', 'cert', 'self-signed', 'private.pem', 'public.pem', '--validity', '365']
        with patch('sys.argv', test_args):
            with patch('cert_manager.cli.commands.cert_commands.handle_cert_command', return_value=0):
                result = self.cli.run()
                self.assertEqual(result, 0)
    
    def test_file_sign_args(self):
        """测试文件签名命令参数"""
        test_args = ['cert-cli', 'file', 'sign', 'test.txt', 'private.pem', '--output', 'signature.sig']
        with patch('sys.argv', test_args):
            with patch('cert_manager.cli.commands.file_commands.handle_file_command', return_value=0):
                result = self.cli.run()
                self.assertEqual(result, 0)
    
    def test_verify_cert_args(self):
        """测试证书验证命令参数"""
        test_args = ['cert-cli', 'verify', 'cert', 'cert.json', 'public.pem']
        with patch('sys.argv', test_args):
            with patch('cert_manager.cli.commands.verify_commands.handle_verify_command', return_value=0):
                result = self.cli.run()
                self.assertEqual(result, 0)
    
    def test_invalid_command(self):
        """测试无效命令"""
        test_args = ['cert-cli', 'invalid-command']
        with patch('sys.argv', test_args):
            # 当提供无效命令时，argparse会退出程序
            with self.assertRaises(SystemExit) as cm:
                self.cli.run()
            self.assertNotEqual(cm.exception.code, 0)
    
    def test_missing_subcommand(self):
        """测试缺少子命令"""
        test_args = ['cert-cli', 'key']
        with patch('sys.argv', test_args):
            with patch('builtins.print') as mock_print:
                result = self.cli.run()
                self.assertEqual(result, 1)
                mock_print.assert_called_with("请指定密钥子命令，使用 --help 查看帮助")


if __name__ == "__main__":
    unittest.main()
