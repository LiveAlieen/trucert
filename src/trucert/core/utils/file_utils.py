# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

"""文件工具模块

提供文件操作相关的工具函数
"""

import os
import json
from typing import Any, Optional, Dict, List


def read_file(filepath: str, encoding: str = "utf-8") -> str:
    """读取文件内容
    
    Args:
        filepath: 文件路径
        encoding: 文件编码，默认为"utf-8"
    
    Returns:
        文件内容字符串
    """
    with open(filepath, "r", encoding=encoding) as f:
        return f.read()


def write_file(filepath: str, content: str, encoding: str = "utf-8") -> None:
    """写入文件内容
    
    Args:
        filepath: 文件路径
        content: 要写入的内容
        encoding: 文件编码，默认为"utf-8"
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, "w", encoding=encoding) as f:
        f.write(content)


def read_binary_file(filepath: str) -> bytes:
    """读取二进制文件内容
    
    Args:
        filepath: 文件路径
    
    Returns:
        文件内容字节流
    """
    with open(filepath, "rb") as f:
        return f.read()


def write_binary_file(filepath: str, content: bytes) -> None:
    """写入二进制文件内容
    
    Args:
        filepath: 文件路径
        content: 要写入的字节流
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, "wb") as f:
        f.write(content)


def read_json_file(filepath: str) -> Dict[str, Any]:
    """读取JSON文件内容
    
    Args:
        filepath: 文件路径
    
    Returns:
        JSON数据字典
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(filepath: str, data: Dict[str, Any], indent: int = 2) -> None:
    """写入JSON文件内容
    
    Args:
        filepath: 文件路径
        data: 要写入的JSON数据
        indent: 缩进空格数，默认为2
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def get_file_extension(filepath: str) -> str:
    """获取文件扩展名
    
    Args:
        filepath: 文件路径
    
    Returns:
        文件扩展名（不含点号）
    """
    return os.path.splitext(filepath)[1][1:].lower()


def get_file_name(filepath: str, with_extension: bool = True) -> str:
    """获取文件名
    
    Args:
        filepath: 文件路径
        with_extension: 是否包含扩展名，默认为True
    
    Returns:
        文件名
    """
    if with_extension:
        return os.path.basename(filepath)
    else:
        return os.path.splitext(os.path.basename(filepath))[0]


def get_directory_path(filepath: str) -> str:
    """获取文件所在目录路径
    
    Args:
        filepath: 文件路径
    
    Returns:
        目录路径
    """
    return os.path.dirname(filepath)


def ensure_directory(directory: str) -> None:
    """确保目录存在
    
    Args:
        directory: 目录路径
    """
    os.makedirs(directory, exist_ok=True)


def list_files(directory: str, pattern: Optional[str] = None) -> List[str]:
    """列出目录中的文件
    
    Args:
        directory: 目录路径
        pattern: 文件模式，可选
    
    Returns:
        文件路径列表
    """
    files = []
    
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if pattern is None or filename.endswith(pattern):
                files.append(os.path.join(root, filename))
    
    return files


def file_exists(filepath: str) -> bool:
    """检查文件是否存在
    
    Args:
        filepath: 文件路径
    
    Returns:
        文件是否存在
    """
    return os.path.isfile(filepath)


def directory_exists(directory: str) -> bool:
    """检查目录是否存在
    
    Args:
        directory: 目录路径
    
    Returns:
        目录是否存在
    """
    return os.path.isdir(directory)


def delete_file(filepath: str) -> None:
    """删除文件
    
    Args:
        filepath: 文件路径
    """
    if file_exists(filepath):
        os.remove(filepath)


def copy_file(src: str, dst: str) -> None:
    """复制文件
    
    Args:
        src: 源文件路径
        dst: 目标文件路径
    """
    import shutil
    # 确保目标目录存在
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def move_file(src: str, dst: str) -> None:
    """移动文件
    
    Args:
        src: 源文件路径
        dst: 目标文件路径
    """
    import shutil
    # 确保目标目录存在
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)