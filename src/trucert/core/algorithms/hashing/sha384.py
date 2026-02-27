# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

"""SHA384哈希算法模块"""

import hashlib
from .. import HashingAlgorithm


class SHA384Algorithm(HashingAlgorithm):
    """SHA384哈希算法实现"""
    
    name = "SHA384"
    version = "1.0"
    description = "SHA384哈希算法，生成384位哈希值"
    
    def calculate(self, data: bytes) -> bytes:
        """计算SHA384哈希值
        
        Args:
            data: 要计算哈希的数据
            
        Returns:
            哈希值（字节形式）
        """
        hash_obj = hashlib.sha384()
        hash_obj.update(data)
        return hash_obj.digest()
    
    def calculate_hex(self, data: bytes) -> str:
        """计算SHA384哈希值（十六进制字符串）
        
        Args:
            data: 要计算哈希的数据
            
        Returns:
            哈希值的十六进制字符串
        """
        hash_obj = hashlib.sha384()
        hash_obj.update(data)
        return hash_obj.hexdigest()
