#!/usr/bin/env python3
"""
测试工具和辅助函数

提供通用的测试辅助功能，如临时目录创建、测试数据生成等
"""

import os
import sys
import tempfile
import shutil
from typing import Optional

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))


def create_temp_directory() -> str:
    """
    创建临时目录
    
    Returns:
        str: 临时目录路径
    """
    return tempfile.mkdtemp()


def create_temp_file(content: str = "test content", suffix: str = None) -> str:
    """
    创建临时文件
    
    Args:
        content: 文件内容
        suffix: 文件后缀（可选）
    
    Returns:
        str: 临时文件路径
    """
    # 生成临时文件
    temp_file = generate_test_file(content)
    
    # 如果指定了后缀，重命名文件
    if suffix:
        import os
        directory = os.path.dirname(temp_file)
        filename = os.path.basename(temp_file)
        new_filename = f"{os.path.splitext(filename)[0]}{suffix}"
        new_temp_file = os.path.join(directory, new_filename)
        os.rename(temp_file, new_temp_file)
        temp_file = new_temp_file
    
    return temp_file


def cleanup_temp_path(path: str) -> None:
    """
    清理临时路径
    
    Args:
        path: 要清理的路径
    """
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except Exception:
            pass


def generate_test_file(content: str = "test content") -> str:
    """
    生成测试文件
    
    Args:
        content: 文件内容
    
    Returns:
        str: 测试文件路径
    """
    temp_dir = create_temp_directory()
    test_file = os.path.join(temp_dir, "test_file.txt")
    with open(test_file, 'w') as f:
        f.write(content)
    return test_file


def get_test_data_dir() -> str:
    """
    获取测试数据目录
    
    Returns:
        str: 测试数据目录路径
    """
    test_data_dir = os.path.join(os.path.dirname(__file__), "..", "test_data")
    os.makedirs(test_data_dir, exist_ok=True)
    return test_data_dir


def create_test_key_pair() -> tuple[str, str]:
    """
    创建测试密钥对
    
    Returns:
        tuple[str, str]: (私钥路径, 公钥路径)
    """
    from cert_manager.core.key_manager import KeyManager
    
    key_manager = KeyManager()
    private_key, public_key = key_manager.generate_rsa_key(key_size=2048, auto_save=False)
    
    temp_dir = create_temp_directory()
    private_key_path = os.path.join(temp_dir, "test_private.pem")
    public_key_path = os.path.join(temp_dir, "test_public.pem")
    
    key_manager.save_private_key(private_key, private_key_path)
    key_manager.save_public_key(public_key, public_key_path)
    
    return private_key_path, public_key_path


def create_test_cert(private_key_path: str, public_key_path: str) -> str:
    """
    创建测试证书
    
    Args:
        private_key_path: 私钥路径
        public_key_path: 公钥路径
    
    Returns:
        str: 证书路径
    """
    from cert_manager.core.cert_manager import CertManager
    from cert_manager.core.key_manager import KeyManager
    
    key_manager = KeyManager()
    cert_manager = CertManager()
    
    private_key = key_manager.load_private_key(private_key_path)
    public_key = key_manager.load_public_key(public_key_path)
    
    cert_data = cert_manager.generate_self_signed_cert(public_key, private_key, validity_days=7)
    
    temp_dir = create_temp_directory()
    cert_path = os.path.join(temp_dir, "test_cert.json")
    
    # 保存证书到文件
    with open(cert_path, 'w') as f:
        import json
        json.dump(cert_data, f, ensure_ascii=False, indent=2)
    
    return cert_path
