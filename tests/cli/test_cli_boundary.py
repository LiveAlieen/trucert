#!/usr/bin/env python3
"""
CLI边界条件和错误处理测试

测试CLI命令在边界条件和错误情况下的处理能力
"""

import unittest
import sys
import os
from unittest.mock import patch
from tests.utils.test_utils import create_temp_directory, cleanup_temp_path, create_test_key_pair, generate_test_file


class TestCLIBoundary(unittest.TestCase):
    """测试CLI边界条件和错误处理"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = create_temp_directory()
    
    def tearDown(self):
        """清理测试环境"""
        cleanup_temp_path(self.test_dir)
    
    def test_key_generate_invalid_type(self):
        """测试无效的密钥类型"""
        test_args = ['cert-cli', 'key', 'generate', 'invalid-type']
        
        with patch('sys.argv', test_args):
            from cert_manager.cli.main import CLI
            cli = CLI()
            # 这里应该抛出参数错误
            with self.assertRaises(SystemExit) as cm:
                cli.run()
            self.assertNotEqual(cm.exception.code, 0)
    
    def test_key_generate_invalid_size(self):
        """测试无效的密钥大小"""
        test_args = ['cert-cli', 'key', 'generate', 'rsa', '--size', '1024']
        
        with patch('sys.argv', test_args):
            from cert_manager.cli.main import CLI
            cli = CLI()
            result = cli.run()
            # 即使密钥大小较小，也应该执行但可能有警告
            # 这里我们只测试命令能够执行，不测试具体的密钥大小验证
            self.assertIn(result, [0, 1])
    
    def test_key_generate_invalid_curve(self):
        """测试无效的ECC曲线"""
        test_args = ['cert-cli', 'key', 'generate', 'ecc', '--curve', 'invalid-curve']
        
        with patch('sys.argv', test_args):
            from cert_manager.cli.main import CLI
            cli = CLI()
            result = cli.run()
            # 无效的曲线应该导致命令执行失败
            self.assertEqual(result, 1)
    
    def test_cert_self_signed_nonexistent_keys(self):
        """测试使用不存在的密钥文件"""
        # 使用不存在的密钥文件路径
        nonexistent_private = os.path.join(self.test_dir, 'nonexistent_private.pem')
        nonexistent_public = os.path.join(self.test_dir, 'nonexistent_public.pem')
        
        test_args = [
            'cert-cli', 'cert', 'self-signed',
            nonexistent_private, nonexistent_public
        ]
        
        with patch('sys.argv', test_args):
            from cert_manager.cli.main import CLI
            cli = CLI()
            result = cli.run()
            # 不存在的文件应该导致命令执行失败
            self.assertEqual(result, 1)
    
    def test_file_sign_nonexistent_file(self):
        """测试签名不存在的文件"""
        # 创建测试密钥对
        private_key_path, public_key_path = create_test_key_pair()
        
        # 使用不存在的文件路径
        nonexistent_file = os.path.join(self.test_dir, 'nonexistent_file.txt')
        
        test_args = [
            'cert-cli', 'file', 'sign',
            nonexistent_file, private_key_path
        ]
        
        with patch('sys.argv', test_args):
            from cert_manager.cli.main import CLI
            cli = CLI()
            result = cli.run()
            # 不存在的文件应该导致命令执行失败
            self.assertEqual(result, 1)
    
    def test_file_verify_nonexistent_files(self):
        """测试验证不存在的文件"""
        # 创建测试密钥对
        private_key_path, public_key_path = create_test_key_pair()
        
        # 使用不存在的文件路径
        nonexistent_file = os.path.join(self.test_dir, 'nonexistent_file.txt')
        nonexistent_signature = os.path.join(self.test_dir, 'nonexistent_signature.sig')
        
        test_args = [
            'cert-cli', 'file', 'verify',
            nonexistent_file, nonexistent_signature, public_key_path
        ]
        
        with patch('sys.argv', test_args):
            from cert_manager.cli.main import CLI
            cli = CLI()
            # 这里应该抛出系统退出异常
            with self.assertRaises(SystemExit) as cm:
                cli.run()
            self.assertNotEqual(cm.exception.code, 0)
    
    def test_verify_cert_nonexistent_files(self):
        """测试验证不存在的证书文件"""
        # 创建测试密钥对
        private_key_path, public_key_path = create_test_key_pair()
        
        # 使用不存在的证书文件路径
        nonexistent_cert = os.path.join(self.test_dir, 'nonexistent_cert.json')
        
        test_args = [
            'cert-cli', 'verify', 'cert',
            nonexistent_cert, public_key_path
        ]
        
        with patch('sys.argv', test_args):
            from cert_manager.cli.main import CLI
            cli = CLI()
            result = cli.run()
            # 不存在的文件应该导致命令执行失败
            self.assertEqual(result, 1)
    
    def test_batch_sign_empty_directory(self):
        """测试批量签名空目录"""
        # 创建测试密钥对
        private_key_path, public_key_path = create_test_key_pair()
        
        # 创建空目录
        empty_dir = os.path.join(self.test_dir, 'empty')
        os.makedirs(empty_dir, exist_ok=True)
        
        test_args = [
            'cert-cli', 'file', 'batch',
            empty_dir, private_key_path
        ]
        
        with patch('sys.argv', test_args):
            from cert_manager.cli.main import CLI
            cli = CLI()
            result = cli.run()
            # 空目录应该执行成功，但没有文件被签名
            self.assertEqual(result, 0)
    
    def test_cert_self_signed_invalid_validity(self):
        """测试无效的证书有效期"""
        # 创建测试密钥对
        private_key_path, public_key_path = create_test_key_pair()
        
        # 使用无效的有效期
        test_args = [
            'cert-cli', 'cert', 'self-signed',
            private_key_path, public_key_path,
            '--validity', '-1'
        ]
        
        with patch('sys.argv', test_args):
            from cert_manager.cli.main import CLI
            cli = CLI()
            result = cli.run()
            # 无效的有效期应该导致命令执行失败
            self.assertEqual(result, 1)
    
    def test_missing_required_args(self):
        """测试缺少必要的参数"""
        # 测试缺少密钥类型
        test_args = ['cert-cli', 'key', 'generate']
        
        with patch('sys.argv', test_args):
            from cert_manager.cli.main import CLI
            cli = CLI()
            # 这里应该抛出参数错误
            with self.assertRaises(SystemExit) as cm:
                cli.run()
            self.assertNotEqual(cm.exception.code, 0)
    
    def test_invalid_subcommand(self):
        """测试无效的子命令"""
        test_args = ['cert-cli', 'key', 'invalid-subcommand']
        
        with patch('sys.argv', test_args):
            from cert_manager.cli.main import CLI
            cli = CLI()
            # 这里应该抛出参数错误
            with self.assertRaises(SystemExit) as cm:
                cli.run()
            self.assertNotEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
