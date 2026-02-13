"""测试工具模块

提供测试中需要的通用功能
"""

import os
import tempfile
from typing import Optional, Tuple


def create_temp_file(content: str = "", suffix: str = ".txt") -> str:
    """创建临时文件
    
    Args:
        content: 文件内容
        suffix: 文件后缀
    
    Returns:
        临时文件路径
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name


def create_temp_directory() -> str:
    """创建临时目录
    
    Returns:
        临时目录路径
    """
    return tempfile.mkdtemp()


def cleanup_temp_path(path: str) -> None:
    """清理临时路径
    
    Args:
        path: 临时路径
    """
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        import shutil
        shutil.rmtree(path, ignore_errors=True)


def get_test_data_directory() -> str:
    """获取测试数据目录
    
    Returns:
        测试数据目录路径
    """
    test_dir = os.path.dirname(__file__)
    data_dir = os.path.join(test_dir, "test_data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir
